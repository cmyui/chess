#!/usr/bin/env python3
from __future__ import annotations

import secrets
from uuid import uuid4

from app.chess import BoardSquare
from app.chess import ChessGame
from app.chess import ChessPiece
from app.chess import ChessPieceColor
from app.chess import ChessPieceType
from app.chess import Move

if __name__ == "__main__":
    chess_game = ChessGame(
        game_id=uuid4(),
        invite_secret=secrets.token_hex(16),
    )
    chess_game.board.reset_to_starting_position()

    move = Move(
        square_from=BoardSquare(file="E", rank="2"),
        square_to=BoardSquare(file="E", rank="4"),
        chess_piece=ChessPiece(
            piece_type=ChessPieceType.PAWN,
            color=ChessPieceColor.WHITE,
        ),
    )
    chess_game.move_piece(move)
    chess_game.board.print_chess_board()
