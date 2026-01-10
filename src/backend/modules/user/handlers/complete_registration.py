"""
Handler para finalização de cadastro de usuário.

Implementa a lógica completa de finalização de cadastro, incluindo
validação de convite, hashing de senha e geração de tokens JWT.
"""

from typing import TYPE_CHECKING

from backend.exceptions.http_exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from backend.models.session import Session
from backend.models.user import User
from backend.modules.auth.auth_dto import CompleteRegistrationRequest
from backend.modules.session.session_enums import SessionStatus
from backend.modules.user.user_enums import UserStatus
from backend.utils.date import is_past
from backend.utils.jwt import create_user_token
from backend.utils.password import hash_password

if TYPE_CHECKING:
    from backend.modules.user.user_hub import UserHub


async def complete_registration(
    hub: "UserHub",
    invitation_code: str,
    request: CompleteRegistrationRequest
) -> Session:
    """
    Finaliza o cadastro de usuário convocado.

    Args:
        hub: Instância do UserHub
        request: Dados de finalização de cadastro

    Returns:
        Session: Dados da sessão criada para o usuário

    Raises:
        NotFoundException: Se código de convite não for encontrado
        BadRequestException: Se código estiver expirado ou inválido
        ConflictException: Se usuário já completou cadastro
    """
    # 1. Busca usuário pelo código de convite
    user = await hub.repository.find_by_invitation_code(invitation_code)

    if not user or not user.invitation_code:
        raise NotFoundException("CODE_NOT_FOUND")

    # 2. Verifica se o código está expirado
    if is_past(user.invitation_code_expiration_date):
        raise BadRequestException("CODE_EXPIRED")

    # 3. Verifica se usuário ainda tem status INVITED
    if user.status != UserStatus.INVITED:
        raise ConflictException("REGISTRATION_ALREADY_COMPLETED")

    # 4. Faz hash da senha de forma segura
    hashed_password = hash_password(request.password)

    # 5. Atualiza dados do usuário
    update_data = User(
        name=request.name,
        pronouns=request.pronouns,
        password=hashed_password,
        status=UserStatus.ACTIVE,
        invitation_code=None,
        invitation_code_expiration_date=None,
    )

    updated_user = await hub.update(user.id, update_data)

    # 6. Gera token JWT para o usuário
    access_token = create_user_token(updated_user.id)

    # 7. Cria sessão para o usuário
    session = Session(
        user=updated_user,
        token=access_token,
        status=SessionStatus.ACTIVE
    )

    hub.session_repository.insert(session)

    await hub.unit_of_work.commit()

    # 8. Retorna sessão criada
    return session
