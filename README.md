# Lab Eventos

API e frontend para cadastro de eventos do campus, com upload de cartaz.

**Aplicação:** https://ambitious-water-04533f10f.5.azurestaticapps.net/

**API (backend):** https://lab-eventos-laura-f8esasgpc9bqh9bf.brazilsouth-01.azurewebsites.net/docs

## Estrutura

| Pasta | O que é |
|---|---|
| `app/` | Backend FastAPI + SQLAlchemy (publicado no Azure App Service) |
| `frontend/` | Frontend React + Vite (publicado no Azure Static Web Apps) |

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Status da API e do banco |
| GET | `/eventos` | Lista os eventos |
| POST | `/eventos` | Cria um evento |
| GET | `/eventos/{id}` | Busca um evento |
| POST | `/eventos/{id}/cartaz` | Envia o cartaz (JPEG, PNG ou WebP, até 2 MB) |
| DELETE | `/eventos/{id}` | Remove um evento |

## Rodando localmente

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp app/.env.example app/.env   # ajuste as variáveis
fastapi dev app/main.py
```

Variáveis de ambiente:

- `DATABASE_URL` — padrão `sqlite:///./eventos.db`
- `AZURE_STORAGE_CONNECTION_STRING` — conexão do Azure Blob Storage
- `AZURE_STORAGE_CONTAINER` — container dos cartazes (ex.: `cartazes`)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

A URL da API é definida em `VITE_API_URL` (`frontend/.env` para desenvolvimento, `frontend/.env.production` para o build publicado).

## Deploy

- **Frontend:** GitHub Actions publica no Static Web Apps a cada push na `main`.
- **Backend:** publicado no App Service pela extensão Azure App Service do VS Code, a partir da raiz do projeto.
