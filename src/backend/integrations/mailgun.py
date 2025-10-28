from typing import Optional

import httpx
from loguru import logger
from wireup import service

from backend.core.config import settings


@service(lifetime="scoped")
class MailGun:
    """Classe simples para integração com Mailgun usando httpx assíncrono"""

    def __init__(self):
        self.api_key = settings.MAILGUN_API_KEY
        self.domain = settings.MAILGUN_DOMAIN
        self.base_url = f"{settings.MAILGUN_API_URL}/{self.domain}/messages"
        self.from_email = f"noreply@{self.domain}"

    # TODO: Adicionar template de email
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Envia um email simples via Mailgun

        :param to: Email do destinatário
        :param subject: Assunto do email
        :param body: Corpo do email (texto simples)
        :param from_email: Email remetente (opcional)
        :return: True se enviado com sucesso, False caso contrário
        """
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "from": from_email or self.from_email,
                    "to": to,
                    "subject": subject,
                    "html": body
                }

                response = await client.post(
                    self.base_url,
                    data=data,
                    auth=("api", self.api_key),
                    timeout=30.0
                )

                if 200 <= response.status_code < 300:
                    return True

                logger.error(
                    f"Erro ao enviar email: {response.status_code} - {response.text}"
                )

                return False

        except Exception as e:
            logger.error(f"Erro na integração com Mailgun: {str(e)}")
            return False
