"""
Serviço para automação de migrations do Alembic
"""

import asyncio
from datetime import datetime

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.core.config import settings
from backend.core.database import DatabaseConnection
from backend.core.migrations.models import MigrationResult


class MigrationRunner:
    """Serviço para gerenciar migrations automáticas usando Alembic API"""

    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
        self.alembic_cfg = self._get_alembic_config()

    def _get_alembic_config(self) -> Config:
        """Configuração do Alembic usando settings do projeto"""

        config = Config("alembic.ini")
        config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

        return config

    async def check_pending_migrations(self) -> int:
        """
        Verifica se há migrations pendentes

        Returns:
            int: Número de migrations pendentes
        """
        try:

            async with self.connection.session.begin():
                # Obter revisão atual do banco
                result = await self.connection.session.execute(
                    text("SELECT version_num FROM alembic_version LIMIT 1")
                )
                current_revision_row = result.fetchone()
                current_revision = current_revision_row[0] if current_revision_row else None

                logger.info(
                    f"Current database revision: {current_revision}"
                )

                # Se não há tabela alembic_version, todas as migrations estão pendentes
                if current_revision is None:
                    logger.warning(
                        "No alembic_version table found - all migrations are pending"
                    )

                    return self._count_total_migrations()

                # Obter última revisão disponível
                latest_revision = self._get_latest_revision()

                if current_revision == latest_revision:
                    logger.info("Database is up to date")

                    return 0
                else:
                    pending_count = self._count_migrations_after(
                        current_revision
                    )

                    logger.info(f"Found {pending_count} pending migrations")

                    return pending_count

        except SQLAlchemyError as exception:
            logger.error(f"Database error checking migrations: {exception}")

            return 0

        except Exception as exception:
            logger.error(f"Error checking migrations: {exception}")

            return 0

    def _get_latest_revision(self) -> str:
        """Obtém a última revisão disponível nos arquivos de migration"""

        script_dir = ScriptDirectory.from_config(self.alembic_cfg)
        head = script_dir.get_current_head()
        return head or "None"

    def _count_migrations_after(self, current_revision: str) -> int:
        """Conta migrations após uma revisão específica"""
        script_dir = ScriptDirectory.from_config(self.alembic_cfg)
        revisions = script_dir.walk_revisions("head", current_revision)

        return sum(1 for _ in revisions)

    def _count_total_migrations(self) -> int:
        """Conta o total de migrations disponíveis"""

        script_dir = ScriptDirectory.from_config(self.alembic_cfg)
        revisions = list(script_dir.walk_revisions())

        return len(revisions)

    async def apply_migrations(self) -> MigrationResult:
        """
        Aplica migrations pendentes

        Returns:
            MigrationResult: Resultado da operação
        """
        pending_count = await self.check_pending_migrations()

        if not pending_count:
            return MigrationResult(
                success=True,
                message="No pending migrations",
                applied_count=0,
                pending_count=0,
                duration_seconds=0.0
            )

        start_time = datetime.now()

        try:
            logger.info("Starting automatic migrations check")

            # Executar upgrade do Alembic em thread separada para não bloquear
            loop = asyncio.get_event_loop()

            await loop.run_in_executor(
                None,
                self._run_alembic_upgrade
            )

            duration = (datetime.now() - start_time).total_seconds()

            result = MigrationResult(
                success=True,
                message=f"Successfully applied {pending_count} migrations",
                applied_count=pending_count,
                pending_count=0,
                duration_seconds=duration
            )

            logger.info(
                f"Migrations completed successfully in {duration:.2f}s"
            )

            return result

        except Exception as exception:
            duration = (datetime.now() - start_time).total_seconds()
            error_msg = f"Migration failed: {str(exception)}"

            logger.error(f"{error_msg} (after {duration:.2f}s)")

            return MigrationResult(
                success=False,
                message="Migration failed",
                applied_count=0,
                pending_count=pending_count if 'pending_count' in locals() else 0,
                duration_seconds=duration,
                error_details=str(exception)
            )

    def _run_alembic_upgrade(self):
        """Executa comando upgrade do Alembic"""
        try:
            command.upgrade(self.alembic_cfg, "head")
        except Exception as e:
            logger.error(f"Alembic upgrade command failed: {e}")
            raise
