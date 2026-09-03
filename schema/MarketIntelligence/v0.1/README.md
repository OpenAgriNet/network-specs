# Market Intelligence

Status: Proposed for review

## Purpose

Defines price trends, demand forecasts, and nearby market opportunities that a Provider can supply on demand or make directly available.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. An `OnDemand` Resource describes supported commodities, insight types, languages, history, forecast horizon, and coverage. A `Direct` Resource carries one or more market insights.

## Composition

`MarketIntelligence` combines the Agriculture Resource and Market Intelligence field sets with `allOf`.

## Fields

| Field | Meaning |
|---|---|
| `informationMode` | `OnDemand` requires a Provider invocation; `Direct` contains specific market intelligence |
| `supportedCommodities` | Commodities for which intelligence is available on demand |
| `supportedInsightTypes` | Supported categories: price trend, demand forecast, and market opportunity |
| `historyPeriod` | Maximum historical period available for analysis |
| `forecastHorizon` | Maximum demand-forecast horizon |
| `commodity` | Commodity to which direct intelligence applies |
| `generatedAt`, `validity` | Generation time and optional applicability period |
| `insights` | Provider-supplied summaries with optional market, period, indicator, distance, and supporting Resources |
| `source` | Provider or authoritative source that generated the intelligence |

## Boundaries

`MandiPrice` carries individual market-price facts. `MarketIntelligence` carries trends, forecasts, and opportunities derived from market information. It does not prescribe a sell, hold, or market-selection action and does not define market transactions.

The schema does not govern the calculation method, demand scale, or indicator vocabulary. Providers may publish those definitions separately while using `indicator.indicatorName`, `indicator.indicatorValue`, and `indicator.indicatorUnit` for portable results. Price trends and demand forecasts require an explicit `period`.

## Examples

- [On-demand market intelligence](examples/on-demand-market-intelligence.json)
- [Direct cotton market intelligence](examples/direct-cotton-market-intelligence.json)
