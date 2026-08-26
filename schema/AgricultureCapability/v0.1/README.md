# Agriculture Capability

## Purpose

Defines the common agriculture metadata used to discover an agricultural capability. The governed capability type supplies its interaction semantics and expected outcome type.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. The enclosing Beckn `Catalog.provider` identifies the Provider that offers the capability.

## Composition

`AgricultureCapability` combines the Agriculture Resource and Agriculture Capability field sets with `allOf`. Advisory compositions may add further field sets to the same effective contract.

## Capability types

| Type | Interaction | Outcome |
|---|---|---|
| `KnowledgeRetrievalCapability` | Observe | `KnowledgeResource` |
| `MandiPriceCapability` | Observe | `MandiPriceObservation` |
| `WeatherObservationCapability` | Observe | `WeatherObservation` |

A Provider catalog entry declares `AgricultureCapability` together with one governed capability type. It does not repeat the interaction or outcome schemas.

## Non-goals

This schema does not define endpoints, signing keys, protocol envelopes, or Provider onboarding workflow.

## Examples

- [Knowledge retrieval capability](examples/knowledge-retrieval-capability.json)
- [Mandi price capability](examples/mandi-price-capability.json)
