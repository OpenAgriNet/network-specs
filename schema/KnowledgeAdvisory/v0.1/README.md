# Knowledge Advisory

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

Defines actionable agricultural guidance based on knowledge that a Provider can supply on demand or make directly available.

Use `KnowledgeResource` for reusable knowledge content. Use this pack when the Resource communicates a recommendation or action. Use Weather Advisory when weather evidence is central to the guidance. Market Intelligence carries trends, forecasts, and opportunities without prescribing an action.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. Beckn owns the Resource identifier and descriptor.

## Composition

`KnowledgeAdvisory` combines the Agriculture Resource and Knowledge Advisory field sets with `allOf`.

## Fields

"Required when" describes a complete OAN Resource. It does not make the field mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@type` | Always | Identifies the Resource as `openagrinet:KnowledgeAdvisory` |
| `informationMode` | Always | `OnDemand` requires a Provider invocation; `Direct` contains specific guidance |
| `subjectCategories` | Optional | Broad agriculture classification inherited from Agriculture Resource |
| `agricultureSubjects` | Optional | Governed subjects such as a crop, livestock species, pest, or scheme |
| `languages` | `OnDemand`; optional in `Direct` | Supported response languages; each Direct recommendation declares its own language |
| `coverageAreas` | Optional | Geographic applicability or supported coverage |
| `topics` | Both modes | Advisory topics used for discovery and matching |
| `issuedAt` | `Direct` | Time at which the Provider issued the advisory |
| `validity` | Optional in `Direct` | Period during which the advisory applies |
| `recommendations` | `Direct` | Human-readable guidance with optional action lists and Provider-assigned priority |
| `supportingResourceIds` | Optional in `Direct` | Beckn Resource identifiers for supporting Knowledge Resources |
| `rationale` | Optional in `Direct` | Explanation for the recommendation |
| `source` | `Direct` | Provider or authoritative source that issued the advisory |

## Non-goals

This pack does not define recommendation-generation internals, weather measurements, market prices, or protocol request and response envelopes.

## Examples

- [On-demand crop advisory](examples/on-demand-crop-advisory.json)
- [Direct crop advisory](examples/direct-crop-advisory.json)
