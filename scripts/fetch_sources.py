#!/usr/bin/env python3
"""Download every published source this project measures against.

Nothing here is transcribed by hand. Each source is fetched from the body that
publishes it, hashed, and recorded in `sources.lock.json` with its size, its
SHA-256 and the date it was retrieved. A later run that gets different bytes
fails loudly instead of quietly changing the numbers the project publishes.

The raw files are large — ATT&CK alone is ~54 MB — so they live in a cache
outside the repository. Only the extracted catalogues are committed.

The two NIST OLIR coverage exports used for the agreement measurement are
committed under `human-mappings/`. They contain identifiers, not ISO control
text. No copyrighted ISO catalogue is fetched or redistributed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "sources"
LOCK = ROOT / "sources.lock.json"

USER_AGENT = "crosswalk-ledger/0.1 (+https://github.com/v-k-tsalikidis)"


@dataclass(frozen=True)
class Source:
    """One published file, and who published it."""

    key: str
    url: str
    publisher: str
    what: str
    licence: str
    #: Retrieval needing a header the default client does not send.
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def path(self) -> Path:
        return CACHE / self.key


#: The EU Publications Office answers content negotiation; EUR-Lex itself
#: returns 202 with an empty body to an automated request. Learned the hard
#: way on the Regulatory Scope Ledger.
CELLAR = "http://publications.europa.eu/resource/celex/32022R2554"

SOURCES: tuple[Source, ...] = (
    Source(
        key="attack-enterprise.json",
        # Pinned to 16.1, not to the current release. The CTID crosswalk that
        # serves as ground truth was built against 16.1, and measuring a
        # method against a mapping whose techniques have since been renamed,
        # split or revoked would report the method's failures as ATT&CK's
        # version drift. The current release was 19.2 when this was written.
        url=(
            "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/"
            "master/enterprise-attack/enterprise-attack-16.1.json"
        ),
        publisher="MITRE",
        what="ATT&CK Enterprise v16.1, STIX 2.1. Technique identifiers, names and descriptions.",
        licence=(
            "© The MITRE Corporation. Reproduced and distributed with the permission "
            "of The MITRE Corporation."
        ),
    ),
    Source(
        key="nist-800-53r5-catalog.json",
        url=(
            "https://raw.githubusercontent.com/usnistgov/oscal-content/main/"
            "nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json"
        ),
        publisher="NIST",
        what="SP 800-53 Rev 5 control catalogue, OSCAL. Control identifiers, titles and statements.",
        licence="US Government work, not subject to copyright in the United States.",
    ),
    Source(
        key="csf-pf-to-800-53r5.xlsx",
        url=(
            "https://csrc.nist.gov/files/pubs/sp/800/53/r5/upd1/final/docs/"
            "csf-pf-to-sp800-53r5-mappings.xlsx"
        ),
        publisher="NIST",
        what="Crosswalk from the Cybersecurity Framework and Privacy Framework to 800-53 Rev 5.",
        licence="US Government work, not subject to copyright in the United States.",
    ),
    Source(
        key="csf-2.0-core.xlsx",
        # The CSF 2.0 Reference Tool export. The path says json and the bytes
        # are OOXML; NIST serves a spreadsheet from that endpoint. Fetched so
        # the CSF 2.0 text comes from NIST rather than from a third party's
        # copy of it.
        url="https://csrc.nist.gov/extensions/nudp/services/json/csf/download?olirids=all",
        publisher="NIST",
        what="CSF 2.0 core: functions, categories, subcategories and their text.",
        licence="US Government work, not subject to copyright in the United States.",
    ),
    Source(
        key="d3fend.json",
        url="https://d3fend.mitre.org/ontologies/d3fend.json",
        publisher="MITRE",
        what="D3FEND ontology. Defensive techniques and their relationships.",
        licence=(
            "© The MITRE Corporation. Reproduced and distributed with the permission "
            "of The MITRE Corporation."
        ),
    ),
    Source(
        key="d3fend-full-mappings.json",
        url="https://d3fend.mitre.org/api/ontology/inference/d3fend-full-mappings.json",
        publisher="MITRE",
        what="D3FEND mappings out to ATT&CK and to NIST 800-53 Rev 5.",
        licence=(
            "© The MITRE Corporation. Reproduced and distributed with the permission "
            "of The MITRE Corporation."
        ),
    ),
    Source(
        key="ctid-800-53r5-to-attack.json",
        url=(
            "https://raw.githubusercontent.com/center-for-threat-informed-defense/"
            "mappings-explorer/main/mappings/nist_800_53/attack-16.1/nist_800_53-rev5/"
            "enterprise/nist_800_53-rev5_attack-16.1-enterprise.json"
        ),
        publisher="MITRE Center for Threat-Informed Defense",
        what="Direct mapping from 800-53 Rev 5 controls to ATT&CK Enterprise techniques.",
        licence="Apache-2.0.",
    ),
    Source(
        key="dora.xhtml",
        url=CELLAR,
        publisher="Publications Office of the European Union",
        what="Regulation (EU) 2022/2554 (DORA), full text, English.",
        licence="© European Union. Reused under Decision 2011/833/EU (CC BY 4.0).",
        headers={"Accept": "application/xhtml+xml", "Accept-Language": "en"},
    ),
)


def fetch(source: Source, timeout: int = 120) -> bytes:
    request = urllib.request.Request(
        source.url, headers={"User-Agent": USER_AGENT, **source.headers}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"{source.key}: HTTP {response.status}")
        return response.read()


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_lock() -> dict:
    return json.loads(LOCK.read_text(encoding="utf-8")) if LOCK.exists() else {}


def check() -> int:
    """Report what is cached, what is missing, and what drifted."""
    lock = load_lock().get("sources", {})
    missing = 0

    for source in SOURCES:
        if not source.path.exists():
            print(f"  missing   {source.key}")
            missing += 1
            continue
        got = digest(source.path.read_bytes())
        known = lock.get(source.key, {}).get("sha256")
        if not known:
            print(f"  UNLOCKED  {source.key}")
            missing += 1
        elif got != known:
            print(f"  DRIFTED   {source.key}\n            locked {known[:16]}… got {got[:16]}…")
            missing += 1
        else:
            size = source.path.stat().st_size
            print(f"  ok        {source.key:<34} {size:>10,} bytes")

    return 1 if missing else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="report cache state without downloading"
    )
    parser.add_argument(
        "--force", action="store_true", help="re-download even when the cache is current"
    )
    args = parser.parse_args()

    CACHE.mkdir(parents=True, exist_ok=True)
    if args.check:
        return check()

    lock = load_lock()
    entries: dict[str, dict] = lock.get("sources", {})
    failures: list[str] = []

    for source in SOURCES:
        if source.path.exists() and not args.force:
            if source.key not in entries:
                print(f"  FAILED    {source.key}: cached but absent from sources.lock.json")
                failures.append(source.key)
                continue
            print(f"  cached    {source.key}")
            continue
        print(f"  fetching  {source.key} …", end="", flush=True)
        try:
            payload = fetch(source)
        except (urllib.error.URLError, RuntimeError, TimeoutError) as error:
            print(f" FAILED: {error}")
            failures.append(source.key)
            continue

        # A source that answers 200 with nothing is the EUR-Lex failure mode.
        # Refuse it here rather than discover an empty catalogue later.
        if len(payload) < 1024:
            print(f" FAILED: {len(payload)} bytes, too small to be the document")
            failures.append(source.key)
            continue

        source.path.write_bytes(payload)
        got = digest(payload)
        known = entries.get(source.key, {}).get("sha256")
        note = ""
        if known and known != got:
            note = "  ← CHANGED since the last lock"
        entries[source.key] = {
            "url": source.url,
            "publisher": source.publisher,
            "what": source.what,
            "licence": source.licence,
            "sha256": got,
            "bytes": len(payload),
            "retrieved": datetime.now(timezone.utc).date().isoformat(),
        }
        print(f" {len(payload):,} bytes{note}")

    LOCK.write_text(
        json.dumps({"sources": entries}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote {LOCK.relative_to(ROOT)} with {len(entries)} sources.")

    if failures:
        print(f"\nFAILED: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
