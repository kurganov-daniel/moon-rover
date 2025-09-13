import logging

from fastapi import APIRouter, Depends

from app.presentation.dependencies import (
    get_health_status_service,
    get_position_service,
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
):
    position = await position_service.get_current_position()
    return PositionResponse(
        x=position.x, y=position.y, direction=position.direction.name
    )


@router.post('/commands', response_model=CommandResponse)
async def execute_commands(request: CommandRequest):
    pass
