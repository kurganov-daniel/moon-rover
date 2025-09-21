"""Tests for domain models"""

import pytest

from app.domain.entities import (
    Command,
    CommandResult,
    Direction,
    Obstacle,
    Point,
    Position,
)


@pytest.mark.parametrize(
    'direction,expected_forward,expected_backward',
    [
        (Direction.NORTH, (0, 1), (0, -1)),
        (Direction.EAST, (1, 0), (-1, 0)),
        (Direction.SOUTH, (0, -1), (0, 1)),
        (Direction.WEST, (-1, 0), (1, 0)),
    ],
)
def test_movement(direction, expected_forward, expected_backward):
    """Test forward and backward movement in all directions"""
    position = Position(Point(0, 0), direction)

    # Test forward movement
    forward_pos = position.move_forward()
    assert forward_pos.coordinates() == expected_forward
    assert forward_pos.direction == direction

    # Test backward movement
    backward_pos = position.move_backward()
    assert backward_pos.coordinates() == expected_backward
    assert backward_pos.direction == direction


def test_position_turns():
    """Test position turning operations"""
    position = Position(Point(0, 0), Direction.NORTH)

    # Test single turns
    left_pos = position.turn_left()
    assert left_pos.direction == Direction.WEST

    right_pos = position.turn_right()
    assert right_pos.direction == Direction.EAST

    # Test full rotation returns to original direction
    full_left = position
    full_right = position
    for _ in range(4):
        full_left = full_left.turn_left()
        full_right = full_right.turn_right()
    assert full_left.direction == Direction.NORTH
    assert full_right.direction == Direction.NORTH


def test_obstacle_basic_functionality():
    """Test obstacle creation and inheritance from Point"""
    obstacle = Obstacle(2, 3)
    assert obstacle.x == 2
    assert obstacle.y == 3

    # Test it inherits from Point
    point = Point(2, 3)
    assert obstacle.coordinates() == point.coordinates()


def test_command_creation_and_basic_functionality():
    """Test command creation, validation, and basic operations"""
    # Valid command creation
    command = Command('FFLR')
    assert command.command_string == 'FFLR'
    assert not command.is_empty()

    # Empty command
    empty_command = Command('')
    assert empty_command.is_empty()

    # Truncate functionality
    truncated = command.truncate(2)
    assert truncated.command_string == 'FF'


@pytest.mark.parametrize(
    'invalid_input,expected_error',
    [
        ('FfLR', ValueError),  # Lowercase
        ('FFXLR', ValueError),  # Invalid character
        (123, ValueError),  # Non-string
    ],
)
def test_command_validation_errors(invalid_input, expected_error):
    """Test that Command properly validates input"""
    with pytest.raises(expected_error):
        Command(invalid_input)


def test_command_result_basic_functionality():
    """Test CommandResult creation and basic functionality"""
    point = Point(1, 2)
    position = Position(point, Direction.NORTH)
    command = Command('FF')

    result = CommandResult(
        final_position=position,
        stopped_by_obstacle=False,
        executed_command=command,
        initial_command=command,
    )

    assert result.final_position == position
    assert result.stopped_by_obstacle is False
    assert result.executed_command == command
    assert result.initial_command == command
