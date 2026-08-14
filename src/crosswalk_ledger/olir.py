"""Read the coverage exports the NIST OLIR catalogue produces.

OLIR is where NIST publishes informative references — crosswalks submitted by
NIST and by outside parties, each through a thirty-day public comment period
and a limited conformance check against IR 8278A. The catalogue exports a
coverage report per reference as CSV.

The format is two header lines and then one row per focal element:

    References,ISO/IEC 27001:2022
    Cross-Reference Creator,Razilio
    GV.OC-05,"Mandatory Clause: None, Annex A Controls: 5.3"

**Submitters do not write the counterpart column the same way.** One writes
`Annex A Controls: 5.3`, another writes `Control 5.8`, and both appear with
stray double spaces and trailing commas. Reading the numbers out of the cell
with a bare digit pattern would silently pull clause numbers in beside Annex
A control numbers and inflate every comparison, so each notation is matched
explicitly and anything unrecognised is surfaced rather than dropped.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

#: A CSF subcategory: GV.OC-01. Functions (GV) and categories (GV.OC) also
#: appear in the export and are excluded — they are roll-ups of the rows
#: below them, so counting them would score the same judgement twice.
SUBCATEGORY = re.compile(r"^[A-Z]{2}\.[A-Z]{2}-\d{2}$")

#: Both spellings seen in the wild, tolerant of the doubled spaces.
_ANNEX = re.compile(r"(?:Annex\s+A\s+Controls?|Control)\s*:?\s*(\d+\.\d+)", re.I)
_CLAUSE = re.compile(r"Mandatory\s+Clause\s*:?\s*([\d.]+(?:\s*\([a-z]\))?)", re.I)
#: A CSF identifier, for the CSF 2.0 → CSF 1.1 export.
_CSF = re.compile(r"\b([A-Z]{2}\.[A-Z]{2}-\d+)\b")


@dataclass(frozen=True)
class Coverage:
    """One OLIR coverage export."""

    path: Path
    reference: str
    creator: str
    #: subcategory → counterparts. Present with an empty set means the
    #: submitter left the row blank, which is silence and not a claim.
    annex_controls: dict[str, set[str]]
    clauses: dict[str, set[str]]
    csf_elements: dict[str, set[str]]
    #: Cells holding something none of the patterns recognised.
    unparsed: tuple[tuple[str, str], ...]

    @property
    def answered(self) -> int:
        return sum(1 for v in self.annex_controls.values() if v)


def read(path: Path) -> Coverage:
    rows = list(csv.reader(path.read_text(encoding="utf-8-sig").splitlines()))
    if len(rows) < 3:
        raise ValueError(f"{path.name}: too short to be an OLIR coverage export")

    reference = rows[0][1].strip() if len(rows[0]) > 1 else ""
    creator = rows[1][1].strip() if len(rows[1]) > 1 else ""
    if rows[1][0].strip() != "Cross-Reference Creator":
        raise ValueError(f"{path.name}: second row is not the creator line")

    annex: dict[str, set[str]] = {}
    clauses: dict[str, set[str]] = {}
    csf: dict[str, set[str]] = {}
    unparsed: list[tuple[str, str]] = []

    for row in rows[2:]:
        if not row or not row[0].strip():
            continue
        element = row[0].strip()
        if not SUBCATEGORY.match(element):
            continue
        cell = (row[1] if len(row) > 1 else "").strip()

        annex[element] = set(_ANNEX.findall(cell))
        clauses[element] = {m.replace(" ", "") for m in _CLAUSE.findall(cell)}
        csf[element] = set(_CSF.findall(cell))

        # "None" is how submitters write a considered absence; anything else
        # unmatched means the cell holds a notation this reader does not know.
        if (
            cell
            and not (annex[element] or clauses[element] or csf[element])
            and "none" not in cell.lower()
        ):
            unparsed.append((element, cell))

    return Coverage(
        path=path,
        reference=reference,
        creator=creator,
        annex_controls=annex,
        clauses=clauses,
        csf_elements=csf,
        unparsed=tuple(unparsed),
    )
