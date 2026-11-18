---
layout: default
title: Agricultural applicability review
---
# Agricultural applicability review

This proposal is on bv-features, based on schema-packs-api-driven. Nothing here has been merged to main. Review [the API separation](../api-specs/) separately from these agricultural additions.

The shared AgricultureResource field set now offers optional applicability. Existing required fields are unchanged. KnowledgeAdvisory and WeatherAdvisory also allow applicability on individual recommendations. KnowledgeResource receives resource-level applicability through its existing composition. Other domain packs can use the shared field when relevant; it is not mandatory for weather observations, facilities or prices.

## Fields and examples

| Field | Required | Meaning | Example |
|---|---|---|---|
| applicability | No | Alternative condition sets | Cotton in Kharif OR wheat in Rabi |
| subjectIds | No | Subjects within one condition | A governed cotton URI |
| seasons | No | Regional named seasons | Kharif, Rabi, Navarai or Samba with a codeSystem |
| growthStages | No | Observed developmental stage | A provider's versioned rice flowering code |
| relativeTiming | No | Inclusive age window anchored to an event | Sowing, fromDays 20, toDays 30 |
| relativeTiming.event | When timing is supplied | Event used as day zero | Transplanting, not sowing, for DAT |
| fromDays / toDays | At least one | Inclusive non-negative bounds | fromDays 20 means day 20 or later |
| establishmentMethods | No | Production establishment | DirectSeeded or Transplanted |
| waterRegimes | No | Water management | Rainfed or Irrigated |
| extensions | No | Provider-owned restrictions | A soil-class condition keyed by its vocabulary URI |

### Event values

| Value | Meaning | Example |
|---|---|---|
| Sowing | Seed placed for the identified crop cycle | 20 to 30 days after sowing |
| Transplanting | Seedlings moved to their production site | 7 to 10 days after transplanting |
| Emergence | Observed seedling emergence | First week after emergence |
| Pruning | Identified pruning operation | 14 to 21 days after pruning |
| Harvest | Identified harvest operation | First three days after harvest |

The example windows demonstrate data shapes, not verified agronomic recommendations. Event age is calculated from local calendar dates, with day zero on the event date. Do not calculate an age until the crop cycle, event occurrence and date convention are known. Negative offsets are not supported in this proposal. Schema validation checks types and presence; semantic validation must reject reversed bounds.

### Coded values

Seasons and stages require codeSystem and code. A display label is optional. The system URI must identify the vocabulary version and, for stage keys, the relevant crop. A season name does not imply universal months. A growth stage cannot be inferred from days after sowing alone. Example stage codes are synthetic; they are not represented as official BBCH values.

## Filter before embedding ranking

For a crop sown 25 days ago, evaluate within one applicability entry:

```text
relativeTiming.event = Sowing
AND (fromDays is absent OR fromDays <= 25)
AND (toDays is absent OR toDays >= 25)
```

Filter paths are declared in the profiles, but this branch does not modify or test the discovery engine. Conditions in one entry are AND; entries are OR. Values inside one list are OR. Keep nested correlation in the search index. Never flatten cotton/Kharif and wheat/Rabi into independent lists that admit cotton/Rabi.

Store conditions on the indexed passage or recommendation, not indiscriminately on every chunk of a large source document. Resource conditions and recommendation conditions must both match. Embeddings rank semantic relevance after structured filtering; they do not enforce numeric intervals.

Missing facts produce unknown. An unknown extension produces unknown. No applicability supplied means no machine-readable restriction was supplied, not proof of universal applicability. Consumers must agree how to display or resolve these unknowns before automated recommendation filtering is enabled.

## Complete examples

The [KnowledgeAdvisory page](KnowledgeAdvisory/v0.1/) expands complete attributes objects for seven new scenarios:

- Cotton with a season and sowing-age interval.
- Rice with transplanting age and establishment method.
- Mango with a pruning-relative interval.
- Two correlated crop/season alternatives.
- Growth stage combined with irrigation.
- A provider-specific soil restriction that an unaware consumer cannot evaluate.
- Resource-wide crop scope narrowed by recommendation-specific timing.

Existing examples without applicability remain available for comparison. They do not become automatically classified as general advice.

## Extensibility and compatibility

Provider-owned extension keys must be absolute HTTP(S) vocabulary IRIs. Their values are preserved as JSON. Agree the provider's schema and evaluator outside this generic container. Do not dynamically fetch arbitrary schema URLs or index all extension values. Unknown restrictions must not disappear from a generated answer.

Existing OAN fields and canonical types remain unchanged. New fields are optional. Recommendation objects were previously closed, so an older validator will reject recommendation-level applicability; consumers must explicitly adopt the new version before it is sent. This preview retains v0.1 paths for comparison only. A production version decision is still required.

## Evidence and checks

The design distinguishes crop age from regional season and developmental stage using [TNAU paddy guidance](https://agritech.tnau.ac.in/expert_system/paddy/faqs.html), [TNAU regional seasons](https://agritech.tnau.ac.in/expert_system/paddy/season.html), [IMD's KALP manual](https://mausam.imd.gov.in/imd_latest/contents/agromet/kalp/kalp.pdf), and [EPPO's BBCH explanation](https://gd.eppo.int/reporting/article-6219). These sources support the distinctions, not the synthetic example windows.

Run `uv run --with pyyaml --with jsonschema python scripts/check-applicability.py`. It checks complete new examples, malformed conditions, inclusive boundaries, wrong anchors, unknown restrictions and correlated alternatives. It is a reference matcher for review, not an implementation of a vector database filter.

Consumer sign-off is needed on vocabulary ownership, missing-fact behaviour, nested filtering, extension handling, indexing passage metadata and the production version.
