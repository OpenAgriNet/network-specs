# OpenAgriNet Schema Pack

<p class="page-intro">Browse the shared agriculture field set, the active OpenAgriNet domain contracts, and the provider API contracts. Each pack keeps its versioned artifacts together.</p>

Read the [Complete Examples](examples/) to see the domain packs composed inside Beckn Catalog, Provider, and Resource objects.

## Schema Packs

Choose a schema, then a version. Schema names open the newest available version; version numbers link to that exact contract. API operation contracts are listed separately below.

{% include schema-directory.html %}

## How composition works

JSON Schema `allOf` applies each referenced field set to the same JSON object. The selected pack remains the effective contract and declares its own canonical `@type`.

For example, selecting `AgricultureAdvisory` v0.2 validates one flat object against the Agriculture Resource and advisory constraints. Weather-informed guidance adds conditional requirements. KnowledgeAdvisory and WeatherAdvisory remain available as separate v0.1 contracts.

Provider-defined contracts may combine an OAN pack with additional Provider-owned constraints. A resource intended to interoperate as an OAN contract retains the applicable canonical OAN type.

## Information modes

Every domain pack supports two information modes:

| Mode | Meaning | Pack requirements |
|---|---|---|
| `OnDemand` | A Provider invocation is required to obtain specific information | Supported topics, parameters, formats, commodities, horizons, languages, or coverage as applicable |
| `Direct` | The Resource contains or directly references specific information | Actual content, values, recommendation, place, time, validity, and provenance as applicable |

An `OnDemand` Resource advertises what a Provider can supply without introducing a separate capability schema. It may also include current, representative, or precomputed information; the mode still indicates that a Provider invocation is required to fulfil a specific request. A Provider invocation normally returns a `Direct` Resource of the same `@type`. Direct information may also be published to Discovery without a preceding invocation. These modes define minimum requirements and do not prohibit additional fields.

The schemas formerly named `AgricultureCapability`, `AdvisoryCapability`, and `WeatherAdvisoryCapability` are retired. Their capability declarations are represented by the corresponding active pack in `OnDemand` mode.

Grievance and SchemeApplication advertise `OnDemand` services. Their public catalog attributes are separate from the operation request and response contracts.

## Pack contents

| Artifact | Responsibility |
|---|---|
| `vocab.jsonld` | Defines OAN classes and properties |
| `context.jsonld` | Maps compact terms to governed identifiers |
| `attributes.yaml` | Defines the effective validation contract and its `allOf` composition |
| `profile.json` | Supplies discovery, indexing, filtering, and privacy hints |
| `renderer.json` | Supplies optional presentation hints without changing validation |
| `README.md` | Explains purpose, composition, fields, examples, and boundaries |
| `examples/` | Contains complete instances validated directly against the pack |

Review a pack in this order: vocabulary, context, attributes, profile, renderer, README, then examples.

## External definitions

The packs reuse Beckn-owned definitions rather than copying them:

| Definition | Current source | Used for |
|---|---|---|
| Catalog | [Beckn Catalog](https://github.com/beckn/schemas/tree/draft/schema/Catalog) | Provider catalog boundary |
| Provider | [Beckn Provider](https://github.com/beckn/schemas/tree/draft/schema/Provider) | Provider identity in a Catalog |
| Resource | [Beckn Resource](https://github.com/beckn/schemas/tree/draft/schema/Resource) | Resource identity, descriptor, and `resourceAttributes` container |
| Attributes | [Beckn Attributes](https://github.com/beckn/schemas/tree/draft/schema/Attributes) | JSON-LD extension container |
| Descriptor | [Beckn Descriptor](https://github.com/beckn/schemas/tree/draft/schema/Descriptor) | Human-readable and coded descriptions |
| GeoJSONGeometry | [Beckn GeoJSONGeometry 2.0](https://github.com/beckn/schemas/tree/draft/schema/GeoJSONGeometry/v2.0) | Geometry inside a Beckn Location and coordinate-defined `coverageAreas` |
| Location | [Beckn Location 2.0](https://github.com/beckn/schemas/tree/draft/schema/Location/v2.0) | Resolved weather, facility, mandi, and market-intelligence locations |
| Address | [Beckn Address](https://github.com/beckn/schemas/tree/main/schema/Address) | Human-readable facility address |
| Contact | [Beckn Contact](https://github.com/beckn/schemas/tree/main/schema/Contact) | Provider-approved public organizational contact |
| Participant | [Beckn Participant](https://github.com/beckn/schemas/tree/draft/schema/Participant) | Protocol participant boundary, not redefined by OAN |
| Consumer | [Beckn Consumer](https://github.com/beckn/schemas/tree/draft/schema/Consumer) | Consumer data when required by an interaction |

`coverageAreas[]` contains an administrative area reference or a Beckn `GeoJSONGeometry` directly. It does not contain Beckn `Location` objects. A pack-specific field named `location` uses Beckn `Location`, with the geometry under `location.geo` and an optional address alongside it.

## API Schema

[External API specifications](../api/external/) describe operation inputs, outputs and examples by provider. Grievance and SchemeApplication describe public catalog metadata and link to the respective API contracts.

## Namespace

OAN terms use `openagrinet:` for `https://openagrinet.github.io/network-specs/vocab#`. Versioned artifacts are published under `https://openagrinet.github.io/network-specs/schema/`.

## Scope boundary

The packs cover portable agriculture information attributes. Protocol envelopes, Registry records, onboarding APIs, signatures, authentication, protected-data contracts, channel adapters, observability, and network federation require separate contracts.

Use each pack README and its colocated JSON examples to review the effective contract.
