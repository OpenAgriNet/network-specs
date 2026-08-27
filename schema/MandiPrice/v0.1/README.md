# Mandi Price

## Purpose

Defines mandi prices that a Provider can supply on demand or make directly available.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. An `OnDemand` Resource describes supported commodities, price fields, coverage, and history. A `Direct` Resource carries specific market prices.

## Composition

`MandiPrice` combines the Agriculture Resource and Mandi Price field sets with `allOf`. It reuses the Beckn `Descriptor` for commodity identity.

## Fields

| Field | Meaning |
|---|---|
| `informationMode` | `OnDemand` requires a Provider invocation; `Direct` contains specific prices |
| `supportedCommodities` | Commodities available on demand |
| `supportedPriceFields` | Price values available on demand |
| `historicalDataAvailable`, `historyPeriod` | Availability and maximum period of historical data |
| `updateFrequency` | Expected refresh interval for current prices |
| `source` | Authoritative upstream source |
| `commodity` | Beckn descriptor for the commodity |
| `commodityGroup`, `grade`, `variety` | Source classifications |
| `market` | Market identity and optional location |
| `arrivalDate` | Date to which arrivals and prices apply |
| `prices` | Minimum, maximum, and modal prices |
| `generatedAt` | Normalization time |
| `validity` | Optional applicability period for a current snapshot |

## Non-goals

This schema does not define a price-query protocol request. An `OnDemand` Resource declares the searchable scope; the Beckn Intent carries the requested values.

## Examples

- [Onion price at Lasalgaon](examples/onion-lasalgaon.json)
- [Cotton minimum-price observation](examples/cotton-minimum.json)
- [Live mandi price observation](examples/live-mandi-price-observation.json)
- [On-demand mandi prices](examples/on-demand-mandi-prices.json)
