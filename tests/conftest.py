import asyncio
import base64
import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app


@pytest.fixture(scope='session')
def event_loop():
    """Create event loop for entire test session"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def test_engine():
    """Create test DB engine for entire session"""
    engine = create_async_engine(
        os.environ['DATABASE_URL'],
        echo=False,
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0,
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope='function')
async def test_session(test_engine):
    """Create test session for each test with rollback"""
    try:
        async with test_engine.begin() as connection:
            async_session = sessionmaker(
                connection, class_=AsyncSession, expire_on_commit=False, autoflush=False
            )
            async with async_session() as session:
                yield session
                # Automatic rollback happens when exiting context
    except Exception:
        # In case of error just skip
        async_session = sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session


@pytest.fixture(autouse=True)
async def setup_test_dependencies(test_session):
    """Setup dependencies for all tests"""

    from app.infrastructure.db.engine import get_session
    from app.main import app

    async def get_test_session():
        return test_session

    # Override DB dependency
    app.dependency_overrides[get_session] = get_test_session

    yield

    app.dependency_overrides.clear()


# Fixtures for API integration tests
@pytest.fixture
async def async_client():
    """Fixture for asynchronous HTTP client"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client


@pytest.fixture
def valid_api_key() -> str:
    """Valid API key for tests"""
    return os.getenv('API_KEY', '8AqBJfp91OavAcM')


@pytest.fixture
def invalid_api_key() -> str:
    """Invalid API key for tests"""
    return 'invalid-key'


@pytest.fixture
def auth_headers_valid(valid_api_key: str) -> dict:
    """HTTP headers with valid basic authorization"""

    credentials = base64.b64encode(f'user:{valid_api_key}'.encode()).decode()
    return {'Authorization': f'Basic {credentials}'}


@pytest.fixture
def auth_headers_invalid(invalid_api_key: str) -> dict:
    """HTTP headers with invalid basic authorization"""
    credentials = base64.b64encode(f'user:{invalid_api_key}'.encode()).decode()
    return {'Authorization': f'Basic {credentials}'}


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


# Fixtures for repository mocks
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
