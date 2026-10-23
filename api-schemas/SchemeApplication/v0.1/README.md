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

One scheme is covered today — **PM-KISAN** — named by `scheme.code`. The pack is named for
the capability rather than the scheme so a second scheme is a widened enum rather than a
second pack.

This is an API schema, not a domain schema. It says what a named Provider's API will take
and give back.

**It is not a grievance.** Nothing is filed, nothing has a lifecycle, and nothing comes
back with a case number. That is why it is a pack of its own rather than a mode of
[Grievance](../../Grievance/v0.1/README.md) — the two share a desk, an OTP service and a
base schema, and share no subject.

**Filing an application is not implemented.** When it is, it is another pack over the same
`SchemeServiceBase`, not a change to this one.

## Attachment point

| what | where | on which call |
|---|---|---|
| the **declaration** — this desk exists, here is what it accepts | `resourceAttributes` of a catalog `Resource` | `catalog/publish`, `discover`, `on_discover` |
| one farmer's **application record** | `commitmentAttributes` of a `Commitment` | `init`, `status` |

The declaration is catalogable: `informationMode`, `scheme` and the challenge methods
describe the desk, so they sit on `resourceAttributes` as in every other OAN pack. A
status read is not catalogable — it is a promise the portal makes about one farmer's
application, so it sits on `commitmentAttributes`.

Unlike the grievance pack there is **no `support` call**: nothing is being filed, so no
`Support` channel is ever composed and no field moves out of the attributes object.
`x-beckn-container-by-action` therefore lists `discover`, `init` and `status`, and no
`channels`. No field in this family carries an `x-beckn-path` at all, so there is nothing
to fire: every field is read at the same path on both calls.

`Commitment.resources` carries one thin pointer to the catalog entry
(`res:pmkisan:application-status`). It is fixed for the provider and never minted per
farmer: a registration number must not end up in a public, cacheable identifier.

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
information mode the schema can no longer tell an ask from an answer, so the one-way rule
is carried by `x-oan-pii` and the mapping rather than by a gate. `enrolmentId` travels in
both directions. A caller who holds the registration number
sends it; a caller who holds only a mobile number sends `applicant` instead,
and the portal resolves it and returns the registration number under `enrolmentId`. The
two slots are mutually exclusive — exactly one, never both. See "Identity is named, not
sniffed".

Everything about challenging this desk lives under one `challenge` object, which is why
the last two bands are nested rather than top level. The container itself carries no
authorship marking — `methods` is published in the catalog, `issued` is the portal's and
`response` is the caller's, so each member is marked on its own. Exactly one of the three
is present on any payload; the base enforces it, so a catalog entry cannot carry a live
code beside the declaration it publishes.

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

`init` exists here and not on PM-KISAN's grievance desk for the same reason it exists at
all: this read is gated and lodging a grievance is not. The OTP is the same OTP — the same
upstream service issues it and the same four digits satisfy it — so a caller who holds one
from a grievance flow can spend it here.

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
| `enrolmentId` | ASCII alphanumeric, up to 20; twelve bare digits refused | `Ben_id` |
| `applicant.mobile` | `^[6-9][0-9]{9}$` | `Mobile` |

A registration number is `enrolmentId` — the same field under the same name as on the
grievance pack, so a reader writes `.enrolmentId` once for the whole family rather than
learning a second name per capability.

`enrolmentId` has no digit rule on purpose. The portal treats anything that is not a
mobile number as a registration, and a registration that happens to be ten digits is
exactly the case this slot exists to carry safely. It does refuse twelve bare digits:
that is an Aadhaar number's shape, and this capability takes no Aadhaar lookup, so the
refusal keeps one out of the registration slot rather than redirecting it elsewhere.
Both the registration rule and that refusal are `$ref`s into the Grievance pack —
`PMKISANEnrolmentId` over `NotBareAadhaar` — because the grievance desk reads the same
registration on the same portal, and two copies of a rule are two chances to lose one.
The `challenge` narrowing to a four-digit numeric code by SMS is shared the same way.

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
apart by a top-level gate — an
`anyOf` of two `not`/`required` members, the one gate where the condition is which other
field is present — and a further gate requires that every payload
carry at least one of the slots that makes it about something.

**Aadhaar is not a lookup key on this capability.** There is no slot for one, and
`enrolmentId` refuses twelve bare digits so one cannot be sent in the registration slot
either. A caller who holds only an Aadhaar number cannot use this capability; they need
the registration number or the mobile number the portal holds.

`applicant.mobile` resolves to `openagrinet:applicantMobile`, the same term PMFBY's
top-level `applicantMobile` uses. It stays an object rather than a flat `applicantMobile`
because the PM-KISAN grievance branch refuses that name outright, and one term that is
required on one capability and refused on its sibling would read as a contradiction. One
term, two placements.

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

The pack composes **`SchemeServiceBase`** from
[`../../Grievance/v0.1/attributes.yaml`](../../Grievance/v0.1/attributes.yaml), which is
where `informationMode`, `provider`, `scheme`, `enrolmentId` and the whole `challenge`
object come from, with their privacy markings already attached.

That base is the scheme-service layer: what any desk needs whether or not it handles
grievances. The grievance bands — `grievance`, `case`, `grievanceOptions` — sit one layer
up, in `GrievanceBase`, which this pack does not touch. They are not in this pack's
vocabulary, and they are refused by name all the same: the composed root is open, so
not declaring a field is not the same as keeping it out.

`ekyc` and each entry in `blockers` compose Beckn's `Descriptor`, which is the established
idiom for a governed `code` paired with a display `name`. `blockers` uses both: the portal
sends real text and the `code` classifies it. Both also compose `NoDescriptorExtras` from
the grievance pack, which refuses the five `Descriptor` members this network does not
model — see "The gates".

On top of the base this pack:

- adds `applicant` and `application`;
- pins `scheme.code` to `PM-KISAN`, the only scheme offering this capability today;
- pins `challenge.response.method` and `challenge.methods[].method` to `SMS_OTP`, and
  `challenge.response.value` to **four digits** — the base allows four to eight, so each
  desk pins its own;
- pins `challenge.methods[].length` and `challenge.issued.length` to the same four, and
  both `valueType`s to `NUMERIC`, so the catalog, the acknowledgement and the value itself
  cannot drift apart;
- refuses the grievance bands, PMFBY's five fields and `provider` by name, because none
  belongs to this capability and an undeclared field on an open root is accepted, not
  rejected;
- narrows `enrolmentId` to ASCII alphanumeric, between six and twenty characters, and
  refuses twelve bare digits, so an Aadhaar number cannot be sent in the registration
  slot — this capability takes no Aadhaar lookup at all;
- holds `enrolmentId` and `applicant` mutually exclusive, and requires that every payload
  carry at least one slot that says what it is about.

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

Where each field is used, by action and by direction, lives in `x-oan-fields-by-action`,
with paths relative to the attributes object. Four buckets per action: `mustSend`,
`oneOf`, `maySend`, `comesBack`. `oneOf` reads as JSON Schema's does — exactly one of
the paths named, never both and never neither. What this pack refuses is in the schema
itself, not here — the gates are structural and bite on every action.

`commitments[0].offer.provider` is required on both `init` and `status`, both its `id`
and the `descriptor.name` beside it — a provider carrying only an `id` is refused. It
sits outside the attributes object, so it cannot appear in the table, but the `id` is
what resolves the Portal and its base URL in the registry and a call without it cannot
be routed. The `provider` member *inside* the attributes object is a different thing and
is refused here, because this capability has no `support` channel to name a desk on.

| action | mustSend | oneOf | maySend | comesBack |
|---|---|---|---|---|
| `discover` | — | — | — | `informationMode`, `scheme.code`, `scheme.name`, `challenge.methods` |
| `init` | `informationMode`, `scheme.code` | `enrolmentId`, `applicant.mobile` | `scheme.name` | `informationMode`, `scheme.code`, `scheme.name`, `challenge.issued.method`, `challenge.issued.length`, `challenge.issued.valueType`, `challenge.issued.expiresAt` |
| `status` | `informationMode`, `scheme.code`, `challenge.response.method`, `challenge.response.value` | `enrolmentId`, `applicant.mobile` | `scheme.name` | `informationMode`, `scheme.code`, `scheme.name`, `enrolmentId`, `application.registeredOn`, `application.latestInstalmentPaid`, `application.ekyc.code`, `application.blockers` |

`informationMode` and `scheme.code` lead both `mustSend` lists because the base requires
both outright and `scheme.code` is what picks the branch; `scheme.name` is genuinely
optional and stays in `maySend`.

Identity is why `oneOf` exists. Both calls need `enrolmentId` or `applicant.mobile` —
one of them, and not the other beside it. A `mustSend` list is flat and all-of, so
naming either there would be false for the other kind of caller, and leaving both in
`maySend` would let a request builder generated from the lists send no identifier at
all. Two gates enforce it: one refuses a payload that is about nothing, the other
refuses a payload carrying both.

It is an allow-list. A path not named above is not used by this capability. `enrolmentId`
comes back on `status` even when the ask was by mobile — it is the portal's own `Reg_No`,
not an echo — and `applicant` never comes back at all.

## How the pack is laid out

The same three layers the Grievance pack uses, for the same reason: a second scheme
should be an addition, never an edit.

| layer | schema | holds |
|---|---|---|
| envelope | `SchemeApplicationEnvelope` | what holds whatever scheme the payload is about — the service base, the JSON-LD envelope, `applicant`, and the bands this capability refuses |
| branch | `PMKISANApplication` | one per scheme. Pins `scheme.code` to a `const` and composes that scheme's field shapes (`PMKISANApplicationFields`) |
| per call | `PMKISANApplicationCatalog`, `…Init`, `…Status` | what one call must carry on that scheme |

`SchemeApplication` is the published union: the envelope plus a `oneOf` over the scheme
branches. There is one arm today. A second scheme is one more arm there, one more branch,
one more set of per-call schemas — and nothing else moves.

`oneOf`, not `anyOf`. Each branch pins `scheme.code` to a different `const`, so exactly
one can ever match and the two accept the same set. They do not *fail* alike: kin-openapi
throws away the per-arm errors of a failed `anyOf`, so a PMFBY payload sent here would be
told only that no arm matched instead of which field was wrong.

`x-oan-schema-by-action` names the schema each call is validated against:

| action | schema |
|---|---|
| `discover` | `SchemeApplicationCatalog` |
| `init` | `SchemeApplicationInit` |
| `status` | `SchemeApplicationStatus` |

A validator that does not read that key falls back to the union, which accepts and refuses
exactly the same payloads — it is the error messages that differ, not the verdict. Against
the union a caller who omitted one field is told that no arm matched; against the per-call
schema they are told the field's name.

## The gates

Four gates hold whatever call the payload is for. All are tested against the real
validator. `if`/`then` would read more naturally and does not work: this validator parses
it and never evaluates it, so a guard written that way looks like it holds and does not.
`anyOf`, `not` and `oneOf` *are* evaluated.

Where a gate guards a requirement it is written as an exclusive `oneOf` rather than an
`anyOf`, for the reason above. The rest are refusals, and they name their field for the
same reason: a refused field is declared with `FieldNotAllowed`, which admits no value of
any type, so the validator anchors the failure at the property — `value is not allowed
here @ provider` — instead of the `doesn't match all schemas` an object-level `not` would
have produced with no pointer at all.

1. **One identifier slot, not two.** `enrolmentId` and `applicant` are mutually exclusive
   — an `anyOf` of two `not`/`required` members, because the ban is conditional on the
   other field rather than outright. Both at once names the same farmer twice
   with no rule for which wins, and it is also the shape a response would take if it
   leaked the lookup key back beside the registration it resolved to.
2. **Every payload is about something** — `enrolmentId`, `applicant`, `application`, or a
   `challenge` carrying `issued` or `methods`. This is what stops a payload that is a
   scheme name and nothing else. The `on_init` acknowledgement and the catalog entry both
   start at `challenge`, so they are told apart by which member is present: `issued` on
   the acknowledgement, `methods` on the entry. A bare `challenge` with neither is about
   nothing and is refused.
3. **A catalog declaration makes the payload a catalog entry.** An entry names no farmer,
   so carrying `challenge.methods` also requires the absence of `enrolmentId`,
   `applicant` and `application`. A declaration cannot ride alongside a real lookup.
4. **The other capability's fields are refused by name** — the grievance bands
   (`grievance`, `case`, `grievanceOptions`) and PMFBY's five (`applicantMobile`,
   `cropYear`, `season`, `complaintDate`, `receiptSourceId`), both by `$ref` to the
   shared lists `NoGrievanceBands` and `NoPMFBYFields` in the grievance pack, so neither
   side can drift. `applicantMobile` matters most: a mobile number belongs in
   `applicant` here, and a bare `applicantMobile` would be a second way to send one past
   the rules that govern the first. `provider` is refused separately — it belongs on a
   `support` channel and this capability has none. See "The composed root is open".

Each call then adds what it alone must carry, and this is where the rules that used to be
keyed on `informationMode` now live — an answer must carry a record, an answer must name
the farmer, `application` may not ride on an ask, `applicant` may not ride on an answer.
With one information mode there is nothing left to key them on; told apart by shape, they
hold again.

5. **`discover` publishes and names nobody.** A catalog entry carries `challenge.methods`
   and no answer to the challenge, no `enrolmentId`, no `applicant` and no `application`.
6. **`init` is an ask or an acknowledgement.** The ask carries exactly one identifier and
   no `challenge`. The acknowledgement carries `challenge.issued`, no answer to it, and
   does not echo `applicant` — the mobile it was sent to is `no-echo`.
7. **`status` is an ask or an answer, told apart by the record.** The ask carries
   `challenge.response`, exactly one identifier, and no `application`. The answer carries
   `application` and the `enrolmentId` the portal resolved, and never the `applicant` it
   was given.

Two further refusals sit below the root. **Nothing but `code` and `name` travels in a
`Descriptor`:** `application.ekyc` and each entry in `application.blockers` compose
`NoDescriptorExtras`, which refuses `longDesc`, `shortDesc`, `thumbnailImage`, `docs` and
`mediaFile` by name. Two of the five are free text and none is modelled here, so an
adapter that passed a portal's `Descriptor` through wholesale is rejected rather than
quietly widening what travels. And **`enrolmentId` has a floor**: six characters, not
one, alongside the twenty-character ceiling. A single-character registration number is
not a registration number.

Exactly one member of `challenge` is a further rule, and it comes from
`SchemeServiceBase` rather than from here: the container closes with a `oneOf` over the
three members, so a catalog entry cannot carry a live code, an acknowledgement cannot
ride with an answer, and a bare `challenge: {}` is about nothing and refused.

There used to be one more: a check of a declared identifier type against the value beside
it. The named slots removed the need, because there is no pair left to disagree.

The refusal of the three grievance bands **came back**. Rebasing on `SchemeServiceBase`
took them out of this pack's vocabulary, and an earlier revision of this file read that
as having removed the need for the refusal. It had not: the composed root is open, so a
field this pack never declares is accepted rather than rejected, and `grievance` and
`case` validated here for as long as the refusal was gone. They are refused by name
again — and by `$ref` to `NoGrievanceBands` in the grievance pack rather than by a copy,
because the copy is what went stale the first time.

PMFBY's five top-level fields are refused the same way, through `NoPMFBYFields`. They
were never declared here either, and the consequence was the same: a bare
`applicantMobile` validated against this pack, which gives a mobile number a second route
in, beside `applicant.mobile` and outside every rule that governs it.

`provider` joined them in this revision. It is declared on `SchemeServiceBase` and so
*is* in this pack's vocabulary, but it belongs to a `support` call — where a caller names
the desk it is addressing — and this capability has none. Both actions here ride on
`commitmentAttributes`, where the provider is already carried in
`commitments[].offer.provider`, so naming it a second time inside the attributes object
gives a second place for it to disagree with the first.

## The composed root is open

`SchemeApplication` is an `allOf` over `SchemeServiceBase`, the JSON-LD guards and this
pack's own layer. A root composed that way **cannot be closed**: `additionalProperties:
false` on the root sees only the properties the root itself declares, and every real
field is declared in a sibling `allOf` member, so adding it rejects every valid payload.
It is left off deliberately, and the consequence is worth stating plainly: **an unknown
top-level key is accepted.**

Only at the root. The bands below it are ordinary objects, not compositions, and both of
them **are** closed: `applicant` and `application` carry `additionalProperties: false`,
so an unknown key inside either is rejected. So the gap is exactly one level wide — a
stray top-level key is accepted, a stray key anywhere beneath one is not.

Within that one level, a field that must not appear is refused by name: it is declared
with `FieldNotAllowed`, which admits no value. Not declaring it is not a refusal. And the "response mapping is an
allow-list, not a passthrough" rule under "Privacy" is one the adapter keeps, not one the
schema can enforce.

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
