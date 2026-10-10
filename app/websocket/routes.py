import json
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.security import decode_access_token
from app.models.game import Game, GameStatus
from app.models.user import User
from app.schemas.ws import LobbyState
from app.websocket.manager import manager


router = APIRouter()


@router.websocket("/games/{code}")
async def game_lobby(websocket: WebSocket, code: str):
    db: Session = SessionLocal()

    try:
        # 1. Authenticate before accepting the connection.
        token = websocket.query_params.get("token")

        if not token:
            await websocket.close(code=1008)
            return

        try:
            user_id = decode_access_token(token)

            if user_id is None:
                await websocket.close(code=1008)
                return

            user = db.query(User).filter(
                User.id == user_id
            ).first()

            if user is None:
                await websocket.close(code=1008)
                return

        except Exception as exc:
            print("WebSocket authentication failed:", repr(exc))
            await websocket.close(code=1008)
            return

        # 2. Find and validate the game.
        game = db.query(Game).filter(
            Game.code == code.upper()
        ).first()

        if game is None or game.status != GameStatus.WAITING:
            await websocket.close(code=1008)
            return

        # 3. Accept and register the connection.
        await websocket.accept()

        await manager.connect(
            game.id,
            user.id,
            websocket,
        )

        # 4. Broadcast the updated lobby.
        async def broadcast_lobby():
            players = manager.active_connections.get(
                game.id, {}
            )

            await manager.broadcast(
                game.id,
                LobbyState(
                    game_code=game.code,
                    players=[
                        str(player_id)
                        for player_id in players
                    ],
                    host_id=str(game.host_id),
                ).model_dump(),
            )

        await broadcast_lobby()

        # 5. Handle incoming messages.
        while True:
            raw_message = await websocket.receive_text()

            try:
                message = json.loads(raw_message)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                })
                continue

            if not isinstance(message, dict):
                await websocket.send_json({
                    "type": "error",
                    "message": "Message must be a JSON object",
                })
                continue

            if message.get("type") != "start_game":
                await websocket.send_json({
                    "type": "error",
                    "message": "Unknown message type",
                })
                continue

            # Only the host can start the game.
            if user.id != game.host_id:
                await websocket.send_json({
                    "type": "error",
                    "message": "Only the host can start the game",
                })
                continue

            # Only start a game that is still waiting.
            db.refresh(game)

            if game.status != GameStatus.WAITING:
                await websocket.send_json({
                    "type": "error",
                    "message": "Game has already started",
                })
                continue

            game.status = GameStatus.IN_PROGRESS
            db.commit()

            await manager.broadcast(
                game.id,
                {
                    "type": "game_started",
                    "game_code": game.code,
                },
            )

    except WebSocketDisconnect:
        pass

    finally:
        if "game" in locals() and "user" in locals():
            manager.disconnect(game.id, user.id)

            if "broadcast_lobby" in locals():
                await broadcast_lobby()

        db.close()