# OpenAgriNet API Schema Packs

<p class="page-intro">Browse the provider API contracts. Each pack describes what one named Provider's API accepts and returns, states where it attaches in <code>x-beckn-container</code>, and keeps its versioned artifacts together.</p>

Read the [API schema overview](README.md) for how these differ from the [domain schemas](../schema/).

## API Schema Packs

The index is generated from the versioned `profile.json` files under `api-schemas/`. Adding a provider directory with a profile makes it appear here automatically.

{% assign all_profiles = site.static_files | where: "name", "profile.json" | sort: "path" %}
{% assign profile_files = all_profiles | where_exp: "p", "p.path contains '/api-schemas/'" %}
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

## Shared definitions

A pack may publish definitions for another pack to compose, rather than keeping a second copy in step by review. The definitions live in the pack that uses them most; only the schema a pack names in its `profile.json` is indexed, and the rest are there to be referenced.

[`Grievance/v0.1`](Grievance/v0.1/attributes.yaml) is the one doing that today. It defines `SchemeServiceBase` — what any scheme desk needs whether or not it handles grievances — which [SchemeApplication](SchemeApplication/v0.1/README.md) `allOf`-references. `GrievanceBase` sits one layer above it and stays inside the grievance pack. Nothing ever sends `"@type": openagrinet:SchemeServiceBase` or `openagrinet:GrievanceBase`.

The shape is five bands, and the band a field sits in says who wrote it: the context at the top (`informationMode`, `provider`, `scheme`, `enrolmentId`), what the farmer submitted under `grievance`, what the portal has on file under `case`, and the challenge under `challenge` — what the desk accepts, what it sent, and what the caller answered, one member per payload. Anything a pack adds of its own — a crop season, an applicant's mobile — sits at the top with the rest of the context. A desk that issues no challenge refuses the whole band outright. A pack that is not about a complaint takes the base one layer down: SchemeApplication composes `SchemeServiceBase`, so the `grievance` and `case` bands are never inherited, and it carries `applicant` and `application` in their place. The grievance pack also publishes `CaseStatusCode`, `CalendarDate`, `Instant`, `ProviderReference`, `ChallengeMethod` and `GrievanceOption`, so the case-status vocabulary and the two date shapes are defined once.

## Why these are separate

A domain pack is written once for the whole network and says what a thing *is*. An API pack is written for one provider and says what that provider's API will take and give back, so an experience layer can call it without reading adapter mapping files.

The artifacts are identical. The scope differs, and `profile.json` records that in `semantic_model`; the attachment point may differ too, which each pack states for itself in `x-beckn-container`.

## Information modes

`informationMode` says where the answer comes from, and no pack names a Beckn action.

| Mode | Meaning |
|---|---|
| `OnDemand` | The external system answers. The caller makes the `init`, `status` or `support` call that follows discovery. The only value |

What a *particular* action must carry is enforced by that action's mapping guard in the adapter, not by the pack. A pack that required the fields of one action would reject a legitimate payload of another.

## Pack contents

The same seven artifacts as a domain pack.

| Artifact | Responsibility |
|---|---|
| `vocab.jsonld` | Defines OAN classes and properties |
| `context.jsonld` | Maps compact terms to governed identifiers |
| `attributes.yaml` | Defines the effective validation contract and its `allOf` composition |
| `profile.json` | Supplies discovery, indexing, filtering, and privacy hints |
| `renderer.json` | Supplies optional presentation hints without changing validation |
| `README.md` | Explains purpose, composition, fields, examples, and boundaries |
| `examples/` | Contains instances validated directly against the pack |

Review a pack in this order: vocabulary, context, attributes, profile, renderer, README, then examples.
