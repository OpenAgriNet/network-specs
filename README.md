# OpenAgriNet network specifications

Status: Proposed for review

## Purpose

This repository contains the versioned OpenAgriNet domain contracts used to describe agricultural information in Beckn catalogs, Discovery results, and Provider responses.

The contracts add agriculture-specific fields to Beckn `Resource.resourceAttributes`. Beckn continues to define Catalog, Provider, Resource identity, Resource descriptor, and protocol envelopes. Registry records, onboarding APIs, transport, signatures, authentication, deployment, and network federation remain separate specifications.

## Start here

| Entry point | Use it for |
|---|---|
| [Schema pack index](schema/INDEX.md) | See every active schema pack, the fields it declares, the field sets it reuses, and where it is used |
| [Complete examples](schema/examples/README.md) | See OAN attributes composed inside complete Beckn Catalog, Provider, and Resource objects |
| [Provider mappings](mappings/README.md) | See Provider-specific transformations between native APIs and canonical OAN Resources |

## Active version

The active review line is `v0.1`; pack metadata uses semantic version `0.1.0`. The singular `schema/` directory is authoritative.

## Repository layout

| Path | Contents |
|---|---|
| [`schema/`](schema/) | Versioned domain schema packs and examples that validate directly against each pack |
| [`mappings/`](mappings/) | Versioned Provider-specific JSONata transformations, mapping decisions, and fixtures |

Each versioned schema pack contains:

- `vocab.jsonld`: governed classes and properties;
- `context.jsonld`: compact JSON-LD term mappings;
- `attributes.yaml`: OpenAPI 3.1 and JSON Schema validation;
- `profile.json`: discovery and indexing hints;
- `renderer.json`: optional presentation hints;
- `README.md`: purpose, composition, fields, and boundaries;
- `examples/`: complete JSON instances that validate against the pack.

Examples that demonstrate a single contract live with that schema pack. Complete composition examples live in [`schema/examples/`](schema/examples/) and show those attributes inside Beckn-owned objects.

Provider mappings are adapters around these contracts. They may translate native field names, values, and legacy protocol shapes, but they do not redefine canonical OAN fields.

## Beckn dependencies

OAN does not redefine the Beckn objects that carry its domain attributes. The links below point to the current Beckn schema source. The OAN schemas pin the applicable version in each `$ref`.

| Beckn definition | Use in OAN |
|---|---|
| [Catalog 2.2](https://github.com/beckn/schemas/tree/draft/schema/Catalog/v2.2) | Groups a Provider's advertised Resources |
| [Provider 2.1](https://github.com/beckn/schemas/tree/draft/schema/Provider/v2.1) | Identifies the entity offering the Resources in a Catalog |
| [Resource 2.0](https://github.com/beckn/schemas/tree/draft/schema/Resource/v2.0) | Carries OAN data in `resourceAttributes` |
| [Attributes 2.0](https://github.com/beckn/schemas/tree/draft/schema/Attributes/v2.0) | Provides the JSON-LD extension container used by `resourceAttributes` |
| [Descriptor 2.1](https://github.com/beckn/schemas/tree/draft/schema/Descriptor/v2.1) | Supplies names, codes, and human-readable descriptions |
| [GeoJSONGeometry 2.0](https://github.com/beckn/schemas/tree/draft/schema/GeoJSONGeometry/v2.0) | Represents points and geographic areas using GeoJSON |
| [Participant](https://github.com/beckn/schemas/tree/draft/schema/Participant) | Defines the Beckn participant boundary; OAN does not introduce `OANParticipant` |
| [Consumer](https://github.com/beckn/schemas/tree/draft/schema/Consumer) | Defines the Beckn consumer object where a protocol interaction requires one |

## Composition model

The schema packs are composable field sets. A selected contract uses JSON Schema `allOf` to validate one `resourceAttributes` object against every referenced field set. Pack relationships are composition-only.

For example, the effective `WeatherAdvisory` contract combines the shared Agriculture Resource fields with Weather Advisory fields. This composition does not make one runtime object a child of another, and it does not require an intermediate Domain payload.

Each domain pack supports `OnDemand` and `Direct` information. An `OnDemand` Resource describes information that requires a Provider invocation. A `Direct` Resource contains or directly references specific information. The mode does not indicate freshness; timestamps and validity express when the information applies.

The selected domain pack is also the capability type. `OnDemand` advertises what the Provider can supply, and `Direct` carries the supplied information. OAN does not define parallel `*Capability` schema packs.

The canonical OAN `@type` is required. A Provider extension may use a JSON-LD type array only when that array retains the canonical OAN type. A pack-local `@context` is optional inside `resourceAttributes` when the enclosing Beckn document already establishes the same context; standalone JSON-LD documents include it explicitly.

## Canonical identifiers

OAN-governed terms use the `openagrinet:` prefix:

```text
https://schemas.openagrinet.global/vocab#
```

Versioned schema artifacts are published below:

```text
https://schemas.openagrinet.global/schema/
```

Taxonomy identifiers use separately governed taxonomy URLs. They are references from the schema, not schema-host aliases.

## Contract boundary

These specifications define portable domain data. They do not define:

- protocol request and response envelopes;
- synchronous or asynchronous interaction behavior;
- Registry or Provider-onboarding interfaces;
- network endpoints, signing keys, or authentication;
- protected-data or consent artifacts;
- channel adapters, observability, or deployment topology.

Those contracts may reference the domain types defined here without duplicating their fields.

## Conventions

- OpenAPI 3.1.1 with JSON Schema 2020-12 semantics
- JSON-LD 1.1 context and vocabulary per pack
- one `openagrinet:` namespace for OAN-governed terms
- lowerCamelCase property names
- UpperCamelCase governed values in the review draft
- semantic versions for schema packs and versioned Resources
- composition through named `allOf` references
- no personal profiles, credentials, transport addresses, prompts, embeddings, or model traces
