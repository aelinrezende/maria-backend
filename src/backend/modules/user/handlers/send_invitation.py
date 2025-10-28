
from datetime import datetime
from textwrap import dedent
from typing import TYPE_CHECKING

from backend.core.config import settings
from backend.exceptions.http_exceptions import ConflictException
from backend.models.user import User
from backend.modules.auth.auth_dto import InviteRequest
from backend.modules.user.user_enums import UserStatus
from backend.utils import date, random

if TYPE_CHECKING:
    from backend.modules.user.user_service import UserService


async def send_invitation(
    hub: "UserService",
    request: InviteRequest,
) -> bool:
    """
    Handler principal para envio de convites.

    Args:
        user_service: Instância do UserService
        name: Nome do convidado
        email: E-mail do convidado

    Returns:
        bool: True se enviado com sucesso

    Raises:
        ConflictException: Se e-mail já está em uso
    """
    # Verificar se e-mail já está em uso
    existing_user = await hub.repository.find_by_email(request.email)

    if existing_user:
        raise ConflictException("EMAIL_ALREADY_IN_USE")

    # Gerar código e data de expiração
    invitation_code = random.generate_code()
    expiration_date = date.add_days(settings.INVITATION_CODE_EXPIRE_DAYS)

    # Criar usuário convidado
    invited_user = User(
        **request.model_dump(),
        status=UserStatus.INVITED,
        invitation_code=invitation_code,
        invitation_code_expiration_date=expiration_date
    )

    # Salvar usuário no banco
    await hub.create(invited_user.model_dump())

    # Enviar e-mail de convite
    await _send_invitation_email(
        hub,
        user=invited_user,
        invitation_code=invitation_code,
        expiration_date=expiration_date
    )

    return True


async def _send_invitation_email(
    hub: "UserService",
    user: User,
    invitation_code: str,
    expiration_date: datetime
) -> bool:
    """
    Envia e-mail de convite para novo usuário.

    Args:
        hub: Instância do UserService
        user: Instância do usuário convidado
        invitation_code: Código de convite
        expiration_date: Data de expiração do convite

    Returns:
        bool: True se enviado com sucesso
    """

    subject = "🎉 Você foi convidado para a plataforma Mar.IA"

    # Formatar data de expiração
    expiration_text = expiration_date.strftime("%d/%m/%Y às %H:%M")

    # Construir corpo do e-mail
    body = dedent(f"""
      Olá, {user.name}!

      Você foi convidado(a) para acessar a plataforma Mar.IA.<br><br>

      <b>📧 Seu código de convite:</b>
      <a href="{settings.FRONT_USER_URL}/onboarding/1?code={invitation_code}">Acessar</a><br><br>
      <b>⏰ Validade:</b> {expiration_text}"""
    ).strip()

    return await hub.mailgun.send_email(
        to=user.email,
        subject=subject,
        body=body
    )
