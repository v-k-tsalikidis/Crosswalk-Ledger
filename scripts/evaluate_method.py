#!/usr/bin/env python3
"""Step 2: measure automated matching against each human crosswalk.

Runs on the three pairs where the text of both sides is free to redistribute.
CSF 2.0 to ISO/IEC 27001:2022 — the pair with the human-disagreement figure
from step 1 — cannot be run here: the Annex A control text is ISO's copyright,
it appears in none of the published exports, and it is not in this repository.
That gap is stated in the report rather than worked around.

    python3 scripts/evaluate_method.py            # lexical and random; separate report
    python3 scripts/evaluate_method.py --embed    # full canonical report
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from crosswalk_ledger.retrieval import Result, evaluate, random_scores  # noqa: E402

ITEMS = ROOT / "catalogues" / "items"
PAIRS = ROOT / "catalogues" / "pairs"
REPORTS = ROOT / "reports"

#: Pinned. A different model gives different numbers, so the published
#: figures name the one that produced them.
MODEL = "sentence-transformers/all-MiniLM-L6-v2"

EVALUATED = (
    ("nist-800-53", "attack"),
    ("nist-csf-1.1", "nist-800-53"),
    ("attack", "d3fend"),
)


def load_items(name: str) -> list[dict]:
    return json.loads((ITEMS / f"{name}.json").read_text(encoding="utf-8"))


def load_pairs(left: str, right: str) -> list[dict]:
    return json.loads((PAIRS / f"{left}__{right}.json").read_text(encoding="utf-8"))


def corpus(items: list[dict]) -> list[str]:
    """Title and statement together.

    The title carries the subject in a few precise words and the statement
    carries the detail. Dropping either measurably hurts both methods, so
    both are used and the choice is the same for every method compared.
    """
    return [f"{i['title']}. {i['text']}".strip() for i in items]


def lexical_scores(left: list[str], right: list[str]) -> np.ndarray:
    # Fitted on both sides at once so the vocabulary and the document
    # frequencies are shared; fitting separately would score the two halves
    # in different spaces and quietly favour whichever was fitted first.
    vectoriser = TfidfVectorizer(
        stop_words="english", sublinear_tf=True, min_df=1, ngram_range=(1, 2)
    )
    matrix = vectoriser.fit_transform(left + right)
    return (matrix[: len(left)] @ matrix[len(left) :].T).toarray()


def embedding_scores(left: list[str], right: list[str]) -> np.ndarray:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL)
    a = model.encode(left, normalize_embeddings=True, show_progress_bar=False)
    b = model.encode(right, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(a @ b.T)


def run(left_name: str, right_name: str, use_embeddings: bool) -> list[Result]:
    left_items, right_items = load_items(left_name), load_items(right_name)
    pairs = load_pairs(left_name, right_name)

    left_index = {item["id"]: n for n, item in enumerate(left_items)}
    right_index = {item["id"]: n for n, item in enumerate(right_items)}

    forward: dict[int, list[int]] = {}
    backward: dict[int, list[int]] = {}
    for row in pairs:
        i, j = left_index[row["left"]], right_index[row["right"]]
        forward.setdefault(i, []).append(j)
        backward.setdefault(j, []).append(i)

    left_text, right_text = corpus(left_items), corpus(right_items)
    pair_label = f"{left_name} ↔ {right_name}"

    methods = [
        ("random", random_scores((len(left_text), len(right_text)))),
        ("lexical", lexical_scores(left_text, right_text)),
    ]
    if use_embeddings:
        methods.append(("embedding", embedding_scores(left_text, right_text)))

    results = []
    for name, scores in methods:
        results.append(
            evaluate(
                scores,
                forward,
                method=name,
                pair=pair_label,
                direction=f"{left_name} → {right_name}",
            )
        )
        results.append(
            evaluate(
                scores.T,
                backward,
                method=name,
                pair=pair_label,
                direction=f"{right_name} → {left_name}",
            )
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--embed", action="store_true", help=f"also run {MODEL}")
    args = parser.parse_args()
    report_name = "retrieval.json" if args.embed else "retrieval-lexical.json"

    everything: list[Result] = []
    for left, right in EVALUATED:
        print(f"\n═══ {left} ↔ {right} ═══")
        results = run(left, right, args.embed)
        everything.extend(results)
        head = results[0]
        print(f"    {head.queried} elements queried against {head.candidates} candidates\n")
        for result in sorted(results, key=lambda r: (r.direction, r.method)):
            print("   ", result.row())

    REPORTS.mkdir(exist_ok=True)
    (REPORTS / report_name).write_text(
        json.dumps(
            {
                "model": MODEL if args.embed else None,
                "note": (
                    "recall@k against a single human mapping. Precision is deliberately "
                    "absent: the mappings are incomplete, so a proposed pair the human did "
                    "not record is not necessarily wrong. Read beside reports/agreement.json, "
                    "which shows two experts agreeing on 19% of the same task."
                ),
                "not_evaluated": {
                    "csf-2.0 ↔ iso-27001": (
                        "ISO/IEC 27001:2022 Annex A control text is copyrighted, is absent "
                        "from every published export, and is not in this repository."
                    )
                },
                "results": [
                    {
                        "method": r.method,
                        "pair": r.pair,
                        "direction": r.direction,
                        "queried": r.queried,
                        "candidates": r.candidates,
                        "recall_at": {str(k): round(v, 4) for k, v in r.recall_at.items()},
                        "pair_recall_at_10": round(r.pair_recall_at_10, 4),
                        "median_best_rank": r.median_best_rank,
                    }
                    for r in everything
                ],
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote {(REPORTS / report_name).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
