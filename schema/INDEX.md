# OpenAgriNet Schema Pack Index

<p class="page-intro">Browse the shared agriculture field set and the active OpenAgriNet domain contracts. Each domain pack applies to Beckn <code>Resource.resourceAttributes</code> and keeps its versioned artifacts together.</p>

Read the [Complete Examples](examples/README.md) to see these packs composed inside Beckn Catalog, Provider, and Resource objects.

## Shared field set

<div class="schema-grid">
  <a class="schema-card" href="AgricultureResource/v0.1/">
    <span class="schema-card__meta">Shared · v0.1</span>
    <h3>Agriculture Resource</h3>
    <p>Information mode, agriculture classification, governed subjects, language, geography, time and source definitions reused by the domain packs.</p>
  </a>
</div>

## Domain packs

<div class="schema-grid">
  <a class="schema-card" href="KnowledgeResource/v0.1/">
    <span class="schema-card__meta">Knowledge · v0.1</span>
    <h3>Knowledge Resource</h3>
    <p>Reusable agricultural knowledge with inline or URI-based representations, validity and provenance.</p>
  </a>
  <a class="schema-card" href="KnowledgeAdvisory/v0.1/">
    <span class="schema-card__meta">Advisory · v0.1</span>
    <h3>Knowledge Advisory</h3>
    <p>Knowledge-based agricultural guidance with recommendations, supporting resources, validity and source.</p>
  </a>
  <a class="schema-card" href="WeatherObservation/v0.1/">
    <span class="schema-card__meta">Observation · v0.1</span>
    <h3>Weather Observation</h3>
    <p>Measured weather and forecasts with place, observation or model time, validity and source.</p>
  </a>
  <a class="schema-card" href="WeatherAdvisory/v0.1/">
    <span class="schema-card__meta">Advisory · v0.1</span>
    <h3>Weather Advisory</h3>
    <p>Weather-informed agricultural guidance with its weather basis, place, time, validity and source.</p>
  </a>
  <a class="schema-card" href="MandiPrice/v0.1/">
    <span class="schema-card__meta">Observation · v0.1</span>
    <h3>Mandi Price</h3>
    <p>Commodity market prices with market, date, units, supported price fields and source.</p>
  </a>
  <a class="schema-card" href="MarketIntelligence/v0.1/">
    <span class="schema-card__meta">Intelligence · v0.1</span>
    <h3>Market Intelligence</h3>
    <p>Market trends, forecasts and opportunities with periods, indicators, markets and source.</p>
  </a>
  <a class="schema-card" href="AgricultureFacility/v0.1/">
    <span class="schema-card__meta">Directory · v0.1</span>
    <h3>Agriculture Facility</h3>
    <p>Agricultural service facilities with type, location, services, capacity and public contact.</p>
  </a>
</div>

## How composition works

JSON Schema `allOf` applies each referenced field set to the same JSON object. The selected pack remains the effective contract and declares its own canonical `@type`.

For example, selecting `WeatherAdvisory` validates one flat object against the Agriculture Resource and Weather Advisory constraints. It does not create nested base objects and does not establish a parent-child hierarchy among the packs.

Provider-defined contracts may combine an OAN pack with additional Provider-owned constraints. A resource intended to interoperate as an OAN contract retains the applicable canonical OAN type.

## Information modes

Every domain pack supports two information modes:

| Mode | Meaning | Pack requirements |
|---|---|---|
| `OnDemand` | A Provider invocation is required to obtain specific information | Supported topics, parameters, formats, commodities, horizons, languages, or coverage as applicable |
| `Direct` | The Resource contains or directly references specific information | Actual content, values, recommendation, place, time, validity, and provenance as applicable |

An `OnDemand` Resource advertises what a Provider can supply without introducing a separate capability schema. A Provider invocation normally returns a `Direct` Resource of the same `@type`. Direct information may also be published to Discovery without a preceding invocation.

The schemas formerly named `AgricultureCapability`, `AdvisoryCapability`, and `WeatherAdvisoryCapability` are retired. Their capability declarations are represented by the corresponding active pack in `OnDemand` mode.

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
| GeoJSONGeometry | [Beckn GeoJSONGeometry](https://github.com/beckn/schemas/tree/draft/schema/GeoJSONGeometry) | Point and area geometry |
| Location | [Beckn Location](https://github.com/beckn/schemas/tree/main/schema/Location) | Verified facility geometry with optional postal address |
| Address | [Beckn Address](https://github.com/beckn/schemas/tree/main/schema/Address) | Human-readable facility address |
| Contact | [Beckn Contact](https://github.com/beckn/schemas/tree/main/schema/Contact) | Provider-approved public organizational contact |
| Participant | [Beckn Participant](https://github.com/beckn/schemas/tree/draft/schema/Participant) | Protocol participant boundary, not redefined by OAN |
| Consumer | [Beckn Consumer](https://github.com/beckn/schemas/tree/draft/schema/Consumer) | Consumer data when required by an interaction |

## Namespace

OAN terms use `openagrinet:` for `https://openagrinet.github.io/network-specs/vocab#`. Versioned artifacts are published under `https://openagrinet.github.io/network-specs/schema/`.

## Scope boundary

The packs cover portable agriculture information attributes. Protocol envelopes, Registry records, onboarding APIs, signatures, authentication, protected-data contracts, channel adapters, observability, and network federation require separate contracts.

Use each pack README and its colocated JSON examples to review the effective contract.

## Open item

The proposed field and values are `informationMode: OnDemand | Direct`.

| Alternative | Values | Tradeoff |
|---|---|---|
| `informationMode` | `ProviderResolved`, `Materialized` | More precise, but more technical |
| `resourceForm` | `Resolvable`, `Materialized` | Schema-oriented, but resolution may be confused with Registry or endpoint resolution |
| `availabilityMode` | `OnDemand`, `Published` | Business-friendly, but published may incorrectly imply storage in Discovery |
| `accessMode` | `ProviderInvocation`, `Direct` | Makes the access path explicit, but says less about completeness |

The terminology requires review before the v0.1 contracts are accepted. The underlying distinction is required: `OnDemand` needs a Provider invocation; `Direct` contains or directly references specific information.
