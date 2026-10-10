from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.game import GameStatus


class GameCreate(BaseModel):
    game_mode: str
    question_count: Literal[10, 30, 50]


class GameRead(BaseModel):
    id: UUID
    code: str
    host_id: UUID
    game_mode: str
    question_count: int
    status: GameStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GameCodeValidation(BaseModel):
    valid: bool
    code: str
    status: GameStatus