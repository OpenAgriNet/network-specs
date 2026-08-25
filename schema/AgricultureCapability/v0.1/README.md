# Agriculture Capability

## Purpose

Defines the common metadata used to discover and invoke an agricultural capability.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. The enclosing Beckn `Catalog.provider` identifies the Provider that offers the capability.

## Composition

`AgricultureCapability` combines the Agriculture Resource and Agriculture Capability field sets with `allOf`. Advisory compositions may add further field sets to the same effective contract.

## Fields

| Field | Meaning |
|---|---|
| `interactionTypes` | Supported business interactions: `Advise`, `Observe`, or `Act` |

The capability type and its governed profile define the invocation input and outcome Resource types. Provider catalog entries do not repeat those schemas.

The initial governed profile types are `KnowledgeRetrievalCapability`, `MandiPriceCapability`, and `WeatherObservationCapability`. A Resource declares `AgricultureCapability` together with the applicable profile type.

## Non-goals

This schema does not define endpoints, signing keys, protocol envelopes, or Provider onboarding workflow.

## Examples

- [Knowledge retrieval capability](examples/knowledge-retrieval-capability.json)
- [Mandi price capability](examples/mandi-price-capability.json)
