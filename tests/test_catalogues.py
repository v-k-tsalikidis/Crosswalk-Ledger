"""Tests for the committed catalogues.

The catalogues are built from 119 MB of published sources by a script that
needs the network. These tests read the committed output instead, so the suite
never touches a government endpoint, and they fix the counts that every
published figure rests on.

The identifier tests are the important ones. CTID writes a control `AC-02`,
OSCAL writes it `ac-2`, D3FEND writes it `CM-5(3)`. The raw intersection of
CTID's controls with OSCAL's is zero. A regression there would report a method
that recovers nothing, and the fault would look like the method's.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "catalogues" / "items"
PAIRS = ROOT / "catalogues" / "pairs"

EXPECTED_ITEMS = {
    "attack": 656,
    "nist-800-53": 1014,
    "nist-csf-1.1": 108,
    "nist-csf-2.0": 106,
    "d3fend": 272,
    "dora": 64,
}

EXPECTED_PAIRS = {
    "nist-800-53__attack": 5263,
    "attack__d3fend": 3202,
    "d3fend__nist-800-53": 103,
    "nist-csf-1.1__nist-800-53": 495,
}


def load(folder: Path, name: str) -> list[dict]:
    return json.loads((folder / f"{name}.json").read_text(encoding="utf-8"))


class EveryCatalogueHoldsWhatItSays(unittest.TestCase):
    def test_item_counts(self):
        for name, expected in EXPECTED_ITEMS.items():
            with self.subTest(catalogue=name):
                self.assertEqual(len(load(ITEMS, name)), expected)

    def test_pair_counts(self):
        for name, expected in EXPECTED_PAIRS.items():
            with self.subTest(pair=name):
                self.assertEqual(len(load(PAIRS, name)), expected)

    def test_every_item_carries_text_to_match_on(self):
        for name in EXPECTED_ITEMS:
            with self.subTest(catalogue=name):
                empty = [i["id"] for i in load(ITEMS, name) if not i["text"].strip()]
                self.assertEqual(empty, [])

    def test_no_identifier_appears_twice(self):
        for name in EXPECTED_ITEMS:
            items = load(ITEMS, name)
            with self.subTest(catalogue=name):
                self.assertEqual(len({i["id"] for i in items}), len(items))


class IdentifiersAreNormalised(unittest.TestCase):
    """Zero raw overlap, complete overlap after normalisation."""

    def test_control_identifiers_are_lower_case_and_unpadded(self):
        ids = {i["id"] for i in load(ITEMS, "nist-800-53")}
        self.assertIn("ac-2", ids)
        self.assertNotIn("AC-02", ids)
        self.assertNotIn("ac-02", ids)

    def test_enhancements_use_a_dot_not_brackets(self):
        ids = {i["id"] for i in load(ITEMS, "nist-800-53")}
        self.assertIn("ac-2.1", ids)
        self.assertNotIn("ac-2(1)", ids)

    def test_technique_identifiers_are_upper_case(self):
        ids = {i["id"] for i in load(ITEMS, "attack")}
        self.assertIn("T1059.001", ids)


class EveryPairPointsAtSomethingThatExists(unittest.TestCase):
    """Recall cannot be measured against a counterpart never shown."""

    def test_both_endpoints_of_every_pair_are_in_their_catalogue(self):
        for name in EXPECTED_PAIRS:
            left_name, right_name = name.split("__")
            left = {i["id"] for i in load(ITEMS, left_name)}
            right = {i["id"] for i in load(ITEMS, right_name)}
            rows = load(PAIRS, name)
            with self.subTest(pair=name):
                self.assertEqual({r["left"] for r in rows} - left, set())
                self.assertEqual({r["right"] for r in rows} - right, set())

    def test_no_pair_is_recorded_twice(self):
        for name in EXPECTED_PAIRS:
            rows = load(PAIRS, name)
            with self.subTest(pair=name):
                self.assertEqual(len({(r["left"], r["right"]) for r in rows}), len(rows))


class WhatWasDroppedIsRecorded(unittest.TestCase):
    def test_withdrawn_controls_are_listed_and_absent_from_the_catalogue(self):
        withdrawn = set(
            json.loads((ROOT / "catalogues" / "nist-800-53-withdrawn.json").read_text())
        )
        self.assertEqual(len(withdrawn), 182)
        live = {i["id"] for i in load(ITEMS, "nist-800-53")}
        self.assertEqual(withdrawn & live, set())

    def test_the_two_together_are_the_whole_published_catalogue(self):
        withdrawn = json.loads((ROOT / "catalogues" / "nist-800-53-withdrawn.json").read_text())
        self.assertEqual(len(load(ITEMS, "nist-800-53")) + len(withdrawn), 1196)

    def test_d3fend_pointing_at_withdrawn_controls_is_recorded_not_hidden(self):
        # A published crosswalk citing controls the publisher retired is the
        # kind of decay this project exists to surface.
        dangling = json.loads((ROOT / "catalogues" / "dangling.json").read_text())
        entry = dangling["d3fend__nist-800-53"]
        self.assertEqual(len(entry["right_withdrawn_in_rev5"]), 5)


class TheGroundTruthIsSparseAndSaysSo(unittest.TestCase):
    """Guards a caveat the published documents depend on."""

    def test_ctid_touches_only_a_tenth_of_the_control_catalogue(self):
        rows = load(PAIRS, "nist-800-53__attack")
        controls = {r["left"] for r in rows}
        self.assertEqual(len(controls), 109)
        self.assertLess(len(controls) / len(load(ITEMS, "nist-800-53")), 0.15)

    def test_d3fend_to_800_53_is_the_thinnest_pair(self):
        counts = {name: len(load(PAIRS, name)) for name in EXPECTED_PAIRS}
        self.assertEqual(min(counts, key=lambda k: counts[k]), "d3fend__nist-800-53")


class TheGranularityGapIsReal(unittest.TestCase):
    """The reason DORA articles are split before any comparison."""

    def mean_length(self, name: str) -> float:
        items = load(ITEMS, name)
        return sum(len(i["text"]) for i in items) / len(items)

    def test_dora_articles_are_an_order_of_magnitude_longer_than_subcategories(self):
        self.assertGreater(self.mean_length("dora") / self.mean_length("nist-csf-2.0"), 10)

    def test_and_longer_than_controls_too(self):
        self.assertGreater(self.mean_length("dora") / self.mean_length("nist-800-53"), 10)


if __name__ == "__main__":
    unittest.main()
