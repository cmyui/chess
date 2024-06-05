#!/usr/bin/env python3
import secrets
from uuid import uuid4
from app.chess import ChessGame, BoardSquare, ChessPiece, ChessPieceColor, Move

if __name__ == "__main__":
    chess_game = ChessGame(
        game_id=uuid4(),
        invite_secret=secrets.token_hex(16),
    )
    chess_game.board.reset_to_starting_position()

    move = Move(
        square_from=BoardSquare(file="E", rank="2"),
        square_to=BoardSquare(file="E", rank="4"),
        chess_piece=ChessPiece.PAWN,
        piece_color=ChessPieceColor.WHITE,
    )
    chess_game.move_piece(move)
    chess_game.board.print_chess_board()
