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
`subjectCategories` — a governed field names the variant and concrete shapes refine the
rest — though here it is one code pinned per shape, not a multi-valued array.

This is an API schema, not a domain schema. A domain schema says what a thing *is* in the
agriculture domain; this one says what a named Provider's API will take and give back.

## One schema per scheme per call

**There is no inheritance in this pack.** A scheme does not extend a base, and a call
does not extend a scheme. Each (scheme, call) pair is one flat schema that declares
every field it takes, closes itself to everything else, and says in `x-oan-fields` what
the caller must send and what comes back. There are seven of them today:

| | `catalog/publish` | `init` | `status` | `support` |
|---|---|---|---|---|
| **PMFBY** | `PMFBYCatalog` | — | `PMFBYStatus` | `PMFBYSupport` |
| **PM-KISAN** | `PMKISANCatalog` | `PMKISANInit` | `PMKISANStatus` | `PMKISANSupport` |

PMFBY has no `init` because it issues no challenge — see "PMFBY issues no challenge".
A dash is an absence, not a stub: nothing in the pack stands in for a call a scheme does
not serve.

**Adding a scheme is four additions to this one file and no edits.** A guard pinning its
code, one leaf per call it serves, those leaves listed in the matching per-call schema,
and the same leaves listed on the root `oneOf`. Nothing existing moves, no other pack is
touched, and no other scheme's leaf is read while the new one is written. Adding a *call*
to an existing scheme is the same four additions, one row wider.

The cost of the flat shape is restatement: `scheme`, `informationMode` and the JSON-LD
envelope are written out in all seven leaves rather than inherited from one place. That
is deliberate. The previous revision shared them through a chain of five base schemas,
and the chain was what made a new provider expensive — every addition meant deciding
which layer a field belonged to, and a change to a shared layer silently reached every
desk that composed it. Restating a dozen lines per leaf buys a pack where each leaf can
be read, changed and refused on its own.

### How the three layers resolve

| layer | schemas | what it does |
|---|---|---|
| root | `Grievance` | the published `@type`. Carries `x-oan-schema-by-action` and a `oneOf` over all seven leaves |
| per-call | `GrievanceCatalog`, `GrievanceInit`, `GrievanceStatus`, `GrievanceSupport` | a `oneOf` over the leaves that serve that one call |
| leaf | the seven above | one flat schema: `required`, `properties`, `additionalProperties: false` |

A validator that reads `x-oan-schema-by-action` validates a payload against the per-call
schema for the action in flight, so a `status` payload is checked against the two status
leaves rather than against all seven. A validator that does not read it falls back to the
root `oneOf`.

**The two do not agree, and that is the point.** The root union accepts whatever any leaf
accepts, so a complete `status` payload passes it even when it arrives as `support`. The
per-call schema refuses that same payload, and says why:
`property "provider" is missing`. Reading the key is what catches a well-formed ask sent
to the wrong call, and what makes the refusal name a field instead of saying the payload
matched nothing. The fallback is a safety net for a validator that does not know the key,
not an equivalent to it.

An action the key does not name is validated against the whole type. Which calls exist is
the base spec's to say, and a pack that nominates a schema for four of them is not thereby
refusing the other twenty-three.

**Why `oneOf` and not `if`/`then`.** The network's validator is kin-openapi. It parses
`if`/`then` and never evaluates it, so a per-scheme rule written that way looks like it
holds and does not. `oneOf`, `anyOf` and `not` *are* evaluated. Every guard in this pack
is written in those three, and every one of them is tested against the real validator.

**Why `oneOf` and not `anyOf` for the guarded gates.** The two read alike, but they do not
fail alike. kin-openapi throws away the per-arm errors of a failed `anyOf` and reports only
"doesn't match any schema from anyOf", so a payload that forgot one field is reported no
differently from one that got everything wrong -- the name of the missing field is destroyed
inside the validator and no amount of care in the adapter can recover it. A failed `oneOf`
keeps each arm's error, so `property "applicantMobile" is missing` survives to the caller.

**Why each leaf opens with a scheme guard.** Every leaf is
`allOf: [IsPMFBY | IsPMKISAN, <the flat body>]`, and the guard does nothing the body does
not already do — the body pins `scheme.code` too. It is there for the error message.
kin-openapi reports **one** error per failing `oneOf` arm, and which one is not the pack's
to choose; with the guard folded into the body, the arm for the wrong scheme could surface
`property "challenge" is missing` instead of `value must be "PMFBY"`, and the validator
could not tell a payload aimed at the other desk from one with a real fault. As a separate
conjunct the guard is always collected, so the wrong-scheme arm is recognisably ruled out
and its demands are dropped rather than reported. The result is that a caller who misspells
one field is told about that field and nothing else.

## Attachment point

Two different things travel under this pack, and they do not ride in the same place.

| what | where | on which call |
|---|---|---|
| the **declaration** — this desk exists, here is what it accepts | `resourceAttributes` of a catalog `Resource` | `catalog/publish` |
| a **case** — one farmer's grievance | `commitmentAttributes` of a `Commitment` | `init`, `status` |
| a **case**, where there is no commitment to hang it from | `support.channels[0]` | `support` |

The declaration sits on `resourceAttributes` for the same reason every other OAN pack
does: a grievance desk is a catalogable thing a Provider publishes. `informationMode`,
`scheme`, the challenge methods and the category lists all describe the desk, not any
farmer. That is why the profile declares indexable paths under both prefixes — a caller
filters catalogs on `resourceAttributes.scheme.code` and filters cases on
`commitmentAttributes.case.status.code`.

A case is the other half, and it is not catalogable: it is a promise with a lifecycle,
not a thing of value.
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
commitment — the payload attaches through `Support.channels` instead. See "Where the
answer comes from" below.

The spec puts no `minItems` on `Commitment.resources`, so an empty array is legal. This
pack never sends one — see "Nothing on file".

This is where the pack parts company with the OAN domain packs. A forecast or a mandi
price genuinely is a resource, so those packs carry their payload on `resourceAttributes`
and have nothing that corresponds to a case. Here only the declaration goes there.

## What each desk publishes it can do

A catalog entry says this desk exists and what it accepts. It did not, until now, say
**which calls it serves** — a caller had to know that PMFBY answers `status` and `support`
but has no `init`, and that PM-KISAN answers all three. That knowledge lived in the
caller, which meant every caller held its own copy and any one of them could be wrong.

The `actions` band moves it into the catalog. One entry per call this desk serves:

| field | holds |
|---|---|
| `action` | the Beckn action to call, as it appears in `context.action` |
| `description` | what the call does, what it needs first, and what it returns that a later call consumes |
| `schema` | a URL naming the one leaf this scheme accepts for that call |
| `attributesAt` | a JSONPath to where that payload rides in the envelope |

**A call absent from the list is a call this desk does not serve.** PMFBY publishes two
entries and no `init`, because there is no `PMFBYInit` leaf to point at.

`schema` points at the **leaf**, not the per-call schema the validator uses. A catalog
entry is already scheme-specific — it sits on a resource whose `scheme.code` is pinned —
so naming `GrievanceStatus` would hand the caller a `oneOf` over both schemes and make it
re-derive which arm applies. `PMKISANStatus` is one closed shape. Conforming to the leaf
implies conforming to the per-call schema, so nothing is weakened by being specific.

`description` carries what a schema cannot: ordering. PMFBY's `status` matches on a
`case.ticketNo` that only `support` returns, so for PMFBY `support` must come first;
PM-KISAN's `status` matches on a `case.filedOn` that its `support` returns, and both its
reads need an OTP from `init`. None of that is expressible as a constraint on a single
payload, and all of it is what a caller planning a sequence needs to know. Array order
hints at it; the text states it.

`attributesAt` repeats `x-beckn-container-by-action` on the pack root. That is deliberate
duplication: the caller gets the container in the same read as the schema, rather than
fetching the root to resolve it. Both are generated from the same table, so they cannot
drift apart.

**The whole band is pinned with `const`.** It is not a free-text hint an adapter fills in.
Each catalog leaf declares the exact list it must publish, element for element, so an
adapter that advertises a call it cannot serve — or stops advertising one it can — fails
validation instead of lying to every caller. Order is part of the pin, because the
validator compares the array element by element.

## The five bands

**The band a field sits in says who wrote it.**

| band | holds | written by |
|---|---|---|
| top level | who is asking and about what: `informationMode`, `provider`, `scheme`, `enrolmentId`, and the PMFBY-only `applicantMobile`, `cropYear`, `season`, `complaintDate`, `receiptSourceId` — three of those five inbound only, see below | the caller |
| `grievance` | what the farmer submitted: `category`, `subCategory`, `description` | the farmer |
| `case` | what the portal has on file, the stamps it applied included: `ticketNo`, `status`, `filedOn`, `reply`, `repliedOn`, `cropName` | the portal, except the selector — see below |
| `challenge.response` | proof of identity, presented with the call it guards: `method`, `value`. Inbound only, never echoed, never forwarded | the caller |
| `challenge.issued` | the portal's acknowledgement that it sent a code: `method`, `length`, `valueType`, `expiresAt` | the portal |

Everything about challenging this desk lives under one `challenge` object, which is why
the last two bands are nested rather than top level. The container itself carries no
authorship marking — `methods` is published in the catalog, `issued` is the portal's and
`response` is the caller's, so each member is marked on its own. Exactly one of the three
is present on any payload, and the container enforces it: a catalog entry declares, an
acknowledgement reports, an ask answers, and no payload does two of those at once.

**Three of the five PMFBY-only top-level fields travel inbound and never come back.**
`applicantMobile` is personal data the network does not echo. `complaintDate` is the
farmer's own stated date, where `case.filedOn` is the portal's. `receiptSourceId` names
our channel and has no consumer. None appears in any `comesBack` list, so none is
returned; with a single information mode the pack can no longer tell an ask from an
answer by a field value, so this is a mapping rule rather than a schema gate.

`cropYear` and `season` are not among them. The portal reports both back, as
`RequestYear` and `RequestSeason`, so they travel in both directions.

**The `case` band has one exception, and only one: the selector.** A read has to name the
case it wants, and the handle for that is the portal's own. PMFBY reads by
`case.ticketNo`; PM-KISAN reads by `case.filedOn`, because its portal answers with every
case on the registration and the date is what picks one out. Each scheme's `status` leaf
requires its own selector and nothing else in the band, so a read that names no case is
refused rather than answered with whichever one came back first.

PM-KISAN uses all five. PMFBY uses three: its grievance service has no OTP endpoint, so
neither challenge band could ever be filled honestly there, and no PMFBY leaf declares
`challenge` at all rather than leave it defined and unfillable. Since every leaf is
closed, that single absence takes out the declaration, the acknowledgement and the
answer together.

`challenge.methods` sits in no band. It is published on the catalog entry and never sent
on a payload — and that is enforced, not just stated: only `PMKISANCatalog` declares it,
and that leaf names no farmer and holds no live challenge, because it declares no slot
for either. It is what a caller reads to know whether this desk challenges it before
filing. PMFBY emits no `challenge` at all, which is how a caller learns there is nothing
to ask for; PM-KISAN publishes one pinned entry.

`grievanceOptions` sits in no band either, and for the same reason: it is declared on the
two catalog leaves alone, so a transaction payload carrying it is refused by closure. It
carries the categories — and, where the desk classifies at two levels, the
sub-categories — this desk accepts, so a caller chooses from the portal's vocabulary
instead of keeping a master list of its own. PMFBY numbers two levels and publishes both.
PM-KISAN numbers one and declares no `subCategories`.

`actions` sits in no band either, and is confined the same way: it is declared on the
catalog leaves alone, so a transaction payload carrying it is refused by closure. It
names the calls this desk serves, so a caller reads the desk's capabilities instead of
hard-coding them. See the section above.

Before the containers the same split lived in a prefix — `grievanceCategory` against
`caseStatus` — which read the same and checked nothing: a field named either way
validated either way. As containers the split is enforced, and `grievance` becomes all or
nothing, because `required` inside a block fires whenever the block is present.

Nothing rides in a Beckn `descriptor`, and nothing is named one either. A published
option's help text is `help`, not `descriptor`: a Beckn `Descriptor` is an object
everywhere else in this pack, and a plain string under the same name would have read as
one. An earlier draft hoisted the category and the
farmer's words there, which read well and checked nothing: a `Descriptor` is three
free-text strings, so the category, the sub-category and the complaint all validated as
any string at all. The join was lossy too — PMFBY's own category name contains the
separator the names were joined on (`Enrollment / Portal Issues` + `Login`), so no split
could recover the pair. As fields inside `grievance` each one has bounds the pack holds.

## Where the answer comes from

`informationMode` says where the answer comes from, never which Beckn action is in play.
`OnDemand` is its only value: the Portal answers, so the caller makes the `init`,
`support` or `status` call that follows discovery. The same attributes serve `init`,
`support` and `status` without change.

One action is an exception, and the pack names it. On `support` the payload has no
`Commitment` to sit on, so it attaches through `Support.channels` instead.
`x-beckn-container-by-action` on the root schema records which container each action
uses. That is the whole of it: the container changes, the payload does not. No field
moves out of the attributes object, so every field is read at the same path on every
action — `enrolmentId` included.

The root key carries the union of both schemes' actions — `catalog/publish`, `init`,
`status`, `support`. Strictly `init` belongs to PM-KISAN alone, since PMFBY opens at
`support`; but this key is a network-wide convention used by 14 packs and tooling reads
it at the root, so it stays there. Nothing is lost by that: `x-oan-schema-by-action`
sends `init` to `GrievanceInit`, which is a `oneOf` over `PMKISANInit` alone, so a PMFBY
`init` is still refused.

One field exists only on the `support` call, and it is there so the request can be routed
at all. The adapter picks the upstream call from a binding key,
`participantId|capabilityCode`, and reads both halves out of the payload. On every other
action the payload composes a `Contract`, so the participant is read from
`commitments[].offer.provider.id`. A `SupportAction` composes no contract, and `Support`
is sealed at three fields, none of which names a participant — so the channel carries
`provider` instead, a Beckn `Provider` narrowed to a reference: an `id` and a descriptor
carrying a name.

It is the same shape `init` and `status` supply, so a reader writes `.provider.id` on both,
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
absent one. So `enrolmentId` stays in the attributes object on the `support` call exactly
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

Most of what the previous revision spent gates on is now ordinary schema. A leaf declares
exactly the fields its call takes and closes with `additionalProperties: false`, so a
field that does not belong is refused because it was never declared — there is no list of
banned fields to keep in step with anything. The rules that survive are the ones that are
genuinely about *combinations*, and there are only three.

**`PMKISANInit` is two shapes, not one.** The ask carries an `enrolmentId` and no
challenge; the acknowledgement is the challenge the portal issued. One `oneOf` separates
them:

```yaml
oneOf:
  - allOf:
      - required: [enrolmentId]
      - not: { required: [challenge] }
  - required: [challenge]
```

**`PMKISANStatus.case` refuses a reply date with no reply.** `case.repliedOn` without
`case.reply` is a date for an answer nobody wrote, which is not a fact. Written as an
exclusive `oneOf`, for the reason given above — an `anyOf` here would report
"doesn't match any schema" and throw the field name away:

```yaml
oneOf:
  - not: { required: [repliedOn] }
  - required: [repliedOn, reply]
```

**Each leaf requires its own `mustSend` list outright.** `mustSend` is a published
contract; `required` is how the schema holds a caller to it. The two lists are checked
against each other in the test corpus: drop any one `mustSend` field from a complete
request and the validator refuses it; drop any one `maySend` field and it still passes.

Everything else the old gates did is now structural:

| old gate | what replaced it |
|---|---|
| "every payload must be about something" | each leaf requires the fields its own call is about |
| "a catalog declaration makes the payload a catalog entry" | `grievanceOptions` is declared only in the two catalog leaves |
| "exactly one member of `challenge`" | each leaf declares the one member its call carries — `methods`, `issued` or `response` |
| "PM-KISAN refuses the five PMFBY-only fields" | the PM-KISAN leaves never declare them, and are closed |
| "both branches refuse the `applicant` and `application` bands" | likewise — and `SchemeApplication` is now a separate pack that shares nothing |
| "PMFBY refuses `challenge`" | `PMFBYStatus` and `PMFBYSupport` do not declare it |
| "nothing but `code` and `name` travels in a `Descriptor`" | no leaf composes Beckn's `Descriptor`; each declares the two members it uses |
| "the reply text is the portal's, not the caller's" | the ask leaves declare the selector; `reply` is declared but never required |

**What no schema can catch** is a well-formed ask sent to the wrong endpoint — a complete
`status` payload posted to `support` reads as a status ask and passes the status leaf.
Telling those apart needs the action, which the adapter knows and the schema does not;
`x-oan-schema-by-action` is what hands it over.

**Neither scheme takes twelve bare digits in an enrolment slot.** That is the shape of an
Aadhaar number, and no enrolment slot in either pack carries one: what travels is a
registration or application number, or a token exchanged for an Aadhaar upstream. Each
leaf states the refusal itself — `not: { pattern: "^[0-9]{12}$" }` — rather than sharing
it, so losing it from one leaf cannot quietly lose it from the others.

On PMFBY this rests on an assumption worth stating: that no state issues a crop
insurance application number of exactly twelve digits with no letters. Every number seen
carries a state prefix (`BR295454592`, `KA2026KH00123456`). **PMFBY has not confirmed
it**, and if some state does, this one line comes off the two PMFBY leaves.

**`enrolmentId` has a floor on both schemes.** PMFBY pins 10 to 30 characters, PM-KISAN
6 to 20. One character is not a registration number on any desk.

**Both schemes file under a code.** `grievance.category` and `grievance.subCategory`
require `code` on PMFBY and PM-KISAN alike; `name` rides along as an optional label.
Without the code a caller could send a category named and not coded, which the adapter
has no way to forward. The lists differ — PMFBY's codes are digit strings it never
published, PM-KISAN's are a closed ten — but the requirement does not.

## The pack is closed at every level

**Every leaf is closed.** `additionalProperties: false` sits on the flat body of each
one, and because that body declares every field the leaf takes, the keyword does what it
reads as: an unknown key beside `informationMode` is refused, by name.

This is the one substantive change in verdict from the previous revision, and it is a
tightening. That pack composed its root from a base, a set of JSON-LD guards and a
`oneOf` of branches, and a root composed that way **cannot** be closed — `additionalProperties`
sees only the properties the root itself declares, and every real field was declared in a
sibling `allOf` member. So an unknown top-level key was accepted, and every field that had
to stay out had to be banned by name in a list someone maintained. Two PMFBY fields
(`complaintDate`, `receiptSourceId`) were on no list and rode through on a `status` payload;
they are refused now.

Nothing is banned by name any more. The bands below the top are ordinary closed objects
as before — `grievance`, `case`, `grievanceOptions`, `challenge` and its members, each
option — so the allow-list rule in "Privacy" is now enforced by the schema at every
level rather than kept by the adapter at the top one.

## Upstream response coverage

Every field each portal sends back, and where it goes. Nothing is left unaccounted for.

These tables are the allow-list in readable form. They are built from live responses
where we have them and from the v1 adapter where we do not, and the PMFBY case read
shows why the distinction matters: the v1 adapter reads twelve fields, the portal sends
forty-five, and three facts this branch was designed around turned out to be in the
thirty-three nobody had looked at.

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

`POST /krphapi/FGMS/GetGrievenceTicketsStatus`. A live response carries **45 members of
`responseDynamic`**. The v1 adapter on `Beckn`'s `main` branch reads twelve of them, and
the three absences that shaped an earlier draft of this branch turned out not to be
absences at all: the ticket number, both category ids and the year and season are all in
the record. Eleven are mapped, thirty-four are dropped, and every one is listed.

**Mapped.**

| upstream | here | note |
|---|---|---|
| `ApplicationNo` | `enrolmentId` | |
| `GrievenceSupportTicketNo` | `case.ticketNo` | the number the farmer quotes, returned by the portal. Not to be confused with `GrievenceSupportTicketID` |
| `GrievenceDescription` | `grievance.description` | |
| `TicketCategoryID` | `grievance.category.code` | numeric upstream, string here, as on the lodge |
| `TicketCategoryName` | `grievance.category.name` | |
| `TicketSubCategoryID` | `grievance.subCategory.code` | |
| `TicketSubCategoryName` | `grievance.subCategory.name` | two levels, kept apart: the portal's own category name contains a slash, so any joined form would be lossy |
| `TicketStatus` | `case.status.code` | mapped to a `CaseStatus`. The phrase itself is not forwarded — the pack refuses `name`. The only value yet observed is `Open` |
| `RequestYear` | `cropYear` | |
| `RequestSeason` | `season` | the same 1/2/3 to `Kharif`/`Rabi`/`Zaid` lookup as the lodge, read the other way |
| `CropName` | `case.cropName` | the insured crop |
| `latestRemark` | `case.reply` | **omit when empty.** The portal sends `""` for an unanswered ticket and `case.reply` is `minLength: 1`, so an empty string must be left out, not forwarded as blank |
| `InsertDateTime` | `case.filedOn` | a UTC instant; the adapter takes the IST calendar date from it. See below |

**Dropped as personal data** — `FarmerName`, `RequestorMobileNo`, `Email`,
`StateMasterName`, `DistrictMasterName`, `SubDistrictName`, `VillageName`,
`GramPanchayat`, `NyayPanchayat`. Nine fields naming or locating the farmer.

**Dropped as the portal's internal keys** — `GrievenceSupportTicketID`,
`TicketRequestorID`, `DistrictRequestorID`, `VillageRequestorID`, `NyayPanchayatID`,
`GramPanchayatID`, `SubDistrictID`, `TicketStatusID`, `GrievenceTicketSourceTypeID`,
`ReceiptSourceID`, `InsuranceCompanyID`, `SocialMediaTypeID`, `InsertUserID`,
`StateCodeAlpha`. Row ids and master-table keys nothing outside PMFBY can resolve.

**Dropped as unused** — `InsuranceCompany`, `InsurancePolicyNo`, `RepresentationType`,
`GrievenceSourceOtherType`, `OtherSocialMedia`, `SocialMediaURL`, `IsLegal`,
`LegalRemarks`, `CPGramRegistrationNumber`, `NCIPReferenceNumber`, `ComplaintDate`.
Null in every sample, or carrying no fact a caller asked for.

**The envelope** — `responseCode` is consumed as the success flag the guard tests;
`responseMessage`, `recordCount`, `responseObject` and `jsonString` are dropped. The
portal's own message may carry a stack trace or an internal hostname and is never
returned.

**Two dates, and they disagree.** `ComplaintDate` is a field the *caller* sends on the
lodge, so it is the farmer's stated date. `InsertDateTime` is server-generated. In the
one live sample they are five months apart, which settles it: `case.filedOn` comes from
`InsertDateTime`, and `ComplaintDate` is not echoed back to the caller who sent it.

**One absence is left.** There is no reply *date*. `latestRemark` arrives with nothing
beside it, which is why `PMFBYStatus` declares `case.reply` and no `case.repliedOn`
beside it — and why the rule refusing a date without a reply matters on the PM-KISAN
side, where both exist.

Two things are still open. `recordCount` sits beside a `responseDynamic` that v1 reads as
a single object, so whether a multi-ticket read returns an array is unconfirmed. And
`TicketStatusID` is a key into a PMFBY master table we have not been given; until we are,
the status mapping reads the phrase and degrades unknown values to `UnderReview`.

### PM-KISAN lodge reply

Three values, and the portal spells each of them more than one way. Read each through a
fallback chain; this is the v1 adapter's behaviour, reproduced because it is the portal
that is inconsistent.

| upstream | here | note |
|---|---|---|
| `GrievanceID` / `grievanceId` / `GrievanceNo` | `case.ticketNo` | **the case identifier.** Whichever name arrives, lands here |
| `Status` / `Responce` / `Rsponce` | — | `"True"` / `"False"`, string-valued; becomes the ACK or a NACK, not a field. Absent means success here, so test for `"False"` rather than for `"True"` |
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
| `Reg_No` | *dropped* | the registration number the farmer sent. Nothing structural stops it coming back — `enrolmentId` is an attribute on every call — so this is a deliberate mapping rule: it is matched against the number the caller sent, then discarded. v1's `identity-no` echo on a case read is not carried into v2 |
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

`attributes.yaml` is one flat list of schemas with no inheritance in it.

| schema | holds | published |
|---|---|---|
| `Grievance` | the root: `x-oan-schema-by-action`, `x-beckn-container-by-action`, `x-jsonld`, and a `oneOf` over all seven leaves | **yes** |
| `GrievanceCatalog`, `GrievanceInit`, `GrievanceStatus`, `GrievanceSupport` | one per call, each a `oneOf` over the leaves that serve it | no |
| `IsPMFBY`, `IsPMKISAN` | the scheme guard: `scheme.code` pinned to one value, nothing else | no |
| the seven leaves | one complete payload shape each, closed, with no `$ref` to another leaf | no |
| the value types | `PMFBYOption`, `PMFBYSubject`, `PMKISANOption`, `PMKISANSubject`, `PMKISANEnrolmentId`, `PMKISANChallengeResponse`, `Description`, `Reply`, `CaseStatus`, `Provider`, `CalendarDate`, `Instant`, `Context`, `Type` | no |

Only `Grievance` is sent. Nothing ever carries `@type: openagrinet:PMFBYSupport`; the
leaf names exist so that a reader, and an error message, can say which shape was meant.

There is no base layer. `SchemeServiceBase`, `GrievanceBase`, `PMFBYGrievance` and
`PMKISANGrievance` are gone. A shared base meant one scheme's field list decided what
another scheme could be asked for; every leaf now restates its own fields instead.
Restating four field names beats a hierarchy that has to be re-read in full before a
fifth scheme can be added.

**The pack reaches outside for nothing.** There are no cross-pack `$ref`s and no remote
ones. Beckn's `Provider/v2.1` and the domain `IdentifiedDescriptor` are no longer
composed: `Provider` here is a local two-field object, and `scheme`, the two category
levels and `case.status` are local closed objects too. `SchemeApplication`, which used
to `$ref` eight schemas out of this file, now carries its own copies. Changing a rule
here changes nothing there, which is the point.

It does not compose the Agriculture Resource attributes either: those are framed around
a Resource holding information, which this pack is not.

## Where each field travels

One thing moves between calls, and only one.

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

PMFBY has no `init` call: it publishes no challenge, so its flow opens at `support` and
`status` is the only call it makes that carries a contract.

## Fields

"Required when" describes a complete payload of that kind. It does not make the field
mandatory in a Beckn `Intent` or an identifier-only protocol reference.

### Shared by both schemes

| Field | Required when | Meaning |
|---|---|---|
| `@context` | Always | The JSON-LD context these terms resolve against. Pinned to this pack's own; an array when a Provider publishes extra `@type` values |
| `@type` | Always | Identifies the commitment as `openagrinet:Grievance` |
| `informationMode` | Always | Where the answer comes from. `OnDemand` — the Portal answers — is the only value this version |
| `scheme` | Always | Scheme the grievance is raised against; present in both directions. `code` is the leaf selector — `PMFBY` or `PM-KISAN` |
| `provider` | `support` only | Beckn `Provider` reference — `id` routes the request, `descriptor.name` makes the payload readable. The adapter composes no `Contract` for `support`, so it has nowhere else to read the provider from |
| `enrolmentId` | Ask, when filing; also returned | The enrolment the grievance is about, as the scheme numbers it. Stays in the attributes object on every call, `support` included |
| `grievance.category` | Ask, optional when filing; sometimes returned | The portal's own classification. `code` is required when the field is sent; `name` is an optional label beside it |
| `grievance.description` | Ask, when filing; also returned | The farmer's account of the problem, minimum ten characters |
| `case.ticketNo` | Required on a PMFBY read, and returned; optional on PM-KISAN, and never returned there | The handle the portal issued. A read key on PMFBY. PM-KISAN's portal answers per identity, not per ticket, so a PM-KISAN read will not repeat it -- show the farmer the one kept from `on_support` |
| `case.status` | Returned | Where the grievance stands, as a `CaseStatus`. Branch on it and render your own label; `name` is refused |
| `case.filedOn` | Returned | Date the grievance was filed, as an IST calendar date |
| `challenge.methods` | The catalog entry only | What this desk challenges with before it will act. Never sent on a transaction |
| `grievanceOptions` | The catalog entry only | The categories, and where the desk has them the sub-categories, this desk accepts. Never sent on a transaction |

### PMFBY only

| Field | Required when | Meaning |
|---|---|---|
| `applicantMobile` | Every ask | Ten-digit mobile of the farmer. The portal files it on the ticket and matches a ticket to the mobile it was filed from, so reading a case needs it too. Nothing proves the caller holds it — PMFBY asks for no OTP. Never echoed |
| `cropYear`, `season` | Ask, when filing | Four-digit crop year, and one of `Kharif`, `Rabi`, `Zaid`. They qualify the enrolment, not the complaint, so they sit at the top |
| `complaintDate` | Optional | The filing date, where a caller holds one — a replayed offline submission, say. Defaults to the current IST date at lodge time |
| `receiptSourceId` | Optional | The integrating channel a ticket arrived through. Names the channel, not the farmer. Defaults to the channel id the adapter is configured with |
| `grievance.subCategory` | Ask, optional when filing; returned on a read | The second classification level. PMFBY numbers two; PM-KISAN refuses this field |
| `case.cropName` | Optional, returned | The insured crop the ticket was raised against, as the portal names it. Free text, shown to the farmer, never branched on |

PMFBY's category and sub-category codes are digit strings. The portal publishes no
enumeration, so the pack constrains only "digits" — see "Non-goals".

### PM-KISAN only

| Field | Required when | Meaning |
|---|---|---|
| `challenge.response` | `support` and `status` | `method: SMS_OTP` and a four-digit `value`. Inbound only. Never logged, traced, echoed or forwarded to the lodge call |
| `challenge.issued` | `init` response | The portal's acknowledgement: `method`, `length`, `valueType`, `expiresAt`. Carries no secret and no destination |
| `case.reply`, `case.repliedOn` | Optional, returned | Absent rather than null while nothing has been recorded. `reply` is bounded at 2000 characters, and `repliedOn` without it is refused |

PM-KISAN's `grievance.category.code` is closed to `G001`–`G010`, and `enrolmentId` must
be ASCII alphanumeric and is refused if it is a bare twelve-digit Aadhaar number.

### Per-action use

Where each field is used, by direction, lives in `x-oan-fields` **on each leaf**, with
paths relative to the attributes object. The leaf already says which call it serves, so
the key no longer needs an action index under it.

Four buckets: `mustSend`, `maySend`, `comesBack`, and `oneOf` for a call that needs
exactly one of several paths. No Grievance leaf uses `oneOf` — each requires its
identifiers outright; `SchemeApplication` does use it. What a leaf refuses is in the
schema itself, not here: every leaf is `additionalProperties: false` and declares only
the fields its call uses, so refusal is the absence of a declaration.

**No validator reads `x-oan-fields`.** It is documentation, kept in the schema file so
the two cannot drift. The only extension of this family that code reads is
`x-oan-schema-by-action` on the root.

The buckets earn their place because the leaves are ask-shaped. A leaf constrains what a
caller may send; `comesBack` is the only record in the pack of what the Portal answers
with, and the answer side is never validated — responses are built after validation runs,
and every call here is synchronous.

**The provider must be named on every call that reaches a Portal.** On `support` that is
`provider.id` inside the channel, which is why it is a `mustSend` below, and
`provider.descriptor.name` is one too: the local `Provider` requires `descriptor` and
`descriptor` requires `name`, so a provider carrying only an `id` is refused. On `init`
and `status` the same pair sits at `commitments[0].offer.provider`, outside the
attributes object and so outside these tables — required all the same. The `id` is what
resolves the Portal and its base URL in the registry, so a call without it cannot be
routed.

**PMFBY**

| action | leaf | mustSend | maySend | comesBack |
|---|---|---|---|---|
| `catalog/publish` | `PMFBYCatalog` | `informationMode`, `scheme.code`, `scheme.name`, `grievanceOptions.categories`, `grievanceOptions.subCategories` | — | — |
| `support` | `PMFBYSupport` | `informationMode`, `scheme.code`, `provider.id`, `provider.descriptor.name`, `enrolmentId`, `applicantMobile`, `cropYear`, `season`, `grievance.description` | `scheme.name`, `grievance.category`, `grievance.subCategory`, `complaintDate`, `receiptSourceId` | `informationMode`, `provider.id`, `provider.descriptor.name`, `scheme.code`, `scheme.name`, `enrolmentId`, `grievance.category.code`, `grievance.subCategory.code`, `grievance.description`, `case.ticketNo`, `case.status.code`, `case.filedOn` |
| `status` | `PMFBYStatus` | `informationMode`, `scheme.code`, `applicantMobile`, `case.ticketNo` | `scheme.name`, `enrolmentId`, `cropYear`, `season` | `informationMode`, `scheme.code`, `scheme.name`, `enrolmentId`, `cropYear`, `season`, `grievance.category.code`, `grievance.category.name`, `grievance.subCategory.code`, `grievance.subCategory.name`, `grievance.description`, `case.ticketNo`, `case.status.code`, `case.filedOn`, `case.reply`, `case.cropName` |

**PM-KISAN**

| action | leaf | mustSend | maySend | comesBack |
|---|---|---|---|---|
| `catalog/publish` | `PMKISANCatalog` | `informationMode`, `scheme.code`, `scheme.name`, `challenge.methods`, `grievanceOptions.categories` | — | — |
| `init` | `PMKISANInit` | `informationMode`, `scheme.code`, `enrolmentId` | `scheme.name` | `informationMode`, `scheme.code`, `scheme.name`, `challenge.issued.method`, `challenge.issued.length`, `challenge.issued.valueType`, `challenge.issued.expiresAt` |
| `support` | `PMKISANSupport` | `informationMode`, `scheme.code`, `provider.id`, `provider.descriptor.name`, `enrolmentId`, `grievance.category.code`, `grievance.description`, `challenge.response.method`, `challenge.response.value` | `scheme.name` | `informationMode`, `provider.id`, `provider.descriptor.name`, `scheme.code`, `scheme.name`, `enrolmentId`, `grievance.category.code`, `grievance.description`, `case.ticketNo`, `case.status.code`, `case.filedOn` |
| `status` | `PMKISANStatus` | `informationMode`, `scheme.code`, `enrolmentId`, `case.filedOn`, `challenge.response.method`, `challenge.response.value` | `scheme.name` | `informationMode`, `scheme.code`, `scheme.name`, `grievance.description`, `case.status.code`, `case.filedOn`, `case.reply`, `case.repliedOn` |

Both are allow-lists. A path not named is not used by that call. `catalog/publish` has
no `comesBack` bucket, because the Portal answers it with a bare ACK: the catalog entry
is sent, never asked for.
`informationMode` and `scheme.code` lead every `mustSend` because every leaf requires
both outright and `scheme.code` is what picks the leaf; listing them makes each row the
whole of what the call must carry rather than most of it. `scheme.name` is optional on
every call a caller makes and stays in `maySend` there; `catalog/publish` is the one
place it is required, because a catalog entry naming a scheme only by its code gives a
farmer's screen nothing to show.

Every `mustSend` name is enforced by that leaf's own `required` list. The two lists are
checked against each other: drop any one `mustSend` field from a complete request and
the validator refuses it; drop any one `maySend` field and it still passes.

`enrolmentId` is a `mustSend` on PMFBY's `support` and only a `maySend` on its `status`:
the lodge is about an enrolment, while the read is selected by `case.ticketNo` and
`applicantMobile` together. `applicantMobile` never comes back on either call.
PM-KISAN's `challenge.response` is a `mustSend` on `support` and `status` but absent from
`init`, which is the call that asks for the code rather than spends it. It appears in no
`comesBack` bucket on any call; `challenge.issued` is the whole of what `init` answers
with.

## PMFBY issues no challenge

No PMFBY leaf declares `challenge`, and all three PMFBY leaves are closed, so the
declaration, the acknowledgement and the answer are refused together: all three live
under the same key, and no PMFBY shape has that key. A payload carrying any of them is
rejected rather than quietly ignored, so a caller that assumed an OTP step is told so at
the edge instead of having its proof silently dropped.

PMFBY also has no `init` leaf at all. `GrievanceInit` is a `oneOf` over `PMKISANInit`
alone, so an `init` carrying `scheme.code: PMFBY` is refused on the call itself rather
than on a field inside it.

Absence is the answer here, not a question. A published empty list would be the usual
way to say "nothing to ask for" while leaving absent to mean "unknown", but the leaves
make that distinction unnecessary: `scheme.code: PMFBY` picks shapes on which
`challenge` cannot appear at all, so a caller reading a PMFBY catalog entry without one
knows to open at `support`.

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

If PMFBY ever adds a challenge to FGMS, declare `challenge.methods` on `PMFBYCatalog`
and add a `PMFBYInit` leaf beside it, named in `GrievanceInit`. Nothing else moves.

## PM-KISAN grievance categories

Unlike PMFBY, the portal publishes a closed list, so the PM-KISAN leaves enumerate it
and an unknown code is refused at the network edge rather than upstream. The code goes to the
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
per leaf inside one pack, the structure carries that distinction and the term does not
have to. The JSON keys never changed; only the context mapping did.

## Case status

`case.status` carries a `code` and nothing else: `CaseStatus` is closed around that one
member, so `name` is refused for both schemes. Each portal's own status phrase picks the
code and is then dropped, because no sample of either vocabulary exists and a slot
reserved for values nobody has seen is a guess with a field around it.

Where a portal publishes a status phrase, the adapter maps it to a `CaseStatus`. A
phrase it does not recognise maps to `UnderReview` — never to a terminal state, which
must come from the portal — so an unknown vocabulary degrades rather than fails. If a
portal supplies its phrase list and the list says more than the code can, `name` can be
added back as an optional member without breaking a caller.

Where a portal publishes no status, the adapter infers one and emits `code` alone:

- `Registered` — a lodge reply, which carries no status of any kind, that did not report
  failure.
- `Replied` — a status record with a reply but no status phrase.
- `UnderReview` — a status record with neither.

The seven codes and what each one claims:

| code | what it says | how it is reached today |
|---|---|---|
| `Registered` | filed, nobody has looked at it | inferred from a lodge reply |
| `UnderReview` | with the desk | inferred, and the landing place for any phrase we do not recognise |
| `AwaitingApplicant` | the desk has asked the farmer for something and is waiting | a portal phrase only |
| `Replied` | the desk has answered | inferred from a reply with no status phrase |
| `Resolved` | settled, the complaint was acted on | a portal phrase only |
| `Rejected` | settled, the complaint was not accepted | a portal phrase only |
| `Closed` | shut without a decision — withdrawn, duplicate, or timed out | a portal phrase only |

`Resolved`, `Rejected` and `Closed` are the terminal three: a case in one of them is
finished, and nothing the adapter infers may put a case there. Only a portal saying so
can. Four codes are marked *a portal phrase only* because neither portal has given us its
phrase list, so nothing maps to them yet. They are in the enum because a caller branching
on status should be written against the full set now rather than have codes appear under
it later. **Open with both portals:** the status phrase lists.

## Case reply

Both portals publish a reply, under different names: PM-KISAN sends `OfficerReply`,
PMFBY sends `latestRemark`. The network's is `case.reply`, which adopts neither — a
network term should not be one portal's internal field name, and with two portals
spelling it two ways there is no name to adopt. PM-KISAN is not even consistent with
itself: the companion date is `OfficeReplyDate`, an office rather than an officer.
Naming the field for the case rather than for an author claims only what we can show.

The two differ in one respect that reaches the schema. PM-KISAN sends a reply date
beside the reply; PMFBY sends none, so `PMFBYStatus` declares `case.reply` and no
`case.repliedOn`. And PMFBY writes `""` rather than omitting the field when a ticket is
unanswered, which `minLength: 1` rejects — the mapping must drop an empty
`latestRemark`, not forward it as a blank reply.

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
`handling` draws on `no-log`, `no-trace`, `no-echo` and `no-forward`.
Neither vocabulary is closed — [SchemeApplication](../../SchemeApplication/v0.1/README.md)
adds `aadhaar` and `no-store` for a field this pack does not carry.

The marking is inert — the validator ignores `x-` keys. It exists so the rule can be read
by a tool rather than only by a person: a CI check can assert that no property marked
`no-echo` appears in any answer example, which is the class of mistake the v1
`identity-no` echo was.

**Neither `writeOnly` nor `readOnly` appears in this pack**, and that is deliberate. The
validator visits every payload with `VisitAsRequest`, on the way out as well as in, so
`writeOnly` would assert nothing while `readOnly` would reject the very response it
describes. Direction is carried by `x-oan-pii`, which the adapter reads, and it is
unconditional.

**`challenge.response.value` is the strictest field here.** It is never logged, traced, echoed in
a response, or forwarded to the lodge call. The structural half of that rule is the gate
above; this is the mapping half.

**`applicantMobile` is never echoed**, and no PM-KISAN leaf declares it, so it reaches
only the desk that asks for it. **No desk in this pack reports where it sent a
code.** An earlier revision carried a masked `challenge.issued.sentTo` for a desk that
might; no leaf ever declared it, no payload could ever hold one, and it is gone. A desk
that does report a destination adds the field back with its own masking rule.

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
own message. No error path carries `challenge.response.value`, `enrolmentId`, or a service token.

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
different capability and lives in its own pack, `SchemeApplication`, which shares no
schema with this one. Filing an application is not implemented and has no fields
reserved for it here — when it arrives, it is a leaf in that pack, not a change to
this one.

## Examples

One per call, and every one is `OnDemand`, because every payload on this capability is:
the discovery service holds no case of its own, so the Experience layer always asks the
portal.

**PMFBY**

- [The catalog entry](examples/pmfby-on-demand-capability.json) — one pair, because one pair is all the portal has ever been asked for; see "Non-goals"
- [On-demand: file a grievance](examples/pmfby-on-demand-file-grievance.json)
- [On-demand: read an existing case](examples/pmfby-on-demand-read-case.json)

**PM-KISAN**

- [The catalog entry](examples/pmkisan-on-demand-capability.json)
- [On-demand: request an OTP against a registration](examples/pmkisan-on-demand-request-otp.json)
- [On-demand: OTP issued](examples/pmkisan-on-demand-challenge-issued.json)
- [On-demand: lodge a grievance](examples/pmkisan-on-demand-lodge-grievance.json)
- [On-demand: read a case](examples/pmkisan-on-demand-read-cases.json)
