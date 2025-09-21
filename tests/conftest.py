
import pytest


@pytest.fixture
def sample_position():
    """Sample position for tests"""
    from app.domain.entities import Direction, Point, Position

    return Position(Point(1, 2), Direction.EAST)


@pytest.fixture
def sample_command():
    """Sample command for tests"""
    from app.domain.entities import Command

    return Command('F')


@pytest.fixture
def sample_command_result(sample_position, sample_command):
    """Sample command result for tests"""
    from app.domain.entities import CommandResult

    return CommandResult(
        executed_command=sample_command,
        initial_command=sample_command,
        final_position=sample_position,
        stopped_by_obstacle=False,
        path=[sample_position],
    )


@pytest.fixture
def mock_command_repo():
    """Mock CommandRepository"""
    from unittest.mock import AsyncMock

    from app.application.command_service import CommandRepository

    return AsyncMock(spec=CommandRepository)


@pytest.fixture
def mock_position_repo():
    """Mock PositionRepository"""
    from unittest.mock import AsyncMock

    from app.application.position_service import PositionRepository

    return AsyncMock(spec=PositionRepository)


@pytest.fixture
def mock_obstacle_repo():
    """Mock ObstacleRepository"""
    from unittest.mock import Mock

    from app.application.command_service import ObstacleRepository

    mock = Mock(spec=ObstacleRepository)
    mock.get_obstacles.return_value = set()
    return mock


@pytest.fixture
def mock_start_provider():
    """Mock StartPositionProvider"""
    from unittest.mock import Mock

    from app.application.command_service import StartPositionProvider
    from app.domain.entities import Direction, Point, Position

    mock = Mock(spec=StartPositionProvider)
    mock.get_start_position.return_value = Position(Point(0, 0), Direction.NORTH)
    return mock


@pytest.fixture
def mock_health_checker():
    """Mock HealthChecker"""
    from unittest.mock import AsyncMock

    from app.application.health_service import HealthChecker

    return AsyncMock(spec=HealthChecker)


@pytest.fixture
def mock_uow():
    """Mock Unit of Work"""
    from unittest.mock import AsyncMock

    uow = AsyncMock()
    uow.commands = AsyncMock()
    uow.positions = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


@pytest.fixture
def mock_session():
    """Mock database session for infrastructure tests"""
    from unittest.mock import AsyncMock

    return AsyncMock()
