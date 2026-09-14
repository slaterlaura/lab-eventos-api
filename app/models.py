from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Evento(Base):
    """Esta classe vira a tabela `eventos` no banco."""

    __tablename__ = "eventos"

    # primary_key=True já faz o banco gerar o id em sequência.
    # Some o nosso `proximo_id` global da versão em memória.
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # nullable=False é o NOT NULL: o banco recusa o registro sem este campo.
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    local: Mapped[str] = mapped_column(String(120), nullable=False)
    vagas: Mapped[int] = mapped_column(Integer, nullable=False)
    cartaz_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        return f"<Evento id={self.id} nome={self.nome!r}>"