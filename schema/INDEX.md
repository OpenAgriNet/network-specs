# OpenAgriNet schema pack index

This index lists the active OpenAgriNet domain contracts. Each contract is an independently selectable schema pack applied to Beckn `Resource.resourceAttributes`.

Read the [complete examples](examples/README.md) to see these packs composed inside Beckn Catalog, Provider, and Resource objects.

## Active packs

| Pack | Contract kind | Fields declared by this pack | Reused field sets | Typical placement | Examples |
|---|---|---|---|---|---|
| [Agriculture Resource](AgricultureResource/v0.1/README.md) | Shared agriculture field set | subject areas, subject scope, agriculture subjects, languages, coverage | Beckn Resource boundary | Reused by OAN capability and outcome contracts | [JSON](AgricultureResource/v0.1/examples/) |
| [Agriculture Capability](AgricultureCapability/v0.1/README.md) | Invokable capability | interaction types and governed capability profile type | Agriculture Resource | Provider catalog | [JSON](AgricultureCapability/v0.1/examples/) |
| [Advisory Capability](AdvisoryCapability/v0.1/README.md) | Advisory capability | advisory type and topics | Agriculture Resource, Agriculture Capability | Provider catalog | [JSON](AdvisoryCapability/v0.1/examples/) |
| [Weather Advisory](WeatherAdvisory/v0.1/README.md) | Weather-informed advisory capability | weather parameters, forecast horizon, update frequency, geographic granularity | Agriculture Resource, Agriculture Capability, Advisory Capability | Provider catalog | [JSON](WeatherAdvisory/v0.1/examples/) |
| [Knowledge Resource](KnowledgeResource/v0.1/README.md) | Published or returned resource | knowledge classification, version, content, validity, provenance, supersession | Agriculture Resource | Published catalog or Provider response | [JSON](KnowledgeResource/v0.1/examples/) |
| [Weather Observation](WeatherObservation/v0.1/README.md) | Live observation or forecast | source, location, time, validity, weather parameters | Agriculture Resource | Provider response | [JSON](WeatherObservation/v0.1/examples/) |
| [Mandi Price Observation](MandiPriceObservation/v0.1/README.md) | Live market observation | source, commodity, market, arrival date, price values | Agriculture Resource | Provider response | [JSON](MandiPriceObservation/v0.1/examples/) |

The `Reused field sets` column describes validation composition. It is not a parent-child model.

## How composition works

JSON Schema `allOf` applies each referenced field set to the same JSON object. The selected pack remains the effective contract and declares its own canonical `@type`.

For example, selecting `WeatherAdvisory` validates one object against the agriculture, capability, advisory, and weather-advisory constraints. It does not create four nested objects and does not establish a subtype relationship among the packs.

Provider-defined contracts may combine an OAN pack with additional Provider-owned constraints. A resource intended to interoperate as an OAN contract retains the applicable canonical OAN type.

## Capability profiles

`AgricultureCapability` supplies common capability fields. A specific type identifies the governed invocation profile:

| Capability type | Intended outcome |
|---|---|
| `openagrinet:KnowledgeRetrievalCapability` | `openagrinet:KnowledgeResource` |
| `openagrinet:MandiPriceCapability` | `openagrinet:MandiPriceObservation` |
| `openagrinet:WeatherObservationCapability` | `openagrinet:WeatherObservation` |

An instance declares `openagrinet:AgricultureCapability` and the applicable specific capability type. The Provider catalog does not repeat schema references; the selected governed type supplies that meaning.

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

The packs cover agriculture capability and resource attributes. Protocol envelopes, Registry records, onboarding APIs, signatures, authentication, protected-data contracts, channel adapters, observability, and network federation require separate contracts.

Use each pack README and its colocated JSON examples to review the effective contract.
