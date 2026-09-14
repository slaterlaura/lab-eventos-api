from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.post("/upload-teste")
async def upload_teste(arquivo: UploadFile = File(...)):
    conteudo = await arquivo.read()

    return {
        "nome_original": arquivo.filename,
        "content_type": arquivo.content_type,
        "tamanho_bytes": len(conteudo),
    }
