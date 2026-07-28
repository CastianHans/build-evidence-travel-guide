# Social and official research protocol

## Contents

1. Research layers
2. Query design
3. Full-post review
4. Relevance and polarity
5. Candidate evidence gate
6. Conflict handling
7. Research stopping rule

## 1. Research layers

Use four distinct layers:

1. **Primary official:** transport operators, tourism authorities, museums, ticket offices, meteorological agencies, immigration/customs, manufacturers.
2. **Chinese traveler experience:** Xiaohongshu first when relevant, plus Bilibili, blogs, forums, and map reviews.
3. **International traveler experience:** Reddit and other accessible travel communities.
4. **Local-language evidence:** local blogs, map reviews, forums, news, and institutions using native names.

Record each layer separately. High post count on one platform does not replace missing layers.

## 2. Query design

Create a query matrix for each candidate.

### Positive and duration

- exact name + route/order
- exact name + actual visit time
- exact name + worth it
- exact name + current season
- exact name + toilets/seating/lockers

### Negative

- exact name + 避雷/踩雷/不值得/排队/太热/人多/贵
- exact name + overrated/not worth it/queue/scam/closed
- native name + 별로/비추천/대기/혼잡/바가지/휴무
- transport product + failed/card rejected/cash only/wrong station
- product + irritation/adverse/warranty/region lock

### Connection

- stop A + stop B + route
- exact station + exit + luggage
- hotel name/address + destination

Use the exact local-language name to avoid homonyms and similarly named museums.

## 3. Full-post review

For every counted source:

1. Open the complete post or accessible full indexed text.
2. Confirm exact candidate identity.
3. Confirm the author actually visited or clearly identify second-hand content.
4. Capture date, season, context, and party type.
5. Extract the supported claim and any counterevidence.
6. Read comments for high-impact disputes, operational failures, and current corrections.
7. Mark promotion, copied compilations, or incentive-for-review schemes.

Do not count:

- search snippets without enough context;
- a post about a similarly named attraction;
- “避雷省时间” when the post is purely promotional;
- a general city complaint as a direct candidate complaint;
- a result whose content contradicts its title;
- duplicate reposts as independent evidence.

## 4. Relevance and polarity

Each evidence record needs:

- `relevance`: `direct`, `partial`, `mismatch`;
- `polarity`: `positive`, `negative`, `mixed`, `neutral`, `official`;
- `experience_type`: `first_hand`, `comment`, `indexed_excerpt`, `official`;
- `promotion`: `no`, `possible`, `yes`;
- `claim`;
- `decision_effect`;
- `url` and retrieval date.

Only `direct` records satisfy candidate-level positive or negative counts.

## 5. Candidate evidence gate

Before final writing, produce a table with:

- candidate;
- importance;
- positive-direct count;
- negative-direct count;
- current-official count;
- operational-failure count;
- platforms represented;
- unresolved conflicts;
- decision;
- reason.

If an important candidate lacks negative evidence:

1. run exact-name negative searches in all accessible layers;
2. inspect relevant comments and map reviews;
3. if still absent, mark `UNCOVERED`;
4. downgrade the recommendation or disclose the gap.

Never convert absence of evidence into evidence of safety or value.

## 6. Conflict handling

When sources conflict:

- prioritize current official rules for hard facts;
- preserve both sides for subjective value;
- explain scenario differences such as weekday/weekend, clear/cloudy, summer/winter, adult/child interest, or promotion;
- choose based on the user’s actual goals and constraints;
- define an on-site decision gate instead of forcing certainty.

## 7. Research stopping rule

Stop only when:

- all critical candidates pass the declared gate;
- major uncovered candidates are resolved, rejected, downgraded, or explicitly disclosed;
- each day has a complete route and fallback;
- unstable hard facts have a current source;
- additional posts no longer change decisions.

Post count alone is never a stopping rule.
