# OpenAgriNet API Schema Packs

<p class="page-intro">Browse the provider API contracts. Each pack describes what one named Provider's API accepts and returns, states which schema serves each call in <code>x-oan-schema-by-action</code>, and keeps its versioned artifacts together.</p>

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

## No pack shares a schema with another

Each pack stands alone. Neither `$ref`s into the other, so a change to one cannot reach the other and a reviewer reading one pack has read all of it.

Inside a pack the shape is three layers. The root nominates a schema per action in `x-oan-schema-by-action`; each of those is a `oneOf` over the leaves that serve that call; each leaf is one scheme's version of one call — a guard pinning `scheme.code`, a closed flat body, and where needed a gate stating which combinations the portal accepts. Adding a scheme is adding a leaf; nothing existing is edited.

What the packs do share is vocabulary. `informationMode`, `provider`, `scheme`, `enrolmentId` and `grievance.description` resolve to the same `openagrinet:` IRIs in both, so payloads from either pack line up in a graph without either file referencing the other.

## Why these are separate

A domain pack is written once for the whole network and says what a thing *is*. An API pack is written for one provider and says what that provider's API will take and give back, so an experience layer can call it without reading adapter mapping files.

The artifacts are identical. The scope differs, and `profile.json` records that in `semantic_model`; the attachment point differs per call, which each pack states for itself in `x-beckn-container-by-action`.

## Information modes

`informationMode` says where the answer comes from.

| Mode | Meaning |
|---|---|
| `OnDemand` | The external system answers. The caller makes the `init`, `status` or `support` call that follows discovery. The only value |

What a *particular* action must carry is stated by the pack. `x-oan-schema-by-action` names one schema per action and the validator checks the payload against that schema alone, so a payload that is complete for one call is refused on another — by name, not by a general "matches nothing".

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
