# Planning and PDF production

## Contents

1. Day construction
2. Feasibility arithmetic
3. Execution cards
4. Transport and payment chapters
5. Shopping and products
6. Visual design
7. Reputation and evidence disclosure
8. Final quality assurance

## 1. Day construction

Build a full-day chain from the exact hotel, not isolated attraction cards.

For each day include:

- wake/breakfast or departure assumption;
- hotel-to-first-stop instructions;
- multiple geographically coherent stops;
- every connection and expected navigation buffer;
- meal strategy and queue cap;
- indoor/outdoor rhythm based on actual weather tolerance;
- return-to-hotel instructions;
- latest exit and deletion order;
- a complete fallback if the day depends on weather, tickets, visibility, or closures.

## 2. Feasibility arithmetic

Calculate:

```text
total elapsed =
  attraction stays
  + walking
  + transit in motion
  + waiting/transfers/find-exit time
  + meals
  + toilets/rest
  + contingency
```

Compare official suggested duration with multiple actual traveler durations. State the range and chosen planning value.

Estimate:

- steps/walking distance;
- outdoor exposure;
- transport cost;
- tickets;
- meals;
- taxi range;
- shopping excluded or separately budgeted.

## 3. Execution cards

Each stop card should state:

- arrival time and planned duration;
- local-language name and address when useful;
- what to do after entering;
- must-see subset;
- toilets, seating, lockers, shade, or air conditioning;
- positive reason for inclusion;
- direct negative evidence and mitigation;
- on-site decision rule;
- exact next-leg instructions.

When a card crosses a page, repeat the stop heading.

## 4. Transport and payment chapters

Explain:

- product name and who needs one;
- purchase location and machine/counter;
- exact buying sequence;
- accepted payment methods and current uncertainty;
- activation and validity;
- tapping/use rules;
- coverage and exclusions;
- break-even calculation against the itinerary;
- common failure cases;
- fallback and cash requirement.

Separate airport arrival and departure instructions.
For Chinese travelers, list Alipay, WeChat Pay, UnionPay, Visa, and Mastercard support separately. Do not convert a generic “cards accepted” statement into proof that UnionPay works, and do not convert a QR sign into proof that a mainland wallet can complete payment. Show local-currency settlement, CNY estimate, foreign-transaction fees, dynamic-currency-conversion risk, and a failure fallback when material.

## 5. Shopping and products

For each product:

- exact model, size, formulation, or regional SKU;
- current local price and comparison price;
- dated CNY conversion and a comparable mainland China channel price;
- tax/refund effect;
- benefit claim with appropriate uncertainty;
- direct adverse/negative evidence;
- unsuitable users;
- warranty, region, voltage, language, customs, and luggage issues;
- buy/no-buy threshold.

Do not label products effective merely because they are popular.

## 6. Visual design

- Default to Simplified Chinese headings, body text, labels, and user instructions. Retain exact foreign proper nouns and add local-language names where they help navigation.
- Put weather first and preparation second when requested.
- Use a consistent grid, restrained color palette, readable CJK fonts, page numbers, and clear hierarchy.
- Use route strips, small maps, station-exit diagrams, and recognition photos only when useful.
- Prefer human-readable labels over raw URLs in the main body; keep full links in sources.
- Avoid decorative screenshots, dense collages, tiny text, or random social-post images.
- Credit external images and respect licensing; prefer official or self-generated diagrams.

## 7. Reputation and evidence disclosure

For every named restaurant, store, controversial attraction, or candidate exposed
to paid promotion/black-post risk, show:

- independent positive and negative narrative clusters, not raw post counts;
- source families and time windows;
- commercial-promotion and coordinated-attack signals separately;
- material comment corroboration, refutations, merchant response, and sampling
  limits;
- any D1/D2/D3 nationality-treatment signal scoped to branch and date;
- why the item is included, downgraded, replaced, or avoided.

Do not say “大多数游客” or “普遍歧视” from an online sample.

## 8. Final quality assurance

Content checks:

- all requirements represented;
- no unsupported assumption presented as fact;
- all critical candidates pass evidence gate;
- complete optional and fallback days;
- prices and rules dated;
- product and transit recommendations include contrary evidence.

PDF checks:

- render every page;
- no blank pages, clipping, overlap, missing glyphs, broken images, or illegible URLs;
- inspect cover, weather, preparation, each day opener, dense execution cards, alternatives, sources, and last page at full resolution;
- text extraction contains required sections;
- record page count, bytes, and SHA-256.
- print the current candidate-row and evidence-ledger-row counts in the PDF;
- keep filename, cover/body version, footer, and metadata consistent;
- compare rendered page count with PDF page count and complete the visual
  inspection manifest;
- run `scripts/finalize_run.py`; only its `FINAL` result permits a final-delivery
  claim.
