from typing import Protocol

from app.domain.entities import Command, CommandResult, Obstacle, Position
from app.domain.services import execute_commands


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
        initial_command = Command(command)
        obstacles: set[Obstacle] = self._obstacle_repo.get_obstacles()
        current_position: Position = await self._get_current_position()

        command_result: CommandResult = execute_commands(
            command=initial_command,
            start_position=current_position,
            obstacles=obstacles,
        )

        async with self._uow as uow:
            command_id = await uow.commands.save_command(command_result)
            path = getattr(command_result, 'path', None)
            if path:
                await uow.positions.save_positions_bulk(command_id, path)

        return command_result

    async def _get_current_position(self) -> Position:
        position = await self._position_repo.get_current_position()
        if position is None:
            position = self._start_position_provider.get_start_position()
        return position
