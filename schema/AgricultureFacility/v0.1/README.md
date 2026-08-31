# Agriculture Facility

## Purpose

Defines static information about agricultural service facilities and the facility types a Provider can return on demand.

The initial governed types are Custom Hiring Centre, Krishi Vigyan Kendra, Warehouse, and Soil Testing Facility. `SoilTestingFacility` covers a source described as a Soil Health Centre or Soil Testing Laboratory without asserting that the two administrative labels are always identical.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. Beckn owns the Resource identifier and descriptor. An `OnDemand` Resource describes the facility types available through Provider invocation. A `Direct` Resource describes one facility.

## Composition

`AgricultureFacility` combines the Agriculture Resource and Agriculture Facility field sets with `allOf`.

## Fields

| Field | Meaning |
|---|---|
| `informationMode` | `OnDemand` requires Provider invocation; `Direct` describes a specific facility |
| `supportedFacilityTypes` | Facility categories available on demand |
| `facilityType` | Governed category of a Direct facility |
| `location` | Verified Beckn Location with GeoJSON geometry |
| `address` | Beckn Address used when verified geometry is unavailable |
| `services` | Public services offered at the facility |
| `capacity` | Optional published capacity and unit |
| `publicContact` | Public organizational contact approved for catalog publication |
| `website` | Public facility or service website |
| `source` | Authoritative source of the facility record |

## Mapping rules

The search origin is not the facility location. An adapter must not copy a request coordinate into `location` unless the Provider confirms that the returned coordinate belongs to the facility.

Query-relative distance, ranking, and price are not intrinsic facility attributes. Distance belongs in result metadata. Price and booking terms belong in the applicable Beckn offer or transaction contract.

## Examples

- [On-demand facility discovery](examples/on-demand-facility-discovery.json)
- [Custom Hiring Centre](examples/custom-hiring-centre.json)
- [Krishi Vigyan Kendra](examples/krishi-vigyan-kendra.json)
- [Warehouse](examples/warehouse.json)
- [Soil Testing Facility](examples/soil-testing-facility.json)
