"""Tests for CommandService"""

from unittest.mock import Mock

import pytest

from app.application.command_service import (
    CommandService,
)
from app.domain.entities import (
    Command,
    CommandResult,
    Direction,
    Obstacle,
    Point,
    Position,
)
from app.domain.exceptions import LandingObstacleException


# Fixtures
@pytest.fixture
def command_service(
    mock_command_repo,
    mock_obstacle_repo,
    mock_position_repo,
    mock_start_provider,
    mock_uow,
):
    """Create CommandService instance with all mocks"""
    return CommandService(
        repo=mock_command_repo,
        obstacle_repo=mock_obstacle_repo,
        position_repo=mock_position_repo,
        start_position_provider=mock_start_provider,
        uow=mock_uow,
    )


# Tests for command execution with existing position
async def test_execute_command_success_with_existing_position(
    command_service,
    mock_position_repo,
    mock_uow,
    sample_position,
    sample_command_result,
):
    """Test successful command execution with existing position"""

    mock_position_repo.get_current_position.return_value = sample_position
    mock_uow.commands.save_command.return_value = 123

    # Mock execute_commands function
    with pytest.MonkeyPatch().context() as m:
        mock_execute = Mock(return_value=sample_command_result)
        m.setattr('app.application.command_service.execute_commands', mock_execute)

        result = await command_service.execute_command('F')

        assert result == sample_command_result
        mock_position_repo.get_current_position.assert_called_once()
        mock_uow.commands.save_command.assert_called_once_with(sample_command_result)
        mock_uow.positions.save_positions_bulk.assert_called_once_with(
            123, [sample_position]
        )


async def test_execute_command_success_with_start_position(
    command_service, mock_position_repo, mock_start_provider, mock_uow
):
    """Test successful command execution when no current position exists"""

    start_pos = Position(Point(0, 0), Direction.NORTH)
    mock_position_repo.get_current_position.return_value = None
    mock_start_provider.get_start_position.return_value = start_pos

    result_with_start = CommandResult(
        executed_command=Command('F'),
        initial_command=Command('F'),
        final_position=Position(Point(0, 1), Direction.NORTH),
        stopped_by_obstacle=False,
        path=[Position(Point(0, 1), Direction.NORTH)],
    )

    mock_uow.commands.save_command.return_value = 456

    with pytest.MonkeyPatch().context() as m:
        mock_execute = Mock(return_value=result_with_start)
        m.setattr('app.application.command_service.execute_commands', mock_execute)

        result = await command_service.execute_command('F')

        assert result == result_with_start
        mock_position_repo.get_current_position.assert_called_once()
        mock_start_provider.get_start_position.assert_called_once()
        mock_execute.assert_called_once()

        # Verify the execute_commands was called with start position
        call_args = mock_execute.call_args
        assert call_args[1]['start_position'] == start_pos


async def test_execute_command_with_obstacles(
    command_service, mock_obstacle_repo, mock_position_repo, mock_uow
):
    """Test command execution with obstacles present"""

    obstacles = {Obstacle(2, 3), Obstacle(4, 5)}
    mock_obstacle_repo.get_obstacles.return_value = obstacles
    mock_position_repo.get_current_position.return_value = Position(
        Point(1, 1), Direction.NORTH
    )

    result_with_obstacles = CommandResult(
        executed_command=Command('FF'),
        initial_command=Command('FFF'),
        final_position=Position(Point(1, 3), Direction.NORTH),
        stopped_by_obstacle=True,
        path=[
            Position(Point(1, 2), Direction.NORTH),
            Position(Point(1, 3), Direction.NORTH),
        ],
    )

    mock_uow.commands.save_command.return_value = 789

    with pytest.MonkeyPatch().context() as m:
        mock_execute = Mock(return_value=result_with_obstacles)
        m.setattr('app.application.command_service.execute_commands', mock_execute)

        result = await command_service.execute_command('FFF')

        assert result == result_with_obstacles
        assert result.stopped_by_obstacle is True
        mock_execute.assert_called_once()

        # Verify obstacles were passed to execute_commands
        call_args = mock_execute.call_args
        assert call_args[1]['obstacles'] == obstacles


async def test_execute_command_landing_obstacle_exception(
    command_service, mock_position_repo
):
    """Test that LandingObstacleException is raised directly"""

    mock_position_repo.get_current_position.return_value = Position(
        Point(1, 1), Direction.NORTH
    )

    landing_exception = LandingObstacleException((1, 1))

    with pytest.MonkeyPatch().context() as m:
        mock_execute = Mock(side_effect=landing_exception)
        m.setattr('app.application.command_service.execute_commands', mock_execute)

        with pytest.raises(LandingObstacleException) as exc_info:
            await command_service.execute_command('F')

        assert exc_info.value.position == (1, 1)
        assert exc_info.value == landing_exception


async def test_execute_command_no_path_in_result(
    command_service, mock_position_repo, mock_uow
):
    """Test command execution when result has no path attribute"""

    mock_position_repo.get_current_position.return_value = Position(
        Point(0, 0), Direction.NORTH
    )

    # Create result without path
    result_no_path = CommandResult(
        executed_command=Command(''),
        initial_command=Command('F'),
        final_position=Position(Point(0, 0), Direction.NORTH),
        stopped_by_obstacle=False,
        path=None,
    )

    mock_uow.commands.save_command.return_value = 999

    with pytest.MonkeyPatch().context() as m:
        mock_execute = Mock(return_value=result_no_path)
        m.setattr('app.application.command_service.execute_commands', mock_execute)

        result = await command_service.execute_command('')

        assert result == result_no_path
        mock_uow.commands.save_command.assert_called_once_with(result_no_path)
        # Should not call save_positions_bulk when path is None
        mock_uow.positions.save_positions_bulk.assert_not_called()


async def test_get_current_position_exists(command_service, mock_position_repo):
    """Test _get_current_position when position exists"""

    existing_position = Position(Point(5, 7), Direction.WEST)
    mock_position_repo.get_current_position.return_value = existing_position

    result = await command_service._get_current_position()

    assert result == existing_position
    mock_position_repo.get_current_position.assert_called_once()


async def test_get_current_position_none_returns_start(
    command_service, mock_position_repo, mock_start_provider
):
    """Test _get_current_position when no position exists, returns start position"""

    start_position = Position(Point(10, 15), Direction.SOUTH)
    mock_position_repo.get_current_position.return_value = None
    mock_start_provider.get_start_position.return_value = start_position

    result = await command_service._get_current_position()

    assert result == start_position
    mock_position_repo.get_current_position.assert_called_once()
    mock_start_provider.get_start_position.assert_called_once()
