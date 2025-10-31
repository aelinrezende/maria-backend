"""DTOs relacionados à autenticação"""

from pydantic import EmailStr, Field

from backend.modules.base.base_dto import BaseRequest


class InviteRequest(BaseRequest):
    """Request para convite de usuário"""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nome completo do convidado"
    )

    email: EmailStr = Field(
        ...,
        max_length=255,
        description="Endereço de e-mail válido do convidado"
    )


class ValidateInviteRequest(BaseRequest):
    """Request para validação de código de convite"""

    invitation_code: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Código de convite a ser validado"
    )
