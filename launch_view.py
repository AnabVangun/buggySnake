from collections.abc import Callable

from launch_view_model import DEFAULT_DIMENSION, LaunchViewModel

QUIT_HINT = "(q = quit)"


class LaunchView:
    def __init__(
        self,
        view_model: LaunchViewModel,
        start_game: Callable[[int, int], None],
        read_input: Callable[[str], str] = input,
        write: Callable[[str], None] = print,
    ) -> None:
        self._view_model = view_model
        self._start_game = start_game
        self._read_input = read_input
        self._write = write

    def run(self) -> None:
        while True:
            self._display_screen()
            dimensions = self._ask_dimensions()
            if dimensions is None:
                return
            self._start_game(*dimensions)

    def _display_screen(self) -> None:
        for line in self._view_model.header_lines():
            self._write(line)
        self._write("")
        self._write(QUIT_HINT)

    def _ask_dimensions(self) -> tuple[int, int] | None:
        width = self._ask_dimension("Width")
        if width is None:
            return None
        height = self._ask_dimension("Height")
        if height is None:
            return None
        return width, height

    def _ask_dimension(self, label: str) -> int | None:
        prompt = f"{label} [{DEFAULT_DIMENSION}]: "
        while True:
            raw_input = self._read_input(prompt)
            if self._view_model.is_quit(raw_input):
                return None
            value = self._view_model.parse_dimension(raw_input)
            if value is not None:
                return value