from io import BytesIO

from fastapi import UploadFile


def buffer_file(file: UploadFile, chunk_size: int = 1024) -> BytesIO:
    """Converte um UploadFile do FastAPI em um BytesIO em memória."""
    buffer = BytesIO()

    while chunk := file.file.read(chunk_size):
        buffer.write(chunk)

    buffer.seek(0)

    return buffer
