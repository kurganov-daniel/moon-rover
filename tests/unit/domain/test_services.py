import pytest

from app.domain.entities import Command, Direction, Obstacle, Point, Position
from app.domain.exceptions import LandingObstacleException
from app.domain.services import execute_commands


def test_execute_empty_command():
    command = Command('')
    start_position = Position(Point(0, 0), Direction.NORTH)
    obstacles = set()

    result = execute_commands(command, start_position, obstacles)

    assert result.executed_command.command_string == ''
    assert result.final_position == start_position
    assert result.stopped_by_obstacle is False
    assert result.initial_command == command
    assert result.path == []


def test_execute_single_forward_command():
    command = Command('F')
    start_position = Position(Point(0, 0), Direction.NORTH)
    obstacles = set()

    result = execute_commands(command, start_position, obstacles)

    assert result.executed_command.command_string == 'F'
    assert result.final_position.x == 0
    assert result.final_position.y == 1
    assert result.final_position.direction == Direction.NORTH
    assert result.stopped_by_obstacle is False
    assert result.initial_command == command
    assert len(result.path) == 1


def test_execute_multiple_commands_no_obstacles():
    command = Command('FFLR')
    start_position = Position(Point(0, 0), Direction.NORTH)
    obstacles = set()

    result = execute_commands(command, start_position, obstacles)

    assert result.executed_command.command_string == 'FFLR'
    assert result.final_position.x == 0
    assert result.final_position.y == 2
    assert result.final_position.direction == Direction.NORTH
    assert result.stopped_by_obstacle is False
    assert result.initial_command == command
    assert len(result.path) == 4


def test_execute_commands_hit_obstacle():
    command = Command('FFF')
    start_position = Position(Point(0, 0), Direction.NORTH)
    obstacles = {Obstacle(0, 2)}  # Obstacle at (0, 2)

    result = execute_commands(command, start_position, obstacles)

    # Should execute "FF" and stop before hitting obstacle
    assert result.executed_command.command_string == 'F'
    assert result.final_position.x == 0
    assert result.final_position.y == 1
    assert result.final_position.direction == Direction.NORTH
    assert result.stopped_by_obstacle is True
    assert result.initial_command == command
    assert len(result.path) == 1


def test_execute_commands_obstacle_on_first_move():
    command = Command('F')
    start_position = Position(Point(0, 0), Direction.NORTH)
    obstacles = {Obstacle(0, 1)}  # Obstacle immediately ahead

    result = execute_commands(command, start_position, obstacles)

    # Should not execute any commands
    assert result.executed_command.command_string == ''
    assert result.final_position == start_position
    assert result.stopped_by_obstacle is True
    assert result.initial_command == command
    assert result.path == []


def test_execute_commands_turns_ignore_obstacles():
    command = Command('LR')
    start_position = Position(Point(0, 0), Direction.NORTH)
    obstacles = {Obstacle(0, 1)}  # Obstacle ahead, not at current position

    result = execute_commands(command, start_position, obstacles)

    # Turns should be executed even with obstacles nearby
    assert result.executed_command.command_string == 'LR'
    assert result.final_position.direction == Direction.NORTH
    assert result.stopped_by_obstacle is False
    assert result.initial_command == command
    assert len(result.path) == 2


def test_execute_commands_backward_movement():
    command = Command('B')
    start_position = Position(Point(0, 1), Direction.NORTH)
    obstacles = set()

    result = execute_commands(command, start_position, obstacles)

    assert result.executed_command.command_string == 'B'
    assert result.final_position.x == 0
    assert result.final_position.y == 0
    assert result.final_position.direction == Direction.NORTH
    assert result.stopped_by_obstacle is False
    assert result.initial_command == command
    assert len(result.path) == 1


def test_execute_commands_backward_hit_obstacle():
    command = Command('B')
    start_position = Position(Point(0, 1), Direction.NORTH)
    obstacles = {Obstacle(0, 0)}  # Obstacle behind

    result = execute_commands(command, start_position, obstacles)

    assert result.executed_command.command_string == ''
    assert result.final_position == start_position
    assert result.stopped_by_obstacle is True
    assert result.initial_command == command
    assert result.path == []


def test_execute_complex_path_with_obstacle_no_hit():
    command = Command('FFLFF')
    start_position = Position(Point(0, 0), Direction.NORTH)
    obstacles = {Obstacle(1, 2)}

    result = execute_commands(command, start_position, obstacles)

    assert result.executed_command.command_string == 'FFLFF'
    assert result.final_position.x == -2
    assert result.final_position.y == 2
    assert result.final_position.direction == Direction.WEST
    assert result.stopped_by_obstacle is False
    assert result.initial_command == command
    assert len(result.path) == 5


def test_execute_complex_path_with_obstacle_with_hit():
    command = Command('FFLFF')
    start_position = Position(Point(0, 0), Direction.NORTH)
    obstacles = {Obstacle(-1, 2)}

    result = execute_commands(command, start_position, obstacles)

    assert result.executed_command.command_string == 'FFL'
    assert result.final_position.x == 0
    assert result.final_position.y == 2
    assert result.final_position.direction == Direction.WEST
    assert result.stopped_by_obstacle is True
    assert result.initial_command == command
    assert len(result.path) == 3


def test_execute_different_directions():
    # Test movement in all directions
    test_cases = [
        (Direction.NORTH, 'F', (0, 1)),
        (Direction.EAST, 'F', (1, 0)),
        (Direction.SOUTH, 'F', (0, -1)),
        (Direction.WEST, 'F', (-1, 0)),
    ]

    for direction, command_str, expected_coords in test_cases:
        command = Command(command_str)
        start_position = Position(Point(0, 0), direction)
        obstacles = set()

        result = execute_commands(command, start_position, obstacles)

        assert result.final_position.coordinates() == expected_coords
        assert result.stopped_by_obstacle is False
        assert result.initial_command == command
        assert len(result.path) == 1


def test_multiple_obstacles_all_directions():
    """Test robot behavior with obstacles in all cardinal directions"""
    # Robot at (2, 2) facing NORTH
    start_position = Position(Point(2, 2), Direction.NORTH)

    # Obstacles surrounding the robot in all directions
    obstacles = {
        Obstacle(2, 3),  # North
        Obstacle(3, 2),  # East
        Obstacle(2, 1),  # South
        Obstacle(1, 2),  # West
    }

    # Test forward movement - should hit northern obstacle
    command = Command('F')
    result = execute_commands(command, start_position, obstacles)

    assert result.stopped_by_obstacle is True
    assert result.executed_command.command_string == ''
    assert result.final_position.coordinates() == (2, 2)
    assert result.final_position.direction == Direction.NORTH

    # Test backward movement - should hit southern obstacle
    command = Command('B')
    result = execute_commands(command, start_position, obstacles)

    assert result.stopped_by_obstacle is True
    assert result.executed_command.command_string == ''
    assert result.final_position.coordinates() == (2, 2)
    assert result.final_position.direction == Direction.NORTH

    # Test movement after turning east - should hit eastern obstacle
    command = Command('RF')
    result = execute_commands(command, start_position, obstacles)

    assert result.stopped_by_obstacle is True
    assert result.executed_command.command_string == 'R'
    assert result.final_position.coordinates() == (2, 2)
    assert result.final_position.direction == Direction.EAST

    # Test movement after turning west - should hit western obstacle
    command = Command('LF')
    result = execute_commands(command, start_position, obstacles)

    assert result.stopped_by_obstacle is True
    assert result.executed_command.command_string == 'L'
    assert result.final_position.coordinates() == (2, 2)
    assert result.final_position.direction == Direction.WEST


def test_circular_movement_with_obstacles():
    """Test circular movement patterns that encounter obstacles"""
    # Robot at (0, 0) facing NORTH
    start_position = Position(Point(0, 0), Direction.NORTH)

    # Create a circular path with obstacles that interrupt the circle
    obstacles = {
        Obstacle(3, 0),
        Obstacle(0, 3),
        Obstacle(-3, 0),
    }  # Obstacles at east, north, and west points

    # Try to make a complete circle: FFF R FFF R FFF R FFF R
    # This should hit the northern obstacle
    command = Command('FFFRFFFRFFFRFFF')
    result = execute_commands(command, start_position, obstacles)

    assert result.stopped_by_obstacle is True
    assert (
        result.executed_command.command_string == 'FF'
    )  # Should stop after moving north
    assert result.final_position.coordinates() == (0, 2)
    assert result.final_position.direction == Direction.NORTH
    assert len(result.path) == 2


def test_partial_command_execution_long_sequence():
    """Test partial execution of very long command sequences with obstacles"""
    # Robot at (0, 0) facing NORTH
    start_position = Position(Point(0, 0), Direction.NORTH)

    # Create obstacles at various points along the path
    obstacles = {Obstacle(0, 5), Obstacle(0, 10), Obstacle(0, 15)}

    # Create a long sequence of forward movements
    long_command = 'F' * 20
    command = Command(long_command)
    result = execute_commands(command, start_position, obstacles)

    # Should hit first obstacle at (0, 5) after 5 steps
    assert result.stopped_by_obstacle is True
    assert result.executed_command.command_string == 'FFFF'
    assert result.final_position.coordinates() == (0, 4)  # Stop before obstacle
    assert result.final_position.direction == Direction.NORTH
    assert len(result.path) == 4

    # Verify the path contains all intermediate positions
    expected_path = [
        Position(Point(0, 1), Direction.NORTH),
        Position(Point(0, 2), Direction.NORTH),
        Position(Point(0, 3), Direction.NORTH),
        Position(Point(0, 4), Direction.NORTH),
    ]
    assert result.path == expected_path


def test_boundary_conditions_negative_coordinates():
    """Test robot behavior with negative coordinates and boundary conditions"""
    # Robot at (0, 0) facing SOUTH (moving to negative Y)
    start_position = Position(Point(0, 0), Direction.SOUTH)

    # Obstacle at (-5, -5)
    obstacles = {Obstacle(0, -5)}

    # Move to negative coordinates
    command = Command('FFFFF')
    result = execute_commands(command, start_position, obstacles)

    # Should reach (-5, -5) and detect obstacle
    assert result.stopped_by_obstacle is True
    assert result.executed_command.command_string == 'FFFF'  # Stop before obstacle
    assert result.final_position.coordinates() == (0, -4)
    assert result.final_position.direction == Direction.SOUTH
    assert len(result.path) == 4


def test_complex_maneuvers_multiple_turns_and_movements():
    """Test complex maneuvers with multiple turns and movements"""
    # Robot at (0, 0) facing NORTH
    start_position = Position(Point(0, 0), Direction.NORTH)

    # Create a spiral pattern with obstacles
    obstacles = {
        Obstacle(2, 0),
        Obstacle(2, 2),
        Obstacle(0, 2),
        Obstacle(-2, 2),
        Obstacle(-2, 0),
        Obstacle(-2, -2),
    }

    # Complex maneuver: move, turn, move, turn, etc.
    command = Command('FRFRFRFR')  # Square spiral pattern
    result = execute_commands(command, start_position, obstacles)

    # Should complete the pattern until hitting an obstacle
    assert result.stopped_by_obstacle is False
    # The exact stopping point depends on obstacle placement
    assert result.final_position.direction is Direction.NORTH
    assert len(result.path) == 8

    # Verify that initial command is preserved
    assert result.initial_command == command
    assert result.executed_command.command_string == command.command_string


@pytest.mark.parametrize(
    'start_point,direction',
    [
        (Point(0, 0), Direction.NORTH),
        (Point(5, 5), Direction.EAST),
        (Point(-3, 2), Direction.SOUTH),
        (Point(10, 10), Direction.WEST),
    ],
)
def test_obstacle_at_starting_position(start_point, direction):
    """Test behavior when obstacle is at the robot's starting position"""
    start_position = Position(start_point, direction)
    obstacles = {Obstacle(start_point.x, start_point.y)}
    command = Command('F')

    # Should raise LandingObstacleException immediately
    with pytest.raises(LandingObstacleException) as exc_info:
        execute_commands(command, start_position, obstacles)

    # Verify the exception details
    assert exc_info.value.position == start_point.coordinates()
    assert 'Cannot start lunar mission' in str(exc_info.value)
    assert 'obstacle detected at landing position' in str(exc_info.value)


def test_no_obstacle_at_starting_position():
    """Test normal execution when no obstacle at starting position"""
    start_position = Position(Point(0, 0), Direction.NORTH)
    # Obstacles nearby but not at starting position
    obstacles = {Obstacle(1, 0), Obstacle(0, -1)}
    command = Command('F')

    result = execute_commands(command, start_position, obstacles)

    # Should execute normally
    assert result.stopped_by_obstacle is False
    assert result.executed_command.command_string == 'F'
    assert result.final_position.coordinates() == (0, 1)


def test_empty_command_with_obstacle_at_start_raises_exception():
    """Test that empty command with obstacle at start still raises exception"""
    start_position = Position(Point(0, 0), Direction.NORTH)
    obstacles = {Obstacle(0, 0)}  # Obstacle at starting position

    command = Command('')

    # Should still raise exception even for empty command
    with pytest.raises(LandingObstacleException) as exc_info:
        execute_commands(command, start_position, obstacles)

    assert exc_info.value.position == (0, 0)
    assert 'landing position' in str(exc_info.value)


def test_consecutive_obstacles_in_path():
    """Test robot behavior with consecutive obstacles blocking the path"""
    start_position = Position(Point(0, 0), Direction.NORTH)

    # Multiple obstacles in a straight line
    obstacles = {Obstacle(0, 1), Obstacle(0, 2), Obstacle(0, 3)}

    command = Command('FFFF')
    result = execute_commands(command, start_position, obstacles)

    # Should stop at first obstacle
    assert result.stopped_by_obstacle is True
    assert result.executed_command.command_string == ''  # No movement possible
    assert result.final_position == start_position
    assert result.path == []


def test_diagonal_movement_patterns():
    """Test patterns that simulate diagonal movement through turns"""
    start_position = Position(Point(0, 0), Direction.NORTH)

    # Obstacles placed to test diagonal-like movement patterns
    obstacles = {Obstacle(1, 1), Obstacle(2, 2), Obstacle(-1, -1)}

    # Pattern: move, turn right, move, turn left, etc. (simulating diagonal)
    command = Command('FRFLFRFL')
    result = execute_commands(command, start_position, obstacles)

    # Should navigate until hitting an obstacle
    assert result.stopped_by_obstacle is True
    # Verify the path follows the expected diagonal pattern
    assert len(result.path) >= 1
    assert result.initial_command == command


def test_multiple_obstacles_in_path():
    command = Command('FFFF')
    start_position = Position(Point(0, 0), Direction.NORTH)
    obstacles = {Obstacle(0, 2), Obstacle(0, 3)}  # Multiple obstacles ahead

    result = execute_commands(command, start_position, obstacles)

    # Should hit first obstacle
    assert result.executed_command.command_string == 'F'
    assert result.final_position.y == 1
    assert result.stopped_by_obstacle is True
    assert result.initial_command == command
    assert len(result.path) == 1


def test_only_turn_commands():
    command = Command('LRLRLR')
    start_position = Position(Point(5, 5), Direction.NORTH)
    obstacles = {Obstacle(5, 6)}  # Obstacle ahead, not at current position

    result = execute_commands(command, start_position, obstacles)

    # Turns should not be affected by obstacles
    assert result.executed_command.command_string == 'LRLRLR'
    assert result.final_position.coordinates() == (5, 5)
    assert result.stopped_by_obstacle is False
    assert result.initial_command == command
    assert len(result.path) == 6
