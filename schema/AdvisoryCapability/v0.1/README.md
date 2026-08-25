# Advisory Capability

## Purpose

Defines the advisory fields added to an agricultural capability that produces advice.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource` listed in a Provider catalog.

## Composition

`AdvisoryCapability` combines the Agriculture Resource, Agriculture Capability, and Advisory Capability field sets with `allOf`. The composed contract requires `Advise` among its interaction types.

## Fields

| Field | Meaning |
|---|---|
| `advisoryType` | Advisory classification such as crop, weather, market, or scheme |
| `topics` | Governed or Provider-declared topics covered by the capability |

## Non-goals

This schema does not prescribe a reasoning method, model, prompt, or response transport.

## Examples

- [General crop advisory](examples/general-crop-advisory.json)
- [Specific livestock advisory](examples/specific-livestock-advisory.json)
