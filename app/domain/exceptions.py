from app.domain.entities import Point


class MissionException(Exception):
    """Base exception for mission-related errors"""

    pass


class LandingObstacleException(MissionException):
    """Exception raised when obstacle is detected at landing position"""

    def __init__(self, position: Point):
        coords = position.coordinates() if isinstance(position, Point) else position
        self.position = coords
        super().__init__(
            f'Cannot start lunar mission: obstacle detected at landing position {coords}. Mission aborted for safety.'
        )
