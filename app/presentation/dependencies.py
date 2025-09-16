from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth_service import BasicAuthService, UnauthorizedError
from app.application.command_service import CommandService
from app.application.health_service import HealthStatusService
from app.application.position_service import PositionService
from app.infrastructure.db.engine import get_session
from app.infrastructure.repositories.auth_provider import BasicAuthSettings
from app.infrastructure.repositories.repo_command import RDBCommandRepository
from app.infrastructure.repositories.repo_health import RDBHealthChecker
from app.infrastructure.repositories.repo_obstacle import JSONObstacleRepository
from app.infrastructure.repositories.repo_position import (
    RDBPositionRepository,
    StartPositionEnvSettings,
)
from app.infrastructure.repositories.unit_of_work import AsyncUoW

position_settings = StartPositionEnvSettings()
basic_auth_settings = BasicAuthSettings()
security = HTTPBasic()


async def get_auth_service() -> BasicAuthService:
    """Dependency for authentication service"""
    return BasicAuthService(basic_auth_settings.USERNAME, basic_auth_settings.PASSWORD)


async def verify_credentials(
    credentials: HTTPBasicCredentials = Depends(security),
) -> str:
    """Verify username and password from Basic Auth credentials"""
    auth_service = await get_auth_service()

    try:
        await auth_service.validate_credentials(
            credentials.username, credentials.password
        )
        return credentials.username
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={'WWW-Authenticate': 'Basic'},
        ) from e


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


def get_command_service(
    session: AsyncSession = Depends(get_session),
) -> CommandService:
    """Dependency for command service"""
    repo = RDBCommandRepository(session)
    obstacle_repo = JSONObstacleRepository()
    position_repo = RDBPositionRepository(session)
    start_position_provider = StartPositionEnvSettings()
    uow = AsyncUoW(session)
    return CommandService(
        repo, obstacle_repo, position_repo, start_position_provider, uow
    )
