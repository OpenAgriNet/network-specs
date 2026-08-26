# Advisory Capability

## Purpose

Defines the advisory fields added to an agricultural capability. The profile fixes the interaction type as `Advise`; Provider entries do not repeat it.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource` listed in a Provider catalog.

## Composition

`AdvisoryCapability` combines the Agriculture Resource, Agriculture Capability, and Advisory Capability field sets with `allOf`.

## Fields

| Field | Meaning |
|---|---|
| `topics` | Governed or Provider-declared topics covered by the capability |

## Non-goals

This schema does not prescribe a reasoning method, model, prompt, or response transport.

## Examples

- [General crop advisory](examples/general-crop-advisory.json)
- [Specific livestock advisory](examples/specific-livestock-advisory.json)
