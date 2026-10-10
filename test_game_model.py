import random
import unittest

from game_model import APPLES_TO_WIN, Direction, GameModel, GameStatus

PLACEMENT_SEED = 3


class FirstCellRandom(random.Random):
    def choice(self, seq):
        return seq[0]


def build_model(n, m, snake, apple=None, rng=None):
    model = GameModel(n, m, rng or FirstCellRandom())
    model._snake = list(snake)
    model._apple = apple
    return model


class InitialStateTest(unittest.TestCase):
    def test_head_starts_at_center_of_square_grid(self):
        self.assertEqual(GameModel(8, 8, FirstCellRandom()).head, (4, 4))

    def test_head_starts_at_center_of_5_by_4_grid(self):
        self.assertEqual(GameModel(5, 4, FirstCellRandom()).head, (2, 2))

    def test_head_row_depends_on_height_and_column_on_width(self):
        self.assertEqual(GameModel(7, 4, FirstCellRandom()).head, (2, 3))
        self.assertEqual(GameModel(4, 7, FirstCellRandom()).head, (3, 2))

    def test_head_starts_at_origin_of_1_by_1_grid(self):
        self.assertEqual(GameModel(1, 1, FirstCellRandom()).head, (0, 0))

    def test_initial_counters_and_status(self):
        model = GameModel(8, 8, FirstCellRandom())
        self.assertEqual(len(model.snake), 1)
        self.assertIsNone(model.direction)
        self.assertEqual(model.moves, 0)
        self.assertEqual(model.apples_eaten, 0)
        self.assertEqual(model.status, GameStatus.PLAYING)

    def test_non_positive_dimensions_are_rejected(self):
        for n, m in [(0, 5), (5, 0), (-1, 5), (5, -3)]:
            with self.subTest(n=n, m=m):
                with self.assertRaises(ValueError):
                    GameModel(n, m, FirstCellRandom())

    def test_free_cells_are_sorted_by_row_then_column(self):
        model = GameModel(2, 2, FirstCellRandom())
        self.assertEqual(model.free_cells(), [(0, 0), (0, 1), (1, 0)])


class MovementTest(unittest.TestCase):
    def test_each_direction_moves_head_by_one_cell(self):
        expected_heads = {
            Direction.UP: (1, 2),
            Direction.DOWN: (3, 2),
            Direction.LEFT: (2, 1),
            Direction.RIGHT: (2, 3),
        }
        for direction, expected_head in expected_heads.items():
            with self.subTest(direction=direction):
                model = GameModel(5, 5, FirstCellRandom())
                model.move(direction)
                self.assertEqual(model.snake, (expected_head,))
                self.assertEqual(model.direction, direction)
                self.assertEqual(model.moves, 1)
                self.assertEqual(model.status, GameStatus.PLAYING)

    def test_moves_counter_increments_every_turn(self):
        model = GameModel(8, 8, FirstCellRandom())
        for expected in range(1, 4):
            model.move(Direction.RIGHT)
            self.assertEqual(model.moves, expected)

    def test_snake_without_apple_keeps_its_length(self):
        model = build_model(6, 6, [(2, 2), (2, 1)])
        model.move(Direction.RIGHT)
        self.assertEqual(model.snake, ((2, 3), (2, 2)))

    def test_move_after_game_over_is_rejected(self):
        model = GameModel(1, 1, FirstCellRandom())
        model.move(Direction.UP)
        with self.assertRaises(RuntimeError):
            model.move(Direction.DOWN)


class GrowthTest(unittest.TestCase):
    def test_eating_apple_grows_snake_and_counts_apple(self):
        model = build_model(5, 5, [(2, 2)], apple=(2, 3))
        model.move(Direction.RIGHT)
        self.assertEqual(model.snake, ((2, 3), (2, 2)))
        self.assertEqual(model.apples_eaten, 1)
        self.assertEqual(model.moves, 1)

    def test_eating_apple_places_new_apple_on_free_cell(self):
        model = build_model(5, 5, [(2, 2)], apple=(2, 3))
        model.move(Direction.RIGHT)
        self.assertIsNotNone(model.apple)
        self.assertNotIn(model.apple, model.snake)

    def test_snake_stops_growing_after_apple_is_eaten(self):
        model = build_model(5, 5, [(2, 2)], apple=(2, 3))
        model.move(Direction.RIGHT)
        model.move(Direction.RIGHT)
        self.assertEqual(len(model.snake), 2)


class WallCollisionTest(unittest.TestCase):
    WIDTH = 5
    HEIGHT = 3

    def test_each_wall_is_fatal_on_non_square_grid(self):
        cases = [
            ((0, 2), Direction.UP),
            ((2, 2), Direction.DOWN),
            ((1, 0), Direction.LEFT),
            ((1, 4), Direction.RIGHT),
        ]
        for head, direction in cases:
            with self.subTest(head=head, direction=direction):
                model = build_model(self.WIDTH, self.HEIGHT, [head])
                model.move(direction)
                self.assertEqual(model.status, GameStatus.LOST)

    def test_fatal_move_is_counted(self):
        model = build_model(self.WIDTH, self.HEIGHT, [(0, 0)])
        model.move(Direction.UP)
        self.assertEqual(model.moves, 1)

    def test_last_cells_of_non_square_grid_are_reachable(self):
        cases = [
            ((1, 4), Direction.DOWN, (2, 4)),
            ((0, 3), Direction.RIGHT, (0, 4)),
            ((2, 4), Direction.UP, (1, 4)),
            ((2, 1), Direction.LEFT, (2, 0)),
        ]
        for head, direction, expected_head in cases:
            with self.subTest(head=head, direction=direction):
                model = build_model(self.WIDTH, self.HEIGHT, [head])
                model.move(direction)
                self.assertEqual(model.status, GameStatus.PLAYING)
                self.assertEqual(model.head, expected_head)


class BodyCollisionTest(unittest.TestCase):
    def test_first_move_is_always_free(self):
        for direction in Direction:
            with self.subTest(direction=direction):
                model = GameModel(5, 5, FirstCellRandom())
                model.move(direction)
                self.assertEqual(model.status, GameStatus.PLAYING)

    def test_u_turn_at_length_two_swaps_head_and_tail(self):
        model = build_model(5, 5, [(1, 1), (1, 2)])
        model.move(Direction.RIGHT)
        self.assertEqual(model.status, GameStatus.PLAYING)
        self.assertEqual(model.snake, ((1, 2), (1, 1)))

    def test_u_turn_at_length_five_is_fatal(self):
        model = build_model(7, 3, [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)])
        model.move(Direction.RIGHT)
        self.assertEqual(model.status, GameStatus.LOST)

    def test_hitting_middle_of_body_is_fatal(self):
        model = build_model(5, 5, [(1, 1), (1, 2), (2, 2), (2, 1), (3, 1)])
        model.move(Direction.DOWN)
        self.assertEqual(model.status, GameStatus.LOST)

    def test_chasing_own_tail_at_length_four_is_safe(self):
        model = build_model(5, 5, [(1, 1), (1, 2), (2, 2), (2, 1)])
        model.move(Direction.DOWN)
        self.assertEqual(model.status, GameStatus.PLAYING)
        self.assertEqual(model.snake, ((2, 1), (1, 1), (1, 2), (2, 2)))


class VictoryTest(unittest.TestCase):
    def test_tenth_apple_wins_without_placing_new_apple(self):
        model = build_model(8, 8, [(4, 4)], apple=(4, 5))
        model._apples_eaten = APPLES_TO_WIN - 1
        model.move(Direction.RIGHT)
        self.assertEqual(model.status, GameStatus.WON)
        self.assertEqual(model.apples_eaten, APPLES_TO_WIN)
        self.assertIsNone(model.apple)

    def test_ninth_apple_does_not_win(self):
        model = build_model(8, 8, [(4, 4)], apple=(4, 5))
        model._apples_eaten = APPLES_TO_WIN - 2
        model.move(Direction.RIGHT)
        self.assertEqual(model.status, GameStatus.PLAYING)
        self.assertIsNotNone(model.apple)

    def test_move_after_victory_is_rejected(self):
        model = build_model(8, 8, [(4, 4)], apple=(4, 5))
        model._apples_eaten = APPLES_TO_WIN - 1
        model.move(Direction.RIGHT)
        with self.assertRaises(RuntimeError):
            model.move(Direction.RIGHT)


class AppleTest(unittest.TestCase):
    def test_initial_apple_is_drawn_from_sorted_free_cells(self):
        model = GameModel(8, 8, random.Random(PLACEMENT_SEED))
        expected = random.Random(PLACEMENT_SEED).choice(model.free_cells())
        self.assertEqual(model.apple, expected)
        self.assertNotIn(model.apple, model.snake)

    def test_same_seed_gives_same_initial_apple(self):
        first = GameModel(8, 8, random.Random(PLACEMENT_SEED))
        second = GameModel(8, 8, random.Random(PLACEMENT_SEED))
        self.assertEqual(first.apple, second.apple)

    def test_new_apple_after_capture_is_on_board_and_off_snake(self):
        model = build_model(
            8, 8, [(4, 4)], apple=(4, 5), rng=random.Random(PLACEMENT_SEED)
        )
        model.move(Direction.RIGHT)
        row, col = model.apple
        self.assertTrue(0 <= row < model.m and 0 <= col < model.n)
        self.assertNotIn(model.apple, model.snake)


if __name__ == "__main__":
    unittest.main()
