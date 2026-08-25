# Knowledge Resource

## Purpose

Defines a reusable, versioned unit of agricultural knowledge.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. Beckn owns the Resource identifier and descriptor.

## Composition

`KnowledgeResource` combines the Agriculture Resource and Knowledge Resource field sets with `allOf`.

## Fields

| Field | Meaning |
|---|---|
| `resourceType` | Presentation-neutral knowledge classification |
| `subjectScope` | Declares whether the knowledge is general or specific |
| `agricultureSubjects` | Governed agriculture subjects required only for specific knowledge |
| `version` | Semantic version of the governed knowledge |
| `lifecycleStatus` | Publication lifecycle of the knowledge version |
| `content` | One or more content representations |
| `validity` | Optional applicability period |
| `provenance` | Source, publication, and review evidence |
| `supersedes` | Identifier of a replaced Resource version |

## Non-goals

This schema does not define search requests, retrieval responses, Registry admission, or content-generation internals.

## Examples

- [Published crop guide](examples/published-crop-guide.json)
- [General multilingual FAQ](examples/general-multilingual-faq.json)
- [General agriculture guide](examples/general-agriculture-guide.json)
- [Weather advisory output](examples/weather-advisory-output.json)
