# OpenAgriNet API Schema Packs

A domain schema says what a thing *is* in the agriculture domain. An API schema says what one named Provider's API will take and give back, so an experience layer can call it from the schema alone without reading adapter mapping files.

Each pack carries the same seven artifacts as a domain pack. The difference is scope, not shape: a domain pack is written once for the whole network, an API pack is written for one provider.

Where a pack attaches is its own to say. The domain packs sit on Beckn `Resource.resourceAttributes`, because a forecast or a mandi price genuinely is a catalogable resource. The two grievance packs sit on `Commitment.commitmentAttributes` instead: a grievance is a promise with a lifecycle, not a thing of value in a catalog. Each pack's root schema states its container in `x-beckn-container`, and `x-beckn-container-by-action` records any action that uses a different one.

## No pack names a Beckn action

Direction is carried by `informationMode`, exactly as in the domain packs. `OnDemand` is the ask; `Direct` is an answer carrying a real result. The same attributes therefore serve `init`, `confirm`, `select`, `status`, or any later action without change.

What a *particular* action must carry is enforced by that action's mapping guard in the adapter, not by the pack. A pack that required the fields of one action would reject a legitimate payload of another.

## Two profile values these packs introduce

Both are new with `api-schemas/`; the eight domain packs use neither.

| Key | Value | Why |
|---|---|---|
| `semantic_model` | `provider-api` | The domain packs are `generalised` — written once for the whole network. A provider API pack is scoped to one provider, which is the distinction this folder exists to make. |
| `interaction_type` | `Transact` | These packs describe calls that change state upstream — a grievance is lodged, not looked up. The domain packs describe retrieval. |

## A base is a file, not a pack

A directory here with no `profile.json` is not a pack: it holds definitions for packs to compose, is never indexed, and names no `@type` anything can send. `Grievance/v0.1` is the one so far. It owns the field set both grievance packs share and the vocabulary those fields are written in, so the case-status list is defined once rather than restated in each pack and kept in step by review.

A pack composes it with `allOf`, then pins its own `@type` and `scheme`, adds the fields its own portal has, and restates each inherited field with a `description` recording where its value comes from upstream. The published page shows the base's meaning and the pack's note together, and says which component each field came from.

What `Grievance/v0.1` actually owns is a shape: **five bands, and the band a field sits in says who wrote it.**

| band | holds | written by |
|---|---|---|
| top level | who is asking and about what: `informationMode`, `provider`, `scheme`, `enrolmentId` | the caller |
| `grievance` | what the farmer submitted: `category`, `subCategory`, `description` | the farmer |
| `case` | what the portal has on file, the stamps it applied included: `ticketNo`, `status`, `filedOn`, `remark`, `remarkedOn` | the portal |
| `challenge` | the proof the caller presents with a guarded call: `method`, `value`. Inbound only, never echoed | the caller |
| `challengeIssued` | the portal's acknowledgement that it sent one: `method`, `sentTo`, `expiresAt`. Outbound only, and it carries no secret | the portal |
| anything a pack adds | a crop season, an applicant's phone — sits at the top with the rest of the context | the caller |

Not every pack uses every band. A desk that issues no challenge refuses both challenge bands outright rather than leave them defined and unfillable, and publishes `challengeMethods` empty so a caller can see that before it asks. Two fields sit in no band at all — `challengeMethods`, which says what a desk requires before it will answer, and `grievanceOptions`, which says what it accepts. Both appear on a catalog entry and on no transaction payload, and carrying both is what marks a payload as a declaration rather than an ask.

Before the two containers the same split lived in a prefix — `grievanceCategory` against `caseStatus` — which read the same and checked nothing: a field named either way validated either way. As containers it is enforced, and a grievance becomes all or nothing, because `required` inside a block fires whenever the block is present. What counts as a complete answer and as a meaningful ask is each pack's own statement, because it depends on what the portal issues.

Nothing grievance-related is added to a domain schema under `schema/`. A grievance is a Provider's API surface, not a thing the network describes, so the shared shape belongs beside the packs that use it.

## Shared and unshared terms

Packs reuse a term's IRI when the term means the same thing everywhere — `informationMode`, `provider`, `scheme`, `enrolmentId`, `grievance.description` and the whole of the `case` band are shared across the grievance packs, and all of them are declared once in `Grievance/v0.1`.

A term is split when the value spaces are incompatible. `grievance.category` keeps its JSON key in both grievance packs but resolves to `openagrinet:pmfbyGrievanceCategory` in one and `openagrinet:pmkisanGrievanceCategory` in the other, because PMFBY's numeric ids and a closed `G001`–`G010` list cannot share one property and still be reasoned over. Payloads are identical either way; only the context mapping differs.

A pack may also refuse an inherited term outright, with `not`/`required`, rather than leave it defined and never filled: PM-KISAN refuses `grievance.subCategory` because it classifies at one level, and `case.ticketNo` because it issues no handle for a case. PMFBY refuses `case.remarkedOn` because it publishes no date against a remark. Each is one member to delete if the portal changes.

## Packs

- [Grievance](Grievance/v0.1/attributes.yaml) — **base definitions, not a pack.** The five bands, the `Grievance` and `Case` containers, and `CaseStatusCode`, `CalendarDate` and `ProviderReference` beside them.
- [PMFBY Grievance](PMFBYGrievance/v0.1/README.md) — lodging and reading a PMFBY crop-insurance grievance.
- [PM-KISAN Grievance](PMKISANGrievance/v0.1/README.md) — lodging and reading a PM-KISAN income-support grievance.

OAN terms use `openagrinet:` for `https://openagrinet.github.io/network-specs/vocab#`. Versioned artifacts are published under `https://openagrinet.github.io/network-specs/api-schemas/`.
