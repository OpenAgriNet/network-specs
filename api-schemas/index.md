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

Not every directory under `api-schemas/` is a pack. A directory with no `profile.json` is never indexed and appears on no card above; it holds definitions that packs compose into themselves.

[`Grievance/v0.1`](Grievance/v0.1/attributes.yaml) is the one such directory today. It defines `GrievanceBase` — the shape any grievance has whatever the scheme — which [PMFBYGrievance](PMFBYGrievance/v0.1/README.md) and [PMKISANGrievance](PMKISANGrievance/v0.1/README.md) each `allOf`-reference. Nothing ever sends `"@type": openagrinet:GrievanceBase`.

That shape is four bands, and the band a field sits in says who wrote it: the context at the top (`informationMode`, `provider`, `scheme`, `enrolmentId`), what the farmer submitted under `grievance`, what the portal has on file under `case`, and anything a pack adds of its own — an OTP challenge, a crop season — at the top with the rest of the context. The base also publishes `CaseStatusCode`, `CalendarDate` and `ProviderReference`, so the case-status vocabulary is defined once rather than restated in each pack.

## Why these are separate

A domain pack is written once for the whole network and says what a thing *is*. An API pack is written for one provider and says what that provider's API will take and give back, so an experience layer can call it without reading adapter mapping files.

The artifacts are identical. The scope differs, and `profile.json` records that in `semantic_model`; the attachment point may differ too, which each pack states for itself in `x-beckn-container`.

## Information modes

Direction is carried by `informationMode`, exactly as in the domain packs, and no pack names a Beckn action.

| Mode | Meaning |
|---|---|
| `OnDemand` | The ask — what a caller sends to obtain a result |
| `Direct` | An answer carrying a real result |

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
