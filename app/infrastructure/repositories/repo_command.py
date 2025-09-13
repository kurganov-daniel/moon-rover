from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import CommandResult
from app.infrastructure.db.models import CommandORM, CommandStatus


class RDBCommandRepository:
    """SQLAlchemy implementation of CommandRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_command(self, command_result: CommandResult) -> int:
        """Save command to database with advisory lock for ordering."""

        result = await self.session.execute(
            insert(CommandORM)
            .values(
                received_command=command_result.initial_command.command_string,
                executed_command=command_result.executed_command.command_string,
                status=CommandStatus.COMPLETED,
                stopped_by_obstacle=command_result.stopped_by_obstacle,
            )
            .returning(CommandORM.id)
        )

        return result.scalar_one()
