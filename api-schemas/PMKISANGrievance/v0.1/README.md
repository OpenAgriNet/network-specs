# PM-KISAN Grievance

<nav class="artifact-links" aria-label="Schema artifacts">
  <a href="../../README.md">All API schemas</a>
  <a href="attributes.yaml">attributes.yaml</a>
  <a href="context.jsonld">context.jsonld</a>
  <a href="vocab.jsonld">vocab.jsonld</a>
  <a href="profile.json">profile.json</a>
  <a href="renderer.json">renderer.json</a>
  <a href="#examples">Examples</a>
</nav>

## Purpose

> Upstream ground truth for this pack — what the portal actually accepts and returns,
> with a source citation per field — is `docs/grievance-upstream-contracts.md` in the
> OpenAgriNet docs. Where this README and that page disagree, that page wins.

Describes what the PM-KISAN grievance API accepts and what it returns, so an experience layer can call it from the schema alone without reading adapter mapping files.

This is an API schema, not a domain schema. A domain schema says what a thing *is* in the agriculture domain; this one says what one named Provider's API will take and give back.

## Attachment point

Applied to `commitmentAttributes` of a Beckn `Commitment`, not to
`resourceAttributes`.

A grievance is a promise with a lifecycle, not a catalogable thing of value.
`resourceAttributes` is defined as "all the properties of a resource that
describe its value, its terms of usage, fulfillment, and consideration", and a
`Resource` is what a Provider publishes in a catalog. One farmer's registration
number and case status are none of those, and would be nonsense in a catalog
entry. `Commitment` is "a specific promise... and the current lifecycle
status of that promise", and its `DRAFT | ACTIVE | CLOSED` states are the
grievance's own.

The `Resource` does not disappear — `Commitment.resources` carries one, and each
entry needs an `id` and a `quantity`. It stays thin: a pointer to the catalogable
"grievance handling" entry the offer references. Its id is fixed for the provider
(`res:pmkisan:grievance`) rather than minted per case, and it does not change across the
lifecycle, so it names the catalog entry and never the case. The case itself sits
beside it on the commitment, and `commitmentAttributes` is the only thing that
differs from one response to the next.

This holds wherever a `Commitment` carries the payload. On `support` there is no
commitment — the payload attaches through `Support.channels` instead. See
"Direction, not action" below.

The spec puts no `minItems` on `Commitment.resources`, so an empty array is legal.
This pack never sends one — see "Nothing on file" below.

This is deliberately unlike the OAN domain packs. A forecast or a mandi price
genuinely is a resource, and those packs stay on `resourceAttributes`.

## The four bands

**The band a field sits in says who wrote it.**

| band | holds | written by |
|---|---|---|
| top level | who is asking and about what: `informationMode`, `provider`, `scheme`, `enrolmentId` | the caller |
| `grievance` | what the farmer submitted: `category`, `description` | the farmer |
| `case` | what the portal has on file, the stamps it applied included: `status`, `filedOn`, `remark`, `remarkedOn` | the portal |

There is no fourth band here. PMFBY has a `challenge` band for its OTP; PM-KISAN proves
nothing in either direction, so the band does not exist in this pack.

Before the containers the same split lived in a prefix — `grievanceCategory` against
`caseStatus` — which read the same and checked nothing: a field named either way
validated either way. As containers the split is enforced, and `grievance` becomes all
or nothing, because `required` inside a block fires whenever the block is present.

Nothing rides in a Beckn `descriptor`. An earlier draft hoisted the category and the
farmer's words there, which read well and checked nothing: a `Descriptor` is three
free-text strings, so a `G001`-and-nothing-else category validated as any string at all.
As fields inside `grievance` each one has bounds the pack holds.

## Direction, not action

Direction is carried by `informationMode`, never by the Beckn action. `OnDemand` is the ask; `Direct` is an answer carrying a real case. The same attributes therefore serve `status` without change; there is no `init` leg, because PM-KISAN sends no OTP.

One action is an exception, and the pack names it. On `support` the payload has no
`Commitment` to sit on, so it attaches through `Support.channels`, and one field leaves
the attributes object for a `Support` slot of its own: `enrolmentId` becomes `orderId`.
`x-beckn-container-by-action` on the root schema records which container each action
uses; `x-beckn-path` on that field records where it goes. A field with no `x-beckn-path`
never moves.

A second field exists only on that leg, and it is there so the request can be routed at
all. The adapter picks the upstream call from a binding key, `participantId|capabilityCode`,
and reads both halves out of the payload. On every other action the payload composes a
`Contract`, so the participant is read from `commitments[].offer.provider.id`. A
`SupportAction` composes no contract, and `Support` is sealed at three fields, none of
which names a participant — so the channel carries `provider` instead, a Beckn `Provider`
narrowed to a reference: an `id` and a descriptor carrying a name.

It is the same shape the contract legs supply, so a reader writes `.provider.id` on both,
and the adapter's binding path reads `channels[].provider.id` against a Beckn v2 default of
`commitments[].offer.provider.id` — the same grammar, the same tail, a different container.
The name is advisory and never routed on: the registry owns that word, and a caller who
sends a stale one still reaches the right provider. `scheme.code` is not a substitute: it
names a scheme rather than a participant, and it reads `PM-KISAN` where the registry holds
`pmkisan`.

`Support.orderId` carries the registration number. The spec defines `orderId` as the thing "against which support is required", and on PM-KISAN that thing is the farmer's enrolment: the upstream takes exactly one reference, `IdentityNo`, and nothing in the API names a case, a policy or an application. The registration number is therefore both the identity the portal authenticates on and the subject of the complaint. One value, one slot — and the same slot PMFBY uses for its application number.

`enrolmentId` is not marked `no-echo`, where an earlier draft made it so. `orderId` is the provider's to fill on the way back, and returning the caller's own registration number over the same signed exchange it arrived on discloses nothing to anyone who did not already hold it. `no-log` and `no-trace` are the markings that protect it, and those are unconditional. The echo is confined to `on_support`: a `Contract` has no `orderId`, so nothing carries it back on a case read.

The grievance is lodged through `support`, not `confirm` — the rationale and the live flow are both in `docs/grievance-usecase.md`. `x-beckn-container-by-action` therefore has no `confirm` entry. The privacy markings travel with the field wherever it sits: `no-log` and `no-trace` on `enrolmentId` hold just as firmly in `Support.orderId` as in the attributes object.

## The two gates

Both are top-level `anyOf` members, and both are tested against the real validator.
`if`/`then` would read more naturally and does not work: the validator parses it and
never evaluates it, so a guard written that way looks like it holds and does not.

**A `Direct` payload must carry a case** — a `case` band with `status` and `filedOn` in
it. That is the whole of it, because it is the whole of what a lodge reply and a case
read have in common: the lodge reply echoes the complaint, the case read carries the
latest remark instead. `ticketNo` is allowed and is populated on a lodge, but it is not
required: the status call is not documented to repeat the handle per record, so a case
read may carry none. See "The identifier, and what it is not good for".

**Every payload must be about something** — a `grievance`, a `case` or an `enrolmentId`.
The same `@type` serves filing and reading, and `informationMode` cannot tell them apart
because both asks are `OnDemand`. What separates them is what the payload brought. Before
the containers existed nothing caught a payload that brought none of them.

There is deliberately no narrower `OnDemand` branch. Lodging sends the registration
number, the category and the complaint; reading sends the registration number and
`case.filedOn`. Requiring the lodge fields here would reject a legitimate read. What each
action must carry is enforced by that action's mapping guard.

## Upstream response coverage

Every field the portal sends back, and where it goes. Nothing is left unaccounted for.

**Lodge reply** — three values, and the portal spells each of them more than one way.
Read each through a fallback chain; this is the v1 adapter's behaviour on `Beckn`'s
`main` branch, and it is reproduced because it is the portal that is inconsistent.

| upstream | here | note |
|---|---|---|
| `GrievanceID` / `grievanceId` / `GrievanceNo` | `case.ticketNo` | **the case identifier.** Whichever name arrives, lands here |
| `Status` / `Responce` / `Rsponce` | — | `"True"` / `"False"`, string-valued; becomes the ACK or a NACK, not a field. Absent means success on this leg, so test for `"False"` rather than for `"True"` |
| `Message` / `message` / `Remark` | *dropped* | the portal's own text, never returned; logged redacted |

So a lodge response carries one portal value and no more. `case.status.code` is asserted
`Registered` with no `name`, `case.filedOn` is the request's own date, `provider` is the
registry entry the adapter routed to, and the `grievance` band is the caller's own words
echoed back.

**Case read** — the record the portal returns, all fourteen fields:

| upstream | here | note |
|---|---|---|
| `GrievanceDate` | `case.filedOn` | an IST calendar date |
| `GrievanceDescription` | `grievance.description` | verbatim |
| `GrievanceStatus` | `case.status` | the portal returns it; the legacy direct client's model drops it, so it is missing from any sample taken there. See "Case status" |
| `OfficerReply` | `case.remark` | the network does not adopt the portal's field name; see "Case remark" |
| `OfficeReplyDate` | `case.remarkedOn` | an IST calendar date |
| `Reg_No` | *dropped* | the registration number the farmer sent. A `Contract` has no `orderId` to return it in, and it is not surfaced as an attribute either: it is matched against the number the caller sent, then discarded. |
| `Farmer_Name` | *dropped* | personal data |
| `Father_Name` | *dropped* | personal data |
| `Gender` | *dropped* | personal data |
| `MobileNo` | *dropped* | personal data |
| `StateName` | *dropped* | personal data |
| `DistrictName` | *dropped* | personal data |
| `BlockName` | *dropped* | personal data |
| `RevenueVillageName` | *dropped* | personal data |

Nine of fourteen are dropped. That is the point of the allow-list.

The category is not in the record either — a read cannot tell you what the grievance was
about. `Reg_No_Status` sends no `GrievanceType` back, which is why the base leaves
`grievance.category` optional and why a case read returns a `grievance` band holding the
description alone. Where a response does carry a category, it is the value the caller
sent, echoed.

The v1 gateway also emits a `grievance-id` tag. It is the portal's `GrievanceID`, the
same value this pack carries in `case.ticketNo`. See "The identifier, and what it is not
good for" below.

## The identifier, and what it is not good for

**The portal does issue a case identifier.** The lodge reply carries it as `GrievanceID`, or as `GrievanceNo` where that is absent, and it lands in `case.ticketNo`. An earlier revision of this pack refused the field outright, on the reading that PM-KISAN issued nothing of the kind. That reading came from one client — the direct portal client's response model does not declare the field, so it was dropped before anyone saw it. The v1 Beckn adapter reads it from the same reply.

**It is not a read key.** `/GrievanceStatusCheck` takes an identity and returns **every** grievance on it; there is no per-grievance endpoint and no documented way to ask for one. The status records are not documented to repeat the handle either, so the adapter cannot even match on it after the fact.

So the retrieval story is unchanged: `case.filedOn` is what picks the grievance out of the list. Note where that date comes from — the lodge reply carries none, so it is the filing date the network itself recorded, not a value the portal confirmed. It is sent back on the read and matched against each record's `GrievanceDate`. **Two grievances filed on the same identity on the same day are indistinguishable.** That is recorded as a limitation rather than papered over.

What the identifier does buy is a handle the farmer can quote — to the portal's own helpline, or back to the network. That is why the field is allowed and populated rather than refused.

**What would close the collision:** a `/GrievanceStatusCheck` that accepts the grievance id, or at minimum one that repeats it per record. Either is a question for PM-KISAN.

## Nothing on file

A read that matches no case is an answer, not a failure — but it is stated rather than
implied. It comes back as a `202` with Beckn's `AckNoCallback` body and the error code
`BIZ_NO_RESULTS_FOUND`, with `status: "ACK"` because the request was accepted and processed.
No attribute of this pack appears, and no `informationMode` value describes it.

An earlier draft returned a commitment with `commitmentAttributes` omitted instead. That is
spec-legal, since the property is optional, but a missing field is not a message: a consumer
cannot tell an absent case from a provider that dropped the field. Nor would an empty
`resources` array help — the resource is a fixed catalog pointer that says nothing about
whether a case exists — and `Contract.commitments` has `minItems: 1`, so returning no
commitment at all was never available.

## Composition

`PMKISANGrievance` extends **`GrievanceBase`**, in
[`api-schemas/Grievance/v0.1`](../../Grievance/v0.1/attributes.yaml). The base owns the
four bands and the vocabulary they are written in: `informationMode`, `provider`,
`scheme` and `enrolmentId` at the top, the `Grievance` and `Case` containers, and the
`CaseStatusCode` list, `CalendarDate` and `ProviderReference` beside them. One
definition, both packs; a change to the case vocabulary is one edit, not two kept in step
by review.

`Grievance/v0.1` is not itself a pack. There is no `profile.json` beside it, so it is
never indexed, and nothing ever sends `@type: openagrinet:GrievanceBase`.

**PM-KISAN adds no field of its own.** Everything it sends and everything it returns is
in the base; the whole of this file is pinning, refusal and notes — `@type` and
`scheme.code` pinned to PM-KISAN, `enrolmentId` narrowed to an ASCII alphanumeric
registration number, the closed category vocabulary declared, `grievance.subCategory`
refused, `case.ticketNo` annotated, and the two gates stated. That is the measure of whether the
base is drawn right.

`@type` stays out of the base: it is the pack's identity, so a base could only accept any
string. `grievance.category` is declared in the base but its IRI is pinned here, to
`openagrinet:pmkisanGrievanceCategory`, against a closed ten-value list the PMFBY pack
does not share.

Each inherited field is restated here with a `description` only, recording which upstream
field PM-KISAN fills it from. The shape, the bounds and the IRI stay with the base; the
published page shows both halves.

A grievance is a Provider's API surface, not a thing the network describes, so the base
lives beside the packs in `api-schemas/` and nothing grievance-related is added to a
domain schema. The one thing both reach outside for is `IdentifiedDescriptor`, which the
domain schemas already publish and which wraps Beckn's `Descriptor` for `scheme`,
`grievance.category` and `case.status`.

It does not compose the Agriculture Resource field set: that set is framed around a
Resource holding information, which this pack is not.

## What this pack refuses

One inherited field is refused with `not`/`required` rather than left defined and never
filled, so a caller who sends one is told rather than quietly ignored:

- **`grievance.subCategory`** — PM-KISAN classifies at one level. PMFBY numbers and names
  two.

Nothing else is refused. `case.ticketNo` was, in an earlier revision, and is not any
more: the portal issues one. See "The identifier, and what it is not good for".

## Where each field travels

Two things move between legs, and they are easy to confuse.

**The attributes object itself moves.** On `status` it is
`message.contract.commitments[].commitmentAttributes`. On `support` there is no
contract to hang it from, so it becomes a support channel:
`message.support.channels[0]`. `x-beckn-container-by-action` states this, and
lists those two actions only — PM-KISAN has no `init` leg.

**One field moves out of it.** `x-beckn-path` relocates `enrolmentId` into Beckn's own
`orderId` slot, so a client that has never read this pack still sees a support request
with a subject on it.

| Field | on `support` | on `status` |
|---|---|---|
| `enrolmentId` | `support.orderId` | in attributes — `x-beckn-path` names no status slot |
| `provider` | in attributes (`channels[0]`) | absent — read `commitments[].offer.provider`, which is the same shape |

Everything else stays inside the attributes object wherever that object happens
to be — both containers included. Published examples show the logical form, every field
inline; they are not wire payloads.

## Fields

"Required when" describes a complete payload of that kind. It does not make the field
mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@type` | Always | Identifies the commitment as `openagrinet:PMKISANGrievance` |
| `informationMode` | Always | `OnDemand` is the ask; `Direct` carries a real case |
| `scheme` | Always | Scheme the grievance is raised against; present in both directions |
| `provider` | `support` legs | Beckn `Provider` reference — `id` routes the request, `descriptor.name` makes the payload readable. The adapter composes no `Contract` on this leg, so it has nowhere else to read the provider from |
| `enrolmentId` | Every ask | The farmer's PM-KISAN registration number — both the identity the portal authenticates on and the enrolment the complaint is against. On `support` it is `orderId` |
| `grievance.category` | Ask, when lodging | One of ten published codes, `G001`–`G010`. Echoed on a lodge response; absent from a case read, whose per-record payload carries no category field |
| `grievance.description` | Ask, when lodging; returned on a case read | The farmer's account of the problem, minimum ten characters |
| `case.status` | `Direct` | Where the grievance stands. `code` is the network's `CaseStatusCode` and is what you branch on; `name` is the portal's own phrase, present only when the portal supplied one — see below |
| `case.filedOn` | `Direct` | Date the grievance was filed, as an IST calendar date. Read from the portal on a case read; generated on a lodge. Also half the case selector |
| `case.remark`, `case.remarkedOn` | Optional in `Direct` | Absent rather than null while nothing has been recorded. `remark` is bounded at 2000 characters |

A payload that carries `grievance` carries its `description`: `required` inside the block
fires whenever the block is present. `category` is not in that list, because a case read
returns a `grievance` band with no category in it. Whether a caller must choose one to
file is an action-level rule, enforced by the `support` mapping guard.

## Grievance categories

Unlike PMFBY, the portal publishes a closed list, so the pack enumerates it and an unknown code is refused at the network edge rather than upstream. The code goes to the portal verbatim as `GrievanceType`.

| Code | Meaning |
|---|---|
| `G001` | Account number not correct |
| `G002` | Online application pending for approval |
| `G003` | Installment not received |
| `G004` | Transaction failed |
| `G005` | Problem in Aadhaar correction |
| `G006` | Gender not correct |
| `G007` | Payment related |
| `G008` | Problem in OTP-based eKYC |
| `G009` | Problem in biometric-based eKYC |
| `G010` | Problem in facial-based eKYC |

## Category term

The JSON key is `grievance.category` in both grievance packs, but it resolves to `openagrinet:pmkisanGrievanceCategory` here and to `openagrinet:pmfbyGrievanceCategory` in the PMFBY pack. The two schemes publish incompatible value spaces — a closed `G001`–`G010` list against PMFBY's numeric ids — so one IRI could not hold both. Payloads are unaffected; only the context mapping differs.

## Case status

`case.status.code` is the network's `CaseStatusCode`; `case.status.name` is the portal's own `GrievanceStatus` phrase, kept verbatim. The two are independent facts, which is why only `code` is governed.

Where the portal publishes a `GrievanceStatus`, the phrase goes into `name` and the adapter maps it to a `CaseStatusCode`. A phrase it does not recognise maps to `UnderReview` — never to a terminal state, which must come from the portal — and the phrase survives in `name`, so nothing fails and nothing is lost.

Where the portal publishes no status, the adapter infers one and emits `code` alone:

- `Registered` — a lodge reply, which carries no status of any kind, that did not report failure.
- `Replied` — a status record with a remark but no `GrievanceStatus`.
- `UnderReview` — a status record with neither.

**The absence of `name` is the signal.** A caller can tell the portal's own word from the network's inference by whether `name` is there, which the earlier design could not express.

## Case remark

The portal's field is `OfficerReply`; the network's is `case.remark`. The name is not adopted, for two reasons. A network term should not be one portal's internal field name — and the base has to name something PMFBY could fill too, which today it cannot: that portal publishes no remark at all and refuses both fields. And PM-KISAN is not consistent about who writes it: the companion date is `OfficeReplyDate`, an office rather than an officer. Naming the field for the case rather than for an author claims only what we can show.

## Privacy

Every field carrying personal data is marked in `attributes.yaml` with `x-oan-pii`:

```yaml
x-oan-pii:
  class: identifier
  handling: [no-log, no-trace]
```

`class` is one of `identifier`, `contact`, `credential` or `freetext`. `handling` draws on
`no-log`, `no-trace`, `no-echo`, `no-forward` and `mask-on-echo`.

The marking is inert — the extended-schema validator ignores `x-` keys, exactly as it
ignores the `if`/`then` branches. It exists so the rule can be read by a tool rather than
only by a person: a CI check can assert that no property marked `no-echo` appears in any
`Direct` example, which is the class of mistake the v1 `identity-no` echo was.

**Neither `writeOnly` nor `readOnly` appears in this pack**, and that is deliberate. The
validator visits every payload with `VisitAsRequest`, on the way out as well as in, so
`writeOnly` would assert nothing and `readOnly` would reject the very response it
describes. Direction is carried by `x-oan-pii`, which the adapter reads, and it is
unconditional.

`enrolmentId` is `no-log` and `no-trace` without exception: it is never written to a log, attached to a trace, or included in an error body. It is a bearer key as much as an identifier — anyone holding a registration number can read every remark recorded against it — so those two markings are the ones doing the work.

It is **not** `no-echo`, and the distinction is deliberate. Returning it in `Support.orderId` on `on_support` gives it back to the caller who sent it, over the same signed exchange, and tells them nothing new. That is the only place it comes back.

The v1 adapter's behaviour is still forbidden. It returns `identity-no` and `lookup-type` tags **on a case read**, where the caller asked about an identity and the response re-publishes it as loose tags outside any slot the spec defines. A v2 adapter must not carry that over: on `status` the registration number is consumed, not surfaced. The portal returns it with every record; it is matched against the number the caller sent and then discarded. It appears in no attribute and in no identifier — an earlier draft keyed the resource id on it, which would have put the registration number in a public, cacheable identifier rather than in a field the caller supplied.

Aadhaar is deliberately not accepted in `enrolmentId`. The portal takes a token derived from one and carries it in the same `IdentityNo` field, which would make this value sometimes a stable reference and sometimes an ephemeral secret. Neither an Aadhaar number nor any token derived from one may be logged, traced, or returned in any response or error body.

`grievance.description` is free text that may contain personal details the schema cannot constrain.

**The status record carries far more about the farmer than this pack surfaces.** Alongside the grievance itself it returns the farmer's name, father's name, gender, mobile number, and state, district, block and village. None of it is modelled here and none of it is emitted, which is deliberate: it is not part of a grievance, the caller already knows who they asked about, and publishing it would disclose more than the identity the pack goes to some trouble to withhold. An adapter must drop these fields rather than pass them through — the pack cannot stop it, because `commitmentAttributes` is open.

## Stricter than the upstream client

Three constraints are tighter than what the upstream client would pass through:

- `grievance.category.code` is closed to the ten published codes; the client checks the label it was handed, not the code, so a code reaching it by any other route is forwarded unchecked.
- `grievance.description` requires ten characters; the portal takes an empty string.
- `enrolmentId` must be **ASCII** alphanumeric. The upstream accepts Devanagari, Bengali and Tamil digits and forwards them to the portal unconverted. The pattern refuses them at the edge instead.

Two places the pack is deliberately *not* stricter:

- The registration number is checked only for "non-empty alphanumeric". Eleven alphanumeric characters is the documented shape, but nothing upstream enforces it and the only source is a tool docstring; a length rule built on that would reject a valid grievance before the farmer's complaint reached the portal.
- `grievance.description`'s length is measured on the raw string. The upstream client measures it after trimming, so ten characters of whitespace pass here and fail there. Tightening it would need a regex that rejects payloads the portal accepts, so the adapter trims and re-checks instead.

## Non-goals

This pack does not describe the transport envelope. The portal payload travels encrypted and the response arrives wrapped; both belong to the adapter, and neither the ciphertext nor the service token appears here or in any payload this pack describes.

Two fields the portal returns are absent because the mapping consumes them: the success flag — arriving as `Status`, `Responce` or `Rsponce`, string-valued, and sometimes missing on a lodge, always present on a status check — which decides between a response and an error, and the message — `Message`, `message` or `Remark` — which is transport chatter. The farmer and address fields listed under Privacy are absent because they are withheld, which is a different thing.

It also does not define credentials. Those live in the adapter configuration, where credentials are named by environment variable and never held.

## Examples

The two `Direct` examples show the inferred form of `case.status` — `code` with no `name`. No sample of the portal's own `GrievanceStatus` text exists anywhere in the legacy tree, so rather than invent one the examples demonstrate the inference branch only.

- [On-demand: lodge a grievance](examples/on-demand-lodge-grievance.json)
- [On-demand: read a case](examples/on-demand-read-cases.json)
- [Direct: grievance registered](examples/direct-grievance-registered.json)
- [Direct: grievance with a remark recorded](examples/direct-grievance-replied.json)
