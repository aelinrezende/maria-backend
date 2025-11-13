"""Handler para ingestão de documentos com extração automática via LLM."""

import json
from typing import TYPE_CHECKING

from fastapi import UploadFile
from loguru import logger

from backend.constants.prompts import METADATA_EXTRACTION_PROMPT, RAG_SYSTEM_PROMPT
from backend.exceptions import BadRequestException, InternalServerException
from backend.integrations.llm.factory import LLMFactory
from backend.integrations.llm.models import GeminiConfig
from backend.models.document import Document
from backend.modules.document.document_dto import (
    AIDocumentIngestResponse,
    DocumentIngestMetadata,
)
from backend.services.chunking.smart_chunker import SmartChunker
from backend.services.converter import document_to_markdown
from backend.services.converter.metadata_extractor import (
    MetadataExtractor,
    extract_initial_pages,
)

if TYPE_CHECKING:
    from backend.modules.document.document_service import DocumentService


async def ingest_file_by_ai(
    hub: "DocumentService",
    document_file: UploadFile,
) -> AIDocumentIngestResponse:
    """
    Processa ingestão de arquivo com extração automática de metadados via LLM.

    Args:
        hub: Instância do DocumentService com acesso ao LLM e serviços
        document_file: Arquivo para upload
        source: Fonte do documento

    Returns:
        AIDocumentIngestResponse: Documento criado com metadados extraídos
    """
    logger.info(
        f"Iniciando ingestão via LLM do arquivo: {document_file.filename}"
    )

    # 1. Converte arquivo para Markdown
    metadata_extractor: MetadataExtractor = document_to_markdown(document_file)

    # 2. Extrai conteúdo das primeiras páginas para análise via LLM
    initial_content = extract_initial_pages(
        metadata_extractor.pages,
        max_pages=3,
        max_chars=8000
    )

    # 3. Extrai metadados via LLM
    extracted_metadata = await _extract_metadata(initial_content, document_file.filename)

    # 4. Verifica se o documento foi rejeitado pelo LLM
    if extracted_metadata.should_reject or not extracted_metadata.content:
        logger.warning(
            f"Documento rejeitado pelo LLM: {document_file.filename}"
        )

        raise BadRequestException("DOCUMENT_REJECTED_BY_AI")

    content = extracted_metadata.content

    # 5. Cria objeto documento com metadados extraídos
    document = hub.repository.insert(
        Document(
            **content.model_dump(),
            meta={
                **(metadata_extractor.metadata or {}),
                "date": content.date,
            }
        )
    )

    # 6. Processa com Smart Chunker
    smart_chunker = SmartChunker()

    chunked_pages = smart_chunker.chunk_intelligently(
        metadata_extractor.pages, document.kind
    )

    # 7. Cria os chunks com embeddings
    saved_chunks = await hub.chunk_service.create_chunks_with_embeddings(
        document.id, chunked_pages
    )

    await hub.unit_of_work.commit()

    logger.info(
        f"Documento {document.id} ingerido com sucesso via LLM: {len(saved_chunks)} chunks"
    )

    return AIDocumentIngestResponse(
        document_id=document.id,
        extracted_metadata=extracted_metadata,
        total_chunks=len(saved_chunks),
    )


async def _extract_metadata(
    text_content: str,
    filename: str,
) -> DocumentIngestMetadata:
    """
    Extrai metadados de um documento usando LLM.

    Args:
        text_content: Conteúdo texto do documento para análise

    Returns:
        DocumentIngestMetadata: Metadados extraídos pelo LLM
    """
    try:
        logger.info("Iniciando extração de metadados via LLM")

        llm = LLMFactory.create_provider(
            "gemini", GeminiConfig(model="gemini-2.5-flash-lite")
        )

        prompt = METADATA_EXTRACTION_PROMPT.format(
            document_content=text_content,
            filename=filename
        )

        response = await llm.complete_message(
            system_prompt=RAG_SYSTEM_PROMPT,
            message=prompt,
            temperature=0.1,
            as_json=True,
        )

        metadata = DocumentIngestMetadata(**json.loads(response))

        if metadata.content:
            logger.info(
                f"Metadados extraídos: título={metadata.content.title}, "
            )

        return metadata

    except Exception as exception:
        logger.error(f"Erro ao extrair metadados: {exception}")
        raise InternalServerException(
            "METADATA_EXTRACTION_FAILED"
        ) from exception
