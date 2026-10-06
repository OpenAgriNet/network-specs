# OpenAgriNet API Schema Packs

A domain schema says what a thing *is* in the agriculture domain. An API schema says what one named Provider's API will take and give back, so an experience layer can call it from the schema alone without reading adapter mapping files.

Each pack carries the same seven artifacts as a domain pack and applies to Beckn `Resource.resourceAttributes` in the same way. The difference is scope, not shape: a domain pack is written once for the whole network, an API pack is written for one provider.

## No pack names a Beckn action

Direction is carried by `informationMode`, exactly as in the domain packs. `OnDemand` is the ask; `Direct` is an answer carrying a real result. The same attributes therefore serve `init`, `confirm`, `select`, `status`, or any later action without change.

What a *particular* action must carry is enforced by that action's mapping guard in the adapter, not by the pack. A pack that required the fields of one action would reject a legitimate payload of another.

## Two profile values these packs introduce

Both are new with `api-schemas/`; the eight domain packs use neither.

| Key | Value | Why |
|---|---|---|
| `semantic_model` | `provider-api` | The domain packs are `generalised` — written once for the whole network. A provider API pack is scoped to one provider, which is the distinction this folder exists to make. |
| `interaction_type` | `Transact` | These packs describe calls that change state upstream — a grievance is lodged, not looked up. The domain packs describe retrieval. |

## Shared and unshared terms

Packs reuse a term's IRI when the term means the same thing everywhere — `scheme`, `caseStatus`, `filedOn`, `caseRemark`, `remarkedOn` and `source` are shared across the grievance packs.

A term is split when the value spaces are incompatible. `grievanceCategory` keeps its JSON key in both grievance packs but resolves to `openagrinet:pmfbyGrievanceCategory` in one and `openagrinet:pmkisanGrievanceCategory` in the other, because a dotted `3.10` and a closed `G001`–`G010` list cannot share one property and still be reasoned over. Payloads are identical either way; only the context mapping differs.

## Packs

- [PMFBY Grievance](PMFBYGrievance/v0.1/README.md) — lodging and reading a PMFBY crop-insurance grievance.
- [PM-KISAN Grievance](PMKISANGrievance/v0.1/README.md) — lodging and reading a PM-KISAN income-support grievance.

OAN terms use `openagrinet:` for `https://openagrinet.github.io/network-specs/vocab#`. Versioned artifacts are published under `https://openagrinet.github.io/network-specs/api-schemas/`.
