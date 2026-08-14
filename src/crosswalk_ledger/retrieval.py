"""Can a machine reproduce a human crosswalk from the text alone?

The task is posed as retrieval rather than classification. For each element
on the left, rank every element on the right by similarity and ask where the
human-chosen counterparts land. That matches how a crosswalk is actually
built — somebody reads a requirement and goes looking for the controls that
bear on it — and it avoids inventing a decision threshold before there is any
evidence about what a sensible one would be.

**recall@k is the honest metric here and precision is not.** The published
mappings are incomplete: a pair the method proposes that the human did not
record may be a good link nobody wrote down. Counting those as errors would
measure how closely the method copies one person's coverage, not whether it
finds real correspondences. So the reported numbers say how often a human
choice appears near the top, and precision figures are omitted rather than
published as if they meant something.

**The lexical baseline is the one that decides anything.** Both sides of
these documents are written in the same dense professional vocabulary, so
plain term overlap is a strong method, not a straw man. An embedding model
that cannot beat TF-IDF here is adding a download, a dependency and an
unexplainable score for nothing.

**Direction matters and both are reported.** Mapping 1,014 controls onto 656
techniques is a different problem from the reverse: the number of candidates
differs, and so does the chance of landing one by accident. A single figure
would hide which direction the method is good at.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Result:
    """How one method did on one direction of one framework pair."""

    method: str
    pair: str
    direction: str
    #: Left-hand elements that have at least one recorded counterpart.
    queried: int
    candidates: int
    #: k → share of queried elements with a true counterpart in the top k.
    #:
    #: recall@3 carries more weight than the rest. The two human mappings in
    #: step 1 proposed 2.4 and 3.6 counterparts each, and 59% of the time they
    #: shared at least one. Asking whether a method's top three contains a
    #: human choice is that same question put to a machine, and it is the only
    #: figure here that can honestly be set beside the human-agreement result.
    recall_at: dict[int, float]
    #: Share of all recorded pairs whose counterpart lands in the top 10.
    pair_recall_at_10: float
    #: Median rank of the best-placed true counterpart. Lower is better.
    median_best_rank: float

    def row(self) -> str:
        got = "  ".join(f"@{k}:{v:5.1%}" for k, v in sorted(self.recall_at.items()))
        return (
            f"{self.method:<10} {self.direction:<28} {got}  "
            f"median rank {self.median_best_rank:>5.0f} of {self.candidates}"
        )


def rank_positions(scores: np.ndarray, truth_indices: list[int]) -> list[int]:
    """1-based ranks of the true counterparts, ties broken pessimistically.

    A true counterpart sharing its score with others is placed *after* all of
    them: its rank is one more than the number of candidates scoring at least
    as highly, itself excluded.

    This is not a detail. `argsort` breaks ties by index, which is optimistic
    whenever the true counterpart happens to sit early in the catalogue, and
    the first version of this function did exactly that. It matters most for
    the lexical baseline, where a query sharing no term with hundreds of
    candidates leaves them all at exactly zero — index order would then hand
    the baseline recall it has not earned. With ties resolved this way every
    published figure is a floor.
    """
    ranks = []
    for index in truth_indices:
        value = scores[index]
        at_least_as_high = int(np.count_nonzero(scores >= value))
        ranks.append(at_least_as_high)
    return ranks


def evaluate(
    scores: np.ndarray,
    truth: dict[int, list[int]],
    *,
    method: str,
    pair: str,
    direction: str,
    ks: tuple[int, ...] = (1, 3, 5, 10, 20),
) -> Result:
    """Score a full left × right similarity matrix against recorded pairs.

    `truth` maps a left index to the right indices a human chose. Left
    elements with no recorded counterpart are not queried: their absence from
    the mapping is silence, not a statement that nothing corresponds.
    """
    best_ranks: list[int] = []
    hits: dict[int, int] = dict.fromkeys(ks, 0)
    pairs_total = 0
    pairs_in_10 = 0

    for left_index, right_indices in truth.items():
        ranks = rank_positions(scores[left_index], right_indices)
        best = min(ranks)
        best_ranks.append(best)
        for k in ks:
            if best <= k:
                hits[k] += 1
        pairs_total += len(ranks)
        pairs_in_10 += sum(1 for r in ranks if r <= 10)

    queried = len(truth)
    return Result(
        method=method,
        pair=pair,
        direction=direction,
        queried=queried,
        candidates=scores.shape[1],
        recall_at={k: hits[k] / queried for k in ks} if queried else dict.fromkeys(ks, 0.0),
        pair_recall_at_10=pairs_in_10 / pairs_total if pairs_total else 0.0,
        median_best_rank=float(np.median(best_ranks)) if best_ranks else 0.0,
    )


def random_scores(shape: tuple[int, int], seed: int = 0) -> np.ndarray:
    """The floor. Pinned seed so the published number is reproducible."""
    return np.random.default_rng(seed).random(shape)
