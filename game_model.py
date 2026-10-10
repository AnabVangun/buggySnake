import random
from enum import Enum

Cell = tuple[int, int]

APPLES_TO_WIN = 10


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

    @property
    def row_delta(self) -> int:
        return self.value[0]

    @property
    def col_delta(self) -> int:
        return self.value[1]


class GameStatus(Enum):
    PLAYING = "PLAYING"
    WON = "WON"
    LOST = "LOST"


class GameModel:
    def __init__(self, n: int, m: int, rng: random.Random) -> None:
        self._validate_dimension(n)
        self._validate_dimension(m)
        self.n = n
        self.m = m
        self._rng = rng
        self._snake: list[Cell] = [(m // 2, n // 2)]
        self._direction: Direction | None = None
        self._apple: Cell | None = None
        self._moves = 0
        self._apples_eaten = 0
        self._status = GameStatus.PLAYING
        self._apple = self._draw_apple(self.free_cells())

    @property
    def snake(self) -> tuple[Cell, ...]:
        return tuple(self._snake)

    @property
    def head(self) -> Cell:
        return self._snake[0]

    @property
    def apple(self) -> Cell | None:
        return self._apple

    @property
    def direction(self) -> Direction | None:
        return self._direction

    @property
    def moves(self) -> int:
        return self._moves

    @property
    def apples_eaten(self) -> int:
        return self._apples_eaten

    @property
    def status(self) -> GameStatus:
        return self._status

    def free_cells(self) -> list[Cell]:
        occupied = set(self._snake)
        return [
            (row, col)
            for row in range(self.m)
            for col in range(self.n)
            if (row, col) not in occupied
        ]

    def move(self, direction: Direction) -> None:
        self._ensure_playing()
        self._direction = direction
        self._moves += 1
        new_head = self._compute_new_head(direction)
        if self._is_fatal(new_head):
            self._status = GameStatus.LOST
            return
        self._advance_to(new_head)

    @staticmethod
    def _validate_dimension(value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("dimensions must be strictly positive integers")

    def _ensure_playing(self) -> None:
        if self._status is not GameStatus.PLAYING:
            raise RuntimeError("the game is over")

    def _compute_new_head(self, direction: Direction) -> Cell:
        row, col = self.head
        return row + direction.row_delta, col + direction.col_delta

    def _is_fatal(self, new_head: Cell) -> bool:
        return self._is_outside_board(new_head) or self._hits_body(new_head)

    def _is_outside_board(self, cell: Cell) -> bool:
        row, col = cell
        return not (0 <= row < self.m and 0 <= col < self.n)

    def _hits_body(self, cell: Cell) -> bool:
        return len(self._snake) > 3 and cell in self._snake[:-1]

    def _advance_to(self, new_head: Cell) -> None:
        if new_head == self._apple:
            self._eat_apple_at(new_head)
        else:
            self._slide_to(new_head)

    def _slide_to(self, new_head: Cell) -> None:
        self._snake.insert(0, new_head)
        self._snake.pop()

    def _eat_apple_at(self, new_head: Cell) -> None:
        free_cells = self.free_cells()
        self._snake.insert(0, new_head)
        self._apples_eaten += 1
        if self._apples_eaten >= APPLES_TO_WIN:
            self._finish_with_victory()
        else:
            self._apple = self._draw_apple(free_cells)

    def _finish_with_victory(self) -> None:
        self._status = GameStatus.WON
        self._apple = None

    def _draw_apple(self, free_cells: list[Cell]) -> Cell | None:
        if not free_cells:
            return None
        return self._rng.choice(free_cells)
