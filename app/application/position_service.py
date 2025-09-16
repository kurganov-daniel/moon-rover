import logging
from typing import Protocol

from app.domain.entities import Position

logger = logging.getLogger(__name__)


class PositionRepository(Protocol):
    async def get_current_position(self) -> Position | None: ...


class StartPositionProvider(Protocol):
    def get_start_position(self) -> Position: ...


class PositionService:
    def __init__(self, repo: PositionRepository, start_provider: StartPositionProvider):
        self._repo = repo
        self._start_provider = start_provider

    async def get_current_position(self) -> Position:
        logger.info('Retrieving current position')
        position = await self._repo.get_current_position()
        if position is None:
            logger.info('No current position found, using start position')
            position = self._start_provider.get_start_position()
        else:
            logger.info(
                'Current position found: x=%d, y=%d, direction=%s',
                position.x,
                position.y,
                position.direction.name,
            )
        return position
