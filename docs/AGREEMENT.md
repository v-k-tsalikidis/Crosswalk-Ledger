# How much do published crosswalks agree?

NIST CSF 2.0 → ISO/IEC 27001:2022, comparing the two informative
references published through the NIST OLIR programme. Annex A controls
only: the mandatory clauses are counted separately because only one
submitter mapped them.

Neither mapping is correct and neither is ground truth. Both went
through OLIR's public comment period. What follows measures how far
two expert judgements of the same question land from each other.

## The numbers

| | |
|---|---:|
| Subcategories in CSF 2.0 | 106 |
| Mapped by Razilio | 97 |
| Mapped by Independent | 39 |
| Mapped by both, and so comparable | **37** |
| Pairs proposed by Razilio | 134 |
| Pairs proposed by Independent | 90 |
| Identical pairs | 36 |
| **Exact agreement (Jaccard)** | **19%** |
| **Share at least one control** | **59%** |

Both figures are given because either alone misleads. Jaccard punishes
thoroughness: across the 37 comparable subcategories Razilio proposes
3.6 controls each against 2.4, and the denser mapping cannot
score well however sound its judgement is. The loose figure hides how
much else the two disagree about.

Across their whole mappings the two are equally dense — 2.5 against
2.4 controls per subcategory — so the gap above is specific to
where they overlap, not a difference in house style.

Silence is not disagreement. 62 subcategories were mapped by one
submitter and left blank by the other; those are excluded above rather
than counted as conflict.

## Where they read the same requirement differently

15 of the 37 comparable subcategories share no control at all.
These are not errors. They are defensible readings that landed apart.

Three read plainly. For continuous monitoring `DE.CM-01` one submitter
chose A.8.16 *Monitoring activities* and the other A.8.15 *Logging*.
For recovery plan execution `RC.RP-01` one chose A.5.26 *Response to
information security incidents*, the other A.5.29 *Information security
during disruption*. For `ID.AM-08` one lists nine controls and the
other lists one, and they share none.

Control titles are not reproduced in the table below: they are part of
ISO/IEC 27001:2022 and are copyrighted. The identifiers are what NIST
publishes.

| Subcategory | Razilio | Independent |
| --- | --- | --- |
| `DE.CM-01` | A.8.16 | A.8.15 |
| `DE.CM-09` | A.8.16 | A.8.6 |
| `GV.OC-05` | A.5.3 | A.5.8 |
| `GV.OV-01` | A.5.1, A.5.19 | A.5.5, A.5.6, A.5.24 |
| `GV.OV-02` | A.5.1, A.5.19 | A.5.27, A.5.35, A.5.36 |
| `GV.OV-03` | A.5.1, A.5.19, A.5.20 | A.8.30, A.8.32, A.8.34 |
| `GV.PO-02` | A.5.1 | A.5.31, A.5.32, A.5.34 |
| `GV.SC-07` | A.5.19, A.5.20, A.5.31 | A.5.22 |
| `ID.AM-08` | A.5.8, A.5.9, A.5.12, A.5.13, A.5.19, A.5.22, A.7.10, A.7.13, A.7.14 | A.5.11 |
| `PR.AA-01` | A.5.15, A.5.18, A.8.2, A.8.5 | A.5.16 |
| `PR.DS-10` | A.5.3, A.5.10, A.5.13, A.5.14, A.5.15, A.6.1, A.6.2, A.6.5, A.8.2, A.8.3, A.8.4, A.8.17, A.8.22, A.8.26 | A.5.23 |
| `PR.PS-02` | A.5.9 | A.8.7 |
| `PR.PS-03` | A.5.9 | A.8.1 |
| `RC.RP-01` | A.5.26 | A.5.29 |
| `RC.RP-02` | A.5.26 | A.5.30 |

## What follows from this

A crosswalk is a judgement, not a fact. Two experts working the same
pair, to the same template, under the same programme, agreed on about a
fifth of their mappings.

So a tool reporting that it matches *the* mapping with some accuracy is
reporting agreement with one opinion. This project therefore measures
any automated method against each human mapping separately and never
against a merged truth, and the only claim it will make is comparative:
whether a method agrees with a named mapping about as much as another
human does.

It also reframes a common complaint. Razil, publishing their own
hand-made version of this mapping, reported that ChatGPT and Gemini
produced significant hallucinations on the task. The usual reading is
that the models are bad at it. These numbers suggest something more
useful: the question has no single right answer, so a model asked for
one will invent a confident one.

## Limits

- Only 37 subcategories are comparable. The Independent submitter left
  67 of 106 blank.
- Annex A only. Mandatory clauses 4–10 are mapped by one submitter and
  not the other, so no comparison is possible there.
- Two mappings is not a sample. It is an existence proof that expert
  disagreement on this task is large, not an estimate of how large.

Rebuild with `python3 scripts/measure_agreement.py`.
