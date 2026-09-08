# Agriculture Facility

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

Defines static information about agricultural service facilities and the facility types a Provider can return on demand.

The initial governed types are Custom Hiring Centre, Krishi Vigyan Kendra, Warehouse, and Soil Testing Facility. `SoilTestingFacility` covers a source described as a Soil Health Centre or Soil Testing Laboratory without asserting that the two administrative labels are always identical.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. Beckn owns the Resource identifier and descriptor. An `OnDemand` Resource describes the facility types available through Provider invocation. A `Direct` Resource describes one facility.

## Composition

`AgricultureFacility` combines the Agriculture Resource and Agriculture Facility field sets with `allOf`.

## Fields

"Required when" describes a complete OAN Resource. It does not make the field mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@type` | Always | Identifies the Resource as `openagrinet:AgricultureFacility` |
| `informationMode` | Always | `OnDemand` requires Provider invocation; `Direct` describes a specific facility |
| `subjectCategories` | Optional | Broad agriculture classification inherited from Agriculture Resource |
| `agricultureSubjects` | Optional | Governed crop, commodity, scheme, or other subject references when relevant |
| `languages` | Optional | Languages supported by or present in the facility information |
| `coverageAreas` | Optional | Geographic service or discovery coverage |
| `supportedFacilityTypes` | `OnDemand` | Facility categories available on demand |
| `facilityType` | `Direct` | Governed category of a specific facility |
| `location`, `address` | `Direct`: at least one | Verified Beckn Location, or a non-empty Beckn Address when verified geometry is unavailable |
| `services` | Optional in `Direct` | Public services offered at the facility |
| `capacity` | Optional in `Direct` | Published capacity and unit |
| `publicContact` | Optional in `Direct` | Public organizational contact approved for catalog publication |
| `website` | Optional in `Direct` | Public facility or service website |
| `source` | `Direct` | Authoritative source of the facility record |
| `lastUpdatedAt` | Optional in `Direct` | Time at which the Provider last updated or verified the facility record |

## Mapping rules

The search origin is not the facility location. An adapter must not copy a request coordinate into `location` unless the Provider confirms that the returned coordinate belongs to the facility.

Query-relative distance, ranking, and price are not intrinsic facility attributes. Distance belongs in result metadata. Price and booking terms belong in the applicable Beckn offer or transaction contract.

## Examples

- [On-demand facility discovery](examples/on-demand-facility-discovery.json)
- [Custom Hiring Centre](examples/custom-hiring-centre.json)
- [Krishi Vigyan Kendra](examples/krishi-vigyan-kendra.json)
- [Warehouse](examples/warehouse.json)
- [Soil Testing Facility](examples/soil-testing-facility.json)
