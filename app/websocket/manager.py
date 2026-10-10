from fastapi import WebSocket
from uuid import UUID


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[
            UUID, dict[UUID, WebSocket]
        ] = {}

    async def connect(
        self,
        game_id: UUID,
        user_id: UUID,
        websocket: WebSocket,
    ):
        self.active_connections.setdefault(game_id, {})
        self.active_connections[game_id][user_id] = websocket

    def disconnect(self, game_id: UUID, user_id: UUID):
        players = self.active_connections.get(game_id)

        if players:
            players.pop(user_id, None)

            if not players:
                self.active_connections.pop(game_id, None)

    async def broadcast(self, game_id: UUID, message: dict):
        players = self.active_connections.get(game_id, {})

        for websocket in list(players.values()):
            try:
                await websocket.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()