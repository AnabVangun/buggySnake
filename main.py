import random
import sys
from functools import partial

from game_model import GameModel
from game_view import GameView
from game_view_model import GameViewModel
from launch_view import LaunchView
from launch_view_model import LaunchViewModel
from score_repository import ScoreRepository


def play_game(repository: ScoreRepository, width: int, height: int) -> None:
    model = GameModel(height, width, random.Random())
    GameView(GameViewModel(model, repository)).run()


def build_launch_view(repository: ScoreRepository) -> LaunchView:
    return LaunchView(
        LaunchViewModel(repository),
        partial(play_game, repository),
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    repository = ScoreRepository()
    try:
        build_launch_view(repository).run()
    except (EOFError, KeyboardInterrupt):
        print()


if __name__ == "__main__":
    main()