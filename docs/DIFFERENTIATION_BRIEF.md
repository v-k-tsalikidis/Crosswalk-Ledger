# Differentiation brief — Crosswalk Ledger

Research dated 2026-08-13. Second revision: the first was written before the
data was in hand, and the data changed the project.

Supersedes two rejected briefs: Detection Claim Ledger (built around a
refusal rather than a use) and Defence Chain Ledger (joined data MITRE had
largely joined already).

## What changed, and why the project is now a different one

The first version of this brief planned to measure an automated method
against official crosswalks used as ground truth, and then, if it scored well,
to produce a DORA crosswalk nobody has published.

Then the data arrived, and with it a finding that removes the foundation of
that plan.

**Two expert crosswalks of the same pair, both published by NIST through the
OLIR programme, agree on 19% of their mappings.**

| CSF 2.0 → ISO/IEC 27001:2022, Annex A controls only | |
|---|---:|
| Subcategories where both submitters mapped something | 37 |
| Pairs proposed by Razilio | 134 |
| Pairs proposed by the Independent submitter | 90 |
| Identical pairs | 36 |
| **Exact agreement (Jaccard)** | **19%** |
| **Share at least one control** | **59%** |

This is not carelessness. The disagreements are defensible readings:

- `DE.CM-01`, continuous monitoring — one says A.8.16 *Monitoring
  activities*, the other A.8.15 *Logging*.
- `RC.RP-01`, recovery plan execution — one says A.5.26 *Response to
  information security incidents*, the other A.5.29 *ICT readiness for
  business continuity*.
- `ID.AM-08` — one submitter lists nine controls, the other one, and they
  share none.

**There is no ground truth here. There are opinions, published by NIST as
informative references, that agree about a fifth of the time.**

So the original plan cannot be executed as written. Measuring a method's
"accuracy" against one of these is measuring agreement with one opinion and
calling it correctness. Any product claiming 94% accuracy on framework
mapping is doing exactly that.

## The contribution

**Nobody has published this measurement.** Crosswalks are bought, sold and
cited as if they were facts. The first deliverable of this project is the
evidence that they are not, with the numbers and the disagreeing examples.

It also explains something practitioners already hit. Razil, publishing their
own hand-made CSF 2.0 to ISO 27001 mapping, wrote that they searched
extensively and found nothing, and that they "even tried using ChatGPT and
Gemini for assistance, but both produced significant AI hallucinations". The
usual reading is that the models are bad at this. The measurement suggests
something more useful: **the task has no single right answer, so a model
asked for one will invent a confident one.**

## What is in hand

Seven sources retrieved, hashed and version-pinned; catalogues built with
every structure size-asserted.

| Catalogue | Items |
|---|---:|
| ATT&CK Enterprise 16.1 | 656 |
| NIST 800-53 Rev 5, live controls | 1,014 |
| NIST CSF 1.1 subcategories | 108 |
| D3FEND defensive techniques | 272 |
| DORA articles | 64 |

| Human-made pairs | Count | Publisher |
|---|---:|---|
| 800-53 ↔ ATT&CK | 5,263 | MITRE CTID |
| ATT&CK ↔ D3FEND | 3,202 | MITRE |
| CSF 1.1 ↔ 800-53 | 495 | NIST |
| D3FEND ↔ 800-53 | 103 | MITRE |
| CSF 2.0 ↔ ISO 27001:2022 | two submissions | NIST OLIR |
| CSF 2.0 ↔ CSF 1.1 | 106 | NIST |

The last row is a bridge: composed with CSF 1.1 ↔ 800-53, it yields
CSF 2.0 ↔ 800-53 for 87 of 106 subcategories without any manual download.

ATT&CK is pinned to 16.1 rather than the current 19.2 because the CTID
crosswalk was built against 16.1; measuring against a newer catalogue would
report three releases of renames and revocations as the method's failures.

## The three steps

**1. Measure the disagreement.** Between the two OLIR submissions, and
between any other pair of independent human mappings of the same items.
Report exact and loose agreement, and the cases where competent people read
the same subcategory in incompatible ways. This is the headline result and it
stands on its own.

**2. Measure the automated method against each human mapping separately.**
Never against a merged "truth". The only defensible claim is comparative:
*the method agrees with Razilio about as much as the Independent submitter
does*. If it reaches human-level agreement, that is a real result. If it does
not, that is also a result.

The baselines decide whether embeddings earn their place: random pairing as a
floor, and **TF-IDF or BM25 cosine over the same text** as the one that
matters. Both sides of these documents share dense jargon. If lexical overlap
does as well, the embeddings are cost and opacity for nothing, and the report
says so.

**3. Then DORA**, as candidate pairs carrying the measured human agreement
range beside them — never as an answer. Every row labelled `official`,
`composed` or `proposed`, and accepted rows recorded with who accepted them
and when.

## What this does not promise

**Not an authoritative DORA crosswalk.** We now have evidence that nobody can
produce one, and claiming otherwise would repeat the error the project exists
to document.

**Not compliance.** That a control resembles an obligation does not mean it
discharges it. DORA compliance is a legal determination; this is an input to
that work. The same line the Regulatory Scope Ledger holds.

**Not a single accuracy figure.** Every number is agreement with a named
mapping by a named author, or it is not published.

## Why a number is the deliverable here

Unlike the other tools in this family, what this produces **is** a score, and
that is correct. The denominator is shown, the mappings compared are named
and public, the baselines are stated, and anyone can rerun it. That is the
difference between a measurement and the invented "8% compliance match" that
was removed from the CSF Outcome Ledger.

## Known limits, stated before the numbers are published

- **Small overlap.** The two OLIR submissions both map only 37 subcategories
  in common. The Independent submitter left 67 of 106 empty.
- **Density differs.** Razilio proposes 134 pairs where the Independent
  proposes 90 in the same region. Greater density mechanically lowers
  Jaccard, so 19% overstates the disagreement. The 59% loose figure is
  reported beside it for that reason.
- **Sparse and biased ground truth elsewhere.** CTID's crosswalk maps 5,263
  pairs but touches only 109 of 1,014 live 800-53 controls, concentrated in
  the technical families.
- **Granularity mismatch is real and measurable.** DORA articles average
  3,155 characters; CSF subcategories average 78. A similarity score across
  that gap is not comparing like with like, which is the SECFORCE argument in
  numbers. Article-level DORA text will need splitting into obligations
  before any comparison is meaningful.

## The ISO 27001 constraint

ISO standards are copyrighted and not redistributable. The OLIR coverage
exports carry ISO control *identifiers*, which NIST publishes freely; the ISO
control *text* cannot be shipped. Any step needing that text runs against a
copy the user supplies, and only the resulting scores are published. DORA,
ATT&CK, D3FEND, 800-53 and CSF are all free.

## Why this one, given the author

The BSc thesis was on the Detect stage of NIST CSF using knowledge graphs
over MITRE ATT&CK, with D3FEND and 800-53 in the same work. This is not the
thesis and publishes no part of it. It is the same toolkit pointed at a
question the thesis did not ask, and it is the only project in the set that
reads as research rather than as a tool.

## Kill criteria

Step 1 stands on its own and is already measurable, so the project has a
publishable result regardless of what follows.

Stop before step 3 and publish the negative result if, at step 2, the method
does not beat TF-IDF/BM25 by a clear margin, or does not reach the agreement
level that two humans reach with each other.
