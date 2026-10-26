# Scheme Application

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

Describes what a government scheme's application-status API accepts and what it returns:
how far a farmer's application has got, how many instalments have been paid, whether eKYC
is done, and what is holding payment up.

One scheme is covered today — **PM-KISAN** — named by `scheme.code`. The pack is named
for the capability rather than the scheme so a second scheme is a few more schemas in
this file rather than a second pack.

This is an API schema, not a domain schema. It says what a named Provider's API will take
and give back.

**It is not a grievance.** Nothing is filed, nothing has a lifecycle, and nothing comes
back with a case number. That is why it is a pack of its own rather than a mode of
[Grievance](../../Grievance/v0.1/README.md) — the two share a desk and an OTP service,
and share no subject and, since this revision, no schema either.

**Filing an application is not implemented.** When it is, it is one more leaf in this
file beside the three that are here, and nothing already written moves.

## Attachment point

| what | where | on which call |
|---|---|---|
| the **declaration** — this desk exists, here is what it accepts | `resourceAttributes` of a catalog `Resource` | `catalog/publish` |
| one farmer's **application record** | `commitmentAttributes` of a `Commitment` | `init`, `status` |

The declaration is catalogable: `informationMode`, `scheme` and the challenge methods
describe the desk, so they sit on `resourceAttributes` as in every other OAN pack. A
status read is not catalogable — it is a promise the portal makes about one farmer's
application, so it sits on `commitmentAttributes`.

Unlike the grievance pack there is **no `support` call**: nothing is being filed, so no
`Support` channel is ever composed and no field moves out of the attributes object.
`x-beckn-container-by-action` therefore lists `catalog/publish`, `init` and `status`,
and no `channels`. No field in this family carries an `x-beckn-path` at all, so there is nothing
to fire: every field is read at the same path on both calls.

`Commitment.resources` carries one thin pointer to the catalog entry
(`res:pmkisan:application-status`). It is fixed for the provider and never minted per
farmer: a registration number must not end up in a public, cacheable identifier.

## What this desk publishes it can do

A catalog entry says this desk exists and what it accepts. It did not, until now, say
**which calls it serves** — a caller had to know that reading an application status means
`init` then `status`, and that there is no `support` here at all. That knowledge lived in
the caller, which meant every caller held its own copy and any one of them could be wrong.

The `actions` band moves it into the catalog. One entry per call this desk serves:

| field | holds |
|---|---|
| `action` | the Beckn action to call, as it appears in `context.action` |
| `description` | what the call does, what it needs first, and what it returns that a later call consumes |
| `schema` | a URL naming the one leaf this scheme accepts for that call |
| `attributesAt` | a JSONPath to where that payload rides in the envelope |

**A call absent from the list is a call this desk does not serve.** This pack publishes
`init` and `status` and no `support`: an application is read, never filed through here.
The Grievance pack is where a farmer raises a complaint, and PM-KISAN publishes both, as
two resources on one catalog.

`schema` points at the **leaf**, not the per-call schema the validator uses. A catalog
entry is already scheme-specific — it sits on a resource whose `scheme.code` is pinned —
so naming `SchemeApplicationStatus` would hand the caller a `oneOf` to resolve.
`PMKISANApplicationStatus` is one closed shape. Conforming to the leaf implies conforming
to the per-call schema, so nothing is weakened by being specific. It matters more here
than it looks: PM-KISAN serves this pack *and* Grievance through one plugin, so a bare
schema name would not tell a caller which of the two packs it belongs to.

`description` carries what a schema cannot: ordering. `status` requires
`challenge.response` holding an OTP that only `init` issues, so `init` must come first.
That is not expressible as a constraint on a single payload, and it is exactly what a
caller planning a sequence needs to know.

`attributesAt` repeats `x-beckn-container-by-action` on the pack root. That is deliberate
duplication: the caller gets the container in the same read as the schema, rather than
fetching the root to resolve it. Both are generated from the same table, so they cannot
drift apart.

**The whole band is pinned with `const`.** It is not a free-text hint an adapter fills in.
The catalog leaf declares the exact list it must publish, element for element, so an
adapter that advertises a call it cannot serve — or stops advertising one it can — fails
validation instead of lying to every caller. Order is part of the pin, because the
validator compares the array element by element.

## The bands

**The band a field sits in says who wrote it.**

| band | holds | written by |
|---|---|---|
| top level | what is being asked and under which scheme: `informationMode`, `scheme`, `enrolmentId` | the caller |
| `applicant` | who to look up when the caller has no enrolment number: a `mobile` number | the caller, and inbound only |
| `application` | what the portal holds: `registeredOn`, `latestInstalmentPaid`, `ekyc`, `blockers` | the portal, and outbound only |
| `challenge.response` | the OTP presented on the read | the caller |
| `challenge.issued` | acknowledgement that one was sent | the portal |

`applicant` is the caller's lookup key and `application` is the portal's record. With one
information mode the schema cannot tell an ask from an answer by `informationMode`, so it
tells them apart by shape instead: each call's schema carries a gate whose answer arm
refuses `applicant` outright. `enrolmentId` travels in both directions. A caller who holds the registration number
sends it; a caller who holds only a mobile number sends `applicant` instead,
and the portal resolves it and returns the registration number under `enrolmentId`. The
two slots are mutually exclusive — exactly one, never both. See "Identity is named, not
sniffed".

Everything about challenging this desk lives under one `challenge` object, which is why
the last two bands are nested rather than top level. The container itself carries no
authorship marking — `methods` is published in the catalog, `issued` is the portal's and
`response` is the caller's, so each member is marked on its own. Exactly one of the three
can be present on any payload, and no gate is needed to say so: each call's schema
declares only the member that call uses and is closed, so a catalog entry has no slot for
a live code and an acknowledgement has no slot for an answer.

`challenge.methods` sits in no band. It is published on the catalog entry and never sent
on a payload.

## Where the answer comes from

`informationMode` says where the answer comes from, never which Beckn action is in play.
`OnDemand` is its only value: the Portal answers, so the caller makes the `init` and
`status` calls below. The same attributes serve both `init` and `status`.

The sequence is two calls:

| | action | the caller sends | the portal returns |
|---|---|---|---|
| 1 | `init` | `enrolmentId` **or** `applicant` | `challenge.issued` — an OTP has gone to the number the application is held under |
| 2 | `status` | the same identifier + `challenge.response` | `enrolmentId` + `application` |

Every payload in the sequence is `OnDemand`: the ask, the OTP acknowledgement and the
answer carrying the application alike. The grievance pack does the same.

The OTP is the same OTP as PM-KISAN's grievance desk uses — the same upstream service
issues it and the same four digits satisfy it — so a caller who holds one from a grievance
flow can spend it here, and the `init` leg that issues it is written the same way in both
packs. What differs is the body around it: there the challenge guards lodging and reading
a complaint, here it guards reading an application.

## Identity is named, not sniffed

Every ask carries exactly one identifier, and the slot it is written in says what kind it
is. This is the pack's main correction to the upstream behaviour.

The portal infers what kind of identifier it has been handed from the *shape* of the
value: ten digits beginning 6–9 is a mobile number, anything else is a registration
number. A registration number that happens to be ten
digits starting with a 7 therefore becomes a phone lookup, silently, and returns either
nothing or somebody else's record. Nothing upstream reports that this happened.

So the kind is named outright, each slot carries its own shape rule, and the adapter sends
the named type rather than letting the portal guess:

| slot | shape the pack enforces | sent upstream as |
|---|---|---|
| `enrolmentId` | ASCII alphanumeric, 6 to 20 characters; twelve bare digits refused | `Ben_id` |
| `applicant.mobile` | `^[6-9][0-9]{9}$` | `Mobile` |

A registration number is `enrolmentId` — the same field under the same name as on the
grievance pack, so a reader writes `.enrolmentId` once for the whole family rather than
learning a second name per capability.

`enrolmentId` has no digit rule on purpose. The portal treats anything that is not a
mobile number as a registration, and a registration that happens to be ten digits is
exactly the case this slot exists to carry safely. It does refuse twelve bare digits:
that is an Aadhaar number's shape, and this capability takes no Aadhaar lookup, so the
refusal keeps one out of the registration slot rather than redirecting it elsewhere.
Both rules live in this pack's own `PMKISANEnrolmentId`, and the four-digit SMS challenge
in its own `PMKISANChallengeResponse`. The grievance desk reads the same registration on
the same portal and states the same rules in its own file. Two copies are two chances to
lose one — but a `$ref` across packs is one chance to break both at once, and keeping the
two capabilities independent is worth more here. See "Composition".

The observed form is two letters and nine digits — `BR295454592` is the value v1's own
test fixtures use — and v1 validates it as `/^[A-Z0-9]+$/i`, which is the pattern pinned
here. Whether two-plus-nine holds for every state is not confirmed, so no length rule is
imposed.

One slot per kind, rather than a kind field beside a generic value. A pair has to be
checked against itself — otherwise a caller declares a mobile and sends twelve letters —
and that check is a gate that can be written wrong. Named slots make the mismatch
unrepresentable instead of merely refused, let each identifier carry its own handling
rules, and give each a stable IRI rather than one whose meaning depends on a sibling.

`applicant` requires `mobile` and `additionalProperties: false` closes off anything else,
so the object cannot carry a second identifier. `enrolmentId` and `applicant` are held
apart by each call's own gate: the ask arm is a `oneOf` over the two slots, which says
never both and never neither in one clause. The answer arms refuse `applicant` outright,
so a response cannot leak the lookup key back beside the registration it resolved to.

**Aadhaar is not a lookup key on this capability.** There is no slot for one, and
`enrolmentId` refuses twelve bare digits so one cannot be sent in the registration slot
either. A caller who holds only an Aadhaar number cannot use this capability; they need
the registration number or the mobile number the portal holds.

`applicant.mobile` resolves to `openagrinet:applicantMobile`, the same term PMFBY's
top-level `applicantMobile` uses. It stays an object rather than a flat `applicantMobile`
because no PM-KISAN grievance leaf declares that name, and those leaves are closed — one
term that is required on one capability and rejected on its sibling would read as a
contradiction. One term, two placements.

## Blockers

`application.blockers` is why payment is not arriving, as the portal's beneficiary-status
check reports it.

It is a **set, not a single reason**: two blockers are two separate things for the farmer
to fix, and the upstream returns them as separate keys. v1 collapsed them to one line.

Three states, and they are distinct:

- **absent** — the check was never run, or it did not answer. An `init` acknowledgement
  carries no `application` at all; a `status` answer can carry a complete `application`
  with no `blockers` key, because the record and the blockers are two separate upstream
  reads and only the first is mandatory.
- **present and empty** — the check ran and found nothing. Payment is clear.
- **present and non-empty** — these are the blockers.

v1 conflated the first two, so "we did not ask" and "nothing is wrong" rendered the same.

### Codes

| Code | Meaning |
|---|---|
| `IncomeTaxPayee` | The beneficiary is recorded as an income-tax payee and is therefore ineligible |
| `LandSeedingPending` | Land records have not been seeded against the registration |
| `Other` | Anything else the portal reported |

Only two are governed because only two were ever observed. The legacy client carries a
three-entry lookup table — two blockers and a "No Errors" sentinel — and no master list
exists anywhere in the tree. Rather than invent codes, everything else maps to `Other` and
is read from `name`.

`code` is the network's governed word and is what you branch on. `name` is the portal's
own phrase, kept verbatim, and is what you show. An `Other` blocker is still fully
readable: `{"code": "Other", "name": "Bank account details could not be verified"}`.

## eKYC

`application.ekyc.code` is `Done` or `Pending`. The upstream sends `Y` or `N`; anything the
adapter does not recognise becomes `Pending`, never a guess at `Done`. Telling a farmer
their eKYC is complete when it is not sends them away from the one step that would unblock
their payment.

`ekyc` refuses `name` — the portal sends `Y` or `N`, so there is no phrase to display and
any wording here would be ours presented as the portal's.

## Composition

**This pack stands alone.** It has no cross-pack `$ref` and no remote one. Every schema
it needs is declared in its own `attributes.yaml`, including the ones that read like
another pack's: `PMKISANEnrolmentId`, `PMKISANChallengeResponse`, `Instant`, `Context`
and `Type`.

It used to compose `SchemeServiceBase` out of the Grievance pack, and that is gone.
Checking an application and lodging a grievance are two capabilities; sharing a base
meant a rule written for one silently governed the other, and adding a scheme to one
risked the other. The duplication is a handful of value types, and it buys the property
that matters: **changing the Grievance pack changes nothing here.**

Beckn's `Descriptor` is gone too. `application.ekyc` and each entry in
`application.blockers` are now local closed objects — `ekyc` carries `code` alone,
`blockers` carries `code` and `name` — so the five `Descriptor` members this network does
not model are absent rather than refused by name. That is strictly tighter than the
`NoDescriptorExtras` refusal it replaces, and it is one less file to keep in step.

| schema | holds | published |
|---|---|---|
| `SchemeApplication` | the root: `x-oan-schema-by-action`, `x-beckn-container-by-action`, `x-jsonld`, and a `oneOf` over all three leaves | **yes** |
| `SchemeApplicationCatalog`, `SchemeApplicationInit`, `SchemeApplicationStatus` | one per call, each a `oneOf` over the leaves that serve it | no |
| `IsPMKISAN` | the scheme guard: `scheme.code` pinned to `PM-KISAN`, nothing else | no |
| `PMKISANApplicationCatalog`, `PMKISANApplicationInit`, `PMKISANApplicationStatus` | one complete payload shape each, closed, with no `$ref` to another leaf | no |
| `Applicant`, `PMKISANEnrolmentId`, `PMKISANChallengeResponse`, `Instant`, `Context`, `Type` | the value types | no |

Only `SchemeApplication` is sent. Nothing ever carries
`@type: openagrinet:PMKISANApplicationStatus`; the leaf names exist so that a reader, and
an error message, can say which shape was meant.

What each leaf does on top of the guard:

- pins `scheme.code` to `PM-KISAN`, the only scheme offering this capability today;
- pins `challenge.response.method` and `challenge.methods[].method` to `SMS_OTP`, and
  `challenge.response.value` to **four digits**;
- pins `challenge.methods[].length` and `challenge.issued.length` to the same four, and
  both `valueType`s to `NUMERIC`, so the catalog, the acknowledgement and the value
  itself cannot drift apart;
- narrows `enrolmentId` to ASCII alphanumeric, between six and twenty characters, and
  refuses twelve bare digits, so an Aadhaar number cannot be sent in the registration
  slot — this capability takes no Aadhaar lookup at all;
- closes the leaf with `additionalProperties: false` and declares only the fields the
  call uses, which is how the grievance bands, PMFBY's five fields and `provider` are
  kept out now — by not existing rather than by being named.

## Fields

"Required when" describes a complete payload of that kind. It does not make the field
mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@context` | Always | The JSON-LD context these terms resolve against. Pinned to this pack's own; an array when a Provider publishes extra `@type` values |
| `@type` | Always | Identifies the commitment as `openagrinet:SchemeApplication` |
| `informationMode` | Always | Where the answer comes from. `OnDemand` — the Portal answers — is the only value this version |
| `scheme` | Always | Pinned to `PM-KISAN` |
| `enrolmentId` | An ask by registration, and every answer | The PM-KISAN registration number. Mutually exclusive with `applicant`; returned as the portal's resolution of a mobile lookup |
| `applicant` | An ask by mobile, both calls | Which farmer to look up when the caller has no registration number. Carries `mobile`, and the slot names the kind. Never echoed |
| `challenge.response.method`, `challenge.response.value` | The `status` ask | The four-digit OTP issued by `init`. A credential, not an attribute |
| `challenge.issued` | Returned on `init` | Acknowledgement that an OTP was sent: `method`, `length`, `valueType`, `expiresAt`. Carries no secret and no destination |
| `application.latestInstalmentPaid` | Returned on `status` | How many instalments have been paid. A count, not an instalment number; `0` is an answer, not a missing value |
| `application.blockers` | Optional, returned | Why payment is not arriving. Absent, empty and non-empty are three different answers; see above. `name` is the portal's own phrase and is marked `freetext` / `no-log` / `no-trace` |
| `application.registeredOn` | Optional, returned | When the farmer was registered under the scheme. An instant, not a date — see below |
| `application.ekyc` | Optional, returned | `Done` or `Pending` |
| `challenge.methods` | The catalog entry only | One entry: `method` `SMS_OTP`, `length` `4`, `valueType` `NUMERIC`. A caller reads it to know this desk challenges before answering, and to size the OTP input before any transaction exists. Never sent on a transaction |

`application.registeredOn` is the one timestamp here, and the offset in it is ours.
Upstream `DateOfRegistration` carries a time but no offset — a bare local timestamp, in
practice midnight. The adapter reads it as IST and emits a fully-qualified instant, so
`2021-06-14T00:00:00+05:30` means "the portal said 2021-06-14, and we are telling you we
read that as IST". `Instant` refuses a naked local timestamp precisely so that this
conversion has to happen somewhere nameable rather than being left to the reader.

Where each field is used, by direction, lives in `x-oan-fields` **on each leaf**, with
paths relative to the attributes object. The leaf already says which call it serves, so
the key needs no action index under it. Four buckets: `mustSend`, `oneOf`, `maySend`,
`comesBack`. `oneOf` reads as JSON Schema's does — exactly one of the paths named, never
both and never neither.

**No validator reads `x-oan-fields`.** It is documentation, kept in the schema file so the
two cannot drift. The only extension of this family that code reads is
`x-oan-schema-by-action` on the root. What this pack refuses is in the schema itself, not
here: each leaf is closed and declares only the fields its call uses, so refusal is the
absence of a declaration.

`commitments[0].offer.provider` is required on both `init` and `status`, both its `id`
and the `descriptor.name` beside it — a provider carrying only an `id` is refused. It
sits outside the attributes object, so it cannot appear in the table, but the `id` is
what resolves the Portal and its base URL in the registry and a call without it cannot
be routed. No leaf declares a `provider` member *inside* the attributes object, and all
three are closed, so one sent there is refused: this capability has no `support` channel
to name a desk on, and the provider is already carried in
`commitments[].offer.provider`.

| action | leaf | mustSend | oneOf | maySend | comesBack |
|---|---|---|---|---|---|
| `catalog/publish` | `PMKISANApplicationCatalog` | `informationMode`, `scheme.code`, `scheme.name`, `challenge.methods` | — | — | — |
| `init` | `PMKISANApplicationInit` | `informationMode`, `scheme.code` | `enrolmentId`, `applicant.mobile` | `scheme.name` | `informationMode`, `scheme.code`, `scheme.name`, `challenge.issued.method`, `challenge.issued.length`, `challenge.issued.valueType`, `challenge.issued.expiresAt` |
| `status` | `PMKISANApplicationStatus` | `informationMode`, `scheme.code`, `challenge.response.method`, `challenge.response.value` | `enrolmentId`, `applicant.mobile` | `scheme.name` | `informationMode`, `scheme.code`, `scheme.name`, `enrolmentId`, `application.registeredOn`, `application.latestInstalmentPaid`, `application.ekyc.code`, `application.blockers` |

`informationMode` and `scheme.code` lead every `mustSend` list because every leaf
requires both outright and `scheme.code` is what picks the leaf. `scheme.name` is
optional on `init` and `status` and stays in `maySend` there; `catalog/publish` is the
one place it is required, because a catalog entry naming a scheme only by its code gives
a farmer's screen nothing to show. `catalog/publish` has no `comesBack` bucket: the
Portal answers it with a bare ACK, so the entry is sent and never asked for.

Identity is why `oneOf` exists. Both calls need `enrolmentId` or `applicant.mobile` —
one of them, and not the other beside it. A `mustSend` list is flat and all-of, so
naming either there would be false for the other kind of caller, and leaving both in
`maySend` would let a request builder generated from the lists send no identifier at
all. The ask arm of each leaf's gate enforces it, as a `oneOf` over the two slots: never
both, never neither.

It is an allow-list. A path not named above is not used by this capability. `enrolmentId`
comes back on `status` even when the ask was by mobile — it is the portal's own `Reg_No`,
not an echo — and `applicant` never comes back at all.

## How the pack is laid out

The same shape the Grievance pack uses, for the same reason: a second scheme should be
an addition, never an edit.

| layer | schema | holds |
|---|---|---|
| root | `SchemeApplication` | the published union. A `oneOf` over every leaf, plus the three `x-` keys |
| per call | `SchemeApplicationCatalog`, `SchemeApplicationInit`, `SchemeApplicationStatus` | a `oneOf` over the leaves that serve that call |
| leaf | `PMKISANApplicationCatalog`, `…Init`, `…Status` | one complete payload shape: every field the call uses, closed, and the gate that holds it |

There is no envelope and no per-scheme branch. A leaf restates its own `@context`,
`@type`, `informationMode` and `scheme` rather than inheriting them, which is three lines
repeated three times and the reason **adding a scheme touches one file and edits
nothing**: a new scheme is three or four new leaves, their names added to the per-call
`oneOf`s and to the root, and that is all.

`oneOf`, not `anyOf`. Each leaf pins `scheme.code` to a different value, so at most one
can ever match and the two accept the same payloads. They do not *fail* alike:
kin-openapi throws away the per-arm errors of a failed `anyOf`, so a PMFBY payload sent
here would be told only that no arm matched instead of which field was wrong.

**Each leaf opens with a scheme guard.** `IsPMKISAN` is a separate `allOf` conjunct
rather than a property inside the body, and that placement is load-bearing. kin-openapi
collects exactly **one** error per failing `oneOf` arm but **all** of them per failing
`allOf`. With the guard as its own conjunct, a payload for the wrong scheme always
produces its pinned-value error, which is what lets the validator discard that leaf's
other complaints and report only the fault the caller actually made.

### How the three layers resolve

| what arrives | what it is validated against | what a caller is told |
|---|---|---|
| `init`, named in `x-oan-schema-by-action` | `SchemeApplicationInit` → `PMKISANApplicationInit` | the field's own name |
| an action the key does not name | the root `SchemeApplication` | that no leaf matched, plus the ranked faults |
| anything, through a validator that ignores the key | the root `SchemeApplication` | the same verdict, weaker message |

`x-oan-schema-by-action` names the schema each call is validated against:

| action | schema |
|---|---|
| `catalog/publish` | `SchemeApplicationCatalog` |
| `init` | `SchemeApplicationInit` |
| `status` | `SchemeApplicationStatus` |

The catalog is listed against `catalog/publish` rather than `discover` because a
`discover` request carries an intent and no attributes at all — the catalog this pack
describes travels on the publish call.

**The key narrows, and the narrowing is real.** The root union accepts whatever any leaf
accepts, so a complete `init` payload passes it even when it arrives as `status` — the
union cannot see which call is in flight. The per-call schema can, and refuses it. So the
key changes the verdict, not only the wording: against the union a caller who omitted one
field is told that no leaf matched, and a caller who sent a good payload to the wrong call
is told nothing at all; against the per-call schema both are told the field's name.

An action the key does not name still falls back to the union. That is a safety net for a
validator that does not read the key, not an equivalent to reading it.

## The gates

Each leaf carries one gate, as a third `allOf` conjunct beside the guard and the body.
All are tested against the real validator. `if`/`then` would read more naturally and does
not work: this validator parses it and never evaluates it, so a guard written that way
looks like it holds and does not. `anyOf`, `not` and `oneOf` *are* evaluated.

Where a gate guards a requirement it is written as an exclusive `oneOf` rather than an
`anyOf`, for the reason above: kin-openapi discards an `anyOf`'s per-arm errors, so the
caller would be told only that nothing matched.

1. **`init` is an ask or an acknowledgement.** The ask carries exactly one identifier —
   `enrolmentId` **or** `applicant`, by `oneOf`, never both and never neither — and no
   `challenge`. The acknowledgement carries `challenge.issued` and does not echo
   `applicant`: the mobile it was sent to is `no-echo`.
2. **`status` is an ask or an answer, told apart by the record.** The ask carries
   `challenge.response`, exactly one identifier by the same `oneOf`, and no
   `application`. The answer carries `application` and the `enrolmentId` the portal
   resolved, and never the `applicant` it was given.
3. **The catalog entry needs no gate.** `PMKISANApplicationCatalog` declares
   `informationMode`, `scheme` and `challenge.methods`, and nothing else. An entry names
   no farmer because there is no slot to name one in — not because a rule forbids it.

Everything else that used to be a gate is now a shape.

| the old gate | what holds it now |
|---|---|
| one identifier slot, not two | the `oneOf` in each ask arm; the answer arms refuse `applicant` outright |
| every payload is about something | each leaf's own `required` list plus its gate — there is no shape left that is a scheme name and nothing else |
| a catalog declaration cannot ride with a real lookup | `PMKISANApplicationCatalog` is its own leaf and declares neither |
| the grievance bands and PMFBY's five fields refused by name | `additionalProperties: false` on every leaf — they are not declared, so they are not accepted |
| `provider` refused by name | likewise: no leaf declares it |
| nothing but `code` and `name` in a `Descriptor` | `ekyc` and `blockers` are local closed objects with exactly those members |
| exactly one member of `challenge` | each leaf declares only the member its call uses, and `challenge` is closed |

One rule is unchanged and still lives in a value type: **`enrolmentId` has a floor** —
six characters, not one, alongside the twenty-character ceiling. A single-character
registration number is not a registration number.

There used to be one more gate: a check of a declared identifier type against the value
beside it. The named slots removed the need, because there is no pair left to disagree.

## The pack is closed at every level

Every leaf carries `additionalProperties: false`, and so does every object beneath it —
`scheme`, `applicant`, `application`, `ekyc`, each `blockers` entry, `challenge` and each
member under it. **An unknown key is rejected wherever it appears, top level included.**

This is the one change the flat layout bought outright. The old root was an `allOf` over
a base, the JSON-LD guards and this pack's own layer, and a root composed that way
*cannot* be closed: `additionalProperties: false` on it sees only the properties the root
itself declares, and every real field was declared in a sibling member, so adding it
would have rejected every valid payload. It was left off, and an unknown top-level key
was accepted. A leaf declares all of its own fields in one object, so closing it costs
nothing.

What the schema still cannot enforce is the direction of travel on the way back: the
"response mapping is an allow-list, not a passthrough" rule under "Privacy" is one the
adapter keeps. Responses are built after validation runs and are never validated.

## Privacy

Every identifier here — `enrolmentId` and whichever member `applicant` carries — is
`no-log` and `no-trace` without exception, and never appears in an error body. Each is a
bearer key as much as an identifier: anyone holding one can read the record.

`mobile` is never echoed in a response, and that is structural rather than only a mapping
rule in part: `x-oan-pii` marks it `no-echo`, and the exclusivity gate makes an answer
carrying both the key and the registration it resolved to unrepresentable. `enrolmentId`
is the single deliberate exception: it goes back to the caller who sent it, or comes back
as the portal's resolution of a mobile lookup.

**No Aadhaar number enters this capability.** There is no slot for one, and `enrolmentId`
refuses twelve bare digits, so the question of logging or retaining one does not arise.

`challenge.response.value` is a credential. It is never forwarded to the read it guards,
never logged, never traced, never echoed.

**The upstream record carries far more about the farmer than this pack surfaces.**
Alongside the status it returns the farmer's name, father's name, date of birth, gender,
full address and state, district, sub-district and village. None of it is modelled and none
of it is emitted. The caller already knows who they asked about, and publishing it would
disclose more than the identity the pack goes to some trouble to withhold. An adapter must
drop these fields rather than pass them through — the pack cannot stop it, because
`commitmentAttributes` is open. **The response mapping is an allow-list, not a passthrough.**

This is a deliberate break from the v1 flow, which showed the farmer their own name and
village back to them.

`application.blockers[].name` is the portal's own phrase, returned verbatim, and it is
the **one place in either pack where a portal's phrase travels**. The general rule is
that a portal's message is logged redacted and never returned, because it may hold a
stack trace, an internal hostname or a quoted-back credential. This field is the
deliberate exception: the phrase is the answer — it is the only statement of why payment
is not arriving, and the `code` beside it classifies at a grain too coarse to replace it.
It is marked `freetext` with `no-log` and `no-trace` handling, so it reaches the caller
and nowhere else. Every other `Descriptor` slot in this pack refuses the free-text
members outright; this one keeps `name` and refuses the other five.

## Naming

`latestInstalmentPaid` uses the single-l British spelling the rest of this repo uses for
"instalment". The portal's own category label `Installment not received`, quoted in the
grievance pack, keeps the portal's spelling — that is a value, not a property name.

`SMS_OTP` and `NUMERIC` break the repo's UpperCamelCase convention for governed values.
They are kept as they are: read as acronyms, written that way by every integrator, and
renaming them would churn the mapping files for no gain.

## Non-goals

This pack does not describe the transport envelope. The portal payload travels encrypted
and the response arrives wrapped; both belong to the adapter. Neither the ciphertext nor
the service token appears here or in any payload this pack describes.

The envelope is **not** a confidentiality control and nothing may be built as though it
were: the upstream OTP service transmits its key in the clear beside the ciphertext. A
decryption failure must not log the ciphertext.

The pack also does not define credentials. Those live in the adapter configuration, where
credentials are **named** by environment variable and never held.

Two fields the portal returns are absent because the mapping consumes them: the success
flag (`Rsponce`), which decides between a response and an error, and the message
(`Message`), which is transport chatter and may carry a stack trace or an internal
hostname. The portal's own message is never returned to a caller.

It does not cover filing an application, or any grievance. Those are other capabilities;
the grievance one has [its own pack](../../Grievance/v0.1/README.md).

## Examples

One per call, and every one is `OnDemand`, because every payload on this capability is:
the discovery service holds no application of its own, so the Experience layer always asks
the portal.

- [The catalog entry](examples/on-demand-capability.json)
- [On-demand: request an OTP](examples/on-demand-request-otp.json) — by mobile here; a registration number works the same way, and either one alone is enough
- [On-demand: OTP issued](examples/on-demand-challenge-issued.json)
- [On-demand: read the status](examples/on-demand-read-status.json)

Published examples show the logical form, every field inline; they are not wire payloads.
