---
name: build-evidence-travel-guide
description: 面向中国用户构建、审计、修订并打包循证旅行计划和自包含 PDF 手册；综合官方来源、小红书正向种草与反向避雷、Reddit、目的地本地语言平台、博客、地图和评价网站。用户需要详细行程、家庭旅行、社交平台调研、逐景点避雷、路线可行性、交通卡与机场交通、支付宝/微信/银联等支付分析、境内外商品比价或精美旅行 PDF 时使用；缺少调研软件时也适用。
---

# 构建面向中国用户的循证旅行手册

把交付物当作可直接照着执行的现场手册，而不是景点清单。

## 中国市场默认设置

- 除非用户另有要求，否则使用简体中文沟通和交付。
- 把小红书作为中国游客体验的核心层，同时把官方、国外社区和目的地本地平台证据分层保留。
- 涉及价格决策时，同时给出当地货币、带汇率时间戳的人民币估算和中国常见渠道对比价。
- 按需要分别核验支付宝、微信支付、银联、Visa、Mastercard、境外交易费、动态货币转换、仅收现金例外和支付失败备选。
- 涉及执行时，检查中国护照、从中国大陆出发、漫游/实体 SIM/eSIM、插头、退税、海关、保修、地区型号、App/语言和售后限制。
- 国外平台名、官方产品名、车站名、型号和有用的当地语言检索词保持原文，避免因翻译损失操作精度。

## Non-negotiable rules

1. Separate user facts, user preferences, model assumptions, official facts, and social experiences.
2. Do not infer physical limitations from age or family role. Ask for or use stated mobility and heat tolerance.
3. Verify every unstable hard fact close to delivery: weather, closures, hours, prices, ticket rules, transport coverage, payment methods, and entry requirements.
4. Search both positive and negative experiences for every important candidate.
5. A query containing “避雷” is not evidence. Open the result and confirm that it discusses the exact candidate.
6. Do not count off-topic, copied, promotional, or title-only results as direct evidence.
7. Do not claim complete negative validation while any important candidate remains uncovered.
8. Keep social access read-only. Never auto-login, harvest cookies, post, comment, like, favorite, or bypass platform controls.
9. Cite official sources for hard rules and social sources for lived experience. Do not substitute one for the other.
10. Render and inspect the final PDF page by page before delivery.

## Workflow

### 1. Ingest all supplied material

- Read [references/intake.md](references/intake.md), collect the minimum intake, and stop before broad research if any blocking field is unknown.
- Read every supplied PDF, document, slide deck, image, booking, and prior conversation.
- Extract facts into a requirements ledger before researching.
- Mark each item as `USER_CONFIRMED`, `SOURCE_CONFIRMED`, `ASSUMPTION`, `UNKNOWN`, or `CONFLICT`.
- Preserve exact flights, hotel address, dates, party size, payment limits, health constraints, desired places, optional plans, and prohibited actions.
- Never silently carry an earlier assistant’s guess forward as a user fact.

Use `scripts/init_project.py DESTINATION_DIR` to create reusable ledgers and folders.

### 2. Bootstrap and diagnose research tools

Read [references/bootstrap.md](references/bootstrap.md) when Agent-Reach, OpenCLI, browser bridging, or social-platform access is missing or unhealthy.

- Prefer Agent-Reach as the capability router and health checker.
- Run `python scripts/doctor.py` to identify missing local dependencies without changing the system.
- Run `agent-reach doctor --json` before platform work.
- Use the backend reported as usable; do not infer access from installation alone.
- For Chromium browsers, including Edge, use the user-controlled OpenCLI Browser Bridge session.
- If a logged-in session is unavailable, continue with official pages, public web indexes, and accessible platforms while labeling the gap.
- Do not block independent official verification merely because a social backend is unavailable.

### 3. Build the candidate inventory before collecting posts

List every decision-relevant object:

- attraction, neighborhood, mall, museum, restaurant or food strategy;
- airport transfer, transit pass, rail trip, taxi plan, station transfer;
- hotel operation, luggage step, payment method, SIM/eSIM;
- product, store, tax-refund path, warranty or customs issue;
- weather-dependent branch and complete fallback day.

Assign each candidate:

- stable `candidate_id`;
- category and exact canonical name;
- proposed date and route role;
- importance: `critical`, `major`, or `minor`;
- evidence target;
- inclusion status: `candidate`, `included`, `optional`, or `rejected`.

Do not research only the initial itinerary. Include plausible replacements so negative evidence can change the plan.

### 4. Collect evidence in two passes

Read [references/research-protocol.md](references/research-protocol.md) before starting a substantial collection.

**Pass A - broad route construction**

- Search complete itineraries, neighborhood combinations, seasonal constraints, and traveler archetypes.
- Draft geographically coherent day clusters.
- Use this pass to discover candidates, not to finalize them.

**Pass B - candidate-level validation**

For each critical or major candidate, search separately:

- positive experience and realistic duration;
- direct negative experience, disappointment, queue, heat, accessibility, payment, price, hygiene, closure, or logistics failure;
- current official rules;
- local-language name and local-platform discussion;
- exact connection to the next stop.

Open full posts and relevant comments. Record URLs, dates, platform, author where available, polarity, relevance, and the claim supported.
For every direct social record, also save an excerpt, reviewer, and explicit candidate-identity check.

### 5. Enforce evidence coverage

Use these default targets unless the user specifies stricter thresholds:

| Candidate | Positive | Direct negative | Official/current | Operational failure |
|---|---:|---:|---:|---:|
| Critical attraction/route | 2 | 2 | 1 | when applicable |
| Major attraction/mall | 2 | 2 | 1 if rules/prices exist | when applicable |
| Named restaurant/store | 2 | 2 | menu/price when available | 1 |
| Transit pass/airport transfer | 1 | 2 | 2 primary checks | 2 |
| Product recommendation | 2 | 2 adverse/limitation | current price | warranty/compatibility as applicable |
| Minor connector | 1 | 1 or explicit `NOT_APPLICABLE` | map/current rule | optional |

`NOT_APPLICABLE` is allowed only with a written reason. “No negative post found” is `UNCOVERED`, not `NOT_APPLICABLE`.

Counts use unique canonical URLs only. A duplicated post, duplicated evidence ID, orphan evidence row, invalid enum, missing excerpt, or unchecked candidate identity is a validation error, not a warning.

Run:

```text
python scripts/audit_evidence.py PROJECT_DIR
```

Do not move to final writing while critical candidates fail the gate. If a platform is inaccessible, disclose the shortfall and use the best available alternative without pretending equivalence.

### 6. Construct each day from the hotel

For every day:

1. Start at the exact hotel address.
2. Group stops by geography and opening-day compatibility.
3. State each walk, station entrance/exit, train/bus direction, transfers, taxi leg, expected wait, and navigation buffer.
4. Add realistic stop duration from official information and social reports.
5. Add meals, toilets, seating, luggage, shopping, and weather recovery.
6. Calculate net attraction time, transit/search time, meal time, buffer, total elapsed time, walking range, cost range, and latest exit.
7. Define weather/visibility/ticket gates and a complete fallback route.
8. Remove or demote candidates whose negative evidence outweighs their route value.

Do not turn a complete day into a single attraction merely because travelers are older. Use actual mobility, terrain, temperature, humidity, shade, and stated preferences.

### 7. Audit transport passes and payments separately

For every pass or payment recommendation:

- calculate break-even against the actual itinerary;
- distinguish card price, pass price, deposit, reload method, activation rule, validity, refunds, and service fees;
- list included and excluded modes and geographic boundaries;
- verify whether each traveler needs a separate card;
- separate airport purchase, city purchase, and return-to-airport procedures;
- research failure cases: foreign-card rejection, cash-only machines, wrong product, missed tap, late activation, unavailable stock, incompatible route, and refund difficulty;
- distinguish Alipay/WeChat acceptance from merchant-presented QR compatibility, and UnionPay acceptance from generic “card accepted” claims;
- warn against dynamic currency conversion and state whether local-currency settlement is normally preferable;
- give an exact fallback and state the cash impact.

Never recommend a pass merely because its validity length matches the trip length.

### 8. Audit restaurants, shopping, and products

- Prefer a decision rule over a fragile “must visit” named venue.
- Set queue limits, price transparency rules, ordering checks, and alternatives in the same area.
- For products, compare exact model/size and same-day net price, not list price.
- Compare the destination net price with a dated mainland China reference price and show both in CNY when practical.
- Include adverse reactions, unsuitable users, regional model differences, warranty, voltage/frequency, language, customs, and luggage constraints.
- Treat promotions as expiring observations, never guaranteed prices.

### 9. Write the field manual

Read [references/planning-and-pdf.md](references/planning-and-pdf.md) before authoring.

The PDF must begin with:

1. trip-period weather and update time;
2. pre-departure preparation.

Then include:

- bookings and hard boundaries;
- transport card and airport-transfer operations;
- overview calendar;
- one complete section per day;
- one execution card per stop;
- complete alternatives;
- food, shopping, products, emergency handling, local-language cards;
- evidence coverage and human-readable sources.

Use images only when they materially help recognition, navigation, or a non-obvious decision. Do not use social screenshots as fixed navigation when live signs or map instructions are more reliable.

### 10. Validate and deliver

- Recheck unstable official facts.
- Run the evidence audit and resolve all critical failures.
- Generate the PDF.
- Run `scripts/validate_pdf.py FILE.pdf --require "term" ...`.
- Run `scripts/render_pdf.py FILE.pdf RENDER_DIR`.
- Inspect the contact sheet and representative pages at full resolution.
- Fix clipping, overflow, sparse accidental pages, unreadable URLs, missing glyphs, broken images, and ambiguous cross-page cards.
- Record page count, file size, SHA-256, research counts, uncovered candidates, and verification timestamp.
- Deliver the PDF and, when requested, the source/evidence package.

## Evidence language

Use precise claims:

- `DIRECT`: the opened source discusses the exact candidate and issue.
- `PARTIAL`: same area/category, but not the exact candidate or scenario.
- `MISMATCH`: search result is about another object; exclude it from counts.
- `PROMOTIONAL`: creator incentive or obvious promotion; keep only as discovery.
- `OFFICIAL`: authoritative hard information, not proof of traveler experience.
- `UNCOVERED`: required evidence not found.

Never write “all items were verified by negative posts” unless the evidence audit passes at the declared threshold.
