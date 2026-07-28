# Provisional and final delivery gates

## Contents

1. State machine
2. Traceability gate
3. Research and reputation gates
4. Itinerary gate
5. PDF and visual gate
6. Finalization command

## 1. State machine

Use only these run states:

`initialized -> researching -> planning -> provisional -> final`

An interim PDF, a passed critical-only evidence audit, or a completed draft is
`provisional`. Never say “完成”, “最终版”, or “全部验证” until the finalization
manifest says `final_allowed=true`.

## 2. Traceability gate

Fill `requirements/traceability.csv`.

- Every user-confirmed fact and acceptance requirement gets a stable ID.
- Map it to candidate IDs and a human-readable PDF section.
- A required item must be `satisfied` with a verification note for final delivery.
- `declared_gap` is allowed in a provisional artifact, not a final artifact.
- Every included/optional critical or major candidate must appear in traceability.

Run `scripts/audit_traceability.py PROJECT_DIR --mode final`.

## 3. Research and reputation gates

Run:

```text
python scripts/audit_evidence.py PROJECT_DIR
python scripts/audit_reputation.py PROJECT_DIR
```

Final mode requires critical and major evidence coverage. Rejected candidates
cannot bypass research. Comments, commercial/attack signals, and D2/D3 claims must
pass their schemas and limits.

## 4. Itinerary gate

Fill `work/itinerary.csv` with one arithmetic block per route/stop. Each day must:

- start and end at a candidate representing the exact hotel;
- reference candidate IDs for every block;
- include mode, route detail, all time components, meal/rest and buffer;
- have contiguous, non-overlapping times;
- name a complete fallback day/branch.

Run `scripts/audit_itinerary.py PROJECT_DIR`.

## 5. PDF and visual gate

The PDF must:

- put weather and pre-departure preparation within its first three pages;
- carry one consistent document version in filename and text;
- print current candidate and evidence-ledger row counts;
- avoid stale prior-version text and deterministic long-range forecasts;
- pass text/metadata validation;
- render to exactly the same page count;
- have every rendered page marked `pass` by an inspector with an ISO timestamp.

`render_pdf.py` creates a `visual-inspection.csv` with `pending` rows. Inspect every
page, fix defects, rerender to a new empty directory, then mark only genuinely
reviewed pages `pass`.

## 6. Finalization command

```text
python scripts/finalize_run.py PROJECT_DIR GUIDE_v3.0.pdf \
  --document-version v3.0 \
  --visual-manifest PROJECT_DIR/work/visual-inspection.csv \
  --require "出发前准备" \
  --forbid "v2.0"
```

For a trip beyond the reliable forecast window, also pass `--forecast-issued` and
`--trip-start`; the PDF must label the weather section
`远期趋势，非逐日预报`.

If any final gate fails, fix it or deliberately deliver a provisional artifact:

```text
python scripts/finalize_run.py PROJECT_DIR GUIDE_v3.0.pdf \
  --mode provisional --document-version v3.0
```

The provisional command records gaps and forbids a false final claim.
