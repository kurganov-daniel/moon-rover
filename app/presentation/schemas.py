import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HealthResponse(BaseModel):
    status: str = 'healthy'
    database_connected: bool
    response_datetime: datetime = Field(default_factory=datetime.now)


class PositionResponse(BaseModel):
    x: int
    y: int
    direction: str


class CommandRequest(BaseModel):
    command: str

    model_config = ConfigDict(extra='forbid')

    # Check that string contains only L, R, B, F letters, STRICTLY.
    @field_validator('command')
    def validate_command(cls, v):
        if not v:
            raise ValueError('Command string cannot be empty')
        if not re.match(r'^[LRBF]+$', v):
            raise ValueError('Command must contain only L, R, B, F letters')
        return v


class CommandResponse(PositionResponse):
    stopped_by_obstacle: bool
    message: str | None = None
