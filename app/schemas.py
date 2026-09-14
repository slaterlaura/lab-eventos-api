from datetime import date

from pydantic import BaseModel, Field


class EventoCreate(BaseModel):
    """O que o cliente ENVIA no POST."""
    nome: str = Field(min_length=3, max_length=100)
    data: date
    local: str = Field(min_length=3, max_length=120)
    vagas: int = Field(ge=1, le=1000)


class EventoResponse(BaseModel):
    """O que a API DEVOLVE. Tem `id`, que o cliente não manda."""
    id: int
    nome: str
    data: date
    local: str
    vagas: int
    cartaz_url: str | None = None
