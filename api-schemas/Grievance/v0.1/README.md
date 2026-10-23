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

**Why `oneOf` and not `anyOf` for the guarded gates.** The two read alike, but they do not
fail alike. kin-openapi throws away the per-arm errors of a failed `anyOf` and reports only
"doesn't match any schema from anyOf", so a payload that forgot one field is reported no
differently from one that got everything wrong -- the name of the missing field is destroyed
inside the validator and no amount of care in the adapter can recover it. A failed `oneOf`
keeps each arm's error, so `property "applicantMobile" is missing` survives to the caller.

Every gate that guards a requirement is therefore an exclusive `oneOf`: each arm restates
the guard the others are keyed on -- usually `informationMode`, which the base requires and
pins to one of two values -- so exactly one arm can ever match and `oneOf` accepts the same
set `anyOf` would. The gates are longer to read for it. The trade is a caller who is told
which field they left out.

Two costs remain, and both are the adapter's to absorb. A failing payload is still validated
against both scheme branches, so the losing branch's errors ride along; an adapter that
selects the branch on `scheme.code` before validating never sees them. And the guard arms
report their own `enum` mismatch on `informationMode`, which is noise to be filtered, not a
fault to be fixed. Pinning `scheme.code` per branch is what makes it obvious which branch was
intended.

A refusal -- any gate written as a bare `not` -- is the one case that cannot be improved.
kin-openapi reports `Doesn't match schema "not"` with nothing underneath, so a payload that
smuggles `applicantMobile` onto a `Direct` answer is told that it broke a rule but not which
field broke it. The schema dump beside the error names the field; the structured error does
not.

## Attachment point

Two different things travel under this pack, and they do not ride in the same place.

| what | where | on which call |
|---|---|---|
| the **declaration** — this desk exists, here is what it accepts | `resourceAttributes` of a catalog `Resource` | `catalog/publish`, `discover`, `on_discover` |
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
commitment — the payload attaches through `Support.channels` instead. See "Direction, not
action" below.

The spec puts no `minItems` on `Commitment.resources`, so an empty array is legal. This
pack never sends one — see "Nothing on file".

This is where the pack parts company with the OAN domain packs. A forecast or a mandi
price genuinely is a resource, so those packs carry their payload on `resourceAttributes`
and have nothing that corresponds to a case. Here only the declaration goes there.

## The five bands

**The band a field sits in says who wrote it.**

| band | holds | written by |
|---|---|---|
| top level | who is asking and about what: `informationMode`, `provider`, `scheme`, `enrolmentId`, and the PMFBY-only `applicantMobile`, `cropYear`, `season`, `complaintDate`, `receiptSourceId` | the caller |
| `grievance` | what the farmer submitted: `category`, `subCategory`, `description` | the farmer |
| `case` | what the portal has on file, the stamps it applied included: `ticketNo`, `status`, `filedOn`, `reply`, `repliedOn`, `cropName` | the portal, except the selector — see below |
| top level, PMFBY-only | the caller's own inputs: `applicantMobile`, `cropYear`, `season`, `complaintDate`, `receiptSourceId` | the caller; three of them inbound only — see below |
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
our channel and has no consumer. A `Direct` PMFBY payload carrying any of the three is
refused, which is the mirror of the case rule below — one band is the portal's and may
not ride on an ask, these three are the caller's and may not ride on an answer.

`cropYear` and `season` are not among them. The portal reports both back, as
`RequestYear` and `RequestSeason`, so they travel in both directions.

**The `case` band has one exception, and only one: the selector.** A read has to name the
case it wants, and the handle for that is the portal's own. PMFBY reads by
`case.ticketNo`; PM-KISAN reads by `case.filedOn`, because its portal answers with every
case on the registration and the date is what picks one out. Each branch permits its own
selector on an ask and refuses every other member of the band there, so a caller cannot
hand the portal a status, a reply or a reply date and have it read back as fact.

PM-KISAN uses all five. PMFBY uses three: its grievance service has no OTP endpoint, so
neither challenge band could ever be filled honestly there, and the PMFBY branch refuses
`challenge` outright rather than leave it defined and unfillable. One refusal now takes
out the declaration, the acknowledgement and the answer together.

`challenge.methods` sits in no band. It is published on the catalog entry and never sent
on a payload — and that is enforced, not just stated: a payload carrying it must be
`OnDemand`, must name no farmer and must hold no live challenge. It is what a caller
reads to know whether this desk challenges it before filing. PMFBY emits no `challenge` at all, which is how a caller learns there is
nothing to ask for; PM-KISAN publishes one pinned entry.

`grievanceOptions` sits in no band either, and for the same reason: it is published on
the catalog entry and never sent, under the same enforced rule. It carries the categories — and, where the desk
classifies at two levels, the sub-categories — this desk accepts, so a caller chooses
from the portal's vocabulary instead of keeping a master list of its own. PMFBY numbers
two levels and publishes both. PM-KISAN numbers one and refuses `subCategories`.

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

Every gate is an `anyOf`, a `not` or a `oneOf`, and every one is tested against the real
validator. A gate that guards a requirement is always an exclusive `oneOf`, for the error
message reason given above; `anyOf` is left only where the rule really is a disjunction with
no single right answer, such as "a payload must be about one of a grievance, a case or a
published catalog". Some are stated once on a shared layer and hold for both desks; the rest
are stated on the branch they belong to, and each is marked below.

**A `Direct` payload must carry a case.** A response with no case standing is not an
answer. PMFBY requires `ticketNo`, `status` and `filedOn`; PM-KISAN requires `status` and
`filedOn` only. The difference is real: PMFBY's read is keyed on the ticket, so the
number is always in hand and echoed back, while PM-KISAN's status call is not documented
to repeat the handle per record, so a case read there may carry none. `provider` is not
in either list: on `init` and `status` the same fact lives in `commitments[].offer.provider`,
outside these attributes, where a guard on the attributes object cannot reach it.

**Every payload must be about something** — a `grievance`, a `case`, or the declarations
a catalog entry carries. The same `@type` serves filing, reading and discovery, and
`informationMode` cannot tell them apart because every ask is `OnDemand`. What separates
them is what the payload brought. Before the containers existed nothing caught a payload
that brought none of them.

The list is **narrower on PMFBY than on PM-KISAN**, and the difference is the whole of
why PMFBY has no `init`. On PM-KISAN a bare `enrolmentId` is a real call: it is the ask
for an OTP. PMFBY issues no challenge, so there is nothing a bare enrolment could be
asking for, and it is refused — the three shapes left are the two asks and the published
catalog. PM-KISAN's list also takes a `challenge` carrying `issued`, which is the whole
of an `on_init` acknowledgement.

`applicantMobile` is deliberately not in that list. Every PMFBY ask carries it, so a
branch on it would admit a payload stripped of everything else — a mobile number and
nothing to be about.

`challenge.methods` and `grievanceOptions` are in that list for the catalog entry alone.
A declaration states what this desk needs and what it accepts, and asks for nothing, so
it brings no `grievance`, no `case` and no enrolment. Without the branch the gate would
reject the very entry a caller discovers the desk by. Both are named on the one branch,
so a desk that publishes what it requires without publishing what it accepts — or the
other way round — is refused rather than half-published. The catalog branch and the
`on_init` branch both start at `challenge`, so they are told apart by which member is
present: `methods` on the entry, `issued` on the acknowledgement.

There is deliberately no narrower `OnDemand` branch. The ask side has no field common to
every payload: PMFBY filing sends the mobile, the enrolment, the season and the
complaint; reading a case sends the mobile and the ticket; the catalog entry sends none
of them. What each action must carry is enforced by that action's mapping guard.

**An answer may not carry `challenge.response`** (PM-KISAN). The code is sent, never
returned: a payload carrying it must have `informationMode` other than `Direct`. The
secret could otherwise have been echoed back and still validated. `x-oan-pii` marks the
value `no-echo`, but that binds the mapping; this is the structural half of the same rule.

**Exactly one member of `challenge`.** The container closes with a `oneOf` over
`required: [methods]`, `required: [issued]` and `required: [response]`. Two members match
two branches and fail; none matches zero and fails. This is what stops a catalog entry —
a document published to anyone who discovers the desk — from carrying a live one-time
code beside the declaration, and it is why the rule above no longer has to mention
`issued` separately. It also disposes of a bare `challenge: {}`, which was about nothing.

**A catalog declaration makes the payload a catalog entry.** `grievanceOptions` and
`challenge.methods` are published and never sent, so a payload carrying either must be
`OnDemand`, must bring no `enrolmentId`, no `grievance` and no `case`, and must hold no
`challenge.issued` or `challenge.response`. An earlier revision only kept them off a
`Direct` answer, which left the larger hole open: a farmer's filing could carry the
desk's own published form alongside the complaint, and a catalog entry could carry an
enrolment number. Stated once in `GrievanceBase`, so it holds on both branches.

**Three PMFBY-only top-level fields may not ride on an answer.** `applicantMobile`,
`complaintDate` and `receiptSourceId` appear in no `comesBack` list; the gate refuses
them on a `Direct` payload. Until that gate existed a PMFBY answer could echo the
farmer's mobile number back out over the network.

**Nothing but `code` and `name` travels in a `Descriptor`.** Beckn's `Descriptor` carries
five more members — `longDesc`, `shortDesc`, `thumbnailImage`, `docs`, `mediaFile` — and
every slot in this pack built on one refuses all five through the shared
`NoDescriptorExtras`. That is `scheme`, `grievance.category`, `grievance.subCategory`,
`case.status` and `provider.descriptor`. It matters most on `case.status`, which goes to
the trouble of refusing `name` so the portal's own status phrase cannot travel: without
this, `shortDesc` and `longDesc` were two open doors into the same room.

**The `grievance` and `case` bands are closed.** `additionalProperties: false` on
`Complaint` and on `Case`, so an unknown key inside either is rejected. That is not
possible on the root — see below — but it is possible here, and it is where it matters:
the portal's record holds the farmer's name, father's name, gender and address, and a
mapping slip would otherwise copy any of them straight through. Closing `Case` meant
moving `cropName` out of the PMFBY branch into the shared component, since a sibling
branch's properties are invisible to `additionalProperties` for the same reason the root
cannot close. PM-KISAN goes on refusing it by name.

**The case band on an ask carries the selector and nothing else.** Stated per branch,
because the selector differs: `case.ticketNo` on PMFBY, `case.filedOn` on PM-KISAN. See
"The five bands".

**PM-KISAN refuses all five PMFBY-only top-level fields and `case.cropName`.** The five
are declared inside the PMFBY branch, which is not the same as being kept out of this one
— see "The composed root is open". Each is refused by name, and without the refusal
`applicantMobile` was not even pattern-checked on this branch, because the branch that
holds the pattern was not the branch being matched. The five are named once, in the
shared `NoPMFBYFields`, which the PM-KISAN branch and the `SchemeApplication` pack both
`$ref` — a per-pack list catches only what its author happened to think of, and these two
had drifted apart. `cropName` now sits in the shared `Case`, so the refusal there is a
plain exclusion of a field this desk does not number.

**Both grievance branches refuse the `applicant` and `application` bands.** They belong
to `SchemeApplication`, and `applicant.mobile` is the one that matters: PM-KISAN refuses
`applicantMobile`, and a mobile number nested one level down would have walked straight
past that refusal. The refusal is `NoApplicationBands`, composed on `GrievanceBase` so it
binds both desks, and the mirror of it — `NoGrievanceBands` — is what the other pack
`$ref`s back.

**PMFBY refuses `challenge`** with a single `not`/`required`. See "PMFBY issues no
challenge".

**A reply date needs a reply.** `case.repliedOn` without `case.reply` is refused on both
branches: a date for an answer nobody wrote is not a fact.

**The reply text is the portal's, not the caller's.** `case.reply` is refused on an
`OnDemand` payload on both branches, beside `case.status`, `case.filedOn` and
`case.cropName`. An ask carries the selector and nothing else; the answer is what comes
back.

**Each call must be complete.** `mustSend` is a published contract, and until these
gates existed it was a contract the validator did not hold anyone to — a caller could
omit every field on the list and still pass. The gates close that. There is one per ask,
and each names exactly its branch's `mustSend` list.

The schema cannot be told which call is in flight: one attributes object serves the
catalog entry, `init`, `support` and `status`, and every ask carries
`informationMode: OnDemand`. So each gate reads the call off the payload's own shape --
a `grievance` band means a support ask, a `case` band means a status ask,
`grievanceOptions` means a catalog entry, a `challenge.issued` means an `init` answer,
and `enrolmentId` alone means an `init` ask. Every gate is guarded on `OnDemand`, because
those same bands on a `Direct` payload are the Portal's answer rather than a request.

PM-KISAN's status gate is stated twice over, keyed on the `case` band and again on the
OTP, because either can be the member that goes missing — and dropping `case.filedOn`
leaves `case` empty, so a gate keyed on `case` alone would stop firing at exactly the
moment the payload stopped being complete. PM-KISAN's `init` ask needs no gate of its
own: it carries nothing but `enrolmentId`, which "every payload must be about something"
already requires.

What this cannot catch is a well-formed ask sent to the wrong endpoint — a complete
`status` payload posted to `support` reads as a status ask and passes. Telling those
apart needs the action, which only the adapter knows.

**`enrolmentId` has a floor on both branches.** PMFBY pins 10 to 30 characters, PM-KISAN
6 to 20. The base allowed one character, which is not a registration number on any desk.

**Neither branch takes twelve bare digits.** That is the shape of an Aadhaar number, and
no enrolment slot in either pack carries one: what travels is a registration or
application number, or a token exchanged for an Aadhaar upstream. The refusal is
`NotBareAadhaar`, shared by all three slots — both grievance branches and
`SchemeApplication` — rather than restated, so none of them can quietly lose it.

On PMFBY this rests on an assumption worth stating: that no state issues a crop
insurance application number of exactly twelve digits with no letters. Every number seen
carries a state prefix (`BR295454592`, `KA2026KH00123456`). **PMFBY has not confirmed
it**, and if some state does, this one `$ref` comes off the PMFBY branch.

**PM-KISAN files under a code, never a name.** `Complaint.category` takes a code or a
name, which is right for PMFBY — its case read answers with a name and no id. PM-KISAN
files under a code from a closed list of ten and the portal takes nothing else, so the
branch requires `code`. Without it a caller could send a category named and not coded,
which the adapter has no way to forward.

## The composed root is open

`Grievance` is an `allOf` over a base, the JSON-LD guards and a `oneOf` of two branches.
A root composed that way **cannot be closed**: `additionalProperties: false` on the root
sees only the properties the root itself declares, and every real field is declared in a
sibling `allOf` member, so adding it takes every example from valid to invalid. It is left
off deliberately, and the consequence is worth stating plainly: **an unknown top-level
key is accepted.**

Two things follow. A field that must not appear has to be **refused by name** with a
`not`/`required` — which is what every refusal in this pack is, and why the PM-KISAN
branch names the PMFBY-only fields rather than relying on not declaring them. And the
"response mapping is an allow-list, not a passthrough" rule in "Privacy" is, *at the root
only*, a rule the adapter keeps rather than one the schema enforces.

Only at the root. The bands below it are ordinary objects, not compositions, and every
one of them **is** closed: `grievance`, `case`, `grievanceOptions`, `challenge` and its
three members, and each `GrievanceOption`. A stray portal field copied into `case` is
rejected. So the gap is exactly one level wide — a key hung off the top of the attributes
object, beside `informationMode` — and nowhere else.

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
| `TicketStatus` | `case.status.code` | mapped to a `CaseStatusCode`. The phrase itself is not forwarded — the pack refuses `name`. The only value yet observed is `Open` |
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
beside it, which is why the PMFBY branch refuses `case.repliedOn` while allowing
`case.reply` — and why the `Case` rule refusing a date without a reply matters here.

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

`attributes.yaml` has three layers and two branches.

| schema | holds | published |
|---|---|---|
| `SchemeServiceBase` | what any scheme service needs: `informationMode`, `provider`, `scheme`, `enrolmentId`, and the `challenge` object | no |
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
the provider, and the challenge object. It composes `SchemeServiceBase` and adds its own
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
| `informationMode` | Always | `OnDemand` is the ask; `Direct` carries a real case |
| `scheme` | Always | Scheme the grievance is raised against; present in both directions. `code` is the branch selector — `PMFBY` or `PM-KISAN` |
| `provider` | `support` only | Beckn `Provider` reference — `id` routes the request, `descriptor.name` makes the payload readable. The adapter composes no `Contract` for `support`, so it has nowhere else to read the provider from |
| `enrolmentId` | Ask, when filing; also returned in `Direct` | The enrolment the grievance is about, as the scheme numbers it. Stays in the attributes object on every call, `support` included |
| `grievance.category` | Ask, optional when filing; sometimes returned | The portal's own classification, as a `code`, a `name`, or both |
| `grievance.description` | Ask, when filing; also returned in `Direct` | The farmer's account of the problem, minimum ten characters |
| `case.ticketNo` | PMFBY `Direct`; optional on PM-KISAN | The handle the portal issued. A read key on PMFBY, a quotable handle only on PM-KISAN |
| `case.status` | `Direct` | Where the grievance stands, as a `CaseStatusCode`. Branch on it and render your own label; `name` is refused |
| `case.filedOn` | `Direct` | Date the grievance was filed, as an IST calendar date |
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
| `case.cropName` | Optional in `Direct` | The insured crop the ticket was raised against, as the portal names it. Free text, shown to the farmer, never branched on |

PMFBY's category and sub-category codes are digit strings. The portal publishes no
enumeration, so the pack constrains only "digits" — see "Non-goals".

### PM-KISAN only

| Field | Required when | Meaning |
|---|---|---|
| `challenge.response` | `support` and `status` | `method: SMS_OTP` and a four-digit `value`. Inbound only. Never logged, traced, echoed or forwarded to the lodge call |
| `challenge.issued` | `init` response | The portal's acknowledgement: `method`, `length`, `valueType`, `expiresAt`. Carries no secret and no destination |
| `case.reply`, `case.repliedOn` | Optional in `Direct` | Absent rather than null while nothing has been recorded. `reply` is bounded at 2000 characters, and `repliedOn` without it is refused |

PM-KISAN's `grievance.category.code` is closed to `G001`–`G010`, and `enrolmentId` must
be ASCII alphanumeric and is refused if it is a bare twelve-digit Aadhaar number.

### Per-action use

Where each field is used, by action and by direction, lives in `x-oan-fields-by-action`
**on each branch**, with paths relative to the attributes object. Three buckets per
action: `mustSend`, `maySend`, `comesBack`. The convention allows a fourth, `oneOf`,
for a call that needs exactly one of several paths; neither branch here uses it, because
both require `enrolmentId` outright. What each branch refuses is in the schema itself,
not here — the gates are structural and bite on every action.

**The provider must be named on every call that reaches a Portal.** On `support` that is
`provider.id` inside the channel, which is why it is a `mustSend` below, and
`provider.descriptor.name` is one too: `ProviderReference` requires `descriptor` and
`descriptor` requires `name`, so a provider carrying only an `id` is refused. On `init`
and `status` the same pair sits at `commitments[0].offer.provider`, outside the
attributes object and so outside these tables — required all the same. The `id` is what
resolves the Portal and its base URL in the registry, so a call without it cannot be
routed.

**PMFBY**

| action | mustSend | maySend | comesBack |
|---|---|---|---|
| `discover` | — | — | `informationMode`, `scheme.code`, `scheme.name`, `grievanceOptions.categories`, `grievanceOptions.subCategories` |
| `support` | `informationMode`, `scheme.code`, `provider.id`, `provider.descriptor.name`, `enrolmentId`, `applicantMobile`, `cropYear`, `season`, `grievance.description` | `scheme.name`, `grievance.category.code`, `grievance.subCategory.code`, `complaintDate`, `receiptSourceId` | `informationMode`, `provider.id`, `provider.descriptor.name`, `scheme.code`, `scheme.name`, `enrolmentId`, `grievance.category.code`, `grievance.subCategory.code`, `grievance.description`, `case.ticketNo`, `case.status.code`, `case.filedOn` |
| `status` | `informationMode`, `scheme.code`, `applicantMobile`, `case.ticketNo` | `scheme.name`, `enrolmentId` | `informationMode`, `scheme.code`, `scheme.name`, `enrolmentId`, `cropYear`, `season`, `grievance.category.code`, `grievance.category.name`, `grievance.subCategory.code`, `grievance.subCategory.name`, `grievance.description`, `case.ticketNo`, `case.status.code`, `case.filedOn`, `case.reply`, `case.cropName` |

**PM-KISAN**

| action | mustSend | maySend | comesBack |
|---|---|---|---|
| `discover` | — | — | `informationMode`, `scheme.code`, `scheme.name`, `challenge.methods`, `grievanceOptions.categories` |
| `init` | `informationMode`, `scheme.code`, `enrolmentId` | `scheme.name` | `informationMode`, `scheme.code`, `scheme.name`, `challenge.issued.method`, `challenge.issued.length`, `challenge.issued.valueType`, `challenge.issued.expiresAt` |
| `support` | `informationMode`, `scheme.code`, `provider.id`, `provider.descriptor.name`, `enrolmentId`, `grievance.category.code`, `grievance.description`, `challenge.response.method`, `challenge.response.value` | `scheme.name` | `informationMode`, `provider.id`, `provider.descriptor.name`, `scheme.code`, `scheme.name`, `enrolmentId`, `grievance.category.code`, `grievance.description`, `case.ticketNo`, `case.status.code`, `case.filedOn` |
| `status` | `informationMode`, `scheme.code`, `enrolmentId`, `case.filedOn`, `challenge.response.method`, `challenge.response.value` | `scheme.name` | `informationMode`, `scheme.code`, `scheme.name`, `grievance.description`, `case.status.code`, `case.filedOn`, `case.reply`, `case.repliedOn` |

Both are allow-lists. A path not named is not used by that capability. `discover` has
only a `comesBack` bucket, because the catalog entry is published, never asked for.
`informationMode` and `scheme.code` lead every `mustSend` because the base requires both
outright and `scheme.code` is what picks the branch; listing them makes each row the
whole of what the call must carry rather than most of it. `scheme.name` is genuinely
optional and stays in `maySend`.

Every other `mustSend` name is enforced by a gate in the schema — see "Completeness,
per call". The two lists are checked against each other: drop any one `mustSend` field
from a complete request and the validator refuses it; drop any one `maySend` field and
it still passes.
`enrolmentId` is a `mustSend` on PMFBY's `support` and only a `maySend` on its `status`:
the lodge is about an enrolment, while the read is selected by `case.ticketNo` and
`applicantMobile` together. `applicantMobile` never comes back on either call.
PM-KISAN's `challenge.response` is a `mustSend` on `support` and `status` but absent from
`init`, which is the call that asks for the code rather than spends it. It appears in no
`comesBack` bucket on either call; `challenge.issued` is the whole of what `init` answers
with.

## PMFBY issues no challenge

The whole `challenge` object is refused on the PMFBY branch, in one line:

```yaml
- not:
    required: [challenge]
```

One refusal takes out the declaration, the acknowledgement and the answer together,
because all three now live under the same key. A payload carrying any of them is
rejected rather than quietly ignored, so a caller that assumed an OTP step is told so at
the edge instead of having its proof silently dropped.

Absence is the answer here, not a question. A published empty list would be the usual
way to say "nothing to ask for" while leaving absent to mean "unknown", but the branch
makes that distinction unnecessary: `scheme.code: PMFBY` selects a branch on which
`challenge` cannot appear at all, so a caller reading a PMFBY entry without one knows to
open at `support`.

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

If PMFBY ever adds a challenge to FGMS, drop the refusal and pin `challenge.methods` on
that branch. Nothing else moves.

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
beside the reply; PMFBY sends none, so the PMFBY branch allows `case.reply` and refuses
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
`no-echo` appears in any `Direct` example, which is the class of mistake the v1
`identity-no` echo was.

**Neither `writeOnly` nor `readOnly` appears in this pack**, and that is deliberate. The
validator visits every payload with `VisitAsRequest`, on the way out as well as in, so
`writeOnly` would assert nothing while `readOnly` would reject the very response it
describes. Direction is carried by `x-oan-pii`, which the adapter reads, and it is
unconditional.

**`challenge.response.value` is the strictest field here.** It is never logged, traced, echoed in
a response, or forwarded to the lodge call. The structural half of that rule is the gate
above; this is the mapping half.

**`applicantMobile` is never echoed**, and PM-KISAN now refuses the field outright, so it
reaches only the desk that asks for it. **No desk in this pack reports where it sent a
code.** An earlier revision carried a masked `challenge.issued.sentTo` for a desk that
might; every branch refused it, no payload could ever hold one, and it is gone. A desk
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
different capability and lives in its own pack over the same `SchemeServiceBase`. Filing
one is not implemented and has no fields reserved for it here — when it arrives, it is
another pack over that base, not a change to this one.

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
