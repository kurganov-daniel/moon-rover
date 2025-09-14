from unittest.mock import AsyncMock

import pytest

from app.application.health_service import HealthChecker, HealthStatusService


# Fixtures
@pytest.fixture
def health_service(mock_health_checker):
    """Create HealthStatusService instance with mock"""
    return HealthStatusService(db_checker=mock_health_checker)


# Tests for basic health check functionality
@pytest.mark.parametrize(
    'db_status,expected_result',
    [
        (True, {'database_connected': True}),
        (False, {'database_connected': False}),
    ],
)
async def test_health_check_with_database_status(
    health_service, mock_health_checker, db_status, expected_result
):
    """Test health check with different database statuses"""

    mock_health_checker.get_health_status.return_value = db_status

    result = await health_service()

    assert result == expected_result
    mock_health_checker.get_health_status.assert_called_once()


async def test_health_check_database_exception(health_service, mock_health_checker):
    """Test health check when database checker raises exception"""

    mock_health_checker.get_health_status.side_effect = Exception(
        'Database connection failed'
    )

    with pytest.raises(Exception) as exc_info:
        await health_service()

    assert str(exc_info.value) == 'Database connection failed'
    mock_health_checker.get_health_status.assert_called_once()


async def test_health_service_multiple_calls(health_service, mock_health_checker):
    """Test that health service can be called multiple times"""

    mock_health_checker.get_health_status.side_effect = [True, False, True]

    result1 = await health_service()
    assert result1 == {'database_connected': True}

    result2 = await health_service()
    assert result2 == {'database_connected': False}

    result3 = await health_service()
    assert result3 == {'database_connected': True}

    # Verify checker was called three times
    assert mock_health_checker.get_health_status.call_count == 3


async def test_health_service_with_different_checkers():
    """Test health service with different health checkers"""

    checker1 = AsyncMock(spec=HealthChecker)
    checker2 = AsyncMock(spec=HealthChecker)

    checker1.get_health_status.return_value = True
    checker2.get_health_status.return_value = False

    service1 = HealthStatusService(checker1)
    service2 = HealthStatusService(checker2)

    result1 = await service1()
    result2 = await service2()

    assert result1 == {'database_connected': True}
    assert result2 == {'database_connected': False}

    checker1.get_health_status.assert_called_once()
    checker2.get_health_status.assert_called_once()


@pytest.mark.parametrize('test_value', [True, False, 'healthy'])
async def test_health_check_returns_correct_format(
    health_service, mock_health_checker, test_value
):
    """Test that health check always returns dict with correct format"""

    mock_health_checker.get_health_status.return_value = test_value

    result = await health_service()

    assert isinstance(result, dict)
    assert 'database_connected' in result
    assert result['database_connected'] == test_value
