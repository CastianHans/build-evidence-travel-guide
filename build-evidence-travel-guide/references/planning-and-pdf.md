# Planning and PDF production

## Contents

1. Day construction
2. Feasibility arithmetic
3. Execution cards
4. Transport and payment chapters
5. Shopping and products
6. Visual design
7. Final quality assurance

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

## 5. Shopping and products

For each product:

- exact model, size, formulation, or regional SKU;
- current local price and comparison price;
- tax/refund effect;
- benefit claim with appropriate uncertainty;
- direct adverse/negative evidence;
- unsuitable users;
- warranty, region, voltage, language, customs, and luggage issues;
- buy/no-buy threshold.

Do not label products effective merely because they are popular.

## 6. Visual design

- Put weather first and preparation second when requested.
- Use a consistent grid, restrained color palette, readable CJK fonts, page numbers, and clear hierarchy.
- Use route strips, small maps, station-exit diagrams, and recognition photos only when useful.
- Prefer human-readable labels over raw URLs in the main body; keep full links in sources.
- Avoid decorative screenshots, dense collages, tiny text, or random social-post images.
- Credit external images and respect licensing; prefer official or self-generated diagrams.

## 7. Final quality assurance

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
