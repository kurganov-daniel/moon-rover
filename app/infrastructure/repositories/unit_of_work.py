from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.repo_command import RDBCommandRepository
from app.infrastructure.repositories.repo_position import RDBPositionRepository


class AsyncUoW:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.commands = RDBCommandRepository(session)
        self.positions = RDBPositionRepository(session)

    async def __aenter__(self) -> AsyncUoW:
        await self.session.execute(text('SELECT pg_advisory_xact_lock(1)'))
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self.session.rollback()
        else:
            await self.session.commit()
