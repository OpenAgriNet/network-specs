# OpenAgriNet schema pack index

This index lists the active OpenAgriNet domain contracts. Each contract is an independently selectable schema pack applied to Beckn `Resource.resourceAttributes`. The shared Agriculture Resource field set supplies `informationMode`, agriculture classification, language, and coverage to all six domain packs.

Read the [complete examples](examples/README.md) to see these packs composed inside Beckn Catalog, Provider, and Resource objects.

## Active packs

| Pack | Contract kind | Fields declared by this pack | Reused field sets | Typical placement | Examples |
|---|---|---|---|---|---|
| [Knowledge Resource](KnowledgeResource/v0.1/README.md) | Reusable agricultural knowledge | topics, supported knowledge types, representations, validity, and provenance | Agriculture Resource | Provider catalog, Discovery result, or Provider response | [JSON](KnowledgeResource/v0.1/examples/) |
| [Knowledge Advisory](KnowledgeAdvisory/v0.1/README.md) | Knowledge-based agricultural guidance | topics, recommendations, supporting Resources, validity, rationale, and source | Agriculture Resource | Provider catalog, Discovery result, or Provider response | [JSON](KnowledgeAdvisory/v0.1/examples/) |
| [Weather Advisory](WeatherAdvisory/v0.1/README.md) | Weather-informed agricultural advice | topics, supported weather basis, recommendation, place, time, validity, and source | Agriculture Resource | Provider catalog, Discovery result, or Provider response | [JSON](WeatherAdvisory/v0.1/examples/) |
| [Weather Observation](WeatherObservation/v0.1/README.md) | Weather observation or forecast | supported and actual weather parameters, place, time, validity, and source | Agriculture Resource | Provider catalog, Discovery result, or Provider response | [JSON](WeatherObservation/v0.1/examples/) |
| [Mandi Price](MandiPrice/v0.1/README.md) | Commodity market price | supported commodities and price fields, market, date, prices, and source | Agriculture Resource | Provider catalog, Discovery result, or Provider response | [JSON](MandiPrice/v0.1/examples/) |
| [Market Intelligence](MarketIntelligence/v0.1/README.md) | Market trends, forecasts, and opportunities | supported insight types and commodities, insights, periods, indicators, markets, and source | Agriculture Resource | Provider catalog, Discovery result, or Provider response | [JSON](MarketIntelligence/v0.1/examples/) |

The `Reused field sets` column describes validation composition. It is not a parent-child model.

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
| Participant | [Beckn Participant](https://github.com/beckn/schemas/tree/draft/schema/Participant) | Protocol participant boundary, not redefined by OAN |
| Consumer | [Beckn Consumer](https://github.com/beckn/schemas/tree/draft/schema/Consumer) | Consumer data when required by an interaction |

## Namespace

OAN terms use `openagrinet:` for `https://schemas.openagrinet.global/vocab#`. Versioned artifacts are published under `https://schemas.openagrinet.global/schema/`.

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
