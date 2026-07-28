# Social reputation, comments, and discrimination

## Contents

1. What the score may and may not mean
2. Independence clustering
3. Promotion and attack risk
4. Comment evidence
5. Scam allegations
6. Discrimination classes and gate
7. Decision language

## 1. What the score may and may not mean

Treat platform evidence as a non-representative independent online sample. Never
infer the share of real customers who approve, complain, or experienced
discrimination. Report deduplicated narrative clusters, source families, time
windows, uncertainty, and counterevidence.

Use `scripts/audit_reputation.py PROJECT_DIR` for candidates marked
`reputation_required=yes`. Its weights are a transparent convergence aid, not a
statistical estimate of customer prevalence.

## 2. Independence clustering

Cluster records that share any likely production origin:

- identical or near-identical text, images, sequence, talking points, or typos;
- the same referral/coupon code or agency contact;
- an implausibly synchronized burst with the same framing;
- reposts, scraped compilations, translations, or media coverage of one incident;
- comments from the same incident, booking, travel group, household, or creator.

Count a cluster at most once. Keep cross-platform copies in the same cluster.
Record why clustering was applied in `notes`. Lack of visible account history is
unknown, not proof of authenticity or fakery.

## 3. Promotion and attack risk

Score polarity separately from manipulation risk.

For positive records, inspect:

- explicit sponsorship, free product/service, affiliate link, coupon, group-buy,
  referral or agency contact;
- undisclosed incentive clues, repeated sales language, copied imagery, and burst
  timing;
- normal account history when visible, without penalizing a private or new account
  by default.

For negative records, inspect:

- concrete first-hand incident details, receipt/menu/order/time evidence, and
  whether the business/branch identity matches;
- copied accusations, pile-ons without new facts, competitor-style calls to
  action, and coordinated burst patterns;
- substantive corrections, neutral operational explanations, and current
  counterevidence.

Use `commercial_signal` and `attack_signal` independently. Do not delete a risky
record; retain it with reduced decision weight and explain the signal.

## 4. Comment evidence

Put comments in `research/comments.csv`, linked by `parent_evidence_id`.

- `first_hand_new_fact`: a new, independently described incident; lower weight than
  a full post and requires `new_fact=yes`.
- `specific_corroboration`: adds a concrete matching detail but may not be
  independent.
- `bare_agreement`: “同意”, emoji, or unspecific approval; weak sentiment only and
  capped within the parent cluster.
- `refutation` or `correction`: retain substantive contradictions and current
  operational corrections.
- `merchant_response`: retain the reply but do not treat it as automatic
  exoneration.

Same-incident comments never become independent incidents. Suspected coordinated
comments share one cluster. Disclose sorting method, whether replies were expanded,
login/rate-limit limits, moderation/deletion risk, and sampling limitations in
`research/comment-limitations.md`.

## 5. Scam allegations

The words “骗局”, “诈骗”, “scam”, or “rip-off” are allegations, not evidence.
Require a concrete operational pattern such as:

- bait-and-switch;
- undisclosed mandatory charge;
- ordered item and billed item mismatch;
- different displayed and charged price;
- promised refund/service not delivered;
- counterfeit or materially misrepresented product.

Preserve the allegation but do not let it trigger an avoid decision when incident
specificity is vague and no independent evidence converges.

## 6. Discrimination classes and gate

Classify only the scoped branch and incident:

- `D0`: ordinary rudeness, cold service, or subjective dislike. Exclude from the
  discrimination gate.
- `D1`: ambiguous differential treatment without a matched comparison. Monitor.
- `D2`: specific nationality-linked differential treatment, such as a different
  price, refusal, or insult while comparable customers were treated differently.
  Require `matched_comparison=yes`.
- `D3`: explicit, current primary artifact such as signage, recording, written
  policy, or official finding. Require `artifact_support=primary_record`.

Before assigning D2/D3, test neutral explanations: reservation status, queue,
language, group size, dress code, sold-out item, menu/package, time, and branch.

Conservatively reassess/avoid when either:

1. a current D3 primary artifact is verified; or
2. at least three independent D2 clusters converge across at least two source
   families and two time windows.

Do not make a legal or universal claim about the business unless an authoritative
finding supports it.

## 7. Decision language

Prefer scoped wording:

> 多起独立一手报告描述疑似针对中国游客的差别待遇，因此保守建议避开该分店；此结论限定于所列分店与时间窗口，并非法律认定。

For weaker evidence, say it is a D1/D2 signal under monitoring and show the
alternative explanation. Record favorable counterevidence and the business reply
next to the concern.
