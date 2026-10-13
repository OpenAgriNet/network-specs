# OpenAgriNet API Schema Packs

A domain schema says what a thing *is* in the agriculture domain. An API schema says what one named Provider's API will take and give back, so an experience layer can call it from the schema alone without reading adapter mapping files.

Each pack carries the same seven artifacts as a domain pack. The difference is scope, not shape: a domain pack is written once for the whole network, an API pack is written for one provider.

Where a pack attaches is its own to say. The domain packs sit on Beckn `Resource.resourceAttributes`, because a forecast or a mandi price genuinely is a catalogable resource. The three packs here sit on `Commitment.commitmentAttributes` instead: a grievance is a promise with a lifecycle and a registration is a standing one, not things of value in a catalog. Each pack's root schema states its container in `x-beckn-container`, and `x-beckn-container-by-action` records any action that uses a different one.

## No pack names a Beckn action

Direction is carried by `informationMode`, exactly as in the domain packs. `OnDemand` is the ask; `Direct` is an answer carrying a real result. The same attributes therefore serve `init`, `confirm`, `select`, `status`, or any later action without change.

What a *particular* action must carry is enforced by that action's mapping guard in the adapter, not by the pack. A pack that required the fields of one action would reject a legitimate payload of another.

## Two profile values these packs introduce

Both are new with `api-schemas/`; the eight domain packs use neither.

| Key | Value | Why |
|---|---|---|
| `semantic_model` | `provider-api` | The domain packs are `generalised` — written once for the whole network. A provider API pack is scoped to one provider, which is the distinction this folder exists to make. |
| `interaction_type` | `Transact` | These packs describe calls that change state upstream — a grievance is lodged, not looked up. The domain packs describe retrieval. |

## A base is a schema, not a pack

A pack may publish definitions for another pack to compose. They live in the pack that uses them most, and only the schema a pack names in its `profile.json` is indexed; the rest are there to be referenced. `Grievance/v0.1` is the one doing that today, in two layers:

- **`SchemeServiceBase`** — what any scheme desk needs whether or not it handles grievances: `informationMode`, `provider`, `scheme`, `enrolmentId`, and the challenge trio. `SchemeApplication` composes this one.
- **`GrievanceBase`** — `SchemeServiceBase` plus the complaint: the `grievance` and `case` bands, and `grievanceOptions`. Only grievances compose this one.

Splitting the base in two is what lets a pack that is not about a complaint inherit the desk without inheriting the complaint. An earlier revision had one base and made the application pack refuse three bands it could never fill; the split removed the need to write those refusals at all.

A pack composes a base with `allOf`, then pins its own `@type` and `scheme`, and adds the fields its own portal has. The published page shows the base's meaning and the pack's note together, and says which component each field came from.

What the bases own is a shape: **five bands, and the band a field sits in says who wrote it.**

| band | holds | written by |
|---|---|---|
| top level | who is asking and about what: `informationMode`, `provider`, `scheme`, `enrolmentId` | the caller |
| `grievance` | what the farmer submitted: `category`, `subCategory`, `description` | the farmer |
| `case` | what the portal has on file, the stamps it applied included: `ticketNo`, `status`, `filedOn`, `reply`, `repliedOn` | the portal |
| `challenge` | the proof the caller presents with a guarded call: `method`, `value`. Inbound only, never echoed | the caller |
| `challengeIssued` | the portal's acknowledgement that it sent one: `method`, `length`, `valueType`, `sentTo`, `expiresAt`. Outbound only, and it carries no secret | the portal |
| anything a pack adds | a crop season, an applicant's mobile — sits at the top with the rest of the context | the caller |

Not every pack uses every band. `SchemeApplication` swaps two of them for `applicant` and `application`, the same split by author, by composing the lower base. A desk that issues no challenge refuses both challenge bands outright rather than leave them defined and unfillable, and publishes `challengeMethods` empty so a caller can see that before it asks. Two fields sit in no band at all — `challengeMethods`, which describes each challenge a desk requires before it will answer, down to the length and character class of the code, and `grievanceOptions`, which says what it accepts. Both appear on a catalog entry and on no transaction payload, and carrying both is what marks a payload as a declaration rather than an ask.

Before the two containers the same split lived in a prefix — `grievanceCategory` against `caseStatus` — which read the same and checked nothing: a field named either way validated either way. As containers it is enforced, and a grievance becomes all or nothing, because `required` inside a block fires whenever the block is present. What counts as a complete answer and as a meaningful ask is each pack's own statement, because it depends on what the portal issues.

Nothing grievance-related is added to a domain schema under `schema/`. A grievance is a Provider's API surface, not a thing the network describes, so the shared shape belongs beside the packs that use it.

## One pack, two schemes

`Grievance/v0.1` covers PMFBY and PM-KISAN in a single pack rather than one pack each. The two desks share a capability — file a grievance, read it back — and differ in what they accept, so the published type is a `oneOf` over two branches, each pinned by `scheme.code`. A caller reads one pack to learn the capability and one branch to learn the desk.

`SchemeApplication` stays its own pack because checking where an application stands is a different capability, not a different scheme: nothing is filed, nothing has a lifecycle, and nothing comes back with a case number.

## Shared and unshared terms

Packs reuse a term's IRI when the term means the same thing everywhere — `informationMode`, `provider`, `scheme`, `enrolmentId`, `grievance.description` and the whole of the `case` band are declared once in `Grievance/v0.1` and mean the same on both branches and in `SchemeApplication`. `applicantMobile` is shared across a placement difference: PMFBY carries it at the top level, `SchemeApplication` carries it as `applicant.mobile`, and both resolve to the same term.

Where two desks classify differently, the difference is carried by the value space, not by a second term. `grievance.category` is one property, `openagrinet:grievanceCategory`, and each branch pins the codes its own portal issues.

A branch or a pack may refuse an inherited term outright, with `not`/`required`, rather than leave it defined and never filled. The PM-KISAN branch refuses `grievance.subCategory`, because it classifies at one level. The PMFBY branch refuses `case.reply` and `case.repliedOn`, because it publishes no reply against a ticket, and it refuses the two challenge bands outright, because its desk asks for no OTP. Each is one member to delete if the portal changes.

## Packs

- [Grievance](Grievance/v0.1/README.md) — lodging and reading a grievance at a scheme desk. Two branches today: PMFBY crop insurance and PM-KISAN income support. Also publishes `SchemeServiceBase` and `GrievanceBase` for other packs to compose.
- [Scheme Application](SchemeApplication/v0.1/README.md) — reading where a farmer's application to a scheme stands: instalments paid, eKYC standing, and what is blocking payment. PM-KISAN today.

OAN terms use `openagrinet:` for `https://openagrinet.github.io/network-specs/vocab#`. Versioned artifacts are published under `https://openagrinet.github.io/network-specs/api-schemas/`.
