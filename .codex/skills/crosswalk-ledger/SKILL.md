---
name: crosswalk-ledger
description: Work safely on Crosswalk Ledger, reproduce its published framework-agreement measurements, and validate code, data, documentation, and release claims before delivery.
---

# Crosswalk Ledger workflow

## Purpose and boundaries

- Treat this repository as a local-first measurement project, not an authoritative compliance mapping tool.
- Preserve the distinction between published human crosswalks, machine-proposed candidates, and legal or compliance conclusions.
- Do not describe recall against a named reference as accuracy, precision, or proof of compliance.
- Do not change a published figure unless its source data, generation command, report output, tests, and documentation are updated together.

## Stack and commands

- Python 3.10 or newer, packaged with setuptools.
- Core dependencies: NumPy, scikit-learn, and openpyxl.
- Optional embedding path: sentence-transformers and PyTorch.
- Install for validation with `python3 -m pip install -e ".[dev]"`.
- Install the optional embedding path with `python3 -m pip install -e ".[dev,embed]"` only when it is necessary to reproduce embedding results.

## Security and data constraints

- Use only public framework material and synthetic examples already approved for the repository.
- Never add credentials, tokens, private target URLs, classified or operational material, personal data, downloaded model caches, or generated environments.
- Keep normal tests and published-measurement reproduction offline. Networked source refreshes must be explicit and must preserve publisher, licence, retrieval date, and SHA-256 provenance in `sources.lock.json`.

## Verification

Run from the repository root:

```bash
python3 -m pytest tests -q
python3 -m ruff check .
python3 -m mypy src
python3 scripts/measure_agreement.py
python3 scripts/evaluate_method.py
python3 scripts/build_dora_candidates.py
git diff --check
```

When release text cites embedding results, also reproduce the pinned embedding path and compare the generated report with the committed result. Verify every public number against the relevant committed JSON report and the documentation that defines its denominator.

## Git delivery

- Preserve unrelated user changes and keep generated dependencies or caches out of Git.
- Review `git status`, the complete diff, and staged files for secrets and unintended data before committing.
- Use a focused commit message and push only to the configured repository remote after validation succeeds.
