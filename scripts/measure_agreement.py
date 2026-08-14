#!/usr/bin/env python3
"""Step 1: how much do published crosswalks of the same pair agree?

Writes docs/AGREEMENT.md and reports/agreement.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from crosswalk_ledger.agreement import Agreement, compare, density  # noqa: E402
from crosswalk_ledger.olir import read  # noqa: E402

HUMAN = ROOT / "human-mappings"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"

#: Annex A control titles are ISO's copyright and are not reproduced in the
#: table. Three are named in the prose below because the disagreement is
#: unreadable without them, which is comment on a published mapping rather
#: than reproduction of the standard.
ISO_TITLES: dict[str, str] = {}


def sort_key(control: str) -> tuple[int, ...]:
    """Numeric, so A.5.3 sorts before A.5.15 rather than after it."""
    return tuple(int(part) for part in control.split("."))


def label(control: str) -> str:
    return f"A.{control}"


def main() -> int:
    razilio = read(HUMAN / "olir-csf2.0-to-iso27001--razilio.csv")
    independent = read(HUMAN / "olir-csf2.0-to-iso27001--independent.csv")

    for coverage in (razilio, independent):
        if coverage.unparsed:
            print(
                f"  {coverage.creator}: {len(coverage.unparsed)} unreadable cells", file=sys.stderr
            )
            for element, cell in coverage.unparsed[:5]:
                print(f"      {element}: {cell[:70]}", file=sys.stderr)

    result = compare(
        razilio.annex_controls,
        independent.annex_controls,
        razilio.creator,
        independent.creator,
    )

    print(result.summary())
    print(
        f"  answered: {result.left_name} {result.left_answered}, "
        f"{result.right_name} {result.right_answered} of 106"
    )
    print(
        f"  density : {density(razilio.annex_controls):.1f} vs "
        f"{density(independent.annex_controls):.1f} controls per subcategory"
    )
    print(f"  only one side answered: {result.only_one_answered} subcategories")
    print(f"  no overlap at all: {len(result.disagreements)} of {result.compared}")

    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "agreement.json").write_text(
        json.dumps(
            {
                "pair": "NIST CSF 2.0 → ISO/IEC 27001:2022, Annex A controls only",
                "sources": [
                    {"creator": razilio.creator, "file": razilio.path.name},
                    {"creator": independent.creator, "file": independent.path.name},
                ],
                "subcategories_total": 106,
                "answered": {
                    razilio.creator: result.left_answered,
                    independent.creator: result.right_answered,
                },
                "compared": result.compared,
                "pairs": {
                    razilio.creator: result.left_pairs,
                    independent.creator: result.right_pairs,
                    "identical": result.shared_pairs,
                },
                "exact_agreement_jaccard": round(result.exact, 4),
                "loose_agreement_share_one": round(result.loose, 4),
                "density": {
                    razilio.creator: round(density(razilio.annex_controls), 2),
                    independent.creator: round(density(independent.annex_controls), 2),
                },
                "elements_with_no_overlap": [
                    {
                        "element": d.element,
                        razilio.creator: list(d.left_says),
                        independent.creator: list(d.right_says),
                    }
                    for d in result.disagreements
                ],
                "is_ground_truth": False,
                "note": (
                    "Neither mapping is correct. Both are published by NIST through OLIR "
                    "as informative references. The figures measure how far two expert "
                    "judgements of the same question land from each other."
                ),
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )

    DOCS.mkdir(exist_ok=True)
    (DOCS / "AGREEMENT.md").write_text(render(result, razilio, independent), encoding="utf-8")
    print(
        f"\nWrote {(DOCS / 'AGREEMENT.md').relative_to(ROOT)} and "
        f"{(REPORTS / 'agreement.json').relative_to(ROOT)}"
    )
    return 0


def render(result: Agreement, left, right) -> str:
    out = [
        "# How much do published crosswalks agree?",
        "",
        "NIST CSF 2.0 → ISO/IEC 27001:2022, comparing the two informative",
        "references published through the NIST OLIR programme. Annex A controls",
        "only: the mandatory clauses are counted separately because only one",
        "submitter mapped them.",
        "",
        "Neither mapping is correct and neither is ground truth. Both went",
        "through OLIR's public comment period. What follows measures how far",
        "two expert judgements of the same question land from each other.",
        "",
        "## The numbers",
        "",
        "| | |",
        "|---|---:|",
        "| Subcategories in CSF 2.0 | 106 |",
        f"| Mapped by {result.left_name} | {result.left_answered} |",
        f"| Mapped by {result.right_name} | {result.right_answered} |",
        f"| Mapped by both, and so comparable | **{result.compared}** |",
        f"| Pairs proposed by {result.left_name} | {result.left_pairs} |",
        f"| Pairs proposed by {result.right_name} | {result.right_pairs} |",
        f"| Identical pairs | {result.shared_pairs} |",
        f"| **Exact agreement (Jaccard)** | **{result.exact:.0%}** |",
        f"| **Share at least one control** | **{result.loose:.0%}** |",
        "",
        "Both figures are given because either alone misleads. Jaccard punishes",
        f"thoroughness: across the {result.compared} comparable subcategories {result.left_name} proposes",
        f"{result.left_density:.1f} controls each against {result.right_density:.1f}, and the denser mapping cannot",
        "score well however sound its judgement is. The loose figure hides how",
        "much else the two disagree about.",
        "",
        f"Across their whole mappings the two are equally dense — {density(left.annex_controls):.1f} against",
        f"{density(right.annex_controls):.1f} controls per subcategory — so the gap above is specific to",
        "where they overlap, not a difference in house style.",
        "",
        f"Silence is not disagreement. {result.only_one_answered} subcategories were mapped by one",
        "submitter and left blank by the other; those are excluded above rather",
        "than counted as conflict.",
        "",
        "## Where they read the same requirement differently",
        "",
        f"{len(result.disagreements)} of the {result.compared} comparable subcategories share no control at all.",
        "These are not errors. They are defensible readings that landed apart.",
        "",
        "Three read plainly. For continuous monitoring `DE.CM-01` one submitter",
        "chose A.8.16 *Monitoring activities* and the other A.8.15 *Logging*.",
        "For recovery plan execution `RC.RP-01` one chose A.5.26 *Response to",
        "information security incidents*, the other A.5.29 *Information security",
        "during disruption*. For `ID.AM-08` one lists nine controls and the",
        "other lists one, and they share none.",
        "",
        "Control titles are not reproduced in the table below: they are part of",
        "ISO/IEC 27001:2022 and are copyrighted. The identifiers are what NIST",
        "publishes.",
        "",
        f"| Subcategory | {result.left_name} | {result.right_name} |",
        "| --- | --- | --- |",
    ]
    for item in result.disagreements:
        left_side = ", ".join(label(c) for c in sorted(item.left_says, key=sort_key))
        right_side = ", ".join(label(c) for c in sorted(item.right_says, key=sort_key))
        out.append(f"| `{item.element}` | {left_side} | {right_side} |")

    out += [
        "",
        "## What follows from this",
        "",
        "A crosswalk is a judgement, not a fact. Two experts working the same",
        "pair, to the same template, under the same programme, agreed on about a",
        "fifth of their mappings.",
        "",
        "So a tool reporting that it matches *the* mapping with some accuracy is",
        "reporting agreement with one opinion. This project therefore measures",
        "any automated method against each human mapping separately and never",
        "against a merged truth, and the only claim it will make is comparative:",
        "whether a method agrees with a named mapping about as much as another",
        "human does.",
        "",
        "It also reframes a common complaint. Razil, publishing their own",
        "hand-made version of this mapping, reported that ChatGPT and Gemini",
        "produced significant hallucinations on the task. The usual reading is",
        "that the models are bad at it. These numbers suggest something more",
        "useful: the question has no single right answer, so a model asked for",
        "one will invent a confident one.",
        "",
        "## Limits",
        "",
        f"- Only {result.compared} subcategories are comparable. The {result.right_name} submitter left",
        f"  {106 - result.right_answered} of 106 blank.",
        "- Annex A only. Mandatory clauses 4–10 are mapped by one submitter and",
        "  not the other, so no comparison is possible there.",
        "- Two mappings is not a sample. It is an existence proof that expert",
        "  disagreement on this task is large, not an estimate of how large.",
        "",
        "Rebuild with `python3 scripts/measure_agreement.py`.",
        "",
    ]
    return "\n".join(out)


if __name__ == "__main__":
    raise SystemExit(main())
