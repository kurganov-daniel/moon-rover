import pytest

from app.domain.entities import Command, Direction, Obstacle, Point, Position
from app.domain.exceptions import LandingObstacleException
from app.domain.services import execute_commands


def test_complete_mission_scenario():
    """Test a complete mission scenario from technical specification"""
    # Starting position as per requirements: (4, 2) facing WEST
    start_position = Position(Point(4, 2), Direction.WEST)
    obstacles = {Obstacle(1, 4), Obstacle(3, 5), Obstacle(7, 4)}

    # Execute example command from spec: "FLFFFRFLB"
    command = Command('FLFFFRFLB')
    result = execute_commands(command, start_position, obstacles)

    # Should execute all commands since no obstacles in path
    assert result.executed_command.command_string == 'FLFFFRFLB'
    assert result.stopped_by_obstacle is False
    assert result.final_position.x == 2
    assert result.final_position.y == 0
    assert result.final_position.direction == Direction.SOUTH


def test_obstacle_encounter():
    """Test mission that encounters obstacles during movement"""
    start_position = Position(Point(0, 0), Direction.NORTH)
    obstacles = {Obstacle(0, 3)}  # Obstacle 3 steps ahead

    # Try to move 5 steps forward
    command = Command('FFFFF')
    result = execute_commands(command, start_position, obstacles)

    # Should stop after 2 steps before hitting obstacle
    assert result.executed_command.command_string == 'FF'
    assert result.final_position.x == 0
    assert result.final_position.y == 2
    assert result.stopped_by_obstacle is True


@pytest.mark.parametrize(
    'command_str,expected_x,expected_y,expected_dir',
    [
        ('RFLF', 1, 1, Direction.NORTH),  # Navigate around obstacles
        ('RB', -1, 0, Direction.EAST),  # Turn right then backward
    ],
)
def test_navigation_patterns(command_str, expected_x, expected_y, expected_dir):
    """Test various navigation patterns around obstacles"""
    start_position = Position(Point(0, 0), Direction.NORTH)
    obstacles = {Obstacle(0, 1)}  # Obstacle directly ahead

    command = Command(command_str)
    result = execute_commands(command, start_position, obstacles)

    assert result.executed_command.command_string == command_str
    assert result.final_position.x == expected_x
    assert result.final_position.y == expected_y
    assert result.final_position.direction == expected_dir
    assert result.stopped_by_obstacle is False


@pytest.mark.parametrize(
    'start_x,start_y',
    [
        (4, 2),  # Obstacle at start position
        (0, 0),  # Different start position
    ],
)
def test_landing_obstacle_exception(start_x, start_y):
    """Test that mission is aborted when obstacle at landing position"""
    start_position = Position(Point(start_x, start_y), Direction.WEST)
    obstacles = {Obstacle(start_x, start_y)}

    command = Command('FLFFFRFLB')

    # Mission should be aborted immediately with proper exception
    with pytest.raises(LandingObstacleException) as exc_info:
        execute_commands(command, start_position, obstacles)

    assert exc_info.value.position == (start_x, start_y)
    assert 'Cannot start lunar mission' in str(exc_info.value)
