import json
import tempfile
import unittest
from pathlib import Path

from score_repository import ScoreEntry, ScoreRepository


def make_entry(
    player="alice",
    apples=10,
    moves=23,
    width=8,
    height=8,
    date="2026-01-01T10:00:00",
):
    return ScoreEntry(player, apples, moves, width, height, date)


class ScoreRepositoryTest(unittest.TestCase):
    def setUp(self):
        directory = self.enterContext(tempfile.TemporaryDirectory())
        self.path = Path(directory) / "scores.json"
        self.warnings = []
        self.repository = ScoreRepository(self.path, self.warnings.append)

    def test_missing_file_gives_empty_scores_without_warning(self):
        self.assertEqual(self.repository.load_all(), [])
        self.assertEqual(self.repository.top_scores(), [])
        self.assertEqual(self.warnings, [])
        self.assertFalse(self.path.exists())

    def test_save_creates_missing_file(self):
        self.repository.save(make_entry())
        self.assertTrue(self.path.exists())

    def test_saved_entry_is_read_back_identically(self):
        entry = make_entry(player="bob", apples=7, moves=31, width=10, height=10)
        self.repository.save(entry)
        self.assertEqual(self.repository.load_all(), [entry])

    def test_file_contains_a_list_of_objects_with_expected_fields(self):
        self.repository.save(make_entry())
        content = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(len(content), 1)
        self.assertEqual(
            set(content[0]),
            {"player", "apples", "moves", "width", "height", "date"},
        )

    def test_successive_saves_accumulate_entries(self):
        first = make_entry(player="alice")
        second = make_entry(player="bob")
        self.repository.save(first)
        self.repository.save(second)
        self.assertEqual(self.repository.load_all(), [first, second])

    def test_corrupted_file_warns_and_is_treated_as_empty(self):
        self.path.write_text("{not json", encoding="utf-8")
        self.assertEqual(self.repository.load_all(), [])
        self.assertEqual(len(self.warnings), 1)

    def test_corrupted_file_is_not_overwritten_by_loading(self):
        self.path.write_text("{not json", encoding="utf-8")
        self.repository.load_all()
        self.assertEqual(self.path.read_text(encoding="utf-8"), "{not json")

    def test_save_replaces_corrupted_file(self):
        self.path.write_text("{not json", encoding="utf-8")
        entry = make_entry()
        self.repository.save(entry)
        self.assertEqual(self.repository.load_all(), [entry])

    def test_wrong_structure_is_treated_as_corrupted(self):
        invalid_contents = [
            "{}",
            '[{"player": "alice"}]',
            '[{"player": 1, "apples": 1, "moves": 1, "width": 1, "height": 1, "date": "d"}]',
            "[1, 2]",
        ]
        for content in invalid_contents:
            with self.subTest(content=content):
                self.warnings.clear()
                self.path.write_text(content, encoding="utf-8")
                self.assertEqual(self.repository.load_all(), [])
                self.assertEqual(len(self.warnings), 1)

    def test_ranking_orders_by_apples_descending_first(self):
        low = make_entry(player="low", apples=7, moves=1, width=1, height=1)
        high = make_entry(player="high", apples=10, moves=99, width=50, height=50)
        self.repository.save(low)
        self.repository.save(high)
        self.assertEqual(self.repository.top_scores(), [high, low])

    def test_ranking_breaks_apple_ties_by_smaller_area(self):
        large = make_entry(player="large", width=8, height=8, moves=1)
        small = make_entry(player="small", width=6, height=6, moves=99)
        self.repository.save(large)
        self.repository.save(small)
        self.assertEqual(self.repository.top_scores(), [small, large])

    def test_ranking_breaks_area_ties_by_fewer_moves(self):
        slow = make_entry(player="slow", width=6, height=6, moves=41)
        fast = make_entry(player="fast", width=4, height=9, moves=30)
        self.repository.save(slow)
        self.repository.save(fast)
        self.assertEqual(self.repository.top_scores(), [fast, slow])

    def test_ranking_breaks_move_ties_by_earlier_date(self):
        late = make_entry(player="late", date="2026-03-01T10:00:00")
        early = make_entry(player="early", date="2026-02-01T10:00:00")
        self.repository.save(late)
        self.repository.save(early)
        self.assertEqual(self.repository.top_scores(), [early, late])

    def test_ranking_is_global_across_grid_sizes(self):
        carol = make_entry(player="carol", apples=10, moves=41, width=6, height=6)
        alice = make_entry(player="alice", apples=10, moves=23, width=8, height=8)
        bob = make_entry(player="bob", apples=7, moves=31, width=10, height=10)
        for entry in (bob, alice, carol):
            self.repository.save(entry)
        self.assertEqual(self.repository.top_scores(), [carol, alice, bob])

    def test_top_scores_keeps_only_ten_entries(self):
        for index in range(12):
            self.repository.save(make_entry(player=f"player{index}", moves=index))
        top = self.repository.top_scores()
        self.assertEqual(len(top), 10)
        self.assertEqual([entry.moves for entry in top], list(range(10)))

    def test_top_scores_is_reread_from_file_each_time(self):
        self.assertEqual(self.repository.top_scores(), [])
        self.path.write_text(
            json.dumps([make_entry().to_dict()]), encoding="utf-8"
        )
        self.assertEqual(len(self.repository.top_scores()), 1)


if __name__ == "__main__":
    unittest.main()
