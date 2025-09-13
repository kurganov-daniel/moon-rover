from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.health_service import HealthStatusService
from app.application.position_service import PositionService
from app.infrastructure.db.engine import get_session
from app.infrastructure.repositories.repo_health import RDBHealthChecker
from app.infrastructure.repositories.repo_position import (
    RDBPositionRepository,
    StartPositionEnvSettings,
)

position_settings = StartPositionEnvSettings()


def get_health_status_service(
    session: AsyncSession = Depends(get_session),
) -> HealthStatusService:
    """Dependency for health service"""
    checker = RDBHealthChecker(session)
    return HealthStatusService(checker)


def get_position_service(
    session: AsyncSession = Depends(get_session),
) -> PositionService:
    """Dependency for position service"""
    repo = RDBPositionRepository(session)
    return PositionService(repo, position_settings)
