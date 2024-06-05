import logging
from uuid import UUID
from fastapi import APIRouter, Response
from pydantic import BaseModel
from typing import Literal
from typing_extensions import TypedDict
from app.api import responses

from fastapi import Depends
from app.authentication import IdentityContext, authenticate_user
from app.chess import (
    BoardSquare,
    ChessPiece,
    Move,
    ChessPieceColor,
)
from app.context import APIRequestContext
from app.repositories import chess_games

router = APIRouter()


ValidRanks = Literal["1", "2", "3", "4", "5", "6", "7", "8"]
VALID_RANKS: list[ValidRanks] = ["1", "2", "3", "4", "5", "6", "7", "8"]

ValidFiles = Literal["A", "B", "C", "D", "E", "F", "G", "H"]
VALID_FILES: list[ValidFiles] = ["A", "B", "C", "D", "E", "F", "G", "H"]


def convert_input_to_board_square(pos: str) -> BoardSquare | None:
    try:
        if len(pos) != 2:
            return None
        file, rank = pos[0], pos[1]
        if file not in VALID_FILES:
            return None
        if rank not in VALID_RANKS:
            return None
        return BoardSquare(file=file, rank=rank)
    except Exception:
        logging.exception("Error converting input to board square")
        return None


class MoveInputRequestV1(BaseModel):
    square_from: str
    square_to: str


class MovePieceResponseV1(BaseModel):
    square_from: BoardSquare
    square_to: BoardSquare
    chess_piece: ChessPiece


class ErrorResponseV1(BaseModel):
    user_feedback: str


class CreateChessGameRequestV1(BaseModel):
    desired_color: ChessPieceColor


class CreateChessGameResponseV1(BaseModel):
    game_id: UUID
    invite_secret: str

    white_user_id: UUID | None
    black_user_id: UUID | None

    next_turn: ChessPieceColor
    move_history: list[Move]

    board: dict[str, ChessPiece]


@router.post("/api/v1/games")
async def create_chess_game(
    request: CreateChessGameRequestV1,
    identity: IdentityContext | None = Depends(authenticate_user),
    context: APIRequestContext = Depends(),
) -> Response:
    if identity is None:
        return responses.failure(
            user_feedback="Unauthorized",
            status_code=401,
        )

    if request.desired_color is ChessPieceColor.WHITE:
        white_user_id = identity.user_id
        black_user_id = None
    else:
        white_user_id = None
        black_user_id = identity.user_id

    chess_game = await chess_games.create_chess_game(
        context,
        white_user_id=white_user_id,
        black_user_id=black_user_id,
    )
    chess_game.board.reset_to_starting_position()
    await chess_games.update_chess_game(context, chess_game)

    response = CreateChessGameResponseV1(
        game_id=chess_game.game_id,
        invite_secret=chess_game.invite_secret,
        white_user_id=chess_game.white_user_id,
        black_user_id=chess_game.black_user_id,
        next_turn=chess_game.next_turn,
        move_history=chess_game.move_history,
        board={repr(k): v for k, v in chess_game.board.pieces.items()},
    )
    return responses.success(content=response)


class JoinChessGameResponseV1(BaseModel):
    game_id: UUID

    white_user_id: UUID | None
    black_user_id: UUID | None

    next_turn: ChessPieceColor
    move_history: list[Move]

    board: dict[str, ChessPiece]


@router.post("/api/v1/games/{game_id}/join")
async def join_chess_game(
    game_id: UUID,
    invite_secret: str,
    identity: IdentityContext | None = Depends(authenticate_user),
    context: APIRequestContext = Depends(),
) -> Response:
    if identity is None:
        return responses.failure(
            user_feedback="Unauthorized",
            status_code=401,
        )

    chess_game = await chess_games.get_chess_game(context, game_id)
    if chess_game is None:
        return responses.failure(
            user_feedback="Could not find a game by that id",
            status_code=404,
        )

    if chess_game.invite_secret != invite_secret:
        return responses.failure(
            user_feedback="Invalid invite secret",
            status_code=400,
        )

    if chess_game.white_user_id is not None and chess_game.black_user_id is not None:
        return responses.failure(
            user_feedback="Game is already full",
            status_code=400,
        )

    if (
        identity.user_id == chess_game.white_user_id
        or identity.user_id == chess_game.black_user_id
    ):
        return responses.failure(
            user_feedback="You're already in the game",
            status_code=400,
        )

    if chess_game.white_user_id is None:
        chess_game.white_user_id = identity.user_id
    else:
        chess_game.black_user_id = identity.user_id

    await chess_games.update_chess_game(context, chess_game)

    response = JoinChessGameResponseV1(
        game_id=chess_game.game_id,
        white_user_id=chess_game.white_user_id,
        black_user_id=chess_game.black_user_id,
        next_turn=chess_game.next_turn,
        move_history=chess_game.move_history,
        board={repr(k): v for k, v in chess_game.board.pieces.items()},
    )
    return responses.success(content=response)


@router.post("/api/v1/games/{game_id}/moves")
async def play_chess_move(
    game_id: UUID,
    request: MoveInputRequestV1,
    identity: IdentityContext | None = Depends(authenticate_user),
    context: APIRequestContext = Depends(),
) -> Response:
    if identity is None:
        return responses.failure(
            user_feedback="Unauthorized",
            status_code=401,
        )

    square_from = convert_input_to_board_square(request.square_from)
    if square_from is None:
        return responses.failure(
            user_feedback="Invalid square_from position",
            status_code=400,
        )

    square_to = convert_input_to_board_square(request.square_to)
    if square_to is None:
        return responses.failure(
            user_feedback="Invalid square_to position",
            status_code=400,
        )

    chess_game = await chess_games.get_chess_game(context, game_id)
    if chess_game is None:
        return responses.failure(
            user_feedback="Could not find a game by that id",
            status_code=404,
        )

    if (
        chess_game.white_user_id != identity.user_id
        and chess_game.black_user_id != identity.user_id
    ):
        return responses.failure(
            user_feedback="You're not a player in the game",
            status_code=403,
        )

    user_color = chess_game.get_user_color(identity.user_id)
    if user_color is None:
        return responses.failure(
            user_feedback="That piece doesn't belong to you",
            status_code=403,
        )

    if user_color != chess_game.next_turn:
        return responses.failure(
            user_feedback="It's not your turn",
            status_code=403,
        )

    chess_piece = chess_game.board.get_piece_on_square(square_from)
    if chess_piece is None:
        return responses.failure(
            user_feedback="No piece found on that square",
            status_code=400,
        )

    if chess_piece.color != user_color:
        return responses.failure(
            user_feedback="You can't move the other player's piece",
            status_code=403,
        )

    existing_chess_piece_on_new_square = chess_game.board.get_piece_on_square(square_to)
    if existing_chess_piece_on_new_square is not None:
        return responses.failure(
            user_feedback="There's already a piece on that square",
            status_code=400,
        )

    move = Move(
        square_from=square_from,
        square_to=square_to,
        chess_piece=chess_piece,
    )

    if not chess_piece.can_make_move(move):
        return responses.failure(
            user_feedback="Invalid move",
            status_code=400,
        )

    chess_game.move_piece(move)
    await chess_games.update_chess_game(context, chess_game)

    response = MovePieceResponseV1(
        square_from=square_from,
        square_to=square_to,
        chess_piece=chess_piece,
    )
    return responses.success(content=response)
