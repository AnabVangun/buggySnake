from collections.abc import Callable

from game_view_model import GameViewModel, KeyResult

CLEAR_SEQUENCE = "\x1b[2J\x1b[H"
DIRECTION_PROMPT = "Direction (h/b/g/d, q = abandon): "
NAME_PROMPT = "Player name: "


class GameView:
    def __init__(
        self,
        view_model: GameViewModel,
        read_input: Callable[[str], str] = input,
        write: Callable[..., None] = print,
    ) -> None:
        self._view_model = view_model
        self._read_input = read_input
        self._write = write

    def run(self) -> None:
        if self._play_until_finished():
            self._conclude()

    def _play_until_finished(self) -> bool:
        while self._view_model.is_playing:
            self._render()
            key = self._read_input(DIRECTION_PROMPT)
            if self._view_model.handle_key(key) is KeyResult.QUIT:
                return False
        return True

    def _render(self) -> None:
        self._clear_terminal()
        self._write(self._view_model.counters_line)
        for line in self._view_model.board_lines():
            self._write(line)

    def _clear_terminal(self) -> None:
        self._write(CLEAR_SEQUENCE, end="", flush=True)

    def _conclude(self) -> None:
        self._write(self._view_model.result_message)
        self._write(self._view_model.counters_line)
        raw_name = self._read_input(NAME_PROMPT)
        self._view_model.save_score(raw_name)