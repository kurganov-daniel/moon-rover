from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.health_service import HealthStatusService
from app.infrastructure.db.engine import get_session
from app.infrastructure.repositories.repo_health import RDBHealthChecker


def get_health_status_service(
    session: AsyncSession = Depends(get_session),
) -> HealthStatusService:
    """Dependency for health service"""
    checker = RDBHealthChecker(session)
    return HealthStatusService(checker)
