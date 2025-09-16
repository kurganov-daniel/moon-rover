from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import desc, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Direction, Point, Position
from app.infrastructure.db.models import PositionORM


class StartPositionEnvSettings(BaseSettings):
    START_POSITION_X: int = 0
    START_POSITION_Y: int = 0
    START_DIRECTION: str = 'NORTH'

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )

    def get_start_position(self) -> Position:
        return Position(
            point=Point(self.START_POSITION_X, self.START_POSITION_Y),
            direction=Direction[self.START_DIRECTION],
        )


class RDBPositionRepository:
    """SQLAlchemy implementation of PositionRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_current_position(self) -> Position | None:
        """Fetch the latest position from DB (ordered by id desc)."""
        result = await self.session.execute(
            select(PositionORM).order_by(desc(PositionORM.id)).limit(1)
        )
        position_orm: PositionORM | None = result.scalar_one_or_none()

        if position_orm is None:
            return None

        return Position(
            point=Point(position_orm.coord_x, position_orm.coord_y),
            direction=position_orm.direction,
        )

    async def save_positions_bulk(
        self, command_id: int, positions: list[Position]
    ) -> None:
        if not positions:
            return

        payload = [
            {
                'coord_x': p.x,
                'coord_y': p.y,
                'direction': p.direction,
                'command_id': command_id,
            }
            for p in positions
        ]
        await self.session.execute(insert(PositionORM), payload)
