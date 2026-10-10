import secrets
from sqlalchemy.orm import Session
from app.models.game import Game


ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_game_code(db: Session) -> str:
    while True:
        code = "".join(
            secrets.choice(ALPHABET)
            for _ in range(6)
        )

        existing_game = (
            db.query(Game)
            .filter(Game.code == code)
            .first()
        )

        if existing_game is None:
            return code