"""Release guards for every number used in the public project summary."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"


def load(name: str) -> dict:
    return json.loads((REPORTS / name).read_text(encoding="utf-8"))


class ThePublishedAgreementStillMatchesItsEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load("agreement.json")

    def test_the_headline_counts_and_percentages(self):
        self.assertEqual(self.report["compared"], 37)
        self.assertEqual(self.report["pairs"]["Razilio"], 134)
        self.assertEqual(self.report["pairs"]["Independent"], 90)
        self.assertEqual(self.report["pairs"]["identical"], 36)
        self.assertEqual(self.report["exact_agreement_jaccard"], 0.1915)
        self.assertEqual(self.report["loose_agreement_share_one"], 0.5946)

    def test_fifteen_comparable_subcategories_share_nothing(self):
        self.assertEqual(len(self.report["elements_with_no_overlap"]), 15)


class TheCanonicalRetrievalReportIsTheFullRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load("retrieval.json")
        cls.rows = {(row["method"], row["direction"]): row for row in cls.report["results"]}

    def test_the_pinned_embedding_model_is_present(self):
        self.assertEqual(self.report["model"], "sentence-transformers/all-MiniLM-L6-v2")
        self.assertEqual(
            {row["method"] for row in self.report["results"]}, {"random", "lexical", "embedding"}
        )

    def test_the_three_public_recall_figures(self):
        direction = "nist-800-53 → nist-csf-1.1"
        self.assertEqual(self.rows[("embedding", direction)]["recall_at"]["3"], 0.6277)
        self.assertEqual(self.rows[("lexical", direction)]["recall_at"]["3"], 0.4894)
        self.assertEqual(self.rows[("random", direction)]["recall_at"]["3"], 0.0798)


class TheDoraCandidateReportKeepsItsBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load("dora-candidates.json")

    def test_the_public_counts(self):
        self.assertEqual(self.report["dora_obligations"], 209)
        self.assertEqual(self.report["top_n"], 3)
        self.assertEqual(len(self.report["candidates"]), 1_254)
        self.assertEqual(len(self.report["composed_to_attack"]), 3_764)

    def test_every_direct_candidate_is_labelled_proposed(self):
        self.assertEqual({row["provenance"] for row in self.report["candidates"]}, {"proposed"})

    def test_the_report_carries_all_six_embedding_directions(self):
        self.assertEqual(len(self.report["method_performance_on_other_pairs"]), 6)


if __name__ == "__main__":
    unittest.main()
