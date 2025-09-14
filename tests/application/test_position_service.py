"""Tests for PositionService"""

import pytest

from app.application.position_service import (
    PositionService,
)
from app.domain.entities import Direction, Point, Position


# Fixtures
@pytest.fixture
def position_service(mock_position_repo, mock_start_provider):
    """Create PositionService instance with mocks"""
    return PositionService(repo=mock_position_repo, start_provider=mock_start_provider)


async def test_get_current_position_exists(position_service, mock_position_repo):
    """Test get_current_position when position exists in repository"""

    existing_position = Position(Point(5, 7), Direction.WEST)
    mock_position_repo.get_current_position.return_value = existing_position

    result = await position_service.get_current_position()

    assert result == existing_position
    mock_position_repo.get_current_position.assert_called_once()


async def test_get_current_position_none_returns_start(
    position_service, mock_position_repo, mock_start_provider
):
    """Test get_current_position when no position exists, returns start position"""

    start_position = Position(Point(10, 15), Direction.SOUTH)
    mock_position_repo.get_current_position.return_value = None
    mock_start_provider.get_start_position.return_value = start_position

    result = await position_service.get_current_position()

    assert result == start_position
    mock_position_repo.get_current_position.assert_called_once()
    mock_start_provider.get_start_position.assert_called_once()
