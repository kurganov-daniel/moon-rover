import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.exceptions import LandingObstacleException
from app.presentation.dependencies import (
    get_command_service,
    get_health_status_service,
    get_position_service,
    verify_credentials,
)
from app.presentation.schemas import (
    CommandRequest,
    CommandResponse,
    HealthResponse,
    PositionResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get('/health', response_model=HealthResponse)
async def health_check(health_service=Depends(get_health_status_service)):
    health_data = await health_service()
    return HealthResponse(**health_data)


@router.get('/positions', response_model=PositionResponse)
async def get_position(
    position_service=Depends(get_position_service),
    _: str = Depends(verify_credentials),
):
    position = await position_service.get_current_position()
    return PositionResponse(
        x=position.x, y=position.y, direction=position.direction.name
    )


@router.post('/commands', response_model=CommandResponse)
async def execute_commands(
    request: CommandRequest,
    command_service=Depends(get_command_service),
    _: str = Depends(verify_credentials),
):
    try:
        logger.info('Executing command: %s', request.command)
        command_result = await command_service.execute_command(request.command)
        logger.info(
            'Executed command: %s', command_result.executed_command.command_string
        )
        return CommandResponse(
            x=command_result.final_position.x,
            y=command_result.final_position.y,
            direction=command_result.final_position.direction.name,
            stopped_by_obstacle=command_result.stopped_by_obstacle,
            message=f'Command {command_result.executed_command.command_string} executed successfully',
        )
    except LandingObstacleException as e:
        logger.error('MISSION START FAILURE: %s', e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                'error': 'Mission start failure',
                'message': str(e),
                'position': e.position,
                'type': 'landing_obstacle',
            },
        ) from e
