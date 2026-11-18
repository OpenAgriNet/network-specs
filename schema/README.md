# OpenAgriNet Schema Packs

Every active pack lives here, one versioned contract per pack, in one of two kinds. **Domain** packs say what a thing *is*; they attach to Beckn `Resource.resourceAttributes` and compose shared field sets with `allOf`. **Provider API** packs say what one named Provider's API takes and returns; `x-oan-schema-by-action` names the schema per call and `x-beckn-container-by-action` names where it attaches. `profile.json` records which kind a pack is, in `semantic_model`.

| Pack | Kind | Covers |
|---|---|---|
| [AgricultureResource](AgricultureResource/v0.1/README.md) | Domain | The shared agriculture field set the other domain packs compose |
| [AgricultureFacility](AgricultureFacility/v0.1/README.md) | Domain | Facilities discoverable through a Provider or supplied directly |
| [KnowledgeResource](KnowledgeResource/v0.1/README.md) | Domain | Agricultural knowledge obtained on demand or supplied directly |
| [KnowledgeAdvisory](KnowledgeAdvisory/v0.1/README.md) | Domain | Actionable guidance derived from that knowledge |
| [MandiPrice](MandiPrice/v0.1/README.md) | Domain | Mandi prices obtained on demand or supplied directly |
| [MarketIntelligence](MarketIntelligence/v0.1/README.md) | Domain | Price trends, demand forecasts, and nearby market opportunities |
| [WeatherObservation](WeatherObservation/v0.1/README.md) | Domain | Weather information obtained on demand or supplied directly |
| [WeatherAdvisory](WeatherAdvisory/v0.1/README.md) | Domain | Weather-informed agricultural guidance |
| [Grievance](Grievance/v0.1/README.md) | Provider API | Lodging and reading a grievance at a scheme desk. PMFBY and PM-KISAN today |
| [SchemeApplication](SchemeApplication/v0.1/README.md) | Provider API | Reading where a farmer's scheme application stands. PM-KISAN today |

Every pack carries the same artifacts: `vocab.jsonld`, `context.jsonld`, `attributes.yaml`, `profile.json`, `renderer.json`, `README.md`, and `examples/`. Read them in that order.

Use the [Schema Pack index](./) to browse every pack, and the [Complete Examples](examples/) to see domain packs inside Beckn Catalog, Provider, and Resource objects. OAN terms use `openagrinet:` for `https://openagrinet.github.io/network-specs/vocab#`; versioned artifacts are published under `https://openagrinet.github.io/network-specs/schema/`.
