from app.domain.entities import Direction, Point, Position
from app.infrastructure.repositories.repo_position import StartPositionEnvSettings


def test_get_start_position_from_env(monkeypatch):
    monkeypatch.setenv('START_POSITION_X', '5')
    monkeypatch.setenv('START_POSITION_Y', '7')
    monkeypatch.setenv('START_DIRECTION', 'EAST')

    settings = StartPositionEnvSettings()
    pos = settings.get_start_position()

    assert pos == Position(Point(5, 7), Direction.EAST)
