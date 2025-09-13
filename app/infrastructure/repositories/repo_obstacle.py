from __future__ import annotations

import json
import os
from pathlib import Path

from app.domain.entities import Obstacle


class JSONObstacleRepository:
    """Loads obstacles as coordinate pairs from a JSON file.

    The JSON file must contain a top-level list where each item is a 2-length
    list/tuple of integers: [[x, y], ...]. The repository returns a set of
    unique coordinate tuples.
    """

    def __init__(self, json_path: str | Path | None = None):
        if json_path is None:
            json_path = os.getenv('OBSTACLES_JSON_PATH', '/config/obstacles.json')
        self._path = Path(json_path)
        self._cache: set[Obstacle] | None = None

    def get_obstacles(self) -> set[Obstacle]:
        """Read obstacles from the JSON file and return as a set of tuples.

        Raises:
            FileNotFoundError: If the JSON file does not exist.
            ValueError: If the JSON content has an invalid structure.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        if self._cache is not None:
            return self._cache

        if not self._path.exists():
            raise FileNotFoundError(f'Obstacles JSON file not found: {self._path}')

        with self._path.open('r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError('Obstacles JSON must be a list of [x, y] pairs')

        obstacles: set[Obstacle] = set()
        for item in data:
            if not isinstance(item, list | tuple) or len(item) != 2:
                raise ValueError('Each obstacle must be a 2-item list/tuple [x, y]')

            x, y = item
            if not isinstance(x, int) or not isinstance(y, int):
                raise ValueError('Obstacle coordinates must be integers')

            obstacles.add(Obstacle(x=x, y=y))

        self._cache = obstacles
        return obstacles

    def invalidate_cache(self) -> None:
        self._cache = None
