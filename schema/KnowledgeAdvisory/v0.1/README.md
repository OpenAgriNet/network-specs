# Knowledge Advisory

## Purpose

Defines actionable agricultural guidance based on knowledge that a Provider can supply on demand or make directly available.

Use `KnowledgeResource` for reusable knowledge content. Use this pack when the Resource communicates a recommendation or action. Use Weather Advisory when weather evidence is central to the guidance. Market Intelligence carries trends, forecasts, and opportunities without prescribing an action.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. Beckn owns the Resource identifier and descriptor.

## Composition

`KnowledgeAdvisory` combines the Agriculture Resource and Knowledge Advisory field sets with `allOf`.

## Fields

| Field | Meaning |
|---|---|
| `informationMode` | `OnDemand` requires a Provider invocation; `Direct` contains specific guidance |
| `topics` | Advisory topics used for discovery and matching |
| `agricultureSubjects` | Optional governed subjects such as a crop, livestock species, pest, or scheme |
| `issuedAt` | Time at which the Provider issued the advisory |
| `validity` | Optional period during which the advisory applies |
| `recommendations` | Human-readable guidance with optional action lists and Provider-assigned priority |
| `supportingResourceIds` | Optional Beckn Resource identifiers for supporting Knowledge Resources |
| `rationale` | Optional explanation for the recommendation |
| `source` | Provider or authoritative source that issued the advisory |

## Non-goals

This pack does not define recommendation-generation internals, weather measurements, market prices, or protocol request and response envelopes.

## Examples

- [On-demand crop advisory](examples/on-demand-crop-advisory.json)
- [Direct crop advisory](examples/direct-crop-advisory.json)
