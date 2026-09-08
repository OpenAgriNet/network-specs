# Market Intelligence

<nav class="artifact-links" aria-label="Schema artifacts">
  <a href="../../">All schemas</a>
  <a href="attributes.yaml">attributes.yaml</a>
  <a href="context.jsonld">context.jsonld</a>
  <a href="vocab.jsonld">vocab.jsonld</a>
  <a href="profile.json">profile.json</a>
  <a href="renderer.json">renderer.json</a>
  <a href="#examples">Examples</a>
</nav>

## Purpose

Defines price trends, demand forecasts, and nearby market opportunities that a Provider can supply on demand or make directly available.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. An `OnDemand` Resource describes supported commodities, insight types, languages, history, forecast horizon, and coverage. A `Direct` Resource carries one or more market insights.

## Composition

`MarketIntelligence` combines the Agriculture Resource and Market Intelligence field sets with `allOf`.

## Fields

"Required when" describes a complete OAN Resource. It does not make the field mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@type` | Always | Identifies the Resource as `openagrinet:MarketIntelligence` |
| `informationMode` | Always | `OnDemand` requires a Provider invocation; `Direct` contains specific market intelligence |
| `subjectCategories` | Optional | Broad agriculture classification inherited from Agriculture Resource |
| `agricultureSubjects` | Optional | Governed commodity or market references when available |
| `languages` | `OnDemand`; optional in `Direct` | Supported or available BCP 47 languages |
| `coverageAreas` | Optional | Geographic applicability or supported market coverage |
| `supportedCommodities` | `OnDemand` | Commodities for which intelligence is available on demand |
| `supportedInsightTypes` | `OnDemand` | Supported categories: price trend, demand forecast, and market opportunity |
| `historyPeriod` | Optional | Maximum historical period available for analysis |
| `forecastHorizon` | Optional | Maximum demand-forecast horizon |
| `commodity` | `Direct` | Commodity to which the intelligence applies |
| `generatedAt` | `Direct` | Time at which the intelligence Resource was produced |
| `validity` | Optional in `Direct` | Applicability period |
| `insights` | `Direct` | Provider-supplied summaries with optional market, period, indicator, distance, and supporting Resources |
| `source` | `Direct` | Provider or authoritative source that generated the intelligence |

## Boundaries

`MandiPrice` carries individual market-price facts. `MarketIntelligence` carries trends, forecasts, and opportunities derived from market information. It does not prescribe a sell, hold, or market-selection action and does not define market transactions.

The schema does not govern the calculation method, demand scale, or indicator vocabulary. Providers may publish those definitions separately while using `indicator.indicatorName`, `indicator.indicatorValue`, and `indicator.indicatorUnit` for portable results. Price trends and demand forecasts require an explicit `period`.

## Examples

- [On-demand market intelligence](examples/on-demand-market-intelligence.json)
- [Direct cotton market intelligence](examples/direct-cotton-market-intelligence.json)
