# Mandi Price

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

Defines mandi prices that a Provider can supply on demand or make directly available.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. An `OnDemand` Resource describes supported commodities, price fields, coverage, and history. A `Direct` Resource carries specific market prices.

## Composition

`MandiPrice` combines the Agriculture Resource and Mandi Price field sets with `allOf`. It reuses the Beckn `Descriptor` for commodity identity.

## Fields

"Required when" describes a complete OAN Resource. It does not make the field mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@type` | Always | Identifies the Resource as `openagrinet:MandiPrice` |
| `informationMode` | Always | `OnDemand` requires a Provider invocation; `Direct` contains specific prices |
| `subjectCategories` | Always | Required by the composed Agriculture Resource field set; this pack additionally requires `Market` |
| `agricultureSubjects` | Optional | Governed commodity or market references when available |
| `languages` | Optional | Languages used by textual descriptors |
| `coverageAreas` | Optional | Geographic applicability or supported market coverage |
| `supportedCommodities` | `OnDemand` | Commodities available on demand |
| `supportedPriceFields` | `OnDemand` | Price values available on demand |
| `historicalDataAvailable`, `historyPeriod` | Optional | Availability and maximum period of historical data |
| `updateFrequency` | Optional | Expected refresh interval for current prices |
| `source` | `Direct` | Authoritative upstream source |
| `commodity` | `Direct` | Beckn descriptor for the commodity |
| `commodityGroup`, `grade`, `variety` | Optional in `Direct` | Source classifications |
| `market` | `Direct` | Market identity and optional Beckn Location |
| `arrivalDate` | `Direct` | Date to which arrivals and prices apply |
| `prices` | `Direct` | Currency, unit, and at least one of minimum, maximum, or modal price |
| `generatedAt` | `Direct` | Time at which the normalized Resource was produced |
| `validity` | Optional in `Direct` | Applicability period for a current snapshot |

## Non-goals

This schema does not define a price-query protocol request. An `OnDemand` Resource declares the searchable scope; the Beckn Intent carries the requested values.

Conformance checks verify price ordering when multiple values are present: minimum must not exceed modal or maximum, and modal must not exceed maximum.

## Examples

- [Onion price at Lasalgaon](examples/onion-lasalgaon.json)
- [Cotton minimum-price observation](examples/cotton-minimum.json)
- [Live mandi price observation](examples/live-mandi-price-observation.json)
- [On-demand mandi prices](examples/on-demand-mandi-prices.json)
