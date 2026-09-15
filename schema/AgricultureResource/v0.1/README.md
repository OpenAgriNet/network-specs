# Agriculture Resource

<nav class="artifact-links" aria-label="Schema artifacts">
  <a href="../../">All schemas</a>
  <a href="attributes.yaml">attributes.yaml</a>
  <a href="context.jsonld">context.jsonld</a>
  <a href="vocab.jsonld">vocab.jsonld</a>
  <a href="profile.json">profile.json</a>
  <a href="renderer.json">renderer.json</a>
  <a href="./">Public view</a>
  <a href="#examples">Examples</a>
</nav>

## Purpose

Agriculture Resource defines the shared agriculture fields used by OAN domain information contracts. It identifies whether information is obtained on demand or is directly available, then adds broad agriculture categories, optional governed subject references, language, and geographic applicability to a Beckn Resource.

## Attachment point

The schema attaches to `beckn:Resource.resourceAttributes`. Beckn core owns the Resource `id` and `descriptor`.

## Composition

This pack declares the shared agriculture field set. Other selected contracts reference that field set through `allOf` and apply the combined constraints to one `resourceAttributes` object.

### Resolved `allOf` composition

| Component | Fields added | Required fields |
|---|---|---|
| `AgricultureResource` | `@type` | `@type` |
| `AgricultureResourceFields` | `informationMode`, `subjectCategories`, `agricultureSubjects`, `languages`, `coverageAreas` | `informationMode`, `subjectCategories` |
| Effective flat object | All six fields on the same `resourceAttributes` object | `@type`, `informationMode`, `subjectCategories` |

## Fields

"Required when" describes a complete OAN Resource. It does not make the field mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Purpose |
|---|---|---|
| `@type` | Always | Identifies the concrete OAN Resource type and retains it when Provider-defined JSON-LD types are added |
| `informationMode` | Always | Uses `OnDemand` when a Provider invocation is required and `Direct` when the Resource contains or directly references specific information |
| `subjectCategories` | Always | Classifies the Resource for discovery using one or more broad categories such as crop, weather, market, practice, or facility |
| `agricultureSubjects` | Optional | Identifies governed subjects such as Cotton, Rice, or a commodity; absence means broad applicability within the declared categories |
| `languages` | Optional here; refined by selected packs | Declares supported or available BCP 47 languages |
| `coverageAreas` | Optional | Declares geographic applicability using an administrative area reference or a Beckn GeoJSON geometry |

`subjectCategories` is required in the shared field set so downstream systems can apply a consistent discovery filter. A concrete pack may also require a particular value, such as `Weather`, `Market`, or `Facility`.

`facilityType` serves a different purpose. A Direct `AgricultureFacility` must say which concrete kind of facility it describes. An OnDemand facility Resource instead uses `supportedFacilityTypes` to say which kinds the Provider can supply.

## Governed values

### Information mode

| Value | Meaning | Example |
|---|---|---|
| `OnDemand` | A Provider invocation is required to obtain specific information | A Provider advertises that it can answer crop-practice questions in Hindi and English |
| `Direct` | The Resource contains or directly references specific information | A catalog contains a Cotton guide or a response contains today's mandi prices |

The mode does not describe freshness. Selected domain packs use timestamps and `validity` to state when Direct information applies.

### Subject categories

| Value | Meaning | Example |
|---|---|---|
| `Crop` | Crop production, protection, harvest, or crop-specific information | Cotton sowing guidance |
| `Livestock` | Farm animals, poultry, fisheries, animal health, or husbandry | Dairy cattle vaccination guidance |
| `Weather` | Weather conditions, forecasts, alerts, or weather-dependent information | District rainfall forecast |
| `Market` | Commodity prices, demand, trade, or market opportunities | Cotton modal price at an APMC |
| `Scheme` | Government or institutional schemes, benefits, and eligibility information | PM-KISAN eligibility guidance |
| `Practice` | A method used in farming or livestock management | Drip irrigation or integrated pest management |
| `Facility` | An agricultural service location or physical facility | KVK, warehouse, Custom Hiring Centre, or Soil Testing Facility |

An Agriculture Facility uses `Facility` for broad discovery and may add categories for the domains it serves. For example, a Custom Hiring Centre may use `Facility`, `Crop`, and `Practice`. The separate `facilityType` field identifies the concrete facility kind.

### Agriculture subject reference

`agricultureSubjects` identifies a concrete governed subject when broad categories are insufficient. Each item must supply `subjectId`, `descriptor`, or both. Classification belongs in `subjectCategories` and pack-specific fields.

| Nested field | Type | Required | Meaning | Example |
|---|---|---|---|---|
| `subjectId` | URI | At least one of `subjectId` or `descriptor` | Stable identifier from a governed taxonomy | `https://taxonomy.openagrinet.global/crops/cotton` |
| `descriptor` | Beckn Descriptor | At least one of `subjectId` or `descriptor` | Machine-readable code or human-readable name | `{"code":"COTTON","name":"Cotton"}` |

`subjectCategories` supports broad filtering. `agricultureSubjects` identifies a specific entity. A Cotton guide may therefore use category `Crop` with Cotton's taxonomy identifier, descriptor, or both.

### Languages

The `languages` field uses BCP 47 tags. Examples include `en` for English, `hi` for Hindi, `mr` for Marathi, and `te` for Telugu. Applications may resolve a tag to a localized display label.

### Coverage areas

An administrative area reference carries a code system such as ISO 3166, LGD, or PIN and the corresponding code. Use it when a governed area identifier is sufficient.

| Field | Required | Meaning | Example |
|---|---|---|---|
| `codeScheme` | Required | Authority or code system that defines the identifier | `ISO-3166-1`, `ISO-3166-2`, `LGD`, `IN-PIN` |
| `areaCode` | Required | Identifier in the stated code system | `IN`, `IN-BR`, `209801` |
| `areaLevel` | Optional | Administrative or postal level represented by the code | `Country`, `State`, `District`, `Block`, `Village`, `PostalCode`, `Other` |
| `areaName` | Optional | Human-readable name that helps reviewers | `Bihar` |

| `areaLevel` | Meaning | Example |
|---|---|---|
| `Country` | Sovereign country | India |
| `State` | State or equivalent first-level subdivision | Bihar |
| `District` | District-level administrative area | Patna district |
| `Block` | Sub-district development or administrative block | Sampatchak block |
| `Village` | Governed village record | An LGD village identifier |
| `PostalCode` | Postal delivery area | PIN `209801` |
| `Other` | Governed level not covered by the listed values | A locally governed agro-climatic zone |

A GeoJSON geometry carries a Point, Polygon, MultiPolygon, or another geometry supported by Beckn `GeoJSONGeometry`. Use it when the boundary or service area is coordinate-defined.

| Geometry | Required member | Example use |
|---|---|---|
| `Point` | `coordinates` | Facility or observation point |
| `LineString` | `coordinates` | Route or linear feature |
| `Polygon` | `coordinates` | Service boundary or farm area |
| `MultiPoint` | `coordinates` | Related observation points |
| `MultiLineString` | `coordinates` | Multiple linear features |
| `MultiPolygon` | `coordinates` | Disconnected coverage areas |
| `GeometryCollection` | `geometries` | Mixed geometry collection |

GeoJSON coordinates follow longitude, latitude order. H3 and other spatial indexes are implementation projections, not portable Resource fields.

`TimePeriod` requires at least one boundary. Packs that need a bounded window use `ClosedTimePeriod`, which requires both `startsAt` and `endsAt`. Conformance checks verify that the start is not after the end.

## Non-goals

This pack does not identify a Provider, define a Catalog, carry a protocol envelope, or define how fresh the information is. Freshness is expressed by the selected domain pack through timestamps and validity.

## Examples

- [General OnDemand agriculture Resource](examples/general-agriculture.json) shows broad categories, languages, and country coverage without naming a specific crop.
- [Specific Direct crop Resource](examples/specific-crop.json) shows a governed Cotton subject and a coordinate-defined coverage area.
