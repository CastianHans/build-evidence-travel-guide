# Social and official research protocol

## Contents

1. Research layers
2. Query design
3. Full-post review
4. Relevance and polarity
5. Independence and source families
6. Candidate evidence gate
7. Conflict handling
8. Research stopping rule

## 1. Research layers

Use four distinct layers:

1. **Primary official:** transport operators, tourism authorities, museums, ticket offices, meteorological agencies, immigration/customs, manufacturers.
2. **Chinese traveler experience:** Xiaohongshu first when relevant, plus Bilibili, Chinese travel communities, blogs, forums, and map reviews. Search both normal traveler wording and explicit 种草/避雷 wording.
3. **International traveler experience:** Reddit and other accessible travel communities.
4. **Local-language evidence:** local blogs, map reviews, forums, news, and institutions using native names.

Record each layer separately. High post count on one platform does not replace missing layers.
For a Chinese-market deliverable, explain cross-layer conflicts in Simplified Chinese and state whether a problem is especially relevant to mainland Chinese travelers.
Retrieve unstable direct official evidence within 45 days of the audit by default.
For a demonstrably stable rule, document the reason and pass a deliberate
`--official-max-age-days` override instead of self-labeling an old page current.

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
- exact name + 支付宝/微信支付/银联/境外卡失败/现金
- exact product + 国内价格/免税价格/退税/中国保修/国行区别
- destination + 中国护照/中国游客 + current operational issue

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
8. Record whether the source was actually opened: `full_post_opened`,
   `full_indexed_text`, `search_snippet`, or `title_only`.

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
- `experience_type`: `first_hand`, `second_hand`, `official`;
- `source_family`: `china_social`, `international_social`, `local_social`,
  `map_review`, `official`, or `independent_blog_news`;
- `access_level`;
- `independence_cluster_id`;
- `promotion`: `no`, `possible`, `yes`;
- separate `commercial_signal` and `attack_signal`;
- `incident_specificity`, `artifact_support`, and any scoped branch/variant;
- `claim`;
- `decision_effect`;
- `url` and retrieval date.

Only direct, identity-checked, full-read records satisfy candidate-level positive
or negative coverage. Count independent content clusters, not raw posts.

## 5. Independence and source families

Put near-identical text, images, talking points, referral codes, coordinated burst
timing, syndicated agency language, the same incident, and the same travel group in
one `independence_cluster_id`. A cluster counts at most once per polarity.

Do not manufacture “platform diversity” with aliases. Normalize every platform
into a source family. Multiple Xiaohongshu accounts remain one source family; an
independent Reddit cluster and a Korean local-platform cluster are distinct
families.

Promotion risk is not positivity and suspected attack risk is not negativity.
Preserve the post, but keep these risk dimensions separate so neither paid praise
nor coordinated criticism controls the decision merely through volume.

Read [reputation-and-bias.md](reputation-and-bias.md) whenever a candidate has
commercial-promotion, scam, coordinated-attack, comment-corroboration, or
nationality-discrimination risk.

## 6. Candidate evidence gate

Before final writing, produce a table with:

- candidate;
- importance;
- positive-direct count;
- negative-direct count;
- current-official count;
- operational-failure count;
- source families represented;
- unresolved conflicts;
- decision;
- reason.

If an important candidate lacks negative evidence:

1. run exact-name negative searches in all accessible layers;
2. inspect relevant comments and map reviews;
3. if still absent, mark `UNCOVERED`;
4. downgrade the recommendation or disclose the gap.

Never convert absence of evidence into evidence of safety or value. A rejected
candidate still needs a structured reason and direct evidence, unless the reason is
explicitly a `USER_PREFERENCE:`.

## 7. Conflict handling

When sources conflict:

- prioritize current official rules for hard facts;
- preserve both sides for subjective value;
- explain scenario differences such as weekday/weekend, clear/cloudy, summer/winter, adult/child interest, or promotion;
- choose based on the user’s actual goals and constraints;
- define an on-site decision gate instead of forcing certainty.

## 8. Research stopping rule

Stop only when:

- all critical and major candidates pass the declared final gate;
- rejected candidates retain their evidence/reason and replacement when relevant;
- each day has a complete route and fallback;
- unstable hard facts have a current source;
- additional posts no longer change decisions.

Post count alone is never a stopping rule.
Passing the evidence gate does not by itself make the PDF final; traceability,
reputation, itinerary arithmetic, PDF validation, and page-by-page visual inspection
must also pass.
