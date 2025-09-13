from dataclasses import dataclass
from enum import IntEnum

# Direction vectors: (dx, dy) for each direction
DIR_VECTORS = ((0, 1), (1, 0), (0, -1), (-1, 0))


class Direction(IntEnum):
    """Robot direction using mathematical convention"""
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


@dataclass(frozen=True)
class Point:
    """Point on the lunar surface"""
    x: int
    y: int

    def coordinates(self) -> tuple[int, int]:
        return (self.x, self.y)

    def __eq__(self, value: 'Point') -> bool:
        return self.x == value.x and self.y == value.y


@dataclass(frozen=True)
class Obstacle(Point):
    pass


@dataclass(frozen=True)
class Position:
    """Robot position on the lunar surface"""

    point: Point
    direction: Direction

    @property
    def x(self) -> int:
        """X coordinate"""
        return self.point.x

    @property
    def y(self) -> int:
        """Y coordinate"""
        return self.point.y

    def move_forward(self) -> 'Position':
        """Move one step forward in current direction"""
        dx, dy = DIR_VECTORS[self.direction]
        new_point = Point(self.point.x + dx, self.point.y + dy)
        return Position(new_point, self.direction)

    def move_backward(self) -> 'Position':
        """Move one step backward from current direction"""
        dx, dy = DIR_VECTORS[self.direction]
        new_point = Point(self.point.x - dx, self.point.y - dy)
        return Position(new_point, self.direction)

    def turn_left(self) -> 'Position':
        """Turn 90 degrees left"""
        new_direction = Direction((self.direction - 1) % 4)
        return Position(self.point, new_direction)

    def turn_right(self) -> 'Position':
        """Turn 90 degrees right"""
        new_direction = Direction((self.direction + 1) % 4)
        return Position(self.point, new_direction)

    def coordinates(self) -> tuple[int, int]:
        """Get coordinates as tuple"""
        return self.point.coordinates()


@dataclass(frozen=True)
class Command:
    """Robot command with validation"""

    command_string: str

    def __post_init__(self):
        """Validate command string on creation"""
        if not isinstance(self.command_string, str):
            raise ValueError('Command must be a string')

        # Strict validation: lunar rover protocol requires exact uppercase commands.
        # Lowercase letters are invalid commands to ensure protocol compliance.
        valid_chars = set('FBLR')
        invalid_chars = set(self.command_string) - valid_chars
        if invalid_chars:
            raise ValueError(f'Invalid command characters: {invalid_chars}')

    @classmethod
    def from_string(cls, command_string: str) -> 'Command':
        """Create command from string with strict validation"""
        return cls(command_string)

    def is_empty(self) -> bool:
        """Check if command is empty"""
        return len(self.command_string) == 0

    def truncate(self, length: int) -> 'Command':
        """Create truncated command"""
        if length < 0:
            raise ValueError('Length cannot be negative')
        return Command(self.command_string[:length])


@dataclass(frozen=True)
class CommandResult:
    """Result of command execution"""

    executed_command: Command
    initial_command: Command
    final_position: Position
    stopped_by_obstacle: bool
    path: list[Position] | None = None
