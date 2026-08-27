# Knowledge Resource

## Purpose

Defines agricultural knowledge that a Provider can supply on demand or make directly available.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. Beckn owns the Resource identifier and descriptor.

## Composition

`KnowledgeResource` combines the Agriculture Resource and Knowledge Resource field sets with `allOf`.

## Fields

| Field | Meaning |
|---|---|
| `informationMode` | `OnDemand` requires a Provider invocation; `Direct` contains or directly references specific knowledge |
| `topics` | Knowledge topics used for discovery and matching |
| `supportedKnowledgeTypes` | Semantic knowledge kinds available on demand |
| `supportedMediaTypes` | Media formats available on demand |
| `knowledgeType` | Semantic kind such as guide or FAQ, independent of file or media format |
| `agricultureSubjects` | Optional governed subjects such as a crop, livestock species, pest, or scheme |
| `version` | Semantic version of the governed knowledge |
| `lifecycleStatus` | Publication lifecycle of the knowledge version |
| `content` | One or more representations, each carrying either `contentUri` or `inlineContent` and a media type |
| `validity` | Optional applicability period |
| `provenance` | Source, publication, and review evidence |
| `supersedes` | Identifier of a replaced Resource version |

## Non-goals

This schema does not define search requests, Registry admission, or content-generation internals.

`contentUri` points to a Provider-hosted completed representation. It does not require a public download. `inlineContent` carries an answer or representation directly in the Resource. A Provider that keeps its corpus private and answers questions publishes an `OnDemand` Knowledge Resource rather than cataloging every source document.

## Examples

- [Published crop guide](examples/published-crop-guide.json)
- [General multilingual FAQ](examples/general-multilingual-faq.json)
- [General agriculture guide](examples/general-agriculture-guide.json)
- [On-demand agriculture knowledge](examples/on-demand-agriculture-knowledge.json)
