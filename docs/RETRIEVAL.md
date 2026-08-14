# Can a machine reproduce a human crosswalk?

Step 2. For each element on one side, rank every element on the other by
similarity and ask where the human's chosen counterparts land. Read beside
[AGREEMENT.md](AGREEMENT.md), which found two experts agreeing on 19% of the
same kind of task.

Rebuild with `python3 scripts/evaluate_method.py --embed`. Model pinned to
`sentence-transformers/all-MiniLM-L6-v2`, run locally, no API call.

## The answer to the question the baseline was there to ask

**Embeddings earn their place on two of the three pairs and not on the third,
and the pattern is the useful part.**

| Pair | recall@3, lexical → embedding | Verdict |
|---|---|---|
| 800-53 → CSF 1.1 | 48.9% → **62.8%** | embeddings clearly |
| ATT&CK → 800-53 | 9.0% → **24.7%** | embeddings clearly |
| ATT&CK ↔ D3FEND | 36.6% → 41.6% | a tie |

On ATT&CK ↔ D3FEND the two methods are within noise of each other at every
cut-off, and at @20 **lexical is ahead**: 75.8% against 72.0%. An embedding
model, a 90 MB download and an unexplainable score buy nothing there.

The reason is visible once stated. ATT&CK and D3FEND are both MITRE, both
describing technique-level behaviour, both in the same register — the words
already match, so term overlap is enough. Where the two sides speak
differently — a control catalogue against an outcome framework, or a control
against an attacker's behaviour — the vocabulary stops overlapping and the
embedding earns its keep.

That matters for what comes next. DORA is legal prose and ISO and CSF are
control prose: the widest vocabulary gap of any pair here, and therefore the
regime where embeddings help most.

## Full results

Random is a genuine floor, not a formality: with 108 candidates, guessing
lands a hit in the top 20 more than a third of the time.

### NIST 800-53 ↔ CSF 1.1 — 495 human pairs

| Direction | Method | @1 | @3 | @5 | @10 | @20 | median rank |
|---|---|---:|---:|---:|---:|---:|---:|
| 800-53 → CSF | embedding | **43.1%** | **62.8%** | 70.7% | 80.9% | 88.3% | 2 of 108 |
| 800-53 → CSF | lexical | 31.9% | 48.9% | 58.5% | 64.9% | 76.6% | 4 |
| 800-53 → CSF | random | 2.1% | 8.0% | 15.4% | 24.5% | 37.8% | 34 |
| CSF → 800-53 | embedding | **22.6%** | 35.8% | 48.1% | 65.1% | 78.3% | 6 of 1,014 |
| CSF → 800-53 | lexical | 16.0% | 34.0% | 43.4% | 60.4% | 71.7% | 6 |
| CSF → 800-53 | random | 0.9% | 0.9% | 1.9% | 2.8% | 9.4% | 145 |

### NIST 800-53 ↔ ATT&CK — 5,263 human pairs

| Direction | Method | @1 | @3 | @5 | @10 | @20 | median rank |
|---|---|---:|---:|---:|---:|---:|---:|
| ATT&CK → 800-53 | embedding | **10.2%** | **24.7%** | 33.9% | 47.1% | 64.2% | 11 of 1,014 |
| ATT&CK → 800-53 | lexical | 3.2% | 9.0% | 15.8% | 30.9% | 49.9% | 21 |
| ATT&CK → 800-53 | random | 0.6% | 3.4% | 4.5% | 8.5% | 16.4% | 70 |
| 800-53 → ATT&CK | embedding | **22.9%** | 41.3% | 50.5% | 59.6% | 68.8% | 5 of 656 |
| 800-53 → ATT&CK | lexical | 19.3% | 37.6% | 44.0% | 52.3% | 65.1% | 10 |
| 800-53 → ATT&CK | random | 6.4% | 12.8% | 21.1% | 30.3% | 44.0% | 27 |

### ATT&CK ↔ D3FEND — 3,202 human pairs

| Direction | Method | @1 | @3 | @5 | @10 | @20 | median rank |
|---|---|---:|---:|---:|---:|---:|---:|
| ATT&CK → D3FEND | embedding | 21.1% | 41.6% | 48.1% | 61.5% | 72.0% | 6 of 272 |
| ATT&CK → D3FEND | lexical | 19.9% | 36.6% | 45.3% | 60.9% | **75.8%** | 7 |
| ATT&CK → D3FEND | random | 3.1% | 10.6% | 16.8% | 28.3% | 48.1% | 22 |
| D3FEND → ATT&CK | embedding | 22.8% | 39.6% | 45.0% | 58.4% | 71.1% | 8 of 656 |
| D3FEND → ATT&CK | lexical | 20.1% | 36.9% | 46.3% | 58.4% | 70.5% | 7 |
| D3FEND → ATT&CK | random | 5.4% | 10.1% | 15.4% | 24.8% | 36.2% | 45 |

## How this reads next to the humans

The comparison has to be made carefully or not at all. Two humans agreeing is
not the same measurement as a method retrieving.

The one figure that lines up is **recall@3**. The two OLIR submitters proposed
2.4 and 3.6 counterparts each, and shared at least one for **59%** of the
subcategories they both answered. Asking whether a method's top three contains
a counterpart the human chose is the same question.

On 800-53 → CSF 1.1 the embedding method reaches **62.8%** at @3. On the
reverse direction, 35.8%.

**That is the same order of magnitude as two experts agreeing with each
other, and on one direction slightly above it.** It is not a claim that the
method is as good as a person. It is a caution about reading either number as
accuracy: on this task, agreeing with a specific human about 60% of the time
is roughly what another human achieves.

Different framework pairs, so this is an indication and not a controlled
comparison. It is put here because the alternative — reporting recall against
a single mapping with no sense of what agreement is achievable — is how tools
come to advertise 94% accuracy.

## What is deliberately absent

**No precision, and no F1.** The published mappings are incomplete. A pair the
method proposes that the human did not record may be a correct link nobody
wrote down. Counting those as errors would measure how closely a method copies
one person's coverage rather than whether it finds real correspondences.

**No threshold, and no single accuracy figure.** Every number here is recall
against a named mapping by a named publisher, in a stated direction.

## The pair that could not be measured

**CSF 2.0 ↔ ISO/IEC 27001:2022** — the pair with the human-disagreement
figure — is missing from this report. The Annex A control text is ISO's
copyright, it appears in none of the published OLIR exports, and it is not in
this repository. Running the method there needs a copy of the standard the
user supplies; only the resulting scores could ever be published.

So step 1 and step 2 rest on different pairs. That is a real limitation of
this evidence and not a presentational choice.

## Limits

- **The reference mappings are sparse and uneven.** CTID's crosswalk covers
  109 of 1,014 live 800-53 controls, concentrated in the technical families.
  Recall measured there says how well a method reproduces human judgement in
  the areas humans chose to map.
- **Ties are broken pessimistically.** A true counterpart sharing a score with
  others is ranked after all of them, so these figures are a floor. The first
  version of the evaluation used `argsort`, which breaks ties by position in
  the catalogue and quietly handed the lexical baseline recall it had not
  earned — a query sharing no term with hundreds of candidates leaves them all
  at exactly zero. Fixing it moved lexical 800-53 → CSF from 65.4% to 64.9%
  at @10. The embedding figures did not move, because float similarities
  rarely tie.
- **One embedding model.** A larger or domain-tuned model may do better; the
  claim is only that this one beats lexical on two pairs out of three.
- **Title and statement are concatenated** for every method equally. No
  per-method text tuning was done, because tuning one arm and not the other
  is how baselines get beaten on paper.
