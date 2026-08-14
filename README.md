# Crosswalk Ledger

Crosswalks between security frameworks are bought, sold and cited as if they
were facts. This measures how much two of them actually agree.

**Two expert crosswalks of the same framework pair, both published by NIST
through the OLIR programme after a public comment period, agree on 19% of
their pairs.**

That number is the point of the project. Everything else follows from it.

```bash
pip install -e .
python3 scripts/measure_agreement.py
```

No network call, no model download, and the finding reproduces in under a
second from files committed here.

## The three findings

**1. Humans disagree, a lot.** → [docs/AGREEMENT.md](docs/AGREEMENT.md)

NIST CSF 2.0 to ISO/IEC 27001:2022, comparing the two published informative
references. Of 37 subcategories both submitters mapped, they proposed 134 and
90 pairs and 36 were identical: **19% exact, 59% sharing at least one
control.** Fifteen of the 37 share nothing at all.

The disagreements are not errors. For continuous monitoring one chose A.8.16
*Monitoring activities* and the other A.8.15 *Logging*. For recovery plan
execution, A.5.26 against A.5.29. Both readings are defensible.

**2. A machine reaches roughly the same agreement a second human does.**
→ [docs/RETRIEVAL.md](docs/RETRIEVAL.md)

Embedding similarity, measured against each human crosswalk separately and
never against a merged "truth", puts a human-chosen counterpart in its top
three **62.8%** of the time on 800-53 → CSF, against **48.9%** for a TF-IDF
baseline and 8.0% for random guessing.

Embeddings earn their place on two pairs out of three, and the exception is
instructive: on ATT&CK ↔ D3FEND they tie with plain term overlap, and at @20
**lexical wins**. Both sides are MITRE documents in the same register, so the
words already match. Embeddings pay off where the two sides speak
differently — a control catalogue against an outcome framework — which is
exactly the DORA case.

**3. A candidate DORA crosswalk, with its own uncertainty attached.**
→ [docs/DORA.md](docs/DORA.md)

No official DORA crosswalk to anything exists. 209 obligations from Articles
5–45, each with three candidates against 800-53 and CSF 2.0, and 3,764 chains
composed onward to ATT&CK through MITRE's published mapping.

Every row is labelled `proposed`. The measured performance of the method and
the human-agreement figure travel inside the output file, so no number in it
can be read as accuracy.

## Why this exists

Razil, publishing their own hand-made CSF 2.0 to ISO 27001 mapping, reported
that they searched extensively and found nothing, and that they "even tried
using ChatGPT and Gemini for assistance, but both produced significant AI
hallucinations".

The usual reading is that the models are bad at this. The measurement here
suggests something more useful: **the task has no single right answer, so a
model asked for one will invent a confident one.** A tool advertising 94%
accuracy on framework mapping is reporting agreement with one opinion.

## What it does not do

**No single accuracy figure.** Every number is recall against a named mapping
by a named publisher, in a stated direction, or agreement between two named
mappings.

**No precision, no F1.** The reference mappings are incomplete, so a proposed
pair the human did not record is not necessarily wrong. Publishing precision
would measure how closely a method copies one person's coverage.

**Not compliance.** That a control resembles an obligation does not mean it
discharges it. DORA compliance is a legal determination and this produces an
input to it.

**Not authoritative.** Nothing here is a mapping. The word is avoided
throughout in favour of *candidate* and *proposal*.

Fuller version in [DISCLAIMER.md](DISCLAIMER.md).

## What is in the box

| | |
|---|---|
| `catalogues/items/` | ATT&CK 656 · 800-53 1,014 · CSF 1.1 108 · CSF 2.0 106 · D3FEND 272 · DORA 64 |
| `catalogues/pairs/` | the four human crosswalks, normalised: 5,263 · 3,202 · 495 · 103 |
| `human-mappings/` | the NIST OLIR coverage exports the agreement figure is computed from |
| `reports/` | the three results as JSON |
| `sources.lock.json` | every source with its publisher, licence, SHA-256 and retrieval date |

Every byte of framework text comes from the body that publishes it. An earlier
draft took the CSF 2.0 subcategory text from a practitioner's spreadsheet that
carried no licence; NIST publishes the same text itself, and the two agree on
all 106 subcategories character for character, so the dependency was dropped
rather than relied on.

## Reproducing it

The catalogues are committed, so the measurements and the whole test suite run
offline:

```bash
python3 scripts/measure_agreement.py                  # step 1
python3 scripts/evaluate_method.py                    # step 2, lexical only
pip install -e ".[embed]" && \
  python3 scripts/evaluate_method.py --embed          # step 2, full
python3 scripts/build_dora_candidates.py              # step 3
```

Rebuilding the catalogues from source needs the network and 119 MB of
downloads:

```bash
python3 scripts/fetch_sources.py && python3 scripts/build_catalogues.py
```

Two files must be fetched by hand from the
[NIST OLIR catalogue](https://csrc.nist.gov/projects/olir/informative-reference-catalog),
which serves through a JavaScript application with no download endpoint.
`scripts/fetch_sources.py --check` says which and where to put them.

## Things that would have quietly corrupted the results

Kept here because each was caught by an assertion or a test rather than by
reading the output, and each would have produced plausible numbers.

**Identifiers did not match at all.** CTID writes a control `AC-02`, OSCAL
writes it `ac-2`, D3FEND writes it `CM-5(3)`. The raw intersection of CTID's
controls with OSCAL's is **zero**; after normalisation it is 109 of 109. A
pipeline without that step reports a method that recovers nothing, and the
fault looks like the method's.

**The NIST crosswalk is CSF 1.1, not 2.0.** The file name does not say so. The
absence of any `GV.*` identifier proves it: the GOVERN function exists only in
2.0.

**182 of 1,196 controls are withdrawn tombstones** with a title and no
statement. Counting them as parse failures fired the empty-text assertion,
which is how they were found.

**`DE-0002` is not an ATT&CK technique.** D3FEND puts detection identifiers in
the same field as technique identifiers, producing 104 phantom counterparts.

**ATT&CK was pinned to 16.1, not the current 19.2**, because the CTID
crosswalk was built against 16.1. Measuring against a newer catalogue reports
three releases of renames and revocations as the method's failures.

**Ties were broken optimistically.** `argsort` orders ties by position in the
catalogue, which handed the lexical baseline recall it had not earned wherever
hundreds of candidates sat at exactly zero. A test caught the gap between the
docstring and the code.

**DORA → ATT&CK directly produced confident nonsense**: Article 45,
information-sharing on cyber threats, matched against `T1597.002` *Purchase
Technical Data*, which is an adversary buying data. DORA states duties on
defenders and ATT&CK describes attacker behaviour. The route now runs through
a control catalogue, where each link compares like with like.

## Tests

```bash
pip install -e ".[dev]"
PYTHONPATH=src python3 -m pytest tests -q
```

82 tests, no network. Most fix the arithmetic behind a published percentage,
because a measurement whose definition can drift silently is worse than none —
the number keeps being published either way.

## Related

Part of a family of local-first tools that record a decision and the evidence
behind it. This is the only one that is a measurement rather than a tool.

- [Audit Readiness Ledger](https://github.com/v-k-tsalikidis/Audit-Readiness-Ledger) — which of the 93 ISO 27001 Annex A controls a folder of policies never addresses
- [Regulatory Scope Ledger](https://github.com/v-k-tsalikidis/Regulatory-Scope-Ledger) — which NIS2 and DORA criteria your answers trigger, and why a Directive cannot put you in scope
- [Shift Handover Ledger](https://github.com/v-k-tsalikidis/Shift-Handover-Ledger) — a SOC or NOC shift handover as a transfer of accountability
- [Security Headers Ledger](https://github.com/v-k-tsalikidis/Security-Headers-Ledger) — the HTTP security headers a server returned
- [CSF Outcome Ledger](https://v-k-tsalikidis.github.io/CSF-Outcome-Ledger/) — why a control supports a NIST CSF 2.0 outcome, and when that reasoning expires
- [Cyber Posting Ledger](https://github.com/v-k-tsalikidis/Cyber-Posting-Ledger) — a vacancy against a structured record of your experience

## Feedback

If a number here is wrong, please
[open an issue](https://github.com/v-k-tsalikidis/Crosswalk-Ledger/issues).
That is more useful than a citation.

Apache-2.0. See [LICENSE](LICENSE).
