# OpenAgriNet Schema Pack

<p class="page-intro">Browse the shared agriculture field set and the active OpenAgriNet domain contracts. Each domain pack applies to Beckn <code>Resource.resourceAttributes</code> and keeps its versioned artifacts together.</p>

Read the [Complete Examples](examples/) to see these packs composed inside Beckn Catalog, Provider, and Resource objects.

## Schema Packs

The index is generated from the versioned `profile.json` files. Adding a schema directory with a profile makes it appear here automatically.

{% assign profile_files = site.static_files | where: "name", "profile.json" | sort: "path" %}
<div class="schema-grid">
{% for profile in profile_files %}
  {% assign path_parts = profile.path | split: "/" %}
  {% assign schema_name = path_parts[2] %}
  {% assign schema_version = path_parts[3] %}
  {% assign pack_root = profile.path | remove: "/profile.json" %}
  {% assign pack_index_path = pack_root | remove_first: "/" | append: "/index.md" %}
  {% assign pack_index = site.pages | where: "path", pack_index_path | first %}
  <article class="schema-card">
    <span class="schema-card__meta">{{ schema_version }}</span>
    {% if pack_index %}
      <h3><a class="schema-card__title" href="{{ pack_root | append: '/' | relative_url }}">{{ schema_name }}</a></h3>
    {% else %}
      <h3><a class="schema-card__title" href="{{ pack_root | append: '/README.md' | relative_url }}">{{ schema_name }}</a></h3>
    {% endif %}
    <nav class="schema-card__links" aria-label="{{ schema_name }} artifacts">
      <a href="{{ pack_root | append: '/vocab.jsonld' | relative_url }}">Vocabulary</a>
      <a href="{{ pack_root | append: '/context.jsonld' | relative_url }}">Context</a>
      <a href="{{ pack_root | append: '/attributes.yaml' | relative_url }}">Attributes</a>
      <a href="{{ profile.path | relative_url }}">Profile</a>
      <a href="{{ pack_root | append: '/renderer.json' | relative_url }}">Renderer</a>
      {% if pack_index %}
        <a href="{{ pack_root | append: '/#examples' | relative_url }}">Examples</a>
      {% else %}
        <a href="{{ pack_root | append: '/examples/' | relative_url }}">Examples</a>
      {% endif %}
    </nav>
  </article>
{% endfor %}
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

An `OnDemand` Resource advertises what a Provider can supply without introducing a separate capability schema. It may also include current, representative, or precomputed information; the mode still indicates that a Provider invocation is required to fulfil a specific request. A Provider invocation normally returns a `Direct` Resource of the same `@type`. Direct information may also be published to Discovery without a preceding invocation. These modes define minimum requirements and do not prohibit additional fields.

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
| GeoJSONGeometry | [Beckn GeoJSONGeometry](https://github.com/beckn/schemas/tree/draft/schema/GeoJSONGeometry) | Geometry inside a Beckn Location and coordinate-defined `coverageAreas` |
| Location | [Beckn Location](https://github.com/beckn/schemas/tree/main/schema/Location) | Resolved weather, facility, mandi, and market-intelligence locations |
| Address | [Beckn Address](https://github.com/beckn/schemas/tree/main/schema/Address) | Human-readable facility address |
| Contact | [Beckn Contact](https://github.com/beckn/schemas/tree/main/schema/Contact) | Provider-approved public organizational contact |
| Participant | [Beckn Participant](https://github.com/beckn/schemas/tree/draft/schema/Participant) | Protocol participant boundary, not redefined by OAN |
| Consumer | [Beckn Consumer](https://github.com/beckn/schemas/tree/draft/schema/Consumer) | Consumer data when required by an interaction |

## Namespace

OAN terms use `openagrinet:` for `https://openagrinet.github.io/network-specs/vocab#`. Versioned artifacts are published under `https://openagrinet.github.io/network-specs/schema/`.

## Scope boundary

The packs cover portable agriculture information attributes. Protocol envelopes, Registry records, onboarding APIs, signatures, authentication, protected-data contracts, channel adapters, observability, and network federation require separate contracts.

Use each pack README and its colocated JSON examples to review the effective contract.
