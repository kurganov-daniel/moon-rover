from unittest.mock import Mock

from app.domain.entities import Direction, Point, Position
from app.infrastructure.repositories.repo_position import RDBPositionRepository


async def test_get_current_position_found(mock_session):
    # Prepare dummy ORM object
    dummy_orm = Mock(coord_x=2, coord_y=3, direction=Direction.WEST)
    result_mock = Mock()
    result_mock.scalar_one_or_none.return_value = dummy_orm
    mock_session.execute.return_value = result_mock

    repo = RDBPositionRepository(mock_session)
    pos = await repo.get_current_position()

    assert pos == Position(Point(2, 3), Direction.WEST)
    mock_session.execute.assert_called_once()


async def test_get_current_position_none(mock_session):
    result_mock = Mock()
    result_mock.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = result_mock

    repo = RDBPositionRepository(mock_session)
    pos = await repo.get_current_position()

    assert pos is None


async def test_save_positions_bulk_empty(mock_session):
    repo = RDBPositionRepository(mock_session)
    await repo.save_positions_bulk(1, [])

    mock_session.execute.assert_not_called()


async def test_save_positions_bulk_inserts_payload(mock_session):
    repo = RDBPositionRepository(mock_session)

    positions = [
        Position(Point(0, 0), Direction.NORTH),
        Position(Point(1, 1), Direction.SOUTH),
    ]

    await repo.save_positions_bulk(42, positions)

    # Ensure execute was called once and inspect second positional argument (payload)
    mock_session.execute.assert_called_once()
    args, _kwargs = mock_session.execute.call_args  # call_args returns (args, kwargs)
    # args[1] is the payload list we passed to execute
    payload = args[1]
    assert len(payload) == len(positions)
    for p_dict, p_obj in zip(payload, positions, strict=False):
        assert p_dict['coord_x'] == p_obj.x
        assert p_dict['coord_y'] == p_obj.y
        assert p_dict['direction'] == p_obj.direction
        assert p_dict['command_id'] == 42
