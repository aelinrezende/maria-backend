"""Exceções HTTP personalizadas alinhadas aos handlers esperados pela API.

Cada exceção herda de `Exception` (e não diretamente de `HTTPException`) para permitir
um pipeline centralizado que traduz essas exceções em respostas HTTP.

Campos comuns:
- message: mensagem principal (pode já ser traduzida OU um código que será traduzido futuramente)
- status_code: código HTTP associado
    (Caso a mensagem seja um código de tradução, ela mesma será resolvida externamente.)
"""
from __future__ import annotations

from typing import Any


class HttpException(Exception):
    """Base para exceções HTTP de domínio.

    Não expõe diretamente detalhes internos para evitar vazamento de informação.
    """

    status_code: int = 500
    default_message: str = "Erro interno do servidor"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)
        self.message = message or self.default_message

    def to_dict(self) -> dict[str, Any]:
        """Converte a exceção em um dicionário para resposta JSON."""
        return {
            "message": self.message,
            "statusCode": self.status_code,
        }


class BadRequestException(HttpException):
    """Erro de requisição malformada ou parâmetros inválidos (HTTP 400)."""
    status_code = 400
    default_message = "Requisição inválida"


class UnauthorizedException(HttpException):
    """Falha de autenticação: token ausente, expirado ou inválido (HTTP 401)."""
    status_code = 401
    default_message = "Não autenticado"


class ForbiddenException(HttpException):
    """Usuário autenticado, porém sem permissão para o recurso (HTTP 403)."""
    status_code = 403
    default_message = "Acesso negado"


class NotFoundException(HttpException):
    """Recurso solicitado não foi encontrado (HTTP 404)."""
    status_code = 404
    default_message = "Recurso não encontrado"


class ConflictException(HttpException):
    """Conflito de estado atual x operação solicitada (HTTP 409)."""
    status_code = 409
    default_message = "Conflito ao processar a requisição"


class TooManyRequestsException(HttpException):
    """Limite de requisições excedido para a janela de tempo (HTTP 429)."""
    status_code = 429
    default_message = "Muitas requisições - tente novamente mais tarde"


class InternalServerException(HttpException):
    """Erro inesperado no servidor (HTTP 500)."""
    status_code = 500
    default_message = "Erro interno do servidor"
