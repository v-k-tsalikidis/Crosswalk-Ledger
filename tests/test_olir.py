"""Tests for reading the NIST OLIR coverage exports.

Submitters write the counterpart column differently, and the reader has to
tell an Annex A control from a mandatory clause. Getting that wrong does not
raise: it silently pulls clause numbers in beside control numbers and inflates
every figure the project publishes.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from crosswalk_ledger.olir import SUBCATEGORY, read

HEADER = "References,ISO/IEC 27001:2022\nCross-Reference Creator,Test\n"


def written(body: str) -> Path:
    directory = TemporaryDirectory()
    path = Path(directory.name) / "export.csv"
    path.write_text(HEADER + body, encoding="utf-8")
    written.keep.append(directory)  # type: ignore[attr-defined]
    return path


written.keep = []  # type: ignore[attr-defined]


class TheHeaderIsChecked(unittest.TestCase):
    def test_the_creator_is_read(self):
        self.assertEqual(read(written('GV.OC-01,"Control 5.1"\n')).creator, "Test")

    def test_a_file_that_is_not_an_olir_export_is_refused(self):
        directory = TemporaryDirectory()
        path = Path(directory.name) / "other.csv"
        path.write_text("a,b\nc,d\ne,f\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            read(path)


class BothNotationsAreRead(unittest.TestCase):
    def test_annex_a_controls_prefix(self):
        got = read(written('GV.OC-01,"Annex A Controls: 5.20, Annex A Controls: 5.31"\n'))
        self.assertEqual(got.annex_controls["GV.OC-01"], {"5.20", "5.31"})

    def test_bare_control_prefix(self):
        got = read(written('GV.OC-01,"Control 5.8"\n'))
        self.assertEqual(got.annex_controls["GV.OC-01"], {"5.8"})

    def test_the_doubled_spaces_that_appear_in_the_real_files(self):
        got = read(written('GV.OC-01,"Control  5.26"\n'))
        self.assertEqual(got.annex_controls["GV.OC-01"], {"5.26"})


class ClausesAreNotControls(unittest.TestCase):
    """The failure that would not announce itself."""

    def test_a_mandatory_clause_never_reaches_the_control_set(self):
        got = read(written('GV.OC-01,"Mandatory Clause: 6.1, Annex A Controls: 5.1"\n'))
        self.assertEqual(got.annex_controls["GV.OC-01"], {"5.1"})
        self.assertEqual(got.clauses["GV.OC-01"], {"6.1"})

    def test_a_row_of_only_clauses_leaves_the_controls_empty(self):
        got = read(written('GV.OC-01,"Mandatory Clause: 4.2(a), Mandatory Clause: 8.1"\n'))
        self.assertEqual(got.annex_controls["GV.OC-01"], set())

    def test_none_is_read_as_a_considered_absence_not_an_unreadable_cell(self):
        got = read(written('GV.OC-01,"Mandatory Clause: None, Annex A Controls: None"\n'))
        self.assertEqual(got.annex_controls["GV.OC-01"], set())
        self.assertEqual(got.unparsed, ())

    def test_a_notation_nobody_anticipated_is_surfaced_rather_than_dropped(self):
        got = read(written('GV.OC-01,"see the supplier standard"\n'))
        self.assertEqual(len(got.unparsed), 1)


class OnlySubcategoriesAreCompared(unittest.TestCase):
    """Functions and categories are roll-ups of the rows beneath them."""

    def test_a_function_row_is_skipped(self):
        got = read(written('GV,"Annex A Controls: 5.1"\nGV.OC-01,"Control 5.2"\n'))
        self.assertEqual(set(got.annex_controls), {"GV.OC-01"})

    def test_a_category_row_is_skipped(self):
        got = read(written('GV.OC,"Annex A Controls: 5.1"\nGV.OC-01,"Control 5.2"\n'))
        self.assertEqual(set(got.annex_controls), {"GV.OC-01"})

    def test_the_pattern_wants_two_digits_as_csf_2_writes_them(self):
        self.assertTrue(SUBCATEGORY.match("GV.OC-01"))
        self.assertFalse(SUBCATEGORY.match("ID.AM-1"))


class TheRealFilesStillParse(unittest.TestCase):
    """Guards the published figures against a change in the export format."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parent.parent / "human-mappings"

    def test_both_submissions_hold_all_106_subcategories(self):
        for name in ("razilio", "independent"):
            path = self.root / f"olir-csf2.0-to-iso27001--{name}.csv"
            with self.subTest(submission=name):
                self.assertEqual(len(read(path).annex_controls), 106)

    def test_nothing_in_either_file_is_unreadable(self):
        for name in ("razilio", "independent"):
            path = self.root / f"olir-csf2.0-to-iso27001--{name}.csv"
            with self.subTest(submission=name):
                self.assertEqual(read(path).unparsed, ())

    def test_the_answered_counts_the_published_figures_rest_on(self):
        razilio = read(self.root / "olir-csf2.0-to-iso27001--razilio.csv")
        independent = read(self.root / "olir-csf2.0-to-iso27001--independent.csv")
        self.assertEqual(razilio.answered, 97)
        self.assertEqual(independent.answered, 39)


if __name__ == "__main__":
    unittest.main()
