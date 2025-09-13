from datetime import datetime
from enum import Enum
from typing import Annotated

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.domain.entities import Direction


class Base(DeclarativeBase):
    pass


class CommandStatus(Enum):
    PENDING = 'pending'
    EXECUTING = 'executing'
    COMPLETED = 'completed'
    FAILED = 'failed'


created_at = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False),
]


class PositionORM(Base):
    """Position table model - individual points in a path"""

    __tablename__ = 'positions'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    coord_x: Mapped[int] = mapped_column(Integer, nullable=False)
    coord_y: Mapped[int] = mapped_column(Integer, nullable=False)
    direction: Mapped[Direction] = mapped_column(
        SAEnum(Direction, name='position_direction_enum', create_type=False),
        nullable=False,
    )
    created_at: Mapped[created_at]

    command_id: Mapped[int] = mapped_column(ForeignKey('commands.id'), nullable=False)
    command: Mapped['CommandORM'] = relationship(back_populates='positions')


class CommandORM(Base):
    """Command table model - stores command path and execution details"""

    __tablename__ = 'commands'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    received_command: Mapped[str] = mapped_column(String, nullable=False)
    executed_command: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[CommandStatus] = mapped_column(
        SAEnum(CommandStatus, name='command_status_enum', create_type=False),
        nullable=False,
    )
    stopped_by_obstacle: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
    positions: Mapped[list['PositionORM']] = relationship(
        back_populates='command', cascade='all, delete-orphan'
    )
