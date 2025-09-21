from unittest.mock import AsyncMock, Mock

from app.domain.entities import Command, CommandResult, Direction, Point, Position
from app.infrastructure.repositories.repo_command import RDBCommandRepository


async def test_save_command_returns_new_id():
    session = AsyncMock()
    result_mock = Mock()
    result_mock.scalar_one.return_value = 99
    session.execute.return_value = result_mock

    repo = RDBCommandRepository(session)

    command_result = CommandResult(
        executed_command=Command('F'),
        initial_command=Command('F'),
        final_position=Position(Point(0, 1), Direction.NORTH),
        stopped_by_obstacle=False,
        path=[],
    )

    new_id = await repo.save_command(command_result)

    assert new_id == 99
    session.execute.assert_called_once()
