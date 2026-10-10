from score_repository import ScoreEntry, ScoreRepository

DEFAULT_DIMENSION = 8
QUIT_KEY = "q"
TITLE = "=== SNAKE ==="
SCORES_TITLE = "Top scores"
RANK_WIDTH = 2
PLAYER_WIDTH = 20
APPLES_WIDTH = 6
MOVES_WIDTH = 5
COLUMN_SEPARATOR = "  "


class LaunchViewModel:
    def __init__(self, repository: ScoreRepository) -> None:
        self._repository = repository

    def header_lines(self) -> list[str]:
        return [TITLE, SCORES_TITLE, *self.score_table_lines()]

    def score_table_lines(self) -> list[str]:
        rows = [
            self._format_row(rank, entry)
            for rank, entry in enumerate(self._repository.top_scores(), start=1)
        ]
        return [self._format_header(), *rows]

    def is_quit(self, raw_input: str) -> bool:
        return raw_input.strip().lower() == QUIT_KEY

    def parse_dimension(self, raw_input: str) -> int | None:
        stripped = raw_input.strip()
        if stripped == "":
            return DEFAULT_DIMENSION
        if not (stripped.isascii() and stripped.isdigit()):
            return None
        value = int(stripped)
        return value if value > 0 else None

    def _format_header(self) -> str:
        return self._join_columns("#", "Player", "Apples", "Moves", "Grid")

    def _format_row(self, rank: int, entry: ScoreEntry) -> str:
        return self._join_columns(
            str(rank),
            entry.player,
            self._format_apples(entry.apples),
            str(entry.moves),
            f"{entry.width}x{entry.height}",
        )

    def _format_apples(self, apples: int) -> str:
        return str(apples)[-1:]

    def _join_columns(
        self, rank: str, player: str, apples: str, moves: str, grid: str
    ) -> str:
        return COLUMN_SEPARATOR.join(
            [
                f"{rank:>{RANK_WIDTH}}",
                f"{player:<{PLAYER_WIDTH}}",
                f"{apples:<{APPLES_WIDTH}}",
                f"{moves:<{MOVES_WIDTH}}",
                grid,
            ]
        )