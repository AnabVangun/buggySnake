from collections.abc import Callable
from enum import Enum

from game_model import Direction, GameModel, GameStatus
from score_repository import ScoreEntry, ScoreRepository, current_timestamp

ANONYMOUS_NAME = "anonymous"
MAX_NAME_LENGTH = 20
QUIT_KEY = "q"
KEY_TO_DIRECTION = {
    "h": Direction.UP,
    "b": Direction.DOWN,
    "g": Direction.LEFT,
    "d": Direction.RIGHT,
}
EMPTY_CHAR = "\u00b7"
HEAD_CHAR = "@"
BODY_CHAR = "0"
APPLE_CHAR = "*"
CORNER_CHAR = "+"
HORIZONTAL_WALL_CHAR = "-"
VERTICAL_WALL_CHAR = "|"
VICTORY_MESSAGE = "You won!"
DEFEAT_MESSAGE = "Game over."


class KeyResult(Enum):
    MOVED = "MOVED"
    QUIT = "QUIT"
    INVALID = "INVALID"


def normalize_player_name(raw_name: str) -> str:
    if raw_name == "":
        return ANONYMOUS_NAME
    return raw_name.strip()[:MAX_NAME_LENGTH]


class GameViewModel:
    def __init__(
        self,
        model: GameModel,
        repository: ScoreRepository,
        clock: Callable[[], str] = current_timestamp,
    ) -> None:
        self._model = model
        self._repository = repository
        self._clock = clock
        self._x, self._y = model.n, model.m

    @property
    def moves(self) -> int:
        return self._model.moves

    @property
    def apples(self) -> int:
        return self._model.apples_eaten

    @property
    def is_playing(self) -> bool:
        return self._model.status is GameStatus.PLAYING

    @property
    def has_won(self) -> bool:
        return self._model.status is GameStatus.WON

    @property
    def counters_line(self) -> str:
        return f"Moves: {self.moves}   Apples: {self.apples}"

    @property
    def result_message(self) -> str:
        self._ensure_finished()
        return VICTORY_MESSAGE if self.has_won else DEFEAT_MESSAGE

    def board_lines(self) -> list[str]:
        border = self._border_line()
        rows = [self._render_row(row) for row in range(self._x)]
        return [border, *rows, border]

    def handle_key(self, key: str) -> KeyResult:
        if key == QUIT_KEY:
            return KeyResult.QUIT
        direction = KEY_TO_DIRECTION.get(key)
        if direction is None:
            return KeyResult.INVALID
        self._model.move(direction)
        return KeyResult.MOVED

    def save_score(self, raw_name: str) -> ScoreEntry:
        self._ensure_finished()
        entry = self._build_entry(raw_name)
        self._repository.save(entry)
        return entry

    def _ensure_finished(self) -> None:
        if self.is_playing:
            raise RuntimeError("the game is not finished")

    def _build_entry(self, raw_name: str) -> ScoreEntry:
        return ScoreEntry(
            player=normalize_player_name(raw_name),
            apples=self.apples,
            moves=self.moves,
            width=self._y,
            height=self._x,
            date=self._clock(),
        )

    def _border_line(self) -> str:
        return CORNER_CHAR + HORIZONTAL_WALL_CHAR * self._y + CORNER_CHAR

    def _render_row(self, row: int) -> str:
        cells = "".join(self._render_cell((row, col)) for col in range(self._y))
        return VERTICAL_WALL_CHAR + cells + VERTICAL_WALL_CHAR

    def _render_cell(self, cell: tuple[int, int]) -> str:
        if cell == self._model.head:
            return HEAD_CHAR
        if cell in self._model.snake:
            return BODY_CHAR
        if cell == self._model.apple:
            return APPLE_CHAR
        return EMPTY_CHAR