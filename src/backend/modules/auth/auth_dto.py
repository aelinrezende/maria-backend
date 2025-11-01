"""DTOs relacionados à autenticação"""

from typing import Optional

from pydantic import EmailStr, Field

from backend.core.validators import StrongPassword
from backend.modules.base.base_dto import BaseRequest, ModelBase
from backend.modules.user.user_dto import UserResponse


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


class CompleteRegistrationRequest(BaseRequest):
    """Request para finalização de cadastro de usuário"""

    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nome completo do usuário"
    )

    pronouns: Optional[str] = Field(
        None,
        max_length=20,
        description="Pronomes preferidos (ex: ele/dele, ela/dela, etc.)"
    )

    password: StrongPassword = Field(
        ...,
        max_length=128,
        description="Senha forte (mínimo 8 caracteres com maiúscula, número e especial)"
    )


class CompleteRegistrationResponse(ModelBase):
    """Response para finalização bem-sucedida de cadastro"""

    access_token: str = Field(
        ...,
        description="Token JWT de acesso (expira em 7 dias)"
    )

    user: UserResponse = Field(
        ...,
        description="Dados do usuário recém-cadastrado"
    )
