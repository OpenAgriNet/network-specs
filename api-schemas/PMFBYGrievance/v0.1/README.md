# PMFBY Grievance

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

Describes what the PMFBY grievance API accepts and what it returns, so an experience layer can call it from the schema alone without reading adapter mapping files.

This is an API schema, not a domain schema. A domain schema says what a thing *is* in the agriculture domain; this one says what one named Provider's API will take and give back.

## Attachment point

Applied to `commitmentAttributes` of a Beckn `Commitment`, not to
`resourceAttributes`.

A grievance is a promise with a lifecycle, not a catalogable thing of value.
`resourceAttributes` is defined as "all the properties of a resource that
describe its value, its terms of usage, fulfillment, and consideration", and a
`Resource` is what a Provider publishes in a catalog. One farmer's phone number,
ticket number and case status are none of those, and would be nonsense in a
catalog entry. `Commitment` is "a specific promise... and the current lifecycle
status of that promise", and its `DRAFT | ACTIVE | CLOSED` states are the
grievance's own.

The `Resource` does not disappear — `Commitment.resources` carries one, and each
entry needs an `id` and a `quantity`. It stays thin: a pointer to the catalogable
"grievance handling" entry the offer references. Its id is fixed for the provider
(`res:pmfby:grievance`) rather than minted per case, and it does not change across the
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

## The three bands

**The band a field sits in says who wrote it.**

| band | holds | written by |
|---|---|---|
| top level | who is asking and about what: `informationMode`, `provider`, `scheme`, `enrolmentId`, and the PMFBY-only `applicantPhone`, `cropYear`, `season` | the caller |
| `grievance` | what the farmer submitted: `category`, `subCategory`, `description` | the farmer |
| `case` | what the portal has on file, the stamps it applied included: `ticketNo`, `status`, `filedOn`, `cropName` | the portal |

The base has five bands. PMFBY uses three. `challenge` and `challengeIssued` belong to
the PM-KISAN packs — FGMS has no OTP endpoint, so neither band could ever be filled
honestly here, and this pack refuses both outright rather than leave them defined and
unfillable.

`challengeMethods` sits in no band. It is published on the catalog entry and never sent
on a payload, and it is what a caller reads to know whether this desk challenges it
before filing. PMFBY publishes it empty, which is how a caller learns there is nothing
to ask for.

Before the containers the same split lived in a prefix — `grievanceCategory` against
`caseStatus` — which read the same and checked nothing: a field named either way
validated either way. As containers the split is enforced, and `grievance` becomes all
or nothing, because `required` inside a block fires whenever the block is present.

Nothing rides in a Beckn `descriptor`. An earlier draft hoisted the category and the
farmer's words there, which read well and checked nothing: a `Descriptor` is three
free-text strings, so the category, the sub-category and the complaint all validated as
any string at all. The join was lossy too — PMFBY's own category name contains the
separator the names were joined on (`Enrollment / Portal Issues` + `Login`), so no split
could recover the pair. As fields inside `grievance` each one has bounds the pack holds.

## Direction, not action

Direction is carried by `informationMode`, never by the Beckn action. `OnDemand` is the ask; `Direct` is an answer carrying a real case. The same attributes therefore serve `support` and `status` without change.

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
names a scheme rather than a participant, and it reads `PMFBY` where the registry holds
`pmfby`.

`Support.orderId` means the same thing in both directions. The spec defines it as the thing "against which support is required", which is an ask-side meaning, and nothing about a reply changes what the complaint is against — so `on_support` echoes the enrolment back unchanged rather than overwriting it. The ticket the portal issues is a different thing and lives in a different place: `case.ticketNo`. This is the same rule PM-KISAN follows, where `orderId` is the registration number on both legs and the portal's own `GrievanceID` rides in `case.ticketNo`. One field, one meaning, both schemes.

The grievance is lodged through `support`, not `confirm` — the rationale and the live flow are both in `docs/grievance-usecase.md`. `x-beckn-container-by-action` therefore has no `confirm` entry. The privacy markings travel with the field wherever it sits: a `no-echo` field is still `no-echo` in a `Support` slot.

## The two gates

Both are top-level `anyOf` members, and both are tested against the real validator.
`if`/`then` would read more naturally and does not work: the validator parses it and
never evaluates it, so a guard written that way looks like it holds and does not.

**A `Direct` payload must carry a case.** A response with no case standing is not an
answer, so `Direct` requires a `case` band with `ticketNo`, `status` and `filedOn` in it.
On a case read the ticket number is the one the caller asked with, echoed — the portal
does not return it.
That is true of `on_support` and `on_status` alike. `provider` is not in the list: on a
contract leg the same fact lives in `commitments[].offer.provider`, outside these
attributes, where a guard on the attributes object cannot reach it.

**Every payload must be about something** — a `grievance`, a `case`, an `enrolmentId` or
`challengeMethods`. The same `@type` serves filing, reading and discovery, and
`informationMode` cannot tell them apart because every ask is `OnDemand`. What separates
them is what the payload brought. Before the containers existed nothing caught a payload
that brought none of them.

`applicantPhone` is deliberately not in that list. Every ask carries it, so a branch on it
would admit a payload stripped of everything else — a phone number and nothing to be about.

`challengeMethods` is in that list for the catalog entry alone. A declaration states what
this desk needs and asks for nothing, so it brings no `grievance`, no `case` and no
enrolment. Without the branch the gate would reject the very entry a caller discovers the
desk by.

There is deliberately no narrower `OnDemand` branch. The ask side has no field common to
every payload: filing sends the phone, the enrolment, the season and the complaint;
reading a case sends the phone and the ticket; the catalog entry sends none of them. What
each action must carry is enforced by that action's mapping guard.

## Upstream response coverage

Every field the portal sends back, and where it goes. Nothing is left unaccounted for.

**Lodge reply** — `POST /krphapi/FGMS/AddKRPHNCIPGrievenceSupportTicket`. The FGMS
envelope plus two values inside `responseDynamic`:

| upstream | here | note |
|---|---|---|
| `responseCode` | `case.status` | the lodge reply states no status, so `"1"` asserts `code: Registered` and no `name` accompanies it. Compare the stringified value: it has been seen as both a string and a number |
| `responseDynamic.GrievenceSupportTicketNo` | `case.ticketNo` | the number the farmer is told |
| `responseDynamic.GrievenceSupportTicketID` | *dropped* | the portal's own row id. An internal key with no consumer: nothing sends it and the read is keyed on the ticket *number* |
| `recordCount` | *dropped* | a count of a single record |
| `responseMessage` | *dropped* | the portal's own text. It may carry a stack trace, an internal hostname, or a quoted-back credential, so it is never returned. Log it redacted and return our own message. |

`case.filedOn` and `provider` are not in the reply. The adapter asserts them — `filedOn`
from the request's own filing date, `provider` from the registry entry it routed to. They
are network-asserted, not portal-reported, and a caller cannot tell the difference from
the payload. That is a known weakness. `case.status` no longer has it: an inferred status
carries `code` alone, so the absent `name` tells a caller the portal did not say so.

**Case read** — the record is much richer than the lodge reply. Every field it carries.

**Verified.** `POST /krphapi/FGMS/GetGrievenceTicketsStatus`. The twelve
`responseDynamic` fields are read from the v1 adapter on `Beckn`'s `main` branch; see
`docs/grievance-upstream-contracts.md` §0, which is the master reference for what each
portal actually sends.

| upstream | here | note |
|---|---|---|
| `ApplicationNo` | `enrolmentId` | |
| `GrievenceDescription` | `grievance.description` | |
| `TicketCategoryName` | `grievance.category.name` | **no id accompanies it.** The id goes up on the lodge as `ticketCategoryID` and does not come back |
| `TicketSubCategoryName` | `grievance.subCategory.name` | likewise. Two levels, kept apart: the portal's own category name contains a slash, so any joined form would be lossy |
| `TicketStatus` | `case.status` | the phrase verbatim into `name`; mapped to a `CaseStatusCode` for `code` |
| `ComplaintDate` | `case.filedOn` | format unpublished, so the adapter normalises to an IST calendar date |
| `CropName` | `case.cropName` | the insured crop. A field this pack adds rather than inherits |
| `GrievenceSupportTicketID` | *dropped* | the portal's row id, not the number the farmer quotes |
| `FarmerName` | *dropped* | personal data |
| `InsuranceCompany` | *dropped* | personal data |
| `StateMasterName` | *dropped* | personal data |
| `DistrictMasterName` | *dropped* | personal data |
| `responseCode` | *consumed* | the success flag the guard tests; not a field |
| `responseMessage`, `recordCount` | *dropped* | the portal's own text, and a count |

Four of the record's fields are personal data and none of them may reach a payload, a log
or a trace; see "Privacy" below. The response mapping is an allow-list, not a passthrough.

Four absences shape this pack:

- **The ticket number is not returned.** The read answers with `GrievenceSupportTicketID`
  instead, which is not mapped, so on a case read the adapter echoes the number the caller
  asked with.
- **No category ids.** Which is why the base pack requires `code` **or** `name` on a
  classification rather than `code` outright.
- **No `requestYear` or `requestSeason` comes back.** `cropYear` and `season` go up on the
  lodge and are absent from every response.
- **No remark, and no remark date.** Nothing in the record resembles a reply from the
  portal, which is why this pack refuses both `case.remark` and `case.remarkedOn` —
  unlike PM-KISAN, which publishes a reply and a date against it.

One thing is still open: `recordCount` sits beside a `responseDynamic` that v1 reads as a
single object. Whether a multi-ticket read returns an array is unconfirmed.

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

`PMFBYGrievance` extends **`GrievanceBase`**, in
[`api-schemas/Grievance/v0.1`](../../Grievance/v0.1/attributes.yaml). The base owns the
five bands and the vocabulary they are written in: `informationMode`, `provider`,
`scheme` and `enrolmentId` at the top, the `Grievance` and `Case` containers, and the
`CaseStatusCode` list, `CalendarDate`, `Instant` and `ProviderReference` beside them. One
definition, both packs; a change to the case vocabulary is one edit, not two kept in step
by review.

`Grievance/v0.1` is not itself a pack. There is no `profile.json` beside it, so it is
never indexed, and nothing ever sends `@type: openagrinet:GrievanceBase`.

This pack adds what PMFBY alone has — `applicantPhone`, `cropYear`, `season` — pins
`@type` and `scheme.code` to PMFBY, pins the value spaces inside the two containers,
refuses the two challenge bands the base makes available, and states the two gates above.

`@type` stays out of the base: it is the pack's identity, so a base could only accept any
string. `grievance.category` and `grievance.subCategory` are declared in the base but
their IRIs are pinned here, to `openagrinet:pmfbyGrievanceCategory` and
`openagrinet:pmfbyGrievanceSubCategory`, against a numeric value space the PM-KISAN pack
does not share.

Each inherited field is restated here with a `description` only, recording which upstream
field PMFBY fills it from. The shape, the bounds and the IRI stay with the base; the
published page shows both halves.

A grievance is a Provider's API surface, not a thing the network describes, so the base
lives beside the packs in `api-schemas/` and nothing grievance-related is added to a
domain schema. The one thing both reach outside for is `IdentifiedDescriptor`, which the
domain schemas already publish and which wraps Beckn's `Descriptor` for `scheme`, the two
category levels and `case.status`.

It does not compose the Agriculture Resource field set: that set is framed around a
Resource holding information, which this pack is not.

`case.remark` and `case.remarkedOn` are both refused outright, with a single
`not`/`anyOf`/`required`: PMFBY publishes neither. Two members to delete if the portal
ever starts publishing them. In their place the pack adds `case.cropName`, which the
portal does publish and a generic grievance base has no reason to define.

## Where each field travels

Two things move between legs, and they are easy to confuse.

**The attributes object itself moves.** On `status` it is
`message.contract.commitments[].commitmentAttributes`. On `support` there is no
contract to hang it from, so it becomes a support channel:
`message.support.channels[0]`. `x-beckn-container-by-action` states this.

**One field moves out of it.** `x-beckn-path` relocates `enrolmentId` into Beckn's own
`orderId` slot, so a client that has never read this pack still sees a support request
with a subject on it.

There is no `init` column. PMFBY publishes no challenge, so the flow opens at `support`
and the only contract leg is `status`.

| Field | on `support` | on `status` |
|---|---|---|
| `enrolmentId` | `support.orderId` | in attributes — `x-beckn-path` names no status slot |
| `provider` | in attributes (`channels[0]`) | absent — read `commitments[].offer.provider`, which is the same shape |

Everything else stays inside the attributes object wherever that object happens to be —
both containers included. Published examples show the logical form, every field inline;
they are not wire payloads.

## Fields

"Required when" describes a complete payload of that kind. It does not make the field
mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@context` | Always | The JSON-LD context these terms resolve against. Pinned to this pack's own; an array when a Provider publishes extra `@type` values |
| `@type` | Always | Identifies the commitment as `openagrinet:PMFBYGrievance` |
| `informationMode` | Always | `OnDemand` is the ask; `Direct` carries a real case |
| `scheme` | Always | Scheme the grievance is raised against; present in both directions |
| `provider` | `support` legs | Beckn `Provider` reference — `id` routes the request, `descriptor.name` makes the payload readable. The adapter composes no `Contract` on this leg, so it has nowhere else to read the provider from |
| `applicantPhone` | Every ask | Ten-digit mobile of the farmer. The portal files it on the ticket and matches a ticket to the phone it was filed from, so reading a case needs it too. Nothing proves the caller holds it — PMFBY asks for no OTP. Never echoed |
| `enrolmentId` | Ask, when filing; also returned in `Direct` | Crop insurance application number the grievance concerns. Carried as `orderId` on `support` |
| `cropYear`, `season` | Ask, when filing | Four-digit crop year, and one of `Kharif`, `Rabi`, `Zaid`. They qualify the enrolment, not the complaint, so they sit at the top |
| `grievance.category`, `grievance.subCategory` | Ask, when filing; also returned in `Direct` | Two levels, each with the portal's numeric `code` and its own `name`. Kept apart because the portal numbers and names them separately at both ends |
| `grievance.description` | Ask, when filing; also returned in `Direct` | The farmer's account of the problem, minimum ten characters |
| `case.ticketNo` | `Direct`; also the ask when reading a case, alongside `applicantPhone` | Portal grievance ticket number |
| `case.status` | `Direct` | Where the grievance stands. `code` is the network's `CaseStatusCode` and is what you branch on; `name` is the portal's own phrase, present only when the portal supplied one |
| `case.filedOn` | `Direct` | Date the grievance was filed, as an IST calendar date |
| `case.cropName` | Optional in `Direct` | The insured crop the ticket was raised against, as the portal names it. Free text, shown to the farmer, never branched on. Added by this pack; `case.remark` and `case.remarkedOn` are refused, because PMFBY publishes neither |
| `challengeMethods` | The catalog entry only | Pinned empty. It says this desk challenges nothing, so the sequence is `support` → `status`. Never sent on a transaction |

A payload that carries `grievance` carries all three of its fields: `required` inside the
block fires whenever the block is present, so a partial complaint is rejected rather than
half-filed.

## No challenge

**PMFBY's grievance service issues no challenge, so this pack carries none.** `challengeMethods`
is pinned `maxItems: 0` and the catalog entry publishes `[]`. Both bands the shared base
makes available are refused outright:

```yaml
- not:
    anyOf:
      - required: [challenge]
      - required: [challengeIssued]
```

A payload carrying either is rejected rather than quietly ignored, so a caller that assumed
an OTP step is told so at the edge instead of having its proof silently dropped.

The field is published empty rather than omitted. Empty is an answer; absent is a question.
A caller reading `[]` knows to open at `support`.

PMFBY does operate an OTP pair — `/api/v1/services/nic/getOtp` and `/verifyMobile` — but it
sits on the core realm, behind different credentials, and belongs to the policy flow. It
takes a mobile number and sends a code to whatever number it is handed; it never sees an
application number and so proves no link between the caller and the policy they are
complaining about. Borrowing it would impose a control the portal never asked for and would
not deliver the assurance its presence implies.

**The consequence is worth stating plainly: filing here is unauthenticated.** Nothing proves
a caller is the farmer. Anyone holding an application number can lodge a grievance against
it, and PMFBY application numbers have visible structure. That is the portal's own posture,
not a gap this network introduces — but it is worth raising with PMFBY, and any control it
wants belongs on FGMS beside the lodge rather than borrowed from another realm.

If PMFBY ever adds a challenge to FGMS, widen `challengeMethods` and restore the two bands.
Nothing else moves.

## Category term

The JSON keys are `grievance.category` and `grievance.subCategory` in both grievance
packs, but here they resolve to `openagrinet:pmfbyGrievanceCategory` and
`openagrinet:pmfbyGrievanceSubCategory`, and in the PM-KISAN pack to the `pmkisan…`
pair. The two schemes publish incompatible value spaces — PMFBY's numeric ids against a
closed `G001`–`G010` list — so one IRI could not hold both. Payloads are unaffected; only
the context mapping differs. PM-KISAN has no second level and refuses `subCategory`
outright.

## Privacy

Every field carrying personal data is marked in `attributes.yaml` with `x-oan-pii`:

```yaml
x-oan-pii:
  class: contact
  handling: [no-log, no-trace, no-echo]
```

`class` is one of `identifier`, `contact`, `credential` or `freetext`. `handling` draws on
`no-log`, `no-trace`, `no-echo`, `no-forward` and `mask-on-echo`. `mask-on-echo` is for a
value that *is* returned in a masked form; it says nothing beside `no-echo`, which already
means the value never comes back at all, so the two are never listed together.

The marking is inert — the extended-schema validator ignores `x-` keys, exactly as it
ignores the `if`/`then` branches. It exists so the rule can be read by a tool rather than
only by a person: a CI check can assert that no property marked `no-echo` appears in any
`Direct` example, which is the class of mistake the v1 `identity-no` echo was.

**Neither `writeOnly` nor `readOnly` appears in this pack**, and that is deliberate. The
validator visits every payload with `VisitAsRequest`, on the way out as well as in, so
`writeOnly` would assert nothing while `readOnly` would reject the very response it
describes. Direction is carried by `x-oan-pii`, which the adapter reads, and it is
unconditional.

`applicantPhone` is never echoed, and there is nothing to echo it in: this pack issues no
challenge acknowledgement, so no masked destination is returned anywhere.

`enrolmentId` identifies a named farmer's policy, and `grievance.description` is free text that may contain personal details the schema cannot constrain. Neither belongs in a payload dump.

The portal's case record carries far more about the farmer than this pack surfaces: name, mobile number, email, and the full state / district / sub-district / panchayat / village hierarchy, alongside the insurance policy number and insurer. The adapter must drop all of it and map only the fields listed above. None of it may reach `commitmentAttributes`, a log, or a trace. This is the same class of mistake as the v1 `identity-no` echo, and it is the reason the response mapping is an allow-list rather than a passthrough.

## Stricter than the portal

Three constraints are tighter than what the portal itself would take, and are deliberate:

- `applicantPhone` requires an Indian mobile series (`^[6-9]`); the portal checks only that ten digits arrived.
- `cropYear` requires four digits; the portal takes any digit string.
- `season` is closed to three values; the portal takes the numeric codes the adapter produces.

Each rejects at the network edge something the portal would have rejected later, or would have accepted as nonsense.

## Non-goals

This pack does not define the grievance category list. The portal publishes no enumeration
of valid pairs; it returns a name for whichever pair a case was filed under — `3` is
`Enrollment / Portal Issues`, `10` is `Login` — but there is no endpoint that lists them.
The `code` patterns therefore constrain only "digits", and each `name` is whatever came back.

Category `3` / `10` is the only pair in use today, because v1 hardcoded it for every
grievance regardless of subject. That is a v1 defect carried in the data, not a portal
constraint, and v2 does not repeat it: the category is a caller-supplied field. When the
portal exposes its list the experience layer starts sending a real choice and nothing in
this pack changes.

Two fields the portal requires are optional here, because a caller usually has no reason to set them: `complaintDate` defaults to the current IST date at lodge time, and `receiptSourceId` defaults to the channel id this adapter is configured with. Both are defined so a caller that does hold the value can send it -- a replayed offline submission carrying its original filing date, or a channel holding an id PMFBY issued to it directly. One field the portal returns is absent outright: `GrievenceSupportTicketID` is the portal's own row id, which the farmer never quotes and no call takes.

It also does not define credentials or transport. Those live in the adapter configuration, where credentials are named by environment variable and never held.

## Examples

- [On-demand: file a grievance](examples/on-demand-file-grievance.json)
- [On-demand: read an existing case](examples/on-demand-read-case.json)
- [On-demand: the catalog entry](examples/on-demand-capability.json)
- [Direct: lodge reply, as the portal sends it](examples/direct-grievance-registered.json)
- [Direct: grievance under review, read from the portal](examples/direct-grievance-under-review.json)
