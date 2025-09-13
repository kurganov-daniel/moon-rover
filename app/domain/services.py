"""Domain services for robot command processing"""

from app.domain.entities import Command, CommandResult, Obstacle, Position
from app.domain.exceptions import LandingObstacleException


def execute_commands(
    command: Command, start_position: Position, obstacles: set[Obstacle]
) -> CommandResult:
    """
    Execute command until obstacle is hit or all commands completed.

    Args:
        command: Command object with validated command string
        start_position: Starting position
        obstacles: Set of obstacles

    Returns:
        CommandResult object:
        - executed_command: Truncated command that was actually executed
        - initial_command: Original command
        - final_position: Final position
        - stopped_by_obstacle: Whether the robot stopped by an obstacle
        - path: List of positions visited

    Raises:
        LandingObstacleException: If obstacle is detected at starting position
    """
    # Critical safety check: verify no obstacle at landing position
    if start_position.point in obstacles:
        raise LandingObstacleException(start_position.coordinates())

    if command.is_empty():
        return CommandResult(
            final_position=start_position,
            stopped_by_obstacle=False,
            executed_command=command,
            initial_command=command,
            path=[],
        )

    current_position = start_position
    executed_length = 0
    path = []

    for char in command.command_string:
        if char == 'F':
            new_position = current_position.move_forward()
        elif char == 'B':
            new_position = current_position.move_backward()
        elif char == 'L':
            new_position = current_position.turn_left()
        else:  # char == 'R'
            new_position = current_position.turn_right()

        # Check for obstacles only on movement commands
        if char in ['F', 'B']:
            if new_position.point in obstacles:
                executed_command = command.truncate(executed_length)
                return CommandResult(
                    final_position=current_position,
                    stopped_by_obstacle=True,
                    path=path,
                    executed_command=executed_command,
                    initial_command=command,
                )

        executed_length += 1
        current_position = new_position
        path.append(current_position)

    return CommandResult(
        final_position=current_position,
        stopped_by_obstacle=False,
        path=path,
        executed_command=command,
        initial_command=command,
    )
