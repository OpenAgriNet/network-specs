# Grievance

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

Describes what a government scheme's grievance API accepts and what it returns, so an
experience layer can call it from the schema alone without reading adapter mapping files.

Two capabilities, one pack: **file a grievance** and **check its status**. Two schemes
are covered today — PMFBY and PM-KISAN — named by `scheme.code`.

This is an API schema, not a domain schema. A domain schema says what a thing *is* in the
agriculture domain; this one says what a named Provider's API will take and give back.

## One pack, two schemes

The field set is the same for both schemes. What differs is which fields each portal
fills, and with what. So this is one pack with one `@type`, and `scheme.code` says which
desk a payload is for. That borrows the pattern `AgricultureResource` uses for
`subjectCategories` — a governed field names the variant and concrete branches refine
the rest — though here it is one code pinned per branch, not a multi-valued array.

The pinning is structural, not advisory. `Grievance` closes with a `oneOf` over two
branches:

```yaml
oneOf:
  - $ref: "#/components/schemas/PMFBYGrievance"
  - $ref: "#/components/schemas/PMKISANGrievance"
```

Each branch pins `scheme.code` to a different `const`, so they are mutually exclusive by
construction and `oneOf`'s exactly-one semantics are safe: a payload matches the branch
its `scheme.code` names, or no branch at all. A third scheme is a third branch and
nothing else moves.

**Why `oneOf` and not `if`/`then`.** The network's validator is kin-openapi. It parses
`if`/`then` and never evaluates it, so a per-scheme rule written that way looks like it
holds and does not. `oneOf`, `anyOf` and `not` *are* evaluated. Every guard in this pack
is written in those three, and every one of them is tested against the real validator.

The cost is error messages: a failing payload is reported as "no branch matched", not as
a named field. Pinning `scheme.code` per branch is what makes it obvious which branch was
intended.

## Attachment point

Applied to `commitmentAttributes` of a Beckn `Commitment`, not to `resourceAttributes`.

A grievance is a promise with a lifecycle, not a catalogable thing of value.
`resourceAttributes` is defined as "all the properties of a resource that describe its
value, its terms of usage, fulfillment, and consideration", and a `Resource` is what a
Provider publishes in a catalog. One farmer's mobile number, ticket number and case
status are none of those, and would be nonsense in a catalog entry. `Commitment` is "a
specific promise... and the current lifecycle status of that promise", and its
`DRAFT | ACTIVE | CLOSED` states are the grievance's own.

The `Resource` does not disappear — `Commitment.resources` carries one, and each entry
needs an `id` and a `quantity`. It stays thin: a pointer to the catalogable "grievance
handling" entry the offer references. Its id is fixed for the provider
(`res:pmfby:grievance`, `res:pmkisan:grievance`) rather than minted per case, and it does
not change across the lifecycle, so it names the catalog entry and never the case. The
case itself sits beside it on the commitment, and `commitmentAttributes` is the only
thing that differs from one response to the next.

This holds wherever a `Commitment` carries the payload. On `support` there is no
commitment — the payload attaches through `Support.channels` instead. See "Direction, not
action" below.

The spec puts no `minItems` on `Commitment.resources`, so an empty array is legal. This
pack never sends one — see "Nothing on file".

This is deliberately unlike the OAN domain packs. A forecast or a mandi price genuinely
is a resource, and those packs stay on `resourceAttributes`.

## The five bands

**The band a field sits in says who wrote it.**

| band | holds | written by |
|---|---|---|
| top level | who is asking and about what: `informationMode`, `provider`, `scheme`, `enrolmentId`, and the PMFBY-only `applicantMobile`, `cropYear`, `season`, `complaintDate`, `receiptSourceId` | the caller |
| `grievance` | what the farmer submitted: `category`, `subCategory`, `description` | the farmer |
| `case` | what the portal has on file, the stamps it applied included: `ticketNo`, `status`, `filedOn`, `reply`, `repliedOn`, `cropName` | the portal |
| `challenge` | proof of identity, presented with the call it guards: `method`, `value`. Inbound only, never echoed, never forwarded | the caller |
| `challengeIssued` | the portal's acknowledgement that it sent a code: `method`, `length`, `valueType`, `expiresAt`, and a masked `sentTo` where a desk publishes one | the portal |

PM-KISAN uses all five. PMFBY uses three: its grievance service has no OTP endpoint, so
neither challenge band could ever be filled honestly there, and the PMFBY branch refuses
both outright rather than leave them defined and unfillable.

`challengeMethods` sits in no band. It is published on the catalog entry and never sent
on a payload, and it is what a caller reads to know whether this desk challenges it
before filing. PMFBY publishes it empty, which is how a caller learns there is nothing to
ask for; PM-KISAN publishes one pinned entry.

`grievanceOptions` sits in no band either, and for the same reason: it is published on
the catalog entry and never sent. It carries the categories — and, where the desk
classifies at two levels, the sub-categories — this desk accepts, so a caller chooses
from the portal's vocabulary instead of keeping a master list of its own. PMFBY numbers
two levels and publishes both. PM-KISAN numbers one and refuses `subCategories`.

Before the containers the same split lived in a prefix — `grievanceCategory` against
`caseStatus` — which read the same and checked nothing: a field named either way
validated either way. As containers the split is enforced, and `grievance` becomes all or
nothing, because `required` inside a block fires whenever the block is present.

Nothing rides in a Beckn `descriptor`. An earlier draft hoisted the category and the
farmer's words there, which read well and checked nothing: a `Descriptor` is three
free-text strings, so the category, the sub-category and the complaint all validated as
any string at all. The join was lossy too — PMFBY's own category name contains the
separator the names were joined on (`Enrollment / Portal Issues` + `Login`), so no split
could recover the pair. As fields inside `grievance` each one has bounds the pack holds.

## Direction, not action

Direction is carried by `informationMode`, never by the Beckn action. `OnDemand` is the
ask; `Direct` is an answer carrying a real case. The same attributes therefore serve
`init`, `support` and `status` without change.

One action is an exception, and the pack names it. On `support` the payload has no
`Commitment` to sit on, so it attaches through `Support.channels` instead.
`x-beckn-container-by-action` on the root schema records which container each action
uses. That is the whole of it: the container changes, the payload does not. No field
moves out of the attributes object, so every field is read at the same path on every
action — `enrolmentId` included.

The root key carries the union of both schemes' actions — `init`, `status`, `support`.
Strictly `init` belongs to the PM-KISAN branch alone, since PMFBY opens at `support`. But
this key is a network-wide convention used by 14 packs and tooling reads it at the root,
so it stays there and each branch's `x-oan-fields-by-action` says whether `init` applies.
This is the one place the merge is less precise than two separate packs were.

One field exists only on the `support` leg, and it is there so the request can be routed
at all. The adapter picks the upstream call from a binding key,
`participantId|capabilityCode`, and reads both halves out of the payload. On every other
action the payload composes a `Contract`, so the participant is read from
`commitments[].offer.provider.id`. A `SupportAction` composes no contract, and `Support`
is sealed at three fields, none of which names a participant — so the channel carries
`provider` instead, a Beckn `Provider` narrowed to a reference: an `id` and a descriptor
carrying a name.

It is the same shape the contract legs supply, so a reader writes `.provider.id` on both,
and the adapter's binding path reads `channels[].provider.id` against a Beckn v2 default
of `commitments[].offer.provider.id` — the same grammar, the same tail, a different
container. The name is advisory and never routed on: the registry owns that word, and a
caller who sends a stale one still reaches the right provider. `scheme.code` is not a
substitute: it names a scheme rather than a participant, and it reads `PMFBY` where the
registry holds `pmfby`.

**Merging the packs does not collide the binding keys.** The key's first half is the
participant id, which stays distinct (`pmfby`, `pmkisan`) even though the second half now
collapses to one `openagrinet:Grievance` for both. The mapping files are per-participant
per-action and do not change.

`Support.orderId` is not used. It is not required — `Support` has no `required` array at
all — and it means "the order against which support is required", while nothing here is
an order: a grievance is lodged with `support`, not `confirm`, and no `Order` is ever
composed. An order id that resolves to no order leaves a consumer worse off than an
absent one. So `enrolmentId` stays in the attributes object on the `support` leg exactly
as it does everywhere else, and `on_support` echoes it back unchanged — nothing about a
reply changes what the complaint is against. The ticket the portal issues is a different
thing and lives in a different place: `case.ticketNo`. One field, one path, both schemes.

The v1 PM-KISAN adapter is evidence here rather than counter-evidence. It did populate
`order_id`, but with the OTP, not the enrolment; the registration number travelled in a
`reg-details` tag. There is no inherited placement to preserve, and v1's actual use of
the slot — for a credential — is one this design forbids outright.

The grievance is lodged through `support`, not `confirm` — the rationale and the live
flow are both in `docs/grievance-usecase.md`. `x-beckn-container-by-action` therefore has
no `confirm` entry. The privacy markings are properties of the field, not of the
container it rides in: a `no-echo` field is still `no-echo` inside `Support.channels`.

## The gates

Every gate is an `anyOf`, a `not` or a `oneOf`, and every one is tested against the real
validator. Three are stated on both branches, one on PM-KISAN alone and one on PMFBY alone.

**A `Direct` payload must carry a case.** A response with no case standing is not an
answer. PMFBY requires `ticketNo`, `status` and `filedOn`; PM-KISAN requires `status` and
`filedOn` only. The difference is real: PMFBY's read is keyed on the ticket, so the
number is always in hand and echoed back, while PM-KISAN's status call is not documented
to repeat the handle per record, so a case read there may carry none. `provider` is not
in either list: on a contract leg the same fact lives in `commitments[].offer.provider`,
outside these attributes, where a guard on the attributes object cannot reach it.

**Every payload must be about something** — a `grievance`, a `case`, an `enrolmentId`, or
the two declarations a catalog entry carries. The same `@type` serves filing, reading and
discovery, and `informationMode` cannot tell them apart because every ask is `OnDemand`.
What separates them is what the payload brought. Before the containers existed nothing
caught a payload that brought none of them. On PM-KISAN the list adds `challengeIssued`,
which is the whole of an `on_init` acknowledgement.

`applicantMobile` is deliberately not in that list. Every PMFBY ask carries it, so a
branch on it would admit a payload stripped of everything else — a mobile number and
nothing to be about.

`challengeMethods` and `grievanceOptions` are in that list for the catalog entry alone. A
declaration states what this desk needs and what it accepts, and asks for nothing, so it
brings no `grievance`, no `case` and no enrolment. Without the branch the gate would
reject the very entry a caller discovers the desk by. Both are named on the one branch,
so a desk that publishes what it requires without publishing what it accepts — or the
other way round — is refused rather than half-published.

There is deliberately no narrower `OnDemand` branch. The ask side has no field common to
every payload: PMFBY filing sends the mobile, the enrolment, the season and the
complaint; reading a case sends the mobile and the ticket; the catalog entry sends none
of them. What each action must carry is enforced by that action's mapping guard.

**An answer may not carry the `challenge`** (PM-KISAN). The code is sent, never returned.
A payload carrying `challenge` must be a request: `informationMode` not `Direct`, and no
`challengeIssued` beside it, which rules out the `init` acknowledgement as well. The
secret could otherwise have been echoed back and still validated. `x-oan-pii` marks the
value `no-echo`, but that binds the mapping; this is the structural half of the same rule.

**PMFBY refuses both challenge bands** with a single `not`/`anyOf`/`required`. See "PMFBY
issues no challenge".

**A reply date needs a reply.** `case.repliedOn` without `case.reply` is refused on both
branches: a date for an answer nobody wrote is not a fact.

## Upstream response coverage

Every field each portal sends back, and where it goes. Nothing is left unaccounted for.

### PMFBY lodge reply

`POST /krphapi/FGMS/AddKRPHNCIPGrievenceSupportTicket`. The FGMS envelope plus two values
inside `responseDynamic`:

| upstream | here | note |
|---|---|---|
| `responseCode` | `case.status` | the lodge reply states no status, so `"1"` asserts `code: Registered`. Compare the stringified value: it has been seen as both a string and a number |
| `responseDynamic.GrievenceSupportTicketNo` | `case.ticketNo` | the number the farmer is told |
| `responseDynamic.GrievenceSupportTicketID` | *dropped* | the portal's own row id. An internal key with no consumer: nothing sends it and the read is keyed on the ticket *number* |
| `recordCount` | *dropped* | a count of a single record |
| `responseMessage` | *dropped* | the portal's own text. It may carry a stack trace, an internal hostname, or a quoted-back credential, so it is never returned. Log it redacted and return our own message |

`case.filedOn` and `provider` are not in the reply. The adapter asserts them — `filedOn`
from the request's own filing date, `provider` from the registry entry it routed to. They
are network-asserted, not portal-reported, and a caller cannot tell the difference from
the payload. That is a known weakness. `case.status` no longer has it: an inferred status
carries `code` alone, so the absent `name` tells a caller the portal did not say so.

### PMFBY case read

`POST /krphapi/FGMS/GetGrievenceTicketsStatus`. The twelve `responseDynamic` fields are
read from the v1 adapter on `Beckn`'s `main` branch.

| upstream | here | note |
|---|---|---|
| `ApplicationNo` | `enrolmentId` | |
| `GrievenceDescription` | `grievance.description` | |
| `TicketCategoryName` | `grievance.category.name` | **no id accompanies it.** The id goes up on the lodge as `ticketCategoryID` and does not come back |
| `TicketSubCategoryName` | `grievance.subCategory.name` | likewise. Two levels, kept apart: the portal's own category name contains a slash, so any joined form would be lossy |
| `TicketStatus` | `case.status` | mapped to a `CaseStatusCode` for `code`. The phrase itself is not forwarded — the pack refuses `name` |
| `ComplaintDate` | `case.filedOn` | format unpublished, so the adapter normalises to an IST calendar date |
| `CropName` | `case.cropName` | the insured crop |
| `GrievenceSupportTicketID` | *dropped* | the portal's row id, not the number the farmer quotes |
| `FarmerName`, `InsuranceCompany`, `StateMasterName`, `DistrictMasterName` | *dropped* | personal data |
| `responseCode` | *consumed* | the success flag the guard tests; not a field |
| `responseMessage`, `recordCount` | *dropped* | the portal's own text, and a count |

Four absences shape the PMFBY branch:

- **The ticket number is not returned.** The read answers with `GrievenceSupportTicketID`
  instead, which is not mapped, so on a case read the adapter echoes the number the
  caller asked with.
- **No category ids.** Which is why a classification requires `code` **or** `name` rather
  than `code` outright.
- **No `requestYear` or `requestSeason` comes back.** `cropYear` and `season` go up on the
  lodge and are absent from every response.
- **No reply, and no reply date.** Nothing in the record resembles an answer from the
  portal, which is why the PMFBY branch refuses both `case.reply` and `case.repliedOn` —
  unlike PM-KISAN, which publishes both.

One thing is still open: `recordCount` sits beside a `responseDynamic` that v1 reads as a
single object. Whether a multi-ticket read returns an array is unconfirmed.

### PM-KISAN lodge reply

Three values, and the portal spells each of them more than one way. Read each through a
fallback chain; this is the v1 adapter's behaviour, reproduced because it is the portal
that is inconsistent.

| upstream | here | note |
|---|---|---|
| `GrievanceID` / `grievanceId` / `GrievanceNo` | `case.ticketNo` | **the case identifier.** Whichever name arrives, lands here |
| `Status` / `Responce` / `Rsponce` | — | `"True"` / `"False"`, string-valued; becomes the ACK or a NACK, not a field. Absent means success on this leg, so test for `"False"` rather than for `"True"` |
| `Message` / `message` / `Remark` | *dropped* | the portal's own text, never returned; logged redacted |

So a lodge response carries one portal value and no more. `case.status.code` is asserted
`Registered` with no `name`, `case.filedOn` is the request's own date, `provider` is the
registry entry the adapter routed to, and the `grievance` band is the caller's own words
echoed back.

### PM-KISAN case read

All fourteen fields of the record:

| upstream | here | note |
|---|---|---|
| `GrievanceDate` | `case.filedOn` | an IST calendar date |
| `GrievanceDescription` | `grievance.description` | verbatim |
| `GrievanceStatus` | `case.status` | the portal returns it; the legacy direct client's model drops it, so it is missing from any sample taken there. See "Case status" |
| `OfficerReply` | `case.reply` | the network does not adopt the portal's field name; see "Case reply" |
| `OfficeReplyDate` | `case.repliedOn` | an IST calendar date |
| `Reg_No` | *dropped* | the registration number the farmer sent. Nothing structural stops it coming back — `enrolmentId` is an attribute on every leg — so this is a deliberate mapping rule: it is matched against the number the caller sent, then discarded. v1's `identity-no` echo on a case read is not carried into v2 |
| `Farmer_Name`, `Father_Name`, `Gender`, `MobileNo`, `StateName`, `DistrictName`, `BlockName`, `RevenueVillageName` | *dropped* | personal data |

Nine of fourteen are dropped. That is the point of the allow-list.

The category is not in the record either — a read cannot tell you what the grievance was
about. `Reg_No_Status` sends no `GrievanceType` back, which is why `grievance.category`
is optional and why a PM-KISAN case read returns a `grievance` band holding the
description alone. Where a response does carry a category, it is the value the caller
sent, echoed.

## The PM-KISAN identifier, and what it is not good for

**The portal does issue a case identifier.** The lodge reply carries it as `GrievanceID`,
or as `GrievanceNo` where that is absent, and it lands in `case.ticketNo`.

**It is not a read key.** `/GrievanceStatusCheck` takes an identity and returns **every**
grievance on it; there is no per-grievance endpoint and no documented way to ask for one.
The status records are not documented to repeat the handle either, so the adapter cannot
even match on it after the fact.

So the retrieval story is: `case.filedOn` is what picks the grievance out of the list.
Note where that date comes from — the lodge reply carries none, so it is the filing date
the network itself recorded, not a value the portal confirmed. It is sent back on the
read and matched against each record's `GrievanceDate`. **Two grievances filed on the
same identity on the same day are indistinguishable.** That is recorded as a limitation
rather than papered over.

What the identifier does buy is a handle the farmer can quote — to the portal's own
helpline, or back to the network. That is why the field is allowed and populated rather
than refused. PMFBY is the other way round: there the ticket number *is* the read key.

**What would close the collision:** a `/GrievanceStatusCheck` that accepts the grievance
id, or at minimum one that repeats it per record. Either is a question for PM-KISAN.

## Nothing on file

A read that matches no case is an answer, not a failure — but it is stated rather than
implied. It comes back as a `202` with Beckn's `AckNoCallback` body and the error code
`BIZ_NO_RESULTS_FOUND`, with `status: "ACK"` because the request was accepted and
processed. No attribute of this pack appears, and no `informationMode` value describes it.

An earlier draft returned a commitment with `commitmentAttributes` omitted instead. That
is spec-legal, since the property is optional, but a missing field is not a message: a
consumer cannot tell an absent case from a provider that dropped the field. Nor would an
empty `resources` array help — the resource is a fixed catalog pointer that says nothing
about whether a case exists — and `Contract.commitments` has `minItems: 1`, so returning
no commitment at all was never available.

## Composition

`attributes.yaml` has three layers and two branches.

| schema | holds | published |
|---|---|---|
| `SchemeServiceBase` | what any scheme service needs: `informationMode`, `provider`, `scheme`, `enrolmentId`, and the `challengeMethods` / `challenge` / `challengeIssued` trio | no |
| `GrievanceBase` | `SchemeServiceBase` plus the three grievance bands: `grievance`, `case`, `grievanceOptions` | no |
| `Grievance` | `GrievanceBase`, the `@context` / `@type` guards, and the `oneOf` over the two branches | **yes** |
| `PMFBYGrievance` | the PMFBY branch: `scheme.code: PMFBY`, its five extra top-level fields, its value spaces, its refusals, its gates | branch only |
| `PMKISANGrievance` | the PM-KISAN branch, likewise | branch only |

Only `Grievance` is sent. Nothing ever carries
`@type: openagrinet:GrievanceBase` or `openagrinet:PMFBYGrievance`; the branches are
internal structure, named so a reader can see which rule belongs to which desk.

**The split at `SchemeServiceBase` is the room left for a future capability.** Checking
the status of a *scheme application* is a different capability from a grievance, and it
lives in its own pack — but it needs exactly the top layer: the scheme, the enrolment,
the provider, and the challenge trio. It composes `SchemeServiceBase` and adds its own
bands, so nothing about grievances follows it in. If the network later wants to *file* an
application, that is one more pack over the same base, and this one does not move.

This pack reaches outside for two things. `IdentifiedDescriptor`, which the domain
schemas already publish, wraps Beckn's `Descriptor` for `scheme`, the two category
levels and `case.status`. `ProviderReference` composes Beckn's own `Provider/v2.1` and
narrows it — `id` and `descriptor` required, `availableAt` and `providerAttributes`
refused.

It does not compose the Agriculture Resource field set: that set is framed around a
Resource holding information, which this pack is not.

## Where each field travels

One thing moves between legs, and only one.

**The attributes object itself moves.** On `init` and `status` it is
`message.contract.commitments[].commitmentAttributes`. On `support` there is no contract
to hang it from, so it becomes a support channel: `message.support.channels[0]`.
`x-beckn-container-by-action` states this.

**Nothing moves out of it.** Every field named in this pack is read at the same path on
every action, relative to whichever container the action uses. There is no
`x-beckn-path` anywhere in the pack.

| Field | on `support` | on `init` / `status` |
|---|---|---|
| `enrolmentId` | in attributes (`channels[0]`) | in attributes (`commitmentAttributes`) |
| `provider` | in attributes (`channels[0]`) | absent — read `commitments[].offer.provider`, which is the same shape |

Everything else stays inside the attributes object wherever that object happens to be —
both containers included. Published examples show the logical form, every field inline;
they are not wire payloads.

PMFBY has no `init` leg: it publishes no challenge, so its flow opens at `support` and
its only contract leg is `status`.

## Fields

"Required when" describes a complete payload of that kind. It does not make the field
mandatory in a Beckn `Intent` or an identifier-only protocol reference.

### Shared by both schemes

| Field | Required when | Meaning |
|---|---|---|
| `@context` | Always | The JSON-LD context these terms resolve against. Pinned to this pack's own; an array when a Provider publishes extra `@type` values |
| `@type` | Always | Identifies the commitment as `openagrinet:Grievance` |
| `informationMode` | Always | `OnDemand` is the ask; `Direct` carries a real case |
| `scheme` | Always | Scheme the grievance is raised against; present in both directions. `code` is the branch selector — `PMFBY` or `PM-KISAN` |
| `provider` | `support` legs | Beckn `Provider` reference — `id` routes the request, `descriptor.name` makes the payload readable. The adapter composes no `Contract` on this leg, so it has nowhere else to read the provider from |
| `enrolmentId` | Ask, when filing; also returned in `Direct` | The enrolment the grievance is about, as the scheme numbers it. Stays in the attributes object on every leg, `support` included |
| `grievance.category` | Ask, optional when filing; sometimes returned | The portal's own classification, as a `code`, a `name`, or both |
| `grievance.description` | Ask, when filing; also returned in `Direct` | The farmer's account of the problem, minimum ten characters |
| `case.ticketNo` | PMFBY `Direct`; optional on PM-KISAN | The handle the portal issued. A read key on PMFBY, a quotable handle only on PM-KISAN |
| `case.status` | `Direct` | Where the grievance stands, as a `CaseStatusCode`. Branch on it and render your own label; `name` is refused |
| `case.filedOn` | `Direct` | Date the grievance was filed, as an IST calendar date |
| `challengeMethods` | The catalog entry only | What this desk challenges with before it will act. Never sent on a transaction |
| `grievanceOptions` | The catalog entry only | The categories, and where the desk has them the sub-categories, this desk accepts. Never sent on a transaction |

### PMFBY only

| Field | Required when | Meaning |
|---|---|---|
| `applicantMobile` | Every ask | Ten-digit mobile of the farmer. The portal files it on the ticket and matches a ticket to the mobile it was filed from, so reading a case needs it too. Nothing proves the caller holds it — PMFBY asks for no OTP. Never echoed |
| `cropYear`, `season` | Ask, when filing | Four-digit crop year, and one of `Kharif`, `Rabi`, `Zaid`. They qualify the enrolment, not the complaint, so they sit at the top |
| `complaintDate` | Optional | The filing date, where a caller holds one — a replayed offline submission, say. Defaults to the current IST date at lodge time |
| `receiptSourceId` | Optional | The integrating channel a ticket arrived through. Names the channel, not the farmer. Defaults to the channel id the adapter is configured with |
| `grievance.subCategory` | Ask, optional when filing; returned on a read | The second classification level. PMFBY numbers two; PM-KISAN refuses this field |
| `case.cropName` | Optional in `Direct` | The insured crop the ticket was raised against, as the portal names it. Free text, shown to the farmer, never branched on |

PMFBY's category and sub-category codes are digit strings. The portal publishes no
enumeration, so the pack constrains only "digits" — see "Non-goals".

### PM-KISAN only

| Field | Required when | Meaning |
|---|---|---|
| `challenge` | `support` and `status` | `method: SMS_OTP` and a four-digit `value`. Inbound only. Never logged, traced, echoed or forwarded to the lodge call |
| `challengeIssued` | `init` response | The portal's acknowledgement: `method`, `length`, `valueType`, `expiresAt`. `sentTo` is refused — the portal does not say where it sent the code |
| `case.reply`, `case.repliedOn` | Optional in `Direct` | Absent rather than null while nothing has been recorded. `reply` is bounded at 2000 characters, and `repliedOn` without it is refused |

PM-KISAN's `grievance.category.code` is closed to `G001`–`G010`, and `enrolmentId` must
be ASCII alphanumeric and is refused if it is a bare twelve-digit Aadhaar number.

### Per-action use

Where each field is used, by action and by direction, lives in `x-oan-fields-by-action`
**on each branch**, with paths relative to the attributes object. Three buckets per action
— `mustSend`, `maySend`, `comesBack` — plus a branch-wide `refused` list stated once,
because the gates that enforce it are structural and bite on every action.

**PMFBY**

| action | mustSend | maySend | comesBack |
|---|---|---|---|
| `discover` | — | — | `informationMode`, `scheme.code`, `scheme.name`, `challengeMethods`, `grievanceOptions.categories`, `grievanceOptions.subCategories` |
| `support` | `enrolmentId`, `applicantMobile`, `cropYear`, `season`, `grievance.description` | `informationMode`, `provider.id`, `provider.descriptor.name`, `scheme.code`, `grievance.category.code`, `grievance.subCategory.code`, `complaintDate`, `receiptSourceId` | `informationMode`, `provider.id`, `provider.descriptor.name`, `scheme.code`, `scheme.name`, `enrolmentId`, `grievance.category.code`, `grievance.subCategory.code`, `grievance.description`, `case.ticketNo`, `case.status.code`, `case.filedOn` |
| `status` | `applicantMobile`, `case.ticketNo` | `informationMode`, `scheme.code`, `enrolmentId` | `informationMode`, `scheme.code`, `scheme.name`, `enrolmentId`, `grievance.category.name`, `grievance.subCategory.name`, `grievance.description`, `case.ticketNo`, `case.status.code`, `case.filedOn`, `case.cropName` |

Refused: `challenge`, `challengeIssued`, `case.reply`, `case.repliedOn`,
`case.status.name`, `provider.availableAt`, `provider.providerAttributes`.

**PM-KISAN**

| action | mustSend | maySend | comesBack |
|---|---|---|---|
| `discover` | — | — | `informationMode`, `scheme.code`, `scheme.name`, `challengeMethods`, `grievanceOptions.categories` |
| `init` | `enrolmentId` | `informationMode`, `scheme.code` | `informationMode`, `scheme.code`, `scheme.name`, `challengeIssued.method`, `challengeIssued.length`, `challengeIssued.valueType`, `challengeIssued.expiresAt` |
| `support` | `enrolmentId`, `grievance.category.code`, `grievance.description`, `challenge.method`, `challenge.value` | `informationMode`, `provider.id`, `provider.descriptor.name`, `scheme.code` | `informationMode`, `provider.id`, `provider.descriptor.name`, `scheme.code`, `scheme.name`, `enrolmentId`, `grievance.category.code`, `grievance.description`, `case.ticketNo`, `case.status.code`, `case.filedOn` |
| `status` | `enrolmentId`, `case.filedOn`, `challenge.method`, `challenge.value` | `informationMode`, `scheme.code` | `informationMode`, `scheme.code`, `scheme.name`, `grievance.description`, `case.status.code`, `case.filedOn`, `case.reply`, `case.repliedOn` |

Refused: `grievance.subCategory`, `grievanceOptions.subCategories`, `case.status.name`,
`challengeIssued.sentTo`, `provider.availableAt`, `provider.providerAttributes`.

Both are allow-lists. A path not named is not used by that capability. `discover` has
only a `comesBack` bucket, because the catalog entry is published, never asked for.
`enrolmentId` is a `mustSend` on PMFBY's `support` and only a `maySend` on its `status`:
the lodge is about an enrolment, while the read is selected by `case.ticketNo` and
`applicantMobile` together. `applicantMobile` never comes back on either leg.
PM-KISAN's `challenge` is a `mustSend` on `support` and `status` but absent from `init`,
which is the call that asks for the code rather than spends it. `challenge` appears in
no `comesBack` bucket on either leg; `challengeIssued` is the whole of what `init`
answers with.

## PMFBY issues no challenge

`challengeMethods` is pinned `maxItems: 0` on the PMFBY branch and the catalog entry
publishes `[]`. Both challenge bands are refused outright:

```yaml
- not:
    anyOf:
      - required: [challenge]
      - required: [challengeIssued]
```

A payload carrying either is rejected rather than quietly ignored, so a caller that
assumed an OTP step is told so at the edge instead of having its proof silently dropped.

The field is published empty rather than omitted. Empty is an answer; absent is a
question. A caller reading `[]` knows to open at `support`.

PMFBY does operate an OTP pair — `/api/v1/services/nic/getOtp` and `/verifyMobile` — but
it sits on the core realm, behind different credentials, and belongs to the policy flow.
It takes a mobile number and sends a code to whatever number it is handed; it never sees
an application number and so proves no link between the caller and the policy they are
complaining about. Borrowing it would impose a control the portal never asked for and
would not deliver the assurance its presence implies.

**The consequence is worth stating plainly: filing against PMFBY is unauthenticated.**
Nothing proves a caller is the farmer. Anyone holding an application number can lodge a
grievance against it, and PMFBY application numbers have visible structure. That is the
portal's own posture, not a gap this network introduces — but it is worth raising with
PMFBY, and any control it wants belongs on FGMS beside the lodge rather than borrowed
from another realm.

If PMFBY ever adds a challenge to FGMS, widen `challengeMethods` on that branch and drop
the refusal. Nothing else moves.

## PM-KISAN grievance categories

Unlike PMFBY, the portal publishes a closed list, so the branch enumerates it and an
unknown code is refused at the network edge rather than upstream. The code goes to the
portal verbatim as `GrievanceType`. `grievanceOptions.categories[].code` is held to the
same enum, so a catalog offering an eleventh type fails at publish time rather than at
filing time.

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

`Installment` is the portal's own spelling and is quoted, not corrected.

## Category term

One pack means one term. `grievance.category` resolves to
`openagrinet:grievanceCategory` and `grievance.subCategory` to
`openagrinet:grievanceSubCategory`, for both schemes. The earlier scheme-prefixed pair —
`pmfbyGrievanceCategory` against `pmkisanGrievanceCategory` — existed because two packs
could not share one IRI across incompatible value spaces. With the value spaces pinned
per branch inside one pack, the structure carries that distinction and the term does not
have to. The JSON keys never changed; only the context mapping did.

## Case status

`case.status` carries a `CaseStatusCode` and nothing else. `name` is refused on both
branches: each portal's own status phrase picks the code and is then dropped, because no
sample of either vocabulary exists and a slot reserved for values nobody has seen is a
guess with a field around it.

Where a portal publishes a status phrase, the adapter maps it to a `CaseStatusCode`. A
phrase it does not recognise maps to `UnderReview` — never to a terminal state, which
must come from the portal — so an unknown vocabulary degrades rather than fails. If a
portal supplies its phrase list and the list says more than the code can, `name` can be
added back as an optional member without breaking a caller.

Where a portal publishes no status, the adapter infers one and emits `code` alone:

- `Registered` — a lodge reply, which carries no status of any kind, that did not report
  failure.
- `Replied` — a status record with a reply but no status phrase.
- `UnderReview` — a status record with neither.

## Case reply

PM-KISAN's field is `OfficerReply`; the network's is `case.reply`. The name is not
adopted, for two reasons. A network term should not be one portal's internal field name —
and it has to name something PMFBY could fill too, which today it cannot: that portal
publishes no reply at all and the branch refuses both fields. And PM-KISAN is not
consistent about who writes it: the companion date is `OfficeReplyDate`, an office rather
than an officer. Naming the field for the case rather than for an author claims only what
we can show.

`reply` / `repliedOn` replaced `remark` / `remarkedOn` in this revision. "Remark" is a
note *about* a case; what the portal sends is an answer *to* one, and `reply` says so.

## Privacy

Every field carrying personal data is marked in `attributes.yaml` with `x-oan-pii`:

```yaml
x-oan-pii:
  class: contact
  handling: [no-log, no-trace, no-echo]
```

In this pack `class` is one of `identifier`, `contact`, `credential` or `freetext`, and
`handling` draws on `no-log`, `no-trace`, `no-echo`, `no-forward` and `mask-on-echo`.
Neither vocabulary is closed — [SchemeApplication](../../SchemeApplication/v0.1/README.md)
adds `aadhaar` and `no-store` for a field this pack does not carry. `mask-on-echo` is for a
value that *is* returned in a masked form; it says nothing beside `no-echo`, which already
means the value never comes back at all, so the two are never listed together.

The marking is inert — the validator ignores `x-` keys. It exists so the rule can be read
by a tool rather than only by a person: a CI check can assert that no property marked
`no-echo` appears in any `Direct` example, which is the class of mistake the v1
`identity-no` echo was.

**Neither `writeOnly` nor `readOnly` appears in this pack**, and that is deliberate. The
validator visits every payload with `VisitAsRequest`, on the way out as well as in, so
`writeOnly` would assert nothing while `readOnly` would reject the very response it
describes. Direction is carried by `x-oan-pii`, which the adapter reads, and it is
unconditional.

**`challenge.value` is the strictest field here.** It is never logged, traced, echoed in
a response, or forwarded to the lodge call. The structural half of that rule is the gate
above; this is the mapping half.

**`applicantMobile` is never echoed**, and on PMFBY there is nothing to echo it in: that
desk issues no challenge acknowledgement, so no masked destination is returned anywhere.
Where a desk does publish `challengeIssued.sentTo`, it is a masked destination and never
the full number. PM-KISAN emits no `sentTo` at all.

**`enrolmentId` is `no-log` and `no-trace` without exception**: it is never written to a
log, attached to a trace, or included in an error body. It is a bearer key as much as an
identifier — anyone holding a registration number can read every reply recorded against
it — so those two markings are the ones doing the work.

It is **not** `no-echo`, and the distinction is deliberate. Returning it on `on_support`
gives it back to the caller who sent it, over the same signed exchange, and tells them
nothing new. That is the only place it comes back: a case read drops it, by mapping rule
rather than by structure. The v1 adapter's `identity-no` echo **on a case read** is not
carried into v2.

**Aadhaar is deliberately not accepted in `enrolmentId`.** PM-KISAN's portal takes a token
derived from one and carries it in the same `IdentityNo` field, which would make this
value sometimes a stable reference and sometimes an ephemeral secret. A bare twelve-digit
value is refused structurally. Neither an Aadhaar number nor any token derived from one
may be logged, traced, or returned in any response or error body.

`grievance.description` is free text written by a farmer and may contain personal details
the schema cannot constrain. It is returned verbatim on a case read.

**Both portals' records carry far more about the farmer than this pack surfaces** — name,
father's name, gender, mobile number, email, and the full state / district / sub-district
/ block / panchayat / village hierarchy, alongside the insurance policy number and
insurer. None of it is modelled and none of it is emitted. An adapter must drop these
fields rather than pass them through; the pack cannot stop it, because
`commitmentAttributes` is open. **The response mapping is an allow-list, not a
passthrough.**

**A portal's own message or body is never returned to the caller.** It may hold a stack
trace, an internal hostname, or a quoted-back credential. Log it redacted and return our
own message. No error path carries `challenge.value`, `enrolmentId`, or a service token.

**PM-KISAN's portal payload travels inside an encrypted envelope.** A decryption failure
must not log the ciphertext.

## Stricter than the portals

Constraints tighter than what the portals themselves would take, and deliberate:

- `applicantMobile` requires an Indian mobile series (`^[6-9]`); PMFBY checks only that
  ten digits arrived.
- `cropYear` requires four digits; PMFBY takes any digit string.
- `season` is closed to three values; PMFBY takes the numeric codes the adapter produces.
- `grievance.category.code` on PM-KISAN is closed to the ten published codes; the upstream
  client checks the label it was handed, not the code, so a code reaching it by any other
  route is forwarded unchecked.
- `grievance.description` requires ten characters; both portals take an empty string.
- PM-KISAN's `enrolmentId` must be **ASCII** alphanumeric. The upstream accepts Devanagari,
  Bengali and Tamil digits and forwards them to the portal unconverted. The pattern
  refuses them at the edge instead.

Two places the pack is deliberately *not* stricter:

- PM-KISAN's registration number is checked only for "non-empty alphanumeric, not a bare
  Aadhaar". Eleven alphanumeric characters is the documented shape, but nothing upstream
  enforces it and the only source is a tool docstring; a length rule built on that would
  reject a valid grievance before the farmer's complaint reached the portal.
- `grievance.description`'s length is measured on the raw string. The upstream client
  measures it after trimming, so ten characters of whitespace pass here and fail there.
  Tightening it would need a regex that rejects payloads the portals accept, so the
  adapter trims and re-checks instead.

## Naming

`SMS_OTP`, `NUMERIC` and `ALPHANUMERIC` break the repo's UpperCamelCase convention for
governed values. They are kept as they are, deliberately: they are read as acronyms, they
match how every integrator writes them, and renaming them would churn the mapping files
for no gain. Recorded here so a later reviewer does not "fix" them.

`Installment` in PM-KISAN's category list and `Enrollment / Portal Issues` in PMFBY's are
the portals' own strings, quoted verbatim. They are not spelling defects in this repo and
must not be corrected.

## Non-goals

**This pack does not define PMFBY's grievance category list.** The portal publishes no
enumeration of valid pairs; it returns a name for whichever pair a case was filed under —
`3` is `Enrollment / Portal Issues`, `10` is `Login` — but there is no endpoint that
lists them. The `code` patterns therefore constrain only "digits", and each `name` is
whatever came back.

Category `3` / `10` is the only pair in use today, because v1 hardcoded it for every
grievance regardless of subject. That is a v1 defect carried in the data, not a portal
constraint, and v2 does not repeat it: the category is a caller-supplied field. When the
portal exposes its list the experience layer starts sending a real choice and nothing in
this pack changes.

**It does not describe the transport envelope.** PM-KISAN's portal payload travels
encrypted and the response arrives wrapped; both belong to the adapter, and neither the
ciphertext nor the service token appears here or in any payload this pack describes.

**It does not define credentials.** Those live in the adapter configuration, where
credentials are named by environment variable and never held.

**It does not cover scheme applications.** Checking the status of an application is a
different capability and lives in its own pack over the same `SchemeServiceBase`. Filing
one is not implemented and has no fields reserved for it here — when it arrives, it is
another pack over that base, not a change to this one.

## Examples

Five PMFBY, seven PM-KISAN. The `Direct` examples show `case.status` as a bare `code`,
which is the only form: no sample of either portal's status phrase exists anywhere in the
legacy tree, which is why the phrase does not travel at all.

**PMFBY**

- [The catalog entry](examples/pmfby-on-demand-capability.json)
- [On-demand: file a grievance](examples/pmfby-on-demand-file-grievance.json)
- [On-demand: read an existing case](examples/pmfby-on-demand-read-case.json)
- [Direct: lodge reply, as the portal sends it](examples/pmfby-direct-grievance-registered.json)
- [Direct: grievance under review, read from the portal](examples/pmfby-direct-grievance-under-review.json) — the category and sub-category names in it are illustrative. The portal answers a read with `TicketCategoryName` and `TicketSubCategoryName` and has published no phrase list, so there is no captured value to quote.

**PM-KISAN**

- [The catalog entry](examples/pmkisan-on-demand-capability.json)
- [On-demand: request an OTP against a registration](examples/pmkisan-on-demand-request-otp.json)
- [On-demand: OTP issued](examples/pmkisan-on-demand-challenge-issued.json)
- [On-demand: lodge a grievance](examples/pmkisan-on-demand-lodge-grievance.json)
- [On-demand: read a case](examples/pmkisan-on-demand-read-cases.json)
- [Direct: grievance registered](examples/pmkisan-direct-grievance-registered.json)
- [Direct: grievance with a reply recorded](examples/pmkisan-direct-grievance-replied.json)
