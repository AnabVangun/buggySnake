import json
import warnings
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

DEFAULT_SCORES_PATH = Path(__file__).with_name("scores.json")
DEFAULT_TOP_LIMIT = 10
ENTRY_FIELD_TYPES = {
    "player": str,
    "apples": int,
    "moves": int,
    "width": int,
    "height": int,
    "date": str,
}


def current_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def warn_with_warnings_module(message: str) -> None:
    warnings.warn(message, RuntimeWarning, stacklevel=2)


@dataclass(frozen=True)
class ScoreEntry:
    player: str
    apples: int
    moves: int
    width: int
    height: int
    date: str

    @property
    def area(self) -> int:
        return self.width * self.height

    def ranking_key(self) -> tuple[int, int, int, str]:
        return -self.apples, self.area, self.moves, self.date

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: object) -> "ScoreEntry":
        if not isinstance(data, dict) or data.keys() != ENTRY_FIELD_TYPES.keys():
            raise ValueError("invalid score entry")
        for name, expected_type in ENTRY_FIELD_TYPES.items():
            if not isinstance(data[name], expected_type):
                raise ValueError(f"invalid type for field {name}")
        return cls(**data)


class ScoreRepository:
    def __init__(
        self,
        path: Path | str = DEFAULT_SCORES_PATH,
        warning_handler: Callable[[str], None] = warn_with_warnings_module,
    ) -> None:
        self._path = Path(path)
        self._warning_handler = warning_handler

    def load_all(self) -> list[ScoreEntry]:
        if not self._path.exists():
            return []
        try:
            return self._parse_entries(self._read_text())
        except ValueError:
            self._warning_handler(f"Corrupted scores file ignored: {self._path.name}")
            return []

    def _read_text(self) -> str:
        with self._path.open(encoding="ascii", errors="replace") as file:
            return file.read()

    def top_scores(self, limit: int = DEFAULT_TOP_LIMIT) -> list[ScoreEntry]:
        return sorted(self.load_all(), key=ScoreEntry.ranking_key)[:limit]

    def save(self, entry: ScoreEntry) -> None:
        entries = self.load_all()
        entries.append(entry)
        self._write_entries(entries)

    def _write_entries(self, entries: list[ScoreEntry]) -> None:
        payload = [entry.to_dict() for entry in entries]
        with self._path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    @staticmethod
    def _parse_entries(text: str) -> list[ScoreEntry]:
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("scores file must contain a list")
        return [ScoreEntry.from_dict(item) for item in data]
