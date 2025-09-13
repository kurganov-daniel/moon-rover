import logging

from fastapi import APIRouter

from app.presentation.schemas import (
    CommandRequest,
    CommandResponse,
    HealthResponse,
    PositionResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get('/health', response_model=HealthResponse)
async def health_check():
    pass


@router.get('/positions', response_model=PositionResponse)
async def get_position():
    pass


@router.post('/commands', response_model=CommandResponse)
async def execute_commands(request: CommandRequest):
    pass
