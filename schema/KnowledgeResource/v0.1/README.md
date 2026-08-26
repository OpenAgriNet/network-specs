# Knowledge Resource

## Purpose

Defines a reusable, versioned unit of agricultural knowledge and one or more representations of that knowledge.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. Beckn owns the Resource identifier and descriptor.

## Composition

`KnowledgeResource` combines the Agriculture Resource and Knowledge Resource field sets with `allOf`.

## Fields

| Field | Meaning |
|---|---|
| `knowledgeType` | Semantic kind such as guide or FAQ, independent of file or media format |
| `agricultureSubjects` | Optional governed subjects such as a crop, livestock species, pest, or scheme |
| `version` | Semantic version of the governed knowledge |
| `lifecycleStatus` | Publication lifecycle of the knowledge version |
| `content` | One or more representations, each carrying either `contentUri` or `inlineContent` and a media type |
| `validity` | Optional applicability period |
| `provenance` | Source, publication, and review evidence |
| `supersedes` | Identifier of a replaced Resource version |

## Non-goals

This schema does not define search requests, retrieval responses, Registry admission, or content-generation internals.

`contentUri` points to a Provider-hosted representation. It does not require a public download. `inlineContent` carries a short answer or representation directly in the Resource. A Provider that keeps its corpus private and answers live questions publishes a retrieval capability rather than cataloging every source document.

## Examples

- [Published crop guide](examples/published-crop-guide.json)
- [General multilingual FAQ](examples/general-multilingual-faq.json)
- [General agriculture guide](examples/general-agriculture-guide.json)
- [Weather advisory output](examples/weather-advisory-output.json)
