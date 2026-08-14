"""Tests for splitting DORA articles into obligations.

The splitter exists because an article is not a comparable unit. Its one
subtle rule is that paragraph numbering is trusted only when it counts up,
which is what stops a cross-reference inside a sentence from being read as a
new paragraph.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from crosswalk_ledger.obligations import (
    MINIMUM,
    OBLIGATION_RANGE,
    article_number,
    split,
    split_all,
)

LONG = "Financial entities shall do the thing described at length in this paragraph. " * 3


class NumberingIsTrustedOnlyWhenItCountsUp(unittest.TestCase):
    def test_sequential_paragraphs_are_split(self):
        text = f"1. {LONG} 2. {LONG} 3. {LONG}"
        got = split("Article 9", "Protection", text)
        self.assertEqual([o.paragraph for o in got], [1, 2, 3])

    def test_a_cross_reference_is_not_a_new_paragraph(self):
        # "7." appears where paragraph 3 would be expected, as Article 28 does.
        text = f"1. {LONG} 2. {LONG} 7. {LONG}"
        got = split("Article 28", "Key provisions", text)
        self.assertEqual([o.paragraph for o in got], [1, 2])

    def test_the_out_of_order_text_is_not_lost_but_stays_with_its_paragraph(self):
        text = f"1. {LONG} 2. {LONG} 7. Something referenced elsewhere."
        got = split("Article 28", "Key provisions", text)
        self.assertIn("Something referenced elsewhere", got[-1].text)

    def test_numbering_that_never_starts_at_one_yields_the_whole_article(self):
        got = split("Article 9", "Protection", f"3. {LONG} 4. {LONG}")
        self.assertEqual([o.paragraph for o in got], [0])


class TheParagraphNumberIsNotLeftInTheText(unittest.TestCase):
    def test_the_leading_number_is_stripped(self):
        got = split("Article 9", "Protection", f"1. {LONG} 2. {LONG}")
        self.assertFalse(got[0].text.startswith("1."))

    def test_because_otherwise_every_first_paragraph_shares_a_token(self):
        first = split("Article 9", "A", f"1. {LONG} 2. {LONG}")[0]
        other = split("Article 10", "B", f"1. {LONG} 2. {LONG}")[0]
        self.assertEqual(first.text, other.text)  # same body, no numbering artefact


class ShortFragmentsAreDropped(unittest.TestCase):
    def test_a_paragraph_below_the_minimum_is_not_an_obligation(self):
        text = f"1. {LONG} 2. Short."
        got = split("Article 9", "Protection", text)
        self.assertEqual([o.paragraph for o in got], [1])

    def test_an_article_too_short_to_carry_an_obligation_yields_nothing(self):
        self.assertEqual(split("Article 9", "Protection", "Too short."), [])

    def test_the_minimum_is_stated_rather_than_hidden(self):
        self.assertGreater(MINIMUM, 0)


class IdentifiersAreArticleAndParagraph(unittest.TestCase):
    def test_a_numbered_paragraph_carries_both(self):
        got = split("Article 25", "Testing", f"1. {LONG} 2. {LONG}")
        self.assertEqual(got[0].id, "Article 25(1)")

    def test_an_unnumbered_article_is_paragraph_zero(self):
        self.assertEqual(split("Article 15", "Harmonisation", LONG)[0].id, "Article 15(0)")


class OnlyObligationArticlesAreKept(unittest.TestCase):
    def test_definitions_and_amendments_are_outside_the_range(self):
        for excluded in (1, 2, 3, 4, 46, 60, 64):
            with self.subTest(article=excluded):
                self.assertNotIn(excluded, OBLIGATION_RANGE)

    def test_the_substantive_chapters_are_inside_it(self):
        for included in (5, 12, 17, 25, 28, 45):
            with self.subTest(article=included):
                self.assertIn(included, OBLIGATION_RANGE)

    def test_article_3_is_excluded_because_it_would_match_everything(self):
        articles = [
            {"id": "Article 3", "title": "Definitions", "text": LONG * 20},
            {"id": "Article 9", "title": "Protection", "text": LONG},
        ]
        got = split_all(articles)
        self.assertEqual({o["group"] for o in got}, {"Article 9"})

    def test_the_filter_can_be_turned_off_deliberately(self):
        articles = [{"id": "Article 3", "title": "Definitions", "text": LONG}]
        self.assertEqual(len(split_all(articles, only_obligations=False)), 1)

    def test_article_number_reads_the_identifier(self):
        self.assertEqual(article_number("Article 28"), 28)


class TheRealInstrumentStillSplits(unittest.TestCase):
    """Guards the published figures against a change in the DORA parse."""

    @classmethod
    def setUpClass(cls) -> None:
        path = Path(__file__).resolve().parent.parent / "catalogues" / "items" / "dora.json"
        cls.articles = json.loads(path.read_text(encoding="utf-8"))
        cls.obligations = split_all(cls.articles)

    def test_all_64_articles_were_parsed(self):
        self.assertEqual(len(self.articles), 64)

    def test_the_published_obligation_count(self):
        self.assertEqual(len(self.obligations), 209)

    def test_article_28_gives_ten_paragraphs_not_eleven(self):
        # The duplicate "7." is the reason the counts-up rule exists.
        got = [o for o in self.obligations if o["group"] == "Article 28"]
        self.assertEqual([int(o["id"].split("(")[1][:-1]) for o in got], list(range(1, 11)))

    def test_splitting_brings_the_two_sides_within_an_order_of_magnitude(self):
        mean = sum(len(o["text"]) for o in self.obligations) / len(self.obligations)
        self.assertLess(mean, 1000)  # articles averaged 3,155

    def test_no_obligation_is_the_size_of_a_whole_chapter(self):
        longest = max(len(o["text"]) for o in self.obligations)
        self.assertLess(longest, 4000)


if __name__ == "__main__":
    unittest.main()
