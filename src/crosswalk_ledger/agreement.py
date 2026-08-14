"""How much do two crosswalks of the same thing actually agree?

This is the first deliverable of the project, and the reason the rest of it
changed shape. Crosswalks between security frameworks are bought, sold and
cited as if they were facts. They are judgements, and this measures how far
apart two competent judgements land.

**Two numbers, always reported together, because either alone misleads.**

*Exact* agreement is the Jaccard index over pairs: of every (element,
counterpart) either mapping proposes, what share do both propose. It is the
strict question — do these two crosswalks say the same thing.

*Loose* agreement asks only whether the two mappings share at least one
counterpart for a given element. It is the question a practitioner actually
has: did both of them point me at the same control, even if one listed more.

Reporting only Jaccard overstates disagreement, because a mapper who lists
nine controls where another lists one is penalised for being thorough rather
than for being wrong. Reporting only the loose figure hides that the two
disagree about almost everything else. Neither is the honest number on its
own.

**Coverage is not agreement, and is reported separately.** Where one mapping
is silent, the two are not in conflict — one of them simply did not answer.
Counting silence as disagreement would make a sparse mapping look wrong
rather than incomplete, so elements only one side mapped are excluded from
the agreement figures and counted on their own.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Disagreement:
    """One element where both mappings answered and shared nothing."""

    element: str
    left_says: tuple[str, ...]
    right_says: tuple[str, ...]


@dataclass(frozen=True)
class Agreement:
    """The comparison of two crosswalks over the elements both answered."""

    left_name: str
    right_name: str
    #: Elements either side mapped to at least one counterpart.
    left_answered: int
    right_answered: int
    #: Elements both answered. Everything below is measured on these only.
    compared: int
    left_pairs: int
    right_pairs: int
    shared_pairs: int
    elements_sharing_one: int
    disagreements: tuple[Disagreement, ...]

    @property
    def exact(self) -> float:
        """Jaccard over pairs. 0.0 when neither proposed anything."""
        union = self.left_pairs + self.right_pairs - self.shared_pairs
        return self.shared_pairs / union if union else 0.0

    @property
    def loose(self) -> float:
        """Share of compared elements where the two overlap at all."""
        return self.elements_sharing_one / self.compared if self.compared else 0.0

    @property
    def only_one_answered(self) -> int:
        """Elements one side mapped and the other left empty."""
        return (self.left_answered - self.compared) + (self.right_answered - self.compared)

    @property
    def left_density(self) -> float:
        """Counterparts per element, over the compared elements only.

        Density across the whole mapping is the wrong figure for judging
        whether Jaccard is being dragged down: the two can look alike overall
        and still differ sharply in the region where both answered. Here they
        do — 2.5 against 2.4 across everything, 3.6 against 2.4 where they
        actually overlap.
        """
        return self.left_pairs / self.compared if self.compared else 0.0

    @property
    def right_density(self) -> float:
        return self.right_pairs / self.compared if self.compared else 0.0

    def summary(self) -> str:
        return (
            f"{self.left_name} vs {self.right_name}: "
            f"{self.exact:.0%} exact, {self.loose:.0%} loose, over {self.compared} elements"
        )


Mapping = dict[str, set[str]]


def compare(left: Mapping, right: Mapping, left_name: str, right_name: str) -> Agreement:
    """Compare two mappings from the same elements to the same counterparts.

    Both are element → set of counterparts. An element present with an empty
    set counts as unanswered, not as a claim that nothing corresponds.
    """
    left_answered = {k for k, v in left.items() if v}
    right_answered = {k for k, v in right.items() if v}
    both = sorted(left_answered & right_answered)

    left_pairs = {(k, c) for k in both for c in left[k]}
    right_pairs = {(k, c) for k in both for c in right[k]}
    shared = left_pairs & right_pairs

    disagreements = tuple(
        Disagreement(
            element=key,
            left_says=tuple(sorted(left[key])),
            right_says=tuple(sorted(right[key])),
        )
        for key in both
        if not (left[key] & right[key])
    )

    return Agreement(
        left_name=left_name,
        right_name=right_name,
        left_answered=len(left_answered),
        right_answered=len(right_answered),
        compared=len(both),
        left_pairs=len(left_pairs),
        right_pairs=len(right_pairs),
        shared_pairs=len(shared),
        elements_sharing_one=sum(1 for key in both if left[key] & right[key]),
        disagreements=disagreements,
    )


def density(mapping: Mapping) -> float:
    """Mean counterparts per answered element.

    Reported beside every comparison because it is the main confound: a
    mapping twice as dense as another cannot score well on Jaccard however
    sound its judgement is.
    """
    answered = [v for v in mapping.values() if v]
    return sum(len(v) for v in answered) / len(answered) if answered else 0.0
