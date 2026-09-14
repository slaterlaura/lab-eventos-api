from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import app.models as models
import app.storage as storage
from app.database import Base, engine, get_db
from app.schemas import EventoCreate, EventoResponse

EXTENSAO_POR_TIPO = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

TAMANHO_MAXIMO_BYTES = 2 * 1024 * 1024  # 2 MB

ORIGENS_PERMITIDAS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Cria as tabelas que ainda não existem.
#
# ATENÇÃO: create_all NÃO altera tabelas já criadas. Se você mudar uma
# coluna depois, ele ignora silenciosamente. Em produção isso se resolve
# com migrations (Alembic). Para o laboratório, apagar o eventos.db e
# rodar de novo é suficiente.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Eventos do Campus",
    description="Laboratório da Aula 06 — agora com banco de dados",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def para_resposta(evento: models.Evento) -> EventoResponse:
    return EventoResponse(
        id=evento.id,
        nome=evento.nome,
        data=evento.data,
        local=evento.local,
        vagas=evento.vagas,
        cartaz_url=storage.url_com_sas(evento.cartaz_url) if evento.cartaz_url else None,
    )


@app.get("/")
async def raiz():
    return {"mensagem": "API de Eventos do Campus", "docs": "/docs"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check agora também confirma que o banco responde.

    Se o banco cair, a rota falha e o Azure percebe que a aplicação não
    está saudável — em vez de continuar mandando tráfego para uma API
    que só devolve erro 500.
    """
    total = db.query(models.Evento).count()
    return {"status": "ok", "banco": "conectado", "eventos_cadastrados": total}


@app.get("/eventos", response_model=list[EventoResponse])
async def listar_eventos(db: Session = Depends(get_db)):
    """`db.query(...).all()` substituiu o `return eventos` da lista."""
    return [para_resposta(evento) for evento in db.query(models.Evento).all()]


@app.post(
    "/eventos",
    response_model=EventoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar_evento(evento: EventoCreate, db: Session = Depends(get_db)):
    """
    Três linhas que substituem o `eventos.append()`:

        db.add()      coloca o objeto na sessão (ainda não gravou)
        db.commit()   confirma a transação — AGORA gravou
        db.refresh()  recarrega o objeto com o id que o banco gerou

    Esquecer o commit é o erro mais comum: o código roda, não dá erro
    nenhum, e o dado não aparece.
    """
    novo = models.Evento(**evento.model_dump())

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return para_resposta(novo)


@app.get("/eventos/{evento_id}", response_model=EventoResponse)
async def buscar_evento(evento_id: int, db: Session = Depends(get_db)):
    """O laço `for` da versão em memória virou um filtro no banco."""
    evento = (
        db.query(models.Evento)
        .filter(models.Evento.id == evento_id)
        .first()
    )

    if evento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento {evento_id} não encontrado",
        )

    return para_resposta(evento)


@app.post("/eventos/{evento_id}/cartaz", response_model=EventoResponse)
async def enviar_cartaz(
    evento_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Valida o tipo antes de ler o arquivo e o tamanho antes de chamar o Azure —
    ordem crescente de custo: consulta ao banco, comparação de string, leitura
    em memória e só então a chamada de rede.
    """
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()

    if evento is None:
        raise HTTPException(status_code=404, detail=f"Evento {evento_id} não encontrado")

    if arquivo.content_type not in EXTENSAO_POR_TIPO:
        raise HTTPException(
            status_code=415,
            detail=f"Tipo {arquivo.content_type!r} não aceito.",
        )

    conteudo = await arquivo.read()

    if len(conteudo) > TAMANHO_MAXIMO_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo com {len(conteudo)} bytes; o limite é {TAMANHO_MAXIMO_BYTES}.",
        )

    url = storage.enviar_arquivo(
        nome_do_blob=storage.nome_do_cartaz(evento_id, EXTENSAO_POR_TIPO[arquivo.content_type]),
        conteudo=conteudo,
        content_type=arquivo.content_type,
    )

    evento.cartaz_url = url
    db.commit()
    db.refresh(evento)

    return para_resposta(evento)


@app.delete("/eventos/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_evento(evento_id: int, db: Session = Depends(get_db)):
    """
    204 No Content: deu certo e não há corpo para devolver.

    DELETE é idempotente no resultado final — depois da primeira chamada
    o evento não existe mais, e é isso que importa. Ainda assim devolvemos
    404 na segunda chamada, para o cliente saber que não havia nada ali.
    """
    evento = (
        db.query(models.Evento)
        .filter(models.Evento.id == evento_id)
        .first()
    )

    if evento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento {evento_id} não encontrado",
        )

    db.delete(evento)
    db.commit()
