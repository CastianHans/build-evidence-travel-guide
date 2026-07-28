# Build Evidence Travel Guide

A reusable AI-agent Skill for producing executable, source-bounded travel-guide PDFs from official information and positive/negative traveler experiences.

It is designed for detailed itineraries, family travel, transport-pass decisions, airport transfers, route feasibility, shopping research, and polished PDF field manuals.

## What makes it different

- Separates user facts, source facts, assumptions, unknowns, and conflicts.
- Requires exact candidate-level positive and negative evidence.
- Rejects duplicate URLs, duplicate evidence IDs, mismatched attractions, unchecked identities, and promotional evidence.
- Uses official sources for rules, prices, hours, weather, and transport coverage.
- Calculates every day from the exact hotel, including walking, transit, queues, meals, rest, buffer, costs, and fallback plans.
- Audits transit passes against the actual itinerary instead of recommending them because their duration matches the trip.
- Renders and validates the final PDF before delivery.
- Keeps social-platform access read-only and never requests passwords or cookies.

## Install

Requires Python 3.10 or later. PDF rendering additionally requires Poppler; PDF authoring and validation use ReportLab, pypdf, and Pillow.

With a Skills-compatible installer:

```text
npx skills add CastianHans/build-evidence-travel-guide@build-evidence-travel-guide
```

Manual installation:

1. Copy `build-evidence-travel-guide/` into your agent’s Skill directory.
2. Restart or refresh the agent’s Skill catalog.
3. Invoke `$build-evidence-travel-guide`.

## Quick start

```text
$build-evidence-travel-guide
Build an evidence-backed, executable travel-guide PDF for my trip.
Start by collecting the minimum intake and do not assume limitations from age.
```

The Skill will request at least:

- destination and dates;
- arrival/departure points;
- travelers and actual mobility/weather tolerance;
- hotels or intended lodging areas;
- must-do, optional, and excluded activities;
- budget, pace, language, and output format.

Exact bookings, payment limits, luggage, diet, shopping, and fallback preferences are needed before producing an execution-ready manual.

Never provide passwords, browser cookies, complete passport numbers, payment-card numbers, verification codes, or API keys.

## Optional research stack

The Skill can bootstrap and diagnose:

- [Agent-Reach](https://github.com/Panniantong/Agent-Reach) for platform routing and health checks;
- [OpenCLI](https://github.com/jackwener/opencli) for user-controlled browser-backed reading;
- Poppler, ReportLab, pypdf, and Pillow for PDF production and inspection.

Run the read-only dependency check:

```text
python build-evidence-travel-guide/scripts/doctor.py
```

Installation never proves platform access. The user must manually install/enable the browser bridge and log in where required.

## Evidence gate

Initialize a project:

```text
python build-evidence-travel-guide/scripts/init_project.py path/to/project
```

Fill:

- `research/candidates.csv`
- `research/evidence.csv`

Then audit:

```text
python build-evidence-travel-guide/scripts/audit_evidence.py path/to/project
```

Exit codes:

- `0`: all gated candidates pass;
- `2`: critical or major candidates remain uncovered;
- `3`: schema or evidence-integrity failure.

Only unique, direct, non-promotional evidence with an exact candidate-identity check can satisfy the gate.

## PDF checks

```text
python build-evidence-travel-guide/scripts/validate_pdf.py guide.pdf \
  --require "Weather" --require "Preparation"

python build-evidence-travel-guide/scripts/render_pdf.py \
  guide.pdf path/to/empty-render-directory
```

Text validation does not replace visual review. Inspect the generated contact sheet and representative full-resolution pages.

## Test

```text
python -m unittest discover \
  -s build-evidence-travel-guide/tests -v
```

The test suite covers unique evidence, duplicate URLs and IDs, orphan evidence, mismatched candidates, promotional evidence, identity checks, and successful multi-platform coverage.

## Repository layout

```text
build-evidence-travel-guide/
  SKILL.md
  agents/
  assets/
  references/
  scripts/
  tests/
```

## License

MIT. Third-party tools and source content retain their own licenses and terms.
