from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.core.game_codes import generate_game_code
from app.models.game import Game, GameStatus
from app.models.user import User
from app.schemas.game import (
    GameCreate,
    GameRead,
    GameCodeValidation,
)


router = APIRouter(prefix="/games", tags=["games"])


@router.post(
    "",
    response_model=GameRead,
    status_code=status.HTTP_201_CREATED,
)
def create_game(
    payload: GameCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    game = Game(
        code=generate_game_code(db),
        host_id=current_user.id,
        game_mode=payload.game_mode,
        question_count=payload.question_count,
        status=GameStatus.WAITING,
    )

    db.add(game)
    db.commit()
    db.refresh(game)

    return game


@router.get("/{code}", response_model=GameRead)
def get_game(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    game = (
        db.query(Game)
        .filter(Game.code == code.upper())
        .first()
    )

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    return game


@router.get(
    "/{code}/validate",
    response_model=GameCodeValidation,
)
def validate_game_code(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    game = (
        db.query(Game)
        .filter(Game.code == code.upper())
        .first()
    )

    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    if game.status != GameStatus.WAITING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Game is no longer accepting players",
        )

    return GameCodeValidation(
        valid=True,
        code=game.code,
        status=game.status,
    )