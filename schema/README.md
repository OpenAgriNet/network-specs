# OpenAgriNet schema packs

Each active domain directory contains one versioned contract applied to Beckn `Resource.resourceAttributes`. Contracts reuse named field sets through JSON Schema `allOf`; pack relationships are composition-only. Each domain contract supports `OnDemand` information that requires a Provider invocation and `Direct` information that is already present or directly referenced.

Use the [schema pack index](INDEX.md) to review every pack, its declared fields, its composition inputs, and its examples. Use the [complete examples](examples/README.md) to see those packs inside Beckn Catalog, Provider, and Resource objects.

OAN terms use `openagrinet:` for `https://schemas.openagrinet.global/vocab#`. Versioned artifacts are published under `https://schemas.openagrinet.global/schema/`.
