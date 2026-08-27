# Agriculture Resource

Status: Proposed for review

## Purpose

Agriculture Resource defines the shared agriculture fields used by OAN domain information contracts. It identifies whether information is obtained on demand or is directly available, then adds broad agriculture categories, optional governed subject references, language, and geographic applicability to a Beckn Resource.

## Attachment point

The schema attaches to `beckn:Resource.resourceAttributes`. Beckn core owns the Resource `id` and `descriptor`.

## Composition

This pack declares the shared agriculture field set. Other selected contracts reference that field set through `allOf` and apply the combined constraints to one `resourceAttributes` object.

## Fields

| Field | Purpose |
|---|---|
| `informationMode` | Uses `OnDemand` when a Provider invocation is required and `Direct` when the Resource contains or directly references specific information |
| `subjectCategories` | Classifies the Resource using broad categories such as crop, weather, or market |
| `agricultureSubjects` | Optionally identifies governed subjects such as Cotton, Rice, or a commodity; absence means broad applicability within the declared categories |
| `languages` | Declares supported or available BCP 47 languages |
| `coverageAreas` | Declares geographic applicability using an administrative area reference or a Beckn GeoJSON geometry |

An administrative area reference carries a code system such as ISO 3166, LGD, or PIN and the corresponding code. A GeoJSON geometry carries a Point, Polygon, MultiPolygon, or another geometry supported by Beckn `GeoJSONGeometry`. Use the reference when a governed area code is sufficient. Use geometry when the boundary or service area is coordinate-defined.

## Non-goals

This pack does not identify a Provider, define a Catalog, carry a protocol envelope, or define how fresh the information is. Freshness is expressed by the selected domain pack through timestamps and validity.

## Examples

- [General agriculture](examples/general-agriculture.json)
- [Specific crop](examples/specific-crop.json)
