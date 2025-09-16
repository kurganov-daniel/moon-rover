import logging
from typing import Protocol

from app.domain.entities import Command, CommandResult, Obstacle, Position
from app.domain.services import execute_commands

logger = logging.getLogger(__name__)


class PositionRepository(Protocol):
    async def get_current_position(self) -> Position | None: ...


class StartPositionProvider(Protocol):
    def get_start_position(self) -> Position: ...


class CommandRepository(Protocol):
    async def save_command(self, command_result: CommandResult) -> None: ...


class ObstacleRepository(Protocol):
    def get_obstacles(self) -> set[Obstacle]: ...


class CommandService:
    def __init__(
        self,
        repo: CommandRepository,
        obstacle_repo: ObstacleRepository,
        position_repo: PositionRepository,
        start_position_provider: StartPositionProvider,
        uow,
    ):
        self._repo = repo
        self._obstacle_repo = obstacle_repo
        self._position_repo = position_repo
        self._start_position_provider = start_position_provider
        self._uow = uow

    async def execute_command(self, command: str) -> CommandResult:
        logger.info('Starting command execution: %s', command)

        initial_command = Command(command)
        obstacles: set[Obstacle] = self._obstacle_repo.get_obstacles()
        current_position: Position = await self._get_current_position()

        logger.info(
            'Executing from position: x=%d, y=%d, direction=%s',
            current_position.x,
            current_position.y,
            current_position.direction.name,
        )

        command_result: CommandResult = execute_commands(
            command=initial_command,
            start_position=current_position,
            obstacles=obstacles,
        )

        logger.info(
            'Command execution completed: final position x=%d, y=%d, direction=%s, stopped_by_obstacle=%s',
            command_result.final_position.x,
            command_result.final_position.y,
            command_result.final_position.direction.name,
            command_result.stopped_by_obstacle,
        )

        async with self._uow as uow:
            command_id = await uow.commands.save_command(command_result)
            logger.info('Command result saved with ID: %s', command_id)
            path = getattr(command_result, 'path', None)
            if path:
                await uow.positions.save_positions_bulk(command_id, path)
                logger.info('Position path saved: %d positions', len(path))

        return command_result

    async def _get_current_position(self) -> Position:
        position = await self._position_repo.get_current_position()
        if position is None:
            logger.info('No current position found, using start position')
            position = self._start_position_provider.get_start_position()
        else:
            logger.info('Current position retrieved from repository')
        return position
