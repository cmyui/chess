from __future__ import annotations

import json
import logging
import secrets
from uuid import UUID
from uuid import uuid4

from app.chess import BoardSquare
from app.chess import ChessBoard
from app.chess import ChessGame
from app.chess import ChessPiece
from app.chess import ChessPieceColor
from app.chess import ChessPieceType
from app.chess import Move
from app.context import AbstractContext
from app.json import JSONEncoder


def serialize(chess_game: ChessGame) -> bytes:
    obj = {
        "game_id": chess_game.game_id,
        "board": {
            "pieces": {
                repr(k): {"piece_type": v.piece_type.value, "color": v.color.value}
                for k, v in chess_game.board.pieces.items()
            },
        },
        "move_history": [
            {
                "square_from": repr(move.square_from),
                "square_to": repr(move.square_to),
                "chess_piece": {
                    "piece_type": move.chess_piece.piece_type.value,
                    "color": move.chess_piece.color.value,
                },
            }
            for move in chess_game.move_history
        ],
        "white_user_id": chess_game.white_user_id,
        "black_user_id": chess_game.black_user_id,
        "invite_secret": chess_game.invite_secret,
        "next_turn": chess_game.next_turn,
    }
    return json.dumps(
        obj,
        ensure_ascii=False,
        allow_nan=False,
        cls=JSONEncoder,
        indent=None,
        separators=(",", ":"),
    ).encode("utf-8")


def deserialize(data: bytes) -> ChessGame:
    obj = json.loads(data)
    return ChessGame(
        game_id=obj["game_id"],
        board=ChessBoard(
            pieces={
                BoardSquare(file=k[0], rank=k[1]): v
                for k, v in obj["board"]["pieces"].items()
            },
        ),
        move_history=[
            Move(
                square_from=BoardSquare(
                    file=k["square_from"][0],
                    rank=k["square_from"][1],
                ),
                square_to=BoardSquare(
                    file=k["square_to"][0],
                    rank=k["square_to"][1],
                ),
                chess_piece=ChessPiece(
                    piece_type=ChessPieceType(k["chess_piece"]["piece_type"]),
                    color=ChessPieceColor(k["chess_piece"]["color"]),
                ),
            )
            for k in obj["move_history"]
        ],
        white_user_id=UUID(obj["white_user_id"]) if obj["white_user_id"] else None,
        black_user_id=UUID(obj["black_user_id"]) if obj["black_user_id"] else None,
        invite_secret=obj["invite_secret"],
        next_turn=ChessPieceColor(obj["next_turn"]),
    )


async def create_chess_game(
    context: AbstractContext,
    white_user_id: UUID | None,
    black_user_id: UUID | None,
) -> ChessGame:
    chess_game = ChessGame(
        game_id=uuid4(),
        white_user_id=white_user_id,
        black_user_id=black_user_id,
        invite_secret=secrets.token_hex(16),
    )
    await context.redis_connection.set(
        f"chess_game:{chess_game.game_id}",
        serialize(chess_game),
    )
    return chess_game


async def get_chess_game(context: AbstractContext, game_id: UUID) -> ChessGame | None:
    game_data: bytes | None = await context.redis_connection.get(
        f"chess_game:{game_id}",
    )
    if game_data is None:
        return None
    return deserialize(game_data)


async def get_all_chess_games(context: AbstractContext) -> list[ChessGame]:
    chess_games: list[ChessGame] = []
    for key in await context.redis_connection.keys("chess_game:*"):
        game_data: bytes | None = await context.redis_connection.get(key)
        if game_data is None:
            logging.warning(
                "Failed to deserialize chess game data for key %s",
                key,
                extra={"context": {"key": key}},
            )
            continue
        chess_game = deserialize(game_data)
        chess_games.append(chess_game)
    return chess_games


async def update_chess_game(context: AbstractContext, chess_game: ChessGame) -> None:
    await context.redis_connection.set(
        f"chess_game:{chess_game.game_id}",
        serialize(chess_game),
    )
    return None


async def delete_chess_game(context: AbstractContext, game_id: UUID) -> None:
    await context.redis_connection.delete(f"chess_game:{game_id}")
    return None
