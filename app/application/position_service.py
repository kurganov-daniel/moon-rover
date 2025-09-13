from typing import Protocol

from app.domain.entities import Position


class PositionRepository(Protocol):
    async def get_current_position(self) -> Position | None: ...


class StartPositionProvider(Protocol):
    def get_start_position(self) -> Position: ...


class PositionService:
    def __init__(self, repo: PositionRepository, start_provider: StartPositionProvider):
        self._repo = repo
        self._start_provider = start_provider

    async def get_current_position(self) -> Position:
        position = await self._repo.get_current_position()
        if position is None:
            position = self._start_provider.get_start_position()
        return position
