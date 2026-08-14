"""Split DORA articles into the paragraphs that carry the obligations.

An article is not a comparable unit. DORA articles average 3,155 characters
where a CSF subcategory averages 78, and a similarity score across that gap
measures length as much as meaning. Article 28 alone runs to 9,592 characters
and covers contract terms, registers of information, exit strategies and
concentration risk — nothing on the other side of a crosswalk corresponds to
all of that at once.

The numbered paragraph is the unit the legislator wrote obligations in, and
splitting there brings the two sides within an order of magnitude of each
other.

**Numbering is only trusted when it counts up.** A bare `7.` inside a
sentence — a cross-reference, a figure, the end of an abbreviation — looks
exactly like the start of paragraph 7. Accepting every match found eleven
paragraphs in Article 28, two of them numbered 7. So a candidate boundary is
taken only when its number is one more than the last accepted, which is what
a legislative text actually does and what a stray reference will not.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: A number, a full stop, a space, then something that could begin a sentence.
_BOUNDARY = re.compile(r"(?:(?<=\s)|^)(\d{1,2})\.\s+(?=[A-Z“\"(])")

#: Too short to carry an obligation: cross-reference fragments, stray headings.
MINIMUM = 120


@dataclass(frozen=True)
class Obligation:
    """One numbered paragraph of one article."""

    article: str
    paragraph: int
    title: str
    text: str

    @property
    def id(self) -> str:
        return f"{self.article}({self.paragraph})"


def split(article_id: str, title: str, text: str) -> list[Obligation]:
    """Paragraphs of an article, or the whole article when it has none."""
    boundaries: list[tuple[int, int]] = []  # (position, paragraph number)
    expected = 1
    for match in _BOUNDARY.finditer(text):
        number = int(match.group(1))
        if number == expected:
            boundaries.append((match.start(), number))
            expected += 1

    if not boundaries:
        stripped = text.strip()
        if len(stripped) < MINIMUM:
            return []
        return [Obligation(article_id, 0, title, stripped)]

    out: list[Obligation] = []
    for index, (position, number) in enumerate(boundaries):
        end = boundaries[index + 1][0] if index + 1 < len(boundaries) else len(text)
        body = text[position:end].strip()
        # Drop the leading "N. " so the number does not become a token the
        # matching methods see, which would let every paragraph 1 look alike.
        body = re.sub(r"^\d{1,2}\.\s+", "", body)
        if len(body) >= MINIMUM:
            out.append(Obligation(article_id, number, title, body))
    return out


#: Articles 5 to 45 carry the substantive duties: ICT risk management,
#: incident reporting, resilience testing, third-party risk and information
#: sharing. Articles 1 to 4 are subject matter, scope and definitions;
#: 46 onwards are supervision, penalties, amendments to other regulations and
#: entry into force.
#:
#: The excluded ones are not merely uninteresting, they are actively harmful
#: to a crosswalk. Article 3 is 13,915 characters of definitions and would
#: show a plausible similarity to almost any control, because it contains the
#: vocabulary of the whole instrument. Article 60 amends Regulation (EU) No
#: 648/2012 and corresponds to no security control at all.
OBLIGATION_RANGE = range(5, 46)


def article_number(article_id: str) -> int:
    return int(article_id.split()[1])


def split_all(articles: list[dict], *, only_obligations: bool = True) -> list[dict]:
    """Every article's obligations, as catalogue items."""
    items: list[dict] = []
    for article in articles:
        if only_obligations and article_number(article["id"]) not in OBLIGATION_RANGE:
            continue
        for obligation in split(article["id"], article["title"], article["text"]):
            items.append(
                {
                    "id": obligation.id,
                    "title": obligation.title,
                    "text": obligation.text,
                    "group": obligation.article,
                }
            )
    return items
