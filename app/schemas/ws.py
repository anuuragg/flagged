from typing import Literal
from pydantic import BaseModel
from uuid import UUID


class LobbyState(BaseModel):
    type: Literal["lobby_state"] = "lobby_state"
    game_code: str
    players: list[str]
    host_id: str


class ErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    message: str


class GameStarted(BaseModel):
    type: Literal["game_started"] = "game_started"
    game_code: str