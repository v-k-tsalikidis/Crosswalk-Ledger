# Disclaimer and boundaries

## What this is

Crosswalk Ledger is an independent, open-source measurement written by
Vasileios Tsalikidis. It is not affiliated with, endorsed by, or associated
with NIST, MITRE, the MITRE Center for Threat-Informed Defense, ISO, the
European Commission, ENISA, any European Supervisory Authority, NATO, the NATO
Communications and Information Agency, the Hellenic Armed Forces, or any
government body.

The people whose published crosswalks are compared here — Razilio and the
Independent submitter to the NIST OLIR catalogue — have no involvement in this
work and have not reviewed it.

## Neither mapping compared here is wrong

The central finding is that two expert crosswalks of the same framework pair,
both published by NIST through OLIR after a public comment period, agree on
about a fifth of their pairs.

That is not a criticism of either submitter. The disagreements are defensible
readings of genuinely ambiguous correspondences. Naming them is comment on
published documents, which is what makes the measurement possible; it is not
an assessment of anybody's competence.

If a submitter believes their work is misrepresented here, the comparison is
reproducible from the committed files and an issue will be acted on.

## The candidate crosswalk is not compliance advice

DORA is Regulation (EU) 2022/2554 and applies directly to financial entities.
Whether an obligation is discharged is a legal determination with consequences
that include registration duties, reporting deadlines and personal liability
for management.

That a control resembles an obligation does not mean it discharges it. The
candidates in `reports/dora-candidates.json` are proposals for a qualified
person to accept or reject, and nothing else. Do not put them in front of a
supervisory authority as an answer.

There is no official DORA crosswalk to anything. Any product presenting one as
authoritative — including this one, if it ever did — is presenting a judgement
as a fact.

## No accuracy figure is attached, deliberately

Every number published here is recall against a *named* mapping by a *named*
publisher, in a stated direction, or it is agreement between two named
mappings. There is no single accuracy figure because none can be honestly
computed: the reference mappings are incomplete, so a proposed pair the human
did not record is not necessarily wrong.

Precision and F1 are absent for the same reason and their absence is not an
oversight.

## The method may be wrong in ways this cannot detect

A ranked list always returns something. The weakest first-ranked DORA
candidates score 0.30, which is the method returning the least bad of a
thousand wrong answers rather than finding anything. Similarity scores have no
natural scale: 0.66 does not mean 66% correct.

One embedding model was tested. A different or domain-tuned model would give
different numbers, which is why the model and its version are pinned in the
code and named in every report.

## ISO/IEC 27001 is not reproduced here

ISO standards are copyrighted and not redistributable. This repository holds
ISO control *identifiers*, which NIST publishes freely in its OLIR exports. It
holds no ISO control text, titles or descriptions.

Consequently the pair with the human-disagreement measurement is the one pair
the automated method could not be run on. That is a real limitation of the
evidence and it is stated in the reports rather than worked around.

## Sources and their licences

- **ATT&CK and D3FEND** — © The MITRE Corporation, reproduced and distributed
  with the permission of The MITRE Corporation.
- **NIST SP 800-53, CSF and the OLIR exports** — US Government work, not
  subject to copyright in the United States.
- **The 800-53 to ATT&CK crosswalk** — MITRE Center for Threat-Informed
  Defense, Apache-2.0.
- **DORA** — © European Union, reused under Commission Decision 2011/833/EU
  (CC BY 4.0).

Every source is recorded in `sources.lock.json` with its URL, publisher,
licence, SHA-256 and the date it was retrieved.

## Nothing leaves your machine

There is no network call at analysis time and no hosted model. The embedding
model runs locally. A control baseline or an accepted crosswalk describes what
an organisation believes covers its legal obligations, which is a document its
regulator and its adversary would both like to read.

## No warranty

Licensed under Apache-2.0, which means it is provided on an "AS IS" basis,
without warranties or conditions of any kind. If a number here is wrong,
please open an issue — that is more useful than a citation.
