"""Tests for the retrieval evaluation.

These fix the arithmetic behind published recall figures, and one design
decision that quietly decides whether a method looks good: how ties are
broken. A method that scores everything identically has found nothing, and
optimistic tie-breaking would report it as perfect.
"""

from __future__ import annotations

import unittest

import numpy as np

from crosswalk_ledger.retrieval import evaluate, random_scores, rank_positions


class TiesAreBrokenPessimistically(unittest.TestCase):
    def test_a_flat_score_vector_puts_the_true_answer_last(self):
        scores = np.ones(10)
        self.assertEqual(rank_positions(scores, [0]), [10])

    def test_a_method_with_no_discrimination_scores_zero_not_one(self):
        # Ten candidates, all scored the same, the truth among them.
        scores = np.ones((1, 10))
        result = evaluate(scores, {0: [3]}, method="flat", pair="p", direction="d")
        self.assertEqual(result.recall_at[1], 0.0)
        self.assertEqual(result.recall_at[5], 0.0)

    def test_which_makes_every_published_figure_a_floor(self):
        scores = np.array([[0.9, 0.9, 0.1]])
        # Truth is one of the two tied leaders, so its rank is 2, not 1.
        self.assertEqual(rank_positions(scores[0], [0]), [2])


class RecallCountsElementsNotPairs(unittest.TestCase):
    def test_an_element_hits_when_any_counterpart_is_within_k(self):
        scores = np.array([[0.1, 0.9, 0.2]])
        result = evaluate(scores, {0: [0, 1]}, method="m", pair="p", direction="d")
        self.assertEqual(result.recall_at[1], 1.0)

    def test_a_second_element_is_averaged_in(self):
        scores = np.array([[0.9, 0.1], [0.1, 0.9]])
        result = evaluate(scores, {0: [0], 1: [0]}, method="m", pair="p", direction="d")
        self.assertEqual(result.recall_at[1], 0.5)

    def test_pair_recall_counts_every_recorded_counterpart(self):
        # Both counterparts inside the top 10 of a 3-candidate problem.
        scores = np.array([[0.9, 0.8, 0.1]])
        result = evaluate(scores, {0: [0, 1]}, method="m", pair="p", direction="d")
        self.assertEqual(result.pair_recall_at_10, 1.0)


class UnansweredElementsAreNotQueried(unittest.TestCase):
    def test_only_elements_with_a_recorded_counterpart_count(self):
        scores = np.random.default_rng(0).random((5, 4))
        result = evaluate(scores, {2: [1]}, method="m", pair="p", direction="d")
        self.assertEqual(result.queried, 1)

    def test_because_absence_from_a_mapping_is_silence(self):
        # Four of five elements unmapped; the one mapped is found first.
        scores = np.zeros((5, 4))
        scores[2][1] = 1.0
        result = evaluate(scores, {2: [1]}, method="m", pair="p", direction="d")
        self.assertEqual(result.recall_at[1], 1.0)


class TheReportedFieldsAreConsistent(unittest.TestCase):
    def setUp(self) -> None:
        scores = np.array([[0.9, 0.5, 0.1], [0.1, 0.9, 0.5]])
        self.result = evaluate(
            scores, {0: [0], 1: [2]}, method="m", pair="a ↔ b", direction="a → b"
        )

    def test_candidates_is_the_width_of_the_matrix(self):
        self.assertEqual(self.result.candidates, 3)

    def test_recall_is_monotonic_in_k(self):
        values = [self.result.recall_at[k] for k in sorted(self.result.recall_at)]
        self.assertEqual(values, sorted(values))

    def test_recall_at_3_is_reported_because_humans_worked_at_that_density(self):
        self.assertIn(3, self.result.recall_at)

    def test_the_row_names_the_method_and_direction(self):
        self.assertIn("m", self.result.row())
        self.assertIn("a → b", self.result.row())

    def test_median_best_rank_is_the_median_of_the_best_ranks(self):
        # Element 0 finds its truth at rank 1; element 1 at rank 2.
        self.assertEqual(self.result.median_best_rank, 1.5)


class EmptyTruthDoesNotDivideByZero(unittest.TestCase):
    def test_no_queried_elements_gives_zeroes(self):
        result = evaluate(np.zeros((3, 3)), {}, method="m", pair="p", direction="d")
        self.assertEqual(result.queried, 0)
        self.assertEqual(set(result.recall_at.values()), {0.0})
        self.assertEqual(result.pair_recall_at_10, 0.0)


class TheRandomFloorIsReproducible(unittest.TestCase):
    def test_the_seed_is_pinned_so_the_published_floor_repeats(self):
        first = random_scores((4, 4))
        second = random_scores((4, 4))
        self.assertTrue(np.array_equal(first, second))

    def test_a_different_seed_gives_a_different_matrix(self):
        self.assertFalse(np.array_equal(random_scores((4, 4), 0), random_scores((4, 4), 1)))


if __name__ == "__main__":
    unittest.main()
