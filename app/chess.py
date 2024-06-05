from __future__ import annotations

from enum import StrEnum
from typing import Literal
from typing import TypeGuard
from uuid import UUID

from pydantic import BaseModel


FileType = Literal["A", "B", "C", "D", "E", "F", "G", "H"]
VALID_FILES: list[FileType] = ["A", "B", "C", "D", "E", "F", "G", "H"]

RankType = Literal["1", "2", "3", "4", "5", "6", "7", "8"]
VALID_RANKS: list[RankType] = ["1", "2", "3", "4", "5", "6", "7", "8"]


def is_valid_file(input: str) -> TypeGuard[FileType]:
    return input in VALID_FILES


def is_valid_rank(input: str) -> TypeGuard[RankType]:
    return input in VALID_RANKS


class ChessPieceType(StrEnum):
    KING = "KING"
    QUEEN = "QUEEN"
    ROOK = "ROOK"
    BISHOP = "BISHOP"
    KNIGHT = "KNIGHT"
    PAWN = "PAWN"


class ChessPieceColor(StrEnum):
    WHITE = "WHITE"
    BLACK = "BLACK"


class ChessPiece(BaseModel):
    piece_type: ChessPieceType
    color: ChessPieceColor

    def can_make_move(self, move: Move) -> bool:
        if self.piece_type is ChessPieceType.KING:
            return self._can_king_move(move)
        if self.piece_type is ChessPieceType.QUEEN:
            return self._can_queen_move(move)
        if self.piece_type is ChessPieceType.ROOK:
            return self._can_rook_move(move)
        if self.piece_type is ChessPieceType.BISHOP:
            return self._can_bishop_move(move)
        if self.piece_type is ChessPieceType.KNIGHT:
            return self._can_knight_move(move)
        if self.piece_type is ChessPieceType.PAWN:
            return self._can_pawn_move(move)

        return False

    def _can_king_move(self, move: Move) -> bool:
        # Kings may move in any direction, but only one square at a time.
        # This includes diagonally, horizontally, and vertically.
        return (
            abs(ord(move.square_from.file) - ord(move.square_to.file)) <= 1
            and abs(int(move.square_from.rank) - int(move.square_to.rank)) <= 1
        )

    def _can_queen_move(self, move: Move) -> bool:
        # Queens may move in any direction, but they cannot jump over other pieces.
        return self._can_rook_move(move) or self._can_bishop_move(move)

    def _can_rook_move(self, move: Move) -> bool:
        # Rooks may move horizontally or vertically, but they cannot jump over other pieces.
        return (
            move.square_from.file == move.square_to.file
            or move.square_from.rank == move.square_to.rank
        )

    def _can_bishop_move(self, move: Move) -> bool:
        # Bishops may move diagonally, but they cannot jump over other pieces.
        return abs(ord(move.square_from.file) - ord(move.square_to.file)) == abs(
            int(move.square_from.rank) - int(move.square_to.rank),
        )

    def _can_knight_move(self, move: Move) -> bool:
        # Knights may move in an L-shape, two squares in one direction and one square in the other.
        return (
            abs(ord(move.square_from.file) - ord(move.square_to.file)) == 1
            and abs(int(move.square_from.rank) - int(move.square_to.rank)) == 2
            or abs(ord(move.square_from.file) - ord(move.square_to.file)) == 2
            and abs(int(move.square_from.rank) - int(move.square_to.rank)) == 1
        )

    def _can_pawn_move(self, move: Move) -> bool:
        # Pawns may move forward one square, but they capture diagonally.
        # Pawns may move two squares forward on their first move.
        # Pawns may not move backwards.
        # Pawns may not capture pieces directly in front of them.
        # Pawns may promote to any other piece when they reach the opposite side of the board.
        return (
            move.square_from.file == move.square_to.file
            and (
                (move.square_from.rank == "2" and move.square_to.rank == "4")
                or (move.square_from.rank == "7" and move.square_to.rank == "5")
                or abs(int(move.square_from.rank) - int(move.square_to.rank)) == 1
            )
        ) or (
            abs(ord(move.square_from.file) - ord(move.square_to.file)) == 1
            and abs(int(move.square_from.rank) - int(move.square_to.rank)) == 1
        )


class BoardSquare(BaseModel):
    file: FileType
    rank: RankType

    def __repr__(self) -> str:
        return f"{self.file}{self.rank}"

    def __hash__(self) -> int:
        return hash((self.file, self.rank))


class ChessBoard(BaseModel):
    pieces: dict[BoardSquare, ChessPiece] = {}

    def set_piece(self, *, square: BoardSquare, piece: ChessPiece) -> None:
        self.pieces[square] = piece

    def remove_piece(self, square: BoardSquare) -> None:
        del self.pieces[square]

    def is_square_occupied(self, square: BoardSquare) -> bool:
        return square in self.pieces

    def get_piece_on_square(self, square: BoardSquare) -> ChessPiece | None:
        return self.pieces.get(square)

    def reset_to_starting_position(self) -> None:
        self.pieces = {square: piece for square, piece in STARTING_POSITION.items()}

    def print_chess_board(self) -> None:
        for rank in VALID_RANKS:
            for file in VALID_FILES:
                square = BoardSquare(file=file, rank=rank)
                piece = self.get_piece_on_square(square)
                if piece is not None:
                    print(
                        (
                            piece.piece_type.value.lower()
                            if piece.color is ChessPieceColor.BLACK
                            else piece.piece_type.value
                        ),
                        end="",
                    )
            print()

        print("(White pieces are uppercase, black pieces are lowercase)")


class Move(BaseModel):
    square_from: BoardSquare
    square_to: BoardSquare
    chess_piece: ChessPiece


class ChessGame(BaseModel):
    game_id: UUID
    board: ChessBoard = ChessBoard()
    move_history: list[Move] = []

    white_user_id: UUID | None = None
    black_user_id: UUID | None = None
    invite_secret: str

    next_turn: ChessPieceColor = ChessPieceColor.WHITE

    def move_piece(self, move: Move) -> None:
        piece = self.board.get_piece_on_square(move.square_from)
        if piece is None:
            raise ValueError("No piece on the square")
        self.board.remove_piece(move.square_from)
        self.board.set_piece(square=move.square_to, piece=piece)
        self.move_history.append(move)
        self.next_turn = (
            ChessPieceColor.WHITE
            if self.next_turn == ChessPieceColor.BLACK
            else ChessPieceColor.BLACK
        )

    def get_user_color(self, user_id: UUID) -> ChessPieceColor | None:
        if user_id == self.white_user_id:
            return ChessPieceColor.WHITE
        if user_id == self.black_user_id:
            return ChessPieceColor.BLACK
        return None


# fmt: off
STARTING_POSITION: dict[BoardSquare, ChessPiece] = {
    BoardSquare(file="E", rank="1"): ChessPiece(piece_type=ChessPieceType.KING, color=ChessPieceColor.WHITE),
    BoardSquare(file="D", rank="1"): ChessPiece(piece_type=ChessPieceType.QUEEN, color=ChessPieceColor.WHITE),
    BoardSquare(file="A", rank="1"): ChessPiece(piece_type=ChessPieceType.ROOK, color=ChessPieceColor.WHITE),
    BoardSquare(file="H", rank="1"): ChessPiece(piece_type=ChessPieceType.ROOK, color=ChessPieceColor.WHITE),
    BoardSquare(file="C", rank="1"): ChessPiece(piece_type=ChessPieceType.BISHOP, color=ChessPieceColor.WHITE),
    BoardSquare(file="F", rank="1"): ChessPiece(piece_type=ChessPieceType.BISHOP, color=ChessPieceColor.WHITE),
    BoardSquare(file="B", rank="1"): ChessPiece(piece_type=ChessPieceType.KNIGHT, color=ChessPieceColor.WHITE),
    BoardSquare(file="G", rank="1"): ChessPiece(piece_type=ChessPieceType.KNIGHT, color=ChessPieceColor.WHITE),
    BoardSquare(file="A", rank="2"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.WHITE),
    BoardSquare(file="B", rank="2"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.WHITE),
    BoardSquare(file="C", rank="2"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.WHITE),
    BoardSquare(file="D", rank="2"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.WHITE),
    BoardSquare(file="E", rank="2"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.WHITE),
    BoardSquare(file="F", rank="2"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.WHITE),
    BoardSquare(file="G", rank="2"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.WHITE),
    BoardSquare(file="H", rank="2"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.WHITE),

    BoardSquare(file="E", rank="8"): ChessPiece(piece_type=ChessPieceType.KING, color=ChessPieceColor.BLACK),
    BoardSquare(file="D", rank="8"): ChessPiece(piece_type=ChessPieceType.QUEEN, color=ChessPieceColor.BLACK),
    BoardSquare(file="A", rank="8"): ChessPiece(piece_type=ChessPieceType.ROOK, color=ChessPieceColor.BLACK),
    BoardSquare(file="H", rank="8"): ChessPiece(piece_type=ChessPieceType.ROOK, color=ChessPieceColor.BLACK),
    BoardSquare(file="C", rank="8"): ChessPiece(piece_type=ChessPieceType.BISHOP, color=ChessPieceColor.BLACK),
    BoardSquare(file="F", rank="8"): ChessPiece(piece_type=ChessPieceType.BISHOP, color=ChessPieceColor.BLACK),
    BoardSquare(file="B", rank="8"): ChessPiece(piece_type=ChessPieceType.KNIGHT, color=ChessPieceColor.BLACK),
    BoardSquare(file="G", rank="8"): ChessPiece(piece_type=ChessPieceType.KNIGHT, color=ChessPieceColor.BLACK),
    BoardSquare(file="A", rank="7"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.BLACK),
    BoardSquare(file="B", rank="7"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.BLACK),
    BoardSquare(file="C", rank="7"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.BLACK),
    BoardSquare(file="D", rank="7"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.BLACK),
    BoardSquare(file="E", rank="7"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.BLACK),
    BoardSquare(file="F", rank="7"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.BLACK),
    BoardSquare(file="G", rank="7"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.BLACK),
    BoardSquare(file="H", rank="7"): ChessPiece(piece_type=ChessPieceType.PAWN, color=ChessPieceColor.BLACK),
}
# fmt: on
