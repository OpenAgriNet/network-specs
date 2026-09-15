# Knowledge Resource

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

Defines agricultural knowledge that a Provider can supply on demand or make directly available.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. Beckn owns the Resource identifier and descriptor.

## Composition

`KnowledgeResource` combines the Agriculture Resource and Knowledge Resource field sets with `allOf`.

## Fields

"Required when" describes a complete OAN Resource. It does not make the field mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@type` | Always | Identifies the Resource as `openagrinet:KnowledgeResource` |
| `informationMode` | Always | `OnDemand` requires a Provider invocation; `Direct` contains or directly references specific knowledge |
| `subjectCategories` | Always | Broad discovery classification required by the composed Agriculture Resource field set |
| `agricultureSubjects` | Optional | Governed subjects such as a crop, livestock species, pest, or scheme |
| `languages` | Both modes | Supported or available BCP 47 languages |
| `coverageAreas` | Optional | Geographic applicability or supported coverage |
| `topics` | Both modes | Knowledge topics used for discovery and matching |
| `supportedKnowledgeTypes` | `OnDemand` | Semantic knowledge kinds available on demand |
| `supportedMediaTypes` | Optional | Media formats the Provider supports |
| `knowledgeType` | `Direct` | Semantic kind such as guide or FAQ, independent of file or media format |
| `version` | `Direct` | Semantic version of the governed knowledge |
| `lifecycleStatus` | `Direct` | Publication lifecycle of the knowledge version |
| `content` | `Direct` | One or more representations, each carrying either `contentUri` or `inlineContent`, a media type, and an optional structured integrity digest |
| `validity` | Optional in `Direct` | Applicability period |
| `provenance` | `Direct` | Source and publication evidence; review evidence is optional |
| `supersedes` | Optional in `Direct` | Identifier of a replaced Resource version |

## Non-goals

This schema does not define search requests, Registry admission, or content-generation internals.

`contentUri` points to a Provider-hosted completed representation. It does not require a public download. `inlineContent` carries an answer or representation directly in the Resource. A Provider that keeps its corpus private and answers questions publishes an `OnDemand` Knowledge Resource rather than cataloging every source document.

An integrity digest contains `algorithm` and `digestValue`. Review evidence supplies `lastReviewedAt` and `reviewedBy` together.

## Examples

- [Published crop guide](examples/published-crop-guide.json)
- [General multilingual FAQ](examples/general-multilingual-faq.json)
- [General agriculture guide](examples/general-agriculture-guide.json)
- [On-demand agriculture knowledge](examples/on-demand-agriculture-knowledge.json)
