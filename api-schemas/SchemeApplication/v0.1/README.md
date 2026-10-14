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

Applied to `commitmentAttributes` of a Beckn `Commitment`, on `init` and on `status`.

A status read is a promise the portal makes about one farmer's application, not a
catalogable thing of value, so it does not sit on `resourceAttributes`. Unlike the
grievance pack there is **no `support` leg**: nothing is being filed, so no `Support`
channel is ever composed and no field moves out of the attributes object.
`x-beckn-container-by-action` therefore lists `init` and `status` and nothing else. No
field in this family carries an `x-beckn-path` at all, so there is nothing to fire: every
field is read at the same path on both legs.

`Commitment.resources` carries one thin pointer to the catalog entry
(`res:pmkisan:application-status`). It is fixed for the provider and never minted per
farmer: a registration number must not end up in a public, cacheable identifier.

## The bands

**The band a field sits in says who wrote it.**

| band | holds | written by |
|---|---|---|
| top level | what is being asked and under which scheme: `informationMode`, `scheme`, `enrolmentId` | the caller |
| `applicant` | who to look up when the caller has no enrolment number: exactly one of `mobile` or `aadhaar` | the caller, and inbound only |
| `application` | what the portal holds: `registeredOn`, `latestInstalmentPaid`, `ekyc`, `blockers` | the portal, and outbound only |
| `challenge.response` | the OTP presented on the read | the caller |
| `challenge.issued` | acknowledgement that one was sent | the portal |

`applicant` and `application` are each enforced one-way, not merely described that
way: `applicant` may not ride on a `Direct` payload and `application` may not ride on an
`OnDemand` one. `enrolmentId` is the exception and travels in both directions. A caller who holds the registration number
sends it; a caller who holds only a mobile or an Aadhaar number sends `applicant` instead,
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

## Direction, not action

Direction is carried by `informationMode`, never by the Beckn action. `OnDemand` is the
ask; `Direct` is an answer carrying a real record. The same attributes serve both `init`
and `status`.

The sequence is two calls:

| | action | the caller sends | the portal returns |
|---|---|---|---|
| 1 | `init` | `enrolmentId` **or** `applicant` | `challenge.issued` — an OTP has gone to the number the application is held under |
| 2 | `status` | the same identifier + `challenge.response` | `enrolmentId` + `application` |

The OTP acknowledgement is `OnDemand`, not `Direct`, even though it comes back from the
portal. It carries no record — it says a challenge was sent and nothing else — and `Direct`
is reserved for the payload carrying the application itself. The grievance pack does the
same.

`init` exists here and not on PM-KISAN's grievance leg for the same reason it exists at
all: this read is gated and lodging a grievance is not. The OTP is the same OTP — the same
upstream service issues it and the same four digits satisfy it — so a caller who holds one
from a grievance flow can spend it here.

## Identity is named, not sniffed

Every ask carries exactly one identifier, and the slot it is written in says what kind it
is. This is the pack's main correction to the upstream behaviour.

The portal infers what kind of identifier it has been handed from the *shape* of the
value: ten digits beginning 6–9 is a mobile number, twelve digits is an Aadhaar number,
anything else is a registration number. A registration number that happens to be ten
digits starting with a 7 therefore becomes a phone lookup, silently, and returns either
nothing or somebody else's record. Nothing upstream reports that this happened.

So the kind is named outright, each slot carries its own shape rule, and the adapter sends
the named type rather than letting the portal guess:

| slot | shape the pack enforces | sent upstream as |
|---|---|---|
| `enrolmentId` | ASCII alphanumeric, up to 20; twelve bare digits refused | `Ben_id` |
| `applicant.mobile` | `^[6-9][0-9]{9}$` | `Mobile` |
| `applicant.aadhaar` | `^[0-9]{12}$` | `Aadhar` — the upstream's spelling, not ours |

A registration number is `enrolmentId` — the same field under the same name as on the
grievance pack, so a reader writes `.enrolmentId` once for the whole family rather than
learning a second name per capability.

`enrolmentId` has no digit rule on purpose. The portal treats anything that is not a
mobile or an Aadhaar number as a registration, and a registration that happens to be ten
digits is exactly the case this slot exists to carry safely. It does refuse twelve bare
digits: that is an Aadhaar number's shape, a caller may send this field, and the upstream
would take the value as `Ben_id` and find nothing. An Aadhaar lookup belongs in
`applicant.aadhaar`.

The observed form is two letters and nine digits — `BR295454592` is the value v1's own
test fixtures use — and v1 validates it as `/^[A-Z0-9]+$/i`, which is the pattern pinned
here. Whether two-plus-nine holds for every state is not confirmed, so no length rule is
imposed.

One slot per kind, rather than a kind field beside a generic value. A pair has to be
checked against itself — otherwise a caller declares a mobile and sends twelve letters —
and that check is a gate that can be written wrong. Named slots make the mismatch
unrepresentable instead of merely refused, let each identifier carry its own handling
rules (an Aadhaar number is not governed like a phone number), and give each a stable IRI
rather than one whose meaning depends on a sibling.

Within `applicant`, exactly one of `mobile` and `aadhaar` is enforced by `oneOf` over the
two `required` branches, which this validator does evaluate: two identifiers match two
branches and fail, none matches zero and fails. `additionalProperties: false` closes off
anything else. `enrolmentId` and `applicant` are held apart by a top-level gate — an
`anyOf` of two `not`/`required` members — and a further gate requires that every payload
carry at least one of the slots that makes it about something.

**Aadhaar is accepted here and refused on the grievance pack.** The difference is real,
not an oversight: this is a read of the farmer's own record behind an OTP, where the
upstream genuinely takes an Aadhaar number as a lookup key. On a grievance the same field
would be sometimes a stable reference and sometimes an ephemeral token, which is why that
pack closes it off.

No example in this pack sends `applicant.aadhaar`. That is deliberate: a published
example value would be a twelve-digit string in Aadhaar position, copied into tests and
fixtures by everyone who reads it. The field's shape is in `attributes.yaml`; the
examples take the `mobile` branch.

`applicant.mobile` resolves to `openagrinet:applicantMobile`, the same term PMFBY's
top-level `applicantMobile` uses. The property stays `mobile` here, beside `aadhaar`,
because `applicant.applicantMobile` would be redundant and would break the symmetry of the
two slots. One term, two placements.

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
up, in `GrievanceBase`, which this pack does not touch. An earlier revision composed
`GrievanceBase` and then refused those three members one by one; splitting the base
removed the need. They are not in this pack's vocabulary at all.

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
- refuses `grievance`, `case`, `grievanceOptions` and `provider` by name, because none
  belongs to this capability and an undeclared field on an open root is accepted, not
  rejected;
- narrows `enrolmentId` to ASCII alphanumeric, between six and twenty characters, and
  refuses twelve bare digits so an Aadhaar number cannot be sent in the registration slot;
- holds `enrolmentId` and `applicant` mutually exclusive, and requires that every payload
  carry at least one slot that says what it is about.

## Fields

"Required when" describes a complete payload of that kind. It does not make the field
mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@context` | Always | The JSON-LD context these terms resolve against. Pinned to this pack's own; an array when a Provider publishes extra `@type` values |
| `@type` | Always | Identifies the commitment as `openagrinet:SchemeApplication` |
| `informationMode` | Always | `OnDemand` is the ask; `Direct` carries a real record |
| `scheme` | Always | Pinned to `PM-KISAN` |
| `enrolmentId` | An ask by registration, and every answer | The PM-KISAN registration number. Mutually exclusive with `applicant`; returned as the portal's resolution of a mobile or Aadhaar lookup |
| `applicant` | An ask by mobile or Aadhaar, both legs | Which farmer to look up when the caller has no registration number. Exactly one of `mobile` or `aadhaar`; the member names the kind. Never echoed |
| `challenge.response.method`, `challenge.response.value` | The `status` ask | The four-digit OTP issued by `init`. A credential, not an attribute |
| `challenge.issued` | `Direct` on `init` | Acknowledgement that an OTP was sent: `method`, `length`, `valueType`, `expiresAt`. Carries no secret and no destination |
| `application.latestInstalmentPaid` | `Direct` on `status` | How many instalments have been paid. A count, not an instalment number; `0` is an answer, not a missing value |
| `application.blockers` | Optional in `Direct` | Why payment is not arriving. Absent, empty and non-empty are three different answers; see above. `name` is the portal's own phrase and is marked `freetext` / `no-log` / `no-trace` |
| `application.registeredOn` | Optional in `Direct` | When the farmer was registered under the scheme. An instant, not a date — see below |
| `application.ekyc` | Optional in `Direct` | `Done` or `Pending` |
| `challenge.methods` | The catalog entry only | One entry: `method` `SMS_OTP`, `length` `4`, `valueType` `NUMERIC`. A caller reads it to know this desk challenges before answering, and to size the OTP input before any transaction exists. Never sent on a transaction |

`application.registeredOn` is the one timestamp here, and the offset in it is ours.
Upstream `DateOfRegistration` carries a time but no offset — a bare local timestamp, in
practice midnight. The adapter reads it as IST and emits a fully-qualified instant, so
`2021-06-14T00:00:00+05:30` means "the portal said 2021-06-14, and we are telling you we
read that as IST". `Instant` refuses a naked local timestamp precisely so that this
conversion has to happen somewhere nameable rather than being left to the reader.

Where each field is used, by action and by direction, lives in `x-oan-fields-by-action`,
with paths relative to the attributes object. Three buckets per action — `mustSend`,
`maySend`, `comesBack` — plus a pack-wide `refused` list stated once, because the gates
that enforce it are structural and bite on every action:

| action | mustSend | maySend | comesBack |
|---|---|---|---|
| `discover` | — | — | `informationMode`, `scheme.code`, `scheme.name`, `challenge.methods` |
| `init` | — | `informationMode`, `scheme.code`, `enrolmentId`, `applicant.mobile`, `applicant.aadhaar` | `informationMode`, `scheme.code`, `scheme.name`, `challenge.issued.method`, `challenge.issued.length`, `challenge.issued.valueType`, `challenge.issued.expiresAt` |
| `status` | `challenge.response.method`, `challenge.response.value` | `informationMode`, `scheme.code`, `enrolmentId`, `applicant.mobile`, `applicant.aadhaar` | `informationMode`, `scheme.code`, `scheme.name`, `enrolmentId`, `application.registeredOn`, `application.latestInstalmentPaid`, `application.ekyc.code`, `application.blockers` |

Refused: `provider`, `application.ekyc.name`, `grievance`, `case`, `grievanceOptions`.

Neither `mustSend` names an identifier, and `init` has no `mustSend` at all. Both legs need
one of `enrolmentId`, `applicant.mobile` or `applicant.aadhaar`, but a `mustSend` list is
flat and all-of: naming any one of them there would be false for the other callers. They
sit in `maySend` instead, and the requirement is a gate, which is the only place it can
actually be enforced.

It is an allow-list. A path not named above is not used by this capability. `enrolmentId`
comes back on `status` even when the ask was by mobile or by Aadhaar — it is the portal's
own `Reg_No`, not an echo — and `applicant` never comes back at all.

## The gates

Eight top-level gates, all tested against the real validator. `if`/`then` would read more
naturally and does not work: this validator parses it and never evaluates it, so a guard
written that way looks like it holds and does not. `anyOf`, `not` and `oneOf` *are*
evaluated.

1. **A `Direct` payload carries a record.** Either `informationMode` is `OnDemand`, or
   `application` is present. An answer with nothing in it is not an answer.
2. **One identifier slot, not two.** `enrolmentId` and `applicant` are mutually exclusive
   — an `anyOf` of two `not`/`required` members. Both at once names the same farmer twice
   with no rule for which wins, and it is also the shape a response would take if it
   leaked an Aadhaar number back beside the registration it resolved to.
3. **Every payload is about something** — `enrolmentId`, `applicant`, `application`, or a
   `challenge` carrying `issued` or `methods`. This is what stops a payload that is a
   scheme name and nothing else. The `on_init` acknowledgement and the catalog entry both
   start at `challenge`, so they are told apart by which member is present: `issued` on
   the acknowledgement, `methods` on the entry. A bare `challenge` with neither is about
   nothing and is refused.
4. **An answer may not carry `challenge.response`.** The OTP is sent, never returned: a
   payload carrying it must have `informationMode` other than `Direct`. The member is
   absent vacuously when `challenge` itself is, which is what lets the gate be written
   against the container. `x-oan-pii` marks the value `no-echo`, but that binds the
   mapping; this is the structural half of the same rule.
5. **A catalog declaration makes the payload a catalog entry.** Carrying
   `challenge.methods` is not merely incompatible with `Direct`: an entry names no
   farmer, so the gate also requires `OnDemand` and the absence of `enrolmentId`,
   `applicant` and `application`. A declaration cannot ride alongside a real lookup.
6. **The `application` band may not ride on an ask.** Everything in it is the portal's,
   and unlike a grievance case there is no selector inside it — a read is keyed on
   `enrolmentId` or `applicant` — so nothing in the band is the caller's to send.
7. **The `applicant` band may not ride on an answer.** The mirror of rule 6. It is the
   caller's lookup key, and both members are `no-echo`; where the portal resolves a
   lookup it answers with `enrolmentId`, never with the key it was given. Together with
   rule 2 this makes an Aadhaar echo unrepresentable rather than merely forbidden.
8. **`provider` and the grievance bands are refused by name** — `provider`, `grievance`,
   `case`, `grievanceOptions`. See "The composed root is open".

Two further refusals sit below the root. **Nothing but `code` and `name` travels in a
`Descriptor`:** `application.ekyc` and each entry in `application.blockers` compose
`NoDescriptorExtras`, which refuses `longDesc`, `shortDesc`, `thumbnailImage`, `docs` and
`mediaFile` by name. Two of the five are free text and none is modelled here, so an
adapter that passed a portal's `Descriptor` through wholesale is rejected rather than
quietly widening what travels. And **`enrolmentId` has a floor**: six characters, not
one, alongside the twenty-character ceiling. A single-character registration number is
not a registration number.

Exactly one member of `challenge` is a seventh rule, and it comes from
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
again.

`provider` joined them in this revision. It is declared on `SchemeServiceBase` and so
*is* in this pack's vocabulary, but it belongs to a support leg — where a caller names
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

Within that one level, a field that must not appear is refused by name with a
`not`/`required`. Not declaring it is not a refusal. And the "response mapping is an
allow-list, not a passthrough" rule under "Privacy" is one the adapter keeps, not one the
schema can enforce.

## Privacy

Every identifier here — `enrolmentId` and whichever member `applicant` carries — is
`no-log` and `no-trace` without exception, and never appears in an error body. Each is a
bearer key as much as an identifier: anyone holding one can read the record.

`mobile` and `aadhaar` are never echoed in a response, and that is now structural rather
than only a mapping rule: the whole `applicant` band is refused on a `Direct` payload, so
neither member can be returned. `enrolmentId` is the single deliberate exception: it goes
back to the caller who sent it, or comes back as the portal's resolution of a mobile or
Aadhaar lookup. Between that refusal and the exclusivity gate, an answer carrying both an
Aadhaar number and the registration it resolved to is unrepresentable rather than merely
discouraged.

`aadhaar` is held to a stricter rule still. An Aadhaar number, and any token derived from
one, must never be logged, traced, or returned in any response or error body, and must not
be retained after the lookup it was sent for.

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

- [On-demand: the catalog entry](examples/on-demand-capability.json)
- [On-demand: request an OTP by mobile or Aadhaar](examples/on-demand-request-otp.json)
- [On-demand: request an OTP by registration number](examples/on-demand-request-otp-by-registration.json)
- [On-demand: OTP issued](examples/on-demand-challenge-issued.json)
- [On-demand: read the status](examples/on-demand-read-status.json)
- [Direct: status, nothing blocking](examples/direct-status-clear.json)
- [Direct: status, two blockers](examples/direct-status-blocked.json)

Published examples show the logical form, every field inline; they are not wire payloads.
