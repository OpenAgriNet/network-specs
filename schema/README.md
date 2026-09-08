# OpenAgriNet Schema Packs

Each active domain directory contains one versioned contract applied to Beckn `Resource.resourceAttributes`. Contracts reuse named field sets through JSON Schema `allOf`; pack relationships are composition-only. Each domain contract supports `OnDemand` information that requires a Provider invocation and `Direct` information that is already present or directly referenced.

Use the [Schema Pack Index](INDEX.md) to review every pack, its declared fields, its composition inputs, and its examples. Use the [Complete Examples](examples/README.md) to see those packs inside Beckn Catalog, Provider, and Resource objects.

OAN terms use `openagrinet:` for `https://openagrinet.github.io/network-specs/vocab#`. Versioned artifacts are published under `https://openagrinet.github.io/network-specs/schema/`.
