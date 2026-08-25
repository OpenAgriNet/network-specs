# Mandi Price Observation

## Purpose

Defines a normalized commodity price observation for a mandi and arrival date.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource` produced by a live Provider invocation.

## Composition

`MandiPriceObservation` combines the Agriculture Resource and Mandi Price Observation field sets with `allOf`. It reuses the Beckn `Descriptor` for commodity identity.

## Fields

| Field | Meaning |
|---|---|
| `source` | Authoritative upstream source |
| `commodity` | Beckn descriptor for the commodity |
| `commodityGroup`, `grade`, `variety` | Source classifications |
| `market` | Market identity and optional location |
| `arrivalDate` | Date to which arrivals and prices apply |
| `prices` | Minimum, maximum, and modal prices |
| `generatedAt` | Normalization time |

## Non-goals

This schema does not define a Provider's general coverage or a price-query request.

## Examples

- [Onion price at Lasalgaon](examples/onion-lasalgaon.json)
- [Cotton minimum-price observation](examples/cotton-minimum.json)
- [Live mandi price observation](examples/live-mandi-price-observation.json)
