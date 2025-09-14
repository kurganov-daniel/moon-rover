import json
from pathlib import Path

import pytest

from app.infrastructure.repositories.repo_obstacle import JSONObstacleRepository


@pytest.fixture()
def obstacle_file(tmp_path: Path):
    """Create a temporary obstacles json file and return its path."""
    data = [[1, 2], [3, 4]]
    file_path = tmp_path / 'obstacles.json'
    file_path.write_text(json.dumps(data))
    return file_path


def test_get_obstacles_happy_path(obstacle_file: Path):
    repo = JSONObstacleRepository(json_path=obstacle_file)

    obstacles_first = repo.get_obstacles()

    expected_coords = {(1, 2), (3, 4)}

    # First read returns expected coordinates regardless of object identity
    assert {o.coordinates() for o in obstacles_first} == expected_coords

    # Second read should use cache and still return equal coordinates (identity not required)
    obstacles_second = repo.get_obstacles()
    assert {o.coordinates() for o in obstacles_second} == expected_coords


def test_get_obstacles_file_not_found(tmp_path: Path):
    missing_path = tmp_path / 'missing.json'
    repo = JSONObstacleRepository(json_path=missing_path)
    with pytest.raises(FileNotFoundError):
        repo.get_obstacles()
