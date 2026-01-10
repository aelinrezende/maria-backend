from typing import TYPE_CHECKING

from fastapi import UploadFile

from backend.models.document import Document
from backend.modules.document.document_dto import (
    DocumentIngestRequest,
    DocumentIngestResponse,
)
from backend.services.converter.markdown import document_to_markdown
from backend.services.converter.metadata_extractor import MetadataExtractor

if TYPE_CHECKING:
    from backend.modules.document.document_hub import DocumentHub


async def ingest_file(
    hub: "DocumentHub",
    document_file: UploadFile,
    dto: DocumentIngestRequest,
) -> None:
    """Ingere um arquivo, criando documento e chunks com embeddings."""

    # 1. Converte arquivo para Markdown
    metadata: MetadataExtractor = document_to_markdown(
        document_file
    )

    dto.title = dto.title or metadata.title or "Sem título"
    dto.meta.update(metadata.metadata or {})

    # 2. Processa com Smart Chunker
    chunked_pages = hub.smart_chunker.chunk_intelligently(
        metadata.pages, dto.kind
    )

    # 3. Cria o documento no banco
    document = hub.repository.insert(Document(**dto.model_dump()))

    # 4. Cria os chunks com embeddings
    saved_chunks = await hub.chunk_hub.handlers.create_chunks_with_embeddings(
        hub.chunk_hub, document.id, chunked_pages
    )

    await hub.unit_of_work.commit()

    return DocumentIngestResponse(
        **document.model_dump(),
        total_chunks=len(saved_chunks),
    )
