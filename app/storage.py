import os
from pathlib import Path

from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER", "cartazes")

_service_client: BlobServiceClient | None = None


def _container_client():
    global _service_client

    if not CONNECTION_STRING:
        raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING não está definida.")

    if _service_client is None:
        _service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)

    return _service_client.get_container_client(CONTAINER)


def nome_do_cartaz(evento_id: int, extensao: str) -> str:
    return f"eventos/{evento_id}/cartaz{extensao}"


def enviar_arquivo(nome_do_blob: str, conteudo: bytes, content_type: str) -> str:
    blob_client = _container_client().get_blob_client(nome_do_blob)

    blob_client.upload_blob(
        conteudo,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type),
    )

    return blob_client.url
