"""Tests for the agreement measurement.

The headline result of this project is a pair of percentages, so most of
these fix the arithmetic behind them rather than checking that code runs. A
measurement whose definition can drift silently is worse than no measurement,
because the number keeps being published either way.
"""

from __future__ import annotations

import unittest

from crosswalk_ledger.agreement import compare, density


def mapping(**rows: str) -> dict[str, set[str]]:
    """`a="1.1 1.2"` → {"a": {"1.1", "1.2"}}. Empty string means unanswered."""
    return {key: set(value.split()) for key, value in rows.items()}


class SilenceIsNotDisagreement(unittest.TestCase):
    """The distinction the whole measurement rests on."""

    def test_an_element_only_one_side_mapped_is_not_compared(self):
        result = compare(mapping(a="5.1", b="5.2"), mapping(a="5.1", b=""), "left", "right")
        self.assertEqual(result.compared, 1)

    def test_it_is_counted_separately_rather_than_dropped(self):
        result = compare(mapping(a="5.1", b="5.2"), mapping(a="5.1", b=""), "left", "right")
        self.assertEqual(result.only_one_answered, 1)

    def test_a_sparse_mapping_is_not_punished_for_being_sparse(self):
        # Answers one element out of three, and agrees on it. Silence on the
        # other two must not drag the agreement below 100%.
        result = compare(mapping(a="5.1", b="5.2", c="5.3"), mapping(a="5.1", b="", c=""), "l", "r")
        self.assertEqual(result.exact, 1.0)
        self.assertEqual(result.loose, 1.0)


class TheTwoFiguresMeasureDifferentThings(unittest.TestCase):
    def test_exact_is_jaccard_over_pairs(self):
        # left {5.1, 5.2}, right {5.1, 5.3}: one shared of three distinct.
        result = compare(mapping(a="5.1 5.2"), mapping(a="5.1 5.3"), "l", "r")
        self.assertAlmostEqual(result.exact, 1 / 3)

    def test_loose_asks_only_whether_they_touch(self):
        result = compare(mapping(a="5.1 5.2"), mapping(a="5.1 5.3"), "l", "r")
        self.assertEqual(result.loose, 1.0)

    def test_no_shared_counterpart_scores_zero_on_both(self):
        result = compare(mapping(a="5.1"), mapping(a="8.15"), "l", "r")
        self.assertEqual(result.exact, 0.0)
        self.assertEqual(result.loose, 0.0)

    def test_a_thorough_mapper_is_penalised_by_jaccard_but_not_by_loose(self):
        # This is why both are reported. Nine against one, sharing one.
        many = mapping(a="5.8 5.9 5.12 5.13 5.19 5.22 7.10 7.13 5.11")
        one = mapping(a="5.11")
        result = compare(many, one, "many", "one")
        self.assertAlmostEqual(result.exact, 1 / 9)
        self.assertEqual(result.loose, 1.0)


class DisagreementsAreNamed(unittest.TestCase):
    def test_an_element_with_no_overlap_is_reported_with_both_readings(self):
        result = compare(mapping(a="8.16"), mapping(a="8.15"), "l", "r")
        self.assertEqual(len(result.disagreements), 1)
        self.assertEqual(result.disagreements[0].element, "a")
        self.assertEqual(result.disagreements[0].left_says, ("8.16",))
        self.assertEqual(result.disagreements[0].right_says, ("8.15",))

    def test_an_element_that_overlaps_is_not_listed_as_a_disagreement(self):
        result = compare(mapping(a="8.16 8.15"), mapping(a="8.15"), "l", "r")
        self.assertEqual(result.disagreements, ())


class DensityIsMeasuredWhereItMatters(unittest.TestCase):
    """Overall density and density in the overlap are different numbers.

    Reporting the wrong one was a real error in the first draft of the
    published document: the two mappings are equally dense overall, 2.5
    against 2.4, and the argument that Jaccard punishes thoroughness needs the
    figure from the compared region, where they are 3.6 against 2.4.
    """

    def test_overall_density_ignores_unanswered_elements(self):
        self.assertAlmostEqual(density(mapping(a="5.1 5.2", b="")), 2.0)

    def test_compared_density_counts_only_the_overlap(self):
        result = compare(
            mapping(a="5.1 5.2 5.3", b="5.4 5.5 5.6"),
            mapping(a="5.1", b=""),
            "dense",
            "sparse",
        )
        self.assertAlmostEqual(result.left_density, 3.0)
        self.assertAlmostEqual(result.right_density, 1.0)

    def test_the_two_can_disagree_which_is_the_point(self):
        left = mapping(a="5.1 5.2 5.3", b="5.4")
        right = mapping(a="5.1", b="")
        result = compare(left, right, "l", "r")
        self.assertNotAlmostEqual(density(left), result.left_density)


class EmptyInputDoesNotCrash(unittest.TestCase):
    def test_nothing_in_common_gives_zero_rather_than_dividing_by_zero(self):
        result = compare(mapping(a="5.1"), mapping(b="5.2"), "l", "r")
        self.assertEqual(result.compared, 0)
        self.assertEqual(result.exact, 0.0)
        self.assertEqual(result.loose, 0.0)
        self.assertEqual(result.left_density, 0.0)

    def test_density_of_nothing_is_zero(self):
        self.assertEqual(density({}), 0.0)


if __name__ == "__main__":
    unittest.main()
