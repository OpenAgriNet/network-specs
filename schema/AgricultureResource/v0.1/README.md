# Agriculture Resource

Status: Proposed for review

## Purpose

Agriculture Resource defines the shared agriculture fields used by OAN capability and outcome contracts. It adds broad agriculture classification, structured subject references, language, and geographic applicability to a Beckn Resource.

## Attachment point

The schema attaches to `beckn:Resource.resourceAttributes`. Beckn core owns the Resource `id` and `descriptor`.

## Composition

This pack declares the shared agriculture field set. Other selected contracts reference that field set through `allOf` and apply the combined constraints to one `resourceAttributes` object.

## Fields

| Field | Purpose |
|---|---|
| `subjectAreas` | Classifies the Resource by agriculture subject |
| `subjectScope` | States whether the Resource is general or limited to named agriculture subjects |
| `agricultureSubjects` | Identifies specific governed subjects such as Cotton, Rice, or a commodity; required only when `subjectScope` is `Specific` |
| `languages` | Declares supported or available BCP 47 languages |
| `coverageAreaCodes` | Declares general geographic applicability |

## Non-goals

This pack does not identify a Provider, define a Catalog, carry a protocol envelope, or establish a runtime Domain object.

## Examples

- [General agriculture](examples/general-agriculture.json)
- [Specific crop](examples/specific-crop.json)
