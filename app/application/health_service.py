from typing import Protocol


class HealthChecker(Protocol):
    async def get_health_status(self) -> bool: ...


class HealthStatusService:
    def __init__(self, db_checker: HealthChecker):
        self._db_checker = db_checker

    async def __call__(self) -> dict:
        db_ok = await self._db_checker.get_health_status()
        return {'database_connected': db_ok}
