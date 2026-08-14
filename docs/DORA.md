# DORA candidates

Step 3. Candidate correspondences from DORA obligations to NIST 800-53 and
NIST CSF 2.0, and onward to ATT&CK through MITRE's published crosswalk.

**Every row is a proposal for a person to accept or reject.** The word
*mapping* is avoided throughout. No official DORA crosswalk exists, so there
is nothing here to be right about, and this output has not been scored
because there is nothing to score it against.

Read with [AGREEMENT.md](AGREEMENT.md) and [RETRIEVAL.md](RETRIEVAL.md).
Rebuild with `python3 scripts/build_dora_candidates.py`.

## What was produced

| | |
|---|---:|
| DORA obligations, Articles 5–45 | 209 |
| Candidates to 800-53, top 3 each | 627 |
| Candidates to CSF 2.0, top 3 each | 627 |
| Composed onward to ATT&CK | 3,764 |

Top three per obligation, because that is the density the two human mappers
in step 1 worked at, and the only cut-off for which this project has a
comparable human figure.

## Articles are not comparable units, so they were split

A DORA article averages 3,155 characters against 78 for a CSF subcategory.
Article 28 alone runs to 9,592 and covers contract terms, registers of
information, exit strategies and concentration risk; nothing on the other
side corresponds to all of that at once.

Splitting at the numbered paragraph — the unit the legislator wrote
obligations in — gives 209 units averaging 656 characters, which brings the
two sides within an order of magnitude.

**Paragraph numbering is only trusted when it counts up.** A bare `7.` inside
a sentence looks exactly like the start of paragraph 7, and accepting every
match found eleven paragraphs in Article 28, two of them numbered 7. A
boundary is taken only when its number is one more than the last accepted.

**Articles 1–4 and 46–64 are excluded.** They are subject matter, scope,
definitions, supervision, penalties, amendments to other regulations and
entry into force. This is not tidying. Article 3 is 13,915 characters of
definitions and would show plausible similarity to almost any control,
because it contains the vocabulary of the whole instrument. Article 60 amends
Regulation (EU) No 648/2012 and corresponds to no security control at all.

## ATT&CK is not a direct target, and the first attempt shows why

The first run matched DORA against ATT&CK directly. The results looked
confident and were wrong:

| DORA | Proposed | Why it is nonsense |
|---|---|---|
| Article 45(1), information-sharing arrangements on cyber threat information | `T1597.002` Purchase Technical Data | ATT&CK's technique is an *adversary* buying data |
| Article 35(2), Powers of the Lead Overseer | `T1199` Trusted Relationship | an adversary abusing a trust relationship |

DORA states duties on defenders. ATT&CK describes what attackers do. They are
not the same kind of statement, and similarity over text cannot bridge that —
it matches vocabulary and returns something plausible.

So the route to ATT&CK runs through a control catalogue, where each link
compares like with like:

```
DORA obligation ──similarity──▶ 800-53 control ──MITRE CTID──▶ ATT&CK technique
   proposed                          official
```

3,764 such chains exist, through 15 controls, reaching 418 techniques. The
first leg is a proposal and the second is published, and the output labels
each leg separately so a reader is never told the whole chain is official.

## What the numbers are worth

The strongest candidate in the whole set scores 0.66. The median first-ranked
candidate scores 0.50 and the weakest 0.30. **Nothing here is a strong
match**, and the scale has no natural meaning — 0.66 is not "66% correct".

Two figures give it what context exists:

**This method, on pairs where a human crosswalk exists**, puts a
human-chosen counterpart in its top three between 25% and 63% of the time
depending on the pair and direction. The closest analogue to the DORA task is
outcome-to-control, where it reaches 62.8% one way and 35.8% the other.

**Two experts on a comparable task agreed with each other** on 19% of their
pairs exactly, and shared at least one counterpart 59% of the time.

Neither figure describes this output. DORA has never been measured against
anything because there is nothing to measure it against. They are here so
that no single number attached to these candidates can be read as accuracy.

## Where the candidates look sound, and where they do not

The strongest are the ones a reader can check:

| DORA | Proposed | Score |
|---|---|---:|
| Article 12(6), backup and recovery | `cp-6.2` Recovery Time and Recovery Point Objectives | 0.66 |
| Article 17(3), ICT-related incident management | `ir-6` Incident Reporting | 0.64 |
| Article 12(2), backup and recovery | `RC.RP-03` | 0.65 |

The weakest first-ranked candidates are where the obligation is procedural or
supervisory rather than technical — Article 35(7) on the Lead Overseer's
powers, Article 43(2) on oversight fees. Those articles have no counterpart
in a control catalogue, and a top-ranked candidate at 0.30 is the method
returning the least bad of 1,014 wrong answers rather than finding anything.

**A ranked list always returns something.** That is the failure mode this
whole project documents, and it is not fixed by producing the list more
carefully.

## What this is not

**Not compliance.** That a control resembles an obligation does not mean it
discharges it. DORA compliance is a legal determination and this is an input
to that work — the same line the Regulatory Scope Ledger holds.

**Not authoritative.** Every row is `proposed`. Rows a person accepts are
recorded with who accepted them and when, and only those rows should leave
the tool.

**Not measured.** No accuracy figure is attached because none can be honestly
computed.
