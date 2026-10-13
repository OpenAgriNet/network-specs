# PM-KISAN Application Status

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

Describes what the PM-KISAN application-status API accepts and what it returns: how far a
farmer's registration under the income-support scheme has got, how many instalments have
been paid, whether eKYC is done, and what is holding payment up.

This is an API schema, not a domain schema. It says what one named Provider's API will
take and give back.

**It is not a grievance.** Nothing is filed, nothing has a lifecycle, and nothing comes
back with a case number. That is why it is a pack of its own rather than a mode of
[PM-KISAN Grievance](../../PMKISANGrievance/v0.1/README.md) — the two share a desk, an OTP
service and a base schema, and share no subject.

## Attachment point

Applied to `commitmentAttributes` of a Beckn `Commitment`, on `init` and on `status`.

A status read is a promise the portal makes about one farmer's registration, not a
catalogable thing of value, so it does not sit on `resourceAttributes`. Unlike the
grievance pack there is **no `support` leg**: nothing is being filed, so no `Support`
channel is ever composed and no field moves out of the attributes object.
`x-beckn-container-by-action` therefore lists `init` and `status` and nothing else. No
field in this family carries an `x-beckn-path` at all, so there is nothing to fire:
every field is read at the same path on both legs.

`Commitment.resources` carries one thin pointer to the catalog entry
(`res:pmkisan:application-status`). It is fixed for the provider and never minted per
farmer: a registration number must not end up in a public, cacheable identifier.

## The bands

**The band a field sits in says who wrote it.**

| band | holds | written by |
|---|---|---|
| top level | what is being asked and under which scheme: `informationMode`, `provider`, `scheme`, `enrolmentId` | the caller |
| `applicant` | who to look up when the caller has no registration number: exactly one of `mobile` or `aadhaar` | the caller |
| `application` | what the portal holds: `registeredOn`, `latestInstallmentPaid`, `ekyc`, `blockers` | the portal |
| `challenge` | the OTP presented on the read | the caller |
| `challengeIssued` | acknowledgement that one was sent | the portal |

`enrolmentId` travels in both directions here. A caller who holds the registration number
sends it; a caller who holds only a mobile or an Aadhaar number sends `applicant` instead,
and the portal resolves it and returns the registration number under `enrolmentId`. The
two slots are mutually exclusive — exactly one, never both. See "Identity is named, not
sniffed".

`challengeMethods` sits in no band. It is published on the catalog entry and never sent on
a payload.

## Direction, not action

Direction is carried by `informationMode`, never by the Beckn action. `OnDemand` is the
ask; `Direct` is an answer carrying a real record. The same attributes serve both `init`
and `status`.

The sequence is two calls:

| | action | the caller sends | the portal returns |
|---|---|---|---|
| 1 | `init` | `enrolmentId` **or** `applicant` | `challengeIssued` — an OTP has gone to the number the registration is held under |
| 2 | `status` | the same identifier + `challenge` | `enrolmentId` + `application` |

The OTP acknowledgement is `OnDemand`, not `Direct`, even though it comes back from the
portal. It carries no record — it says a challenge was sent and nothing else — and `Direct`
is reserved for the payload carrying the application itself. The PMFBY pack does the same.

`init` exists on this pack where it does not on PM-KISAN Grievance, because this read is
gated and lodging a grievance is not. The OTP is the same OTP: the same upstream service
issues it and the same four digits satisfy it. A caller who holds one from a grievance
flow can spend it here.

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
grievance packs, so a reader writes `.enrolmentId` once for the whole family rather than
learning a second name per scheme.

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

`application.ekyc.code` is `Done` or `Pending`. The upstream sends `Y` or `N`; anything
the adapter does not recognise becomes `Pending`, never a guess at `Done`. Telling a
farmer their eKYC is complete when it is not sends them away from the one step that would
unblock their payment.

## Composition

The pack composes `GrievanceBase` from
[`../../Grievance/v0.1/attributes.yaml`](../../Grievance/v0.1/attributes.yaml), which is
where `informationMode`, `provider`, `scheme`, `enrolmentId`, `challengeMethods`,
`grievanceOptions`, `challenge` and `challengeIssued` come from, with their privacy
markings already attached.
The base is shared with both grievance packs; the name is historical.

On top of it this pack:

- adds `applicant` and `application`;
- pins `scheme.code` to `PM-KISAN`;
- pins `challenge.method` and `challengeMethods[].method` to `SMS_OTP`, and
  `challenge.value` to **four digits** — PM-KISAN's OTP is four, PMFBY's is six, and the
  base allows four to eight so each pack pins its own;
- pins `challengeMethods[].length` and `challengeIssued.length` to the same four, and both
  `valueType`s to `NUMERIC`, so the catalog, the acknowledgement and the value itself
  cannot drift apart;
- refuses `challengeIssued.sentTo`, because PM-KISAN names no number;
- narrows `enrolmentId` to ASCII alphanumeric, at most twenty characters, and refuses
  twelve bare digits so an Aadhaar number cannot be sent in the registration slot;
- holds `enrolmentId` and `applicant` mutually exclusive, and requires that every payload
  carry at least one slot that says what it is about.

`ekyc` and each entry in `blockers` compose `IdentifiedDescriptor` from the Agriculture
Resource schema, the established idiom for a governed `code` paired with a display `name`.
`blockers` uses both: the portal sends real text and the `code` classifies it. `ekyc`
refuses `name` — the portal sends `Y` or `N`, so there is no phrase to display and any
wording here would be ours presented as the portal's.

## What this pack refuses

Three inherited members are refused outright with `not`/`required`, so a caller who sends
one is told rather than quietly ignored:

- **`grievance`** — nothing is being submitted here.
- **`case`** — nothing has a lifecycle here.
- **`grievanceOptions`** — it publishes the categories a grievance may be filed under, and
  this desk files none. An empty list would claim the desk takes grievances and has none
  to offer; an invented one would describe a service that does not exist.

Sending any of them means the caller has reached for the wrong pack, and the right answer
is to say so.

`challengeIssued.sentTo` is refused for a different reason: the upstream acknowledgement is
a bare success flag with no destination in it, so there is nothing to mask and nothing to
report.

## Fields

"Required when" describes a complete payload of that kind. It does not make the field
mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@context` | Always | The JSON-LD context these terms resolve against. Pinned to this pack's own; an array when a Provider publishes extra `@type` values |
| `@type` | Always | Identifies the commitment as `openagrinet:PMKISANApplicationStatus` |
| `informationMode` | Always | `OnDemand` is the ask; `Direct` carries a real record |
| `scheme` | Always | Pinned to `PM-KISAN` |
| `provider` | Optional | Beckn `Provider` reference. Both legs compose a `Contract`, so the adapter reads the participant from `commitments[].offer.provider.id` and this is advisory |
| `enrolmentId` | An ask by registration, and every answer | The PM-KISAN registration number. Mutually exclusive with `applicant`; returned as the portal's resolution of a mobile or Aadhaar lookup |
| `applicant` | An ask by mobile or Aadhaar, both legs | Which farmer to look up when the caller has no registration number. Exactly one of `mobile` or `aadhaar`; the member names the kind. Never echoed |
| `challenge.method`, `challenge.value` | The `status` ask | The four-digit OTP issued by `init`. A credential, not an attribute |
| `challengeIssued` | `Direct` on `init` | Acknowledgement that an OTP was sent: `method`, `length`, `valueType`, `expiresAt`. Carries no secret and no destination |
| `application.latestInstallmentPaid` | `Direct` on `status` | How many instalments have been paid. A count, not an instalment number; `0` is an answer, not a missing value |
| `application.blockers` | Optional in `Direct` | Why payment is not arriving. Absent, empty and non-empty are three different answers; see above |
| `application.registeredOn` | Optional in `Direct` | When the farmer was registered under the scheme |
| `application.ekyc` | Optional in `Direct` | `Done` or `Pending` |
| `challengeMethods` | The catalog entry only | One entry: `method` `SMS_OTP`, `length` `4`, `valueType` `NUMERIC`. A caller reads it to know this desk challenges before answering, and to size the OTP input before any transaction exists. Never sent on a transaction |

Where each field is used, by action and by direction, lives in `x-oan-fields-by-action`,
with paths relative to the attributes object. Three buckets per action — `mustSend`,
`maySend`, `comesBack` — plus a pack-wide `refused` list stated once, because the gates
that enforce it are structural and bite on every action:

| action | mustSend | maySend | comesBack |
|---|---|---|---|
| `discover` | — | — | `informationMode`, `scheme.code`, `scheme.name`, `challengeMethods` |
| `init` | — | `informationMode`, `scheme.code`, `enrolmentId`, `applicant.mobile`, `applicant.aadhaar` | `informationMode`, `scheme.code`, `scheme.name`, `challengeIssued.method`, `challengeIssued.length`, `challengeIssued.valueType`, `challengeIssued.expiresAt` |
| `status` | `challenge.method`, `challenge.value` | `informationMode`, `scheme.code`, `enrolmentId`, `applicant.mobile`, `applicant.aadhaar` | `informationMode`, `scheme.code`, `scheme.name`, `enrolmentId`, `application.registeredOn`, `application.latestInstallmentPaid`, `application.ekyc.code`, `application.blockers` |

Neither `mustSend` names an identifier, and `init` has no `mustSend` at all. Both legs need
one of `enrolmentId`, `applicant.mobile` or `applicant.aadhaar`, but a `mustSend` list is
flat and all-of: naming any one of them there would be false for the other callers. They sit
in `maySend` instead, and the requirement is a gate, which is the only place it can actually
be enforced.

It is an allow-list. A path not named above is not used by this capability. `enrolmentId`
comes back on `status` even when the ask was by mobile or by Aadhaar — it is the portal's
own `Reg_No`, not an echo — and `applicant` never comes back at all.

## The gates

Four top-level members, all tested against the real validator:

1. **A `Direct` payload carries a record.** Either `informationMode` is `OnDemand`, or
   `application` is present. An answer with nothing in it is not an answer.
2. **One identifier slot, not two.** `enrolmentId` and `applicant` are mutually exclusive
   — an `anyOf` of two `not`/`required` members. Both at once names the same farmer twice
   with no rule for which wins, and it is also the shape a response would take if it
   leaked an Aadhaar number back beside the registration it resolved to.
3. **Every payload is about something** — one of `enrolmentId`, `applicant`,
   `application`, `challengeIssued` or `challengeMethods` must be present. This is what
   stops a payload that is a scheme name and nothing else.
4. **An answer may not carry the `challenge`.** The OTP is sent, never returned. A payload
   carrying `challenge` must be a request: `informationMode` not `Direct`, and no
   `challengeIssued` beside it, which rules out the `init` acknowledgement as well.
   `x-oan-pii` marks the value `no-echo`, but that binds the mapping; this is the
   structural half of the same rule.

There used to be one more, checking a declared identifier type against the value beside
it. The named slots removed the need for it: there is no pair left to disagree.

## Privacy

Every identifier here — `enrolmentId` and whichever member `applicant` carries — is
`no-log` and `no-trace` without exception, and never appears in an error body. Each is a
bearer key as much as an identifier: anyone holding one can read the record.

`mobile` and `aadhaar` are never echoed in a response. `enrolmentId` is, and that is the
single deliberate exception: it goes back to the caller who sent it, or comes back as the
portal's resolution of a mobile or Aadhaar lookup. The identifier the caller sent under
`applicant` is never returned, and the exclusivity gate makes returning both
unrepresentable rather than merely discouraged.

`aadhaar` is held to a stricter rule still. An Aadhaar number, and any token derived from
one, must never be logged, traced, or returned in any response or error body, and must not
be retained after the lookup it was sent for.

`challenge.value` is a credential. It is never forwarded to the read it guards, never
logged, never traced, never echoed.

**The upstream record carries far more about the farmer than this pack surfaces.**
Alongside the status it returns the farmer's name, father's name, date of birth, gender,
full address and state, district, sub-district and village. None of it is modelled and none
of it is emitted. The caller already knows who they asked about, and publishing it would
disclose more than the identity the pack goes to some trouble to withhold. An adapter must
drop these fields rather than pass them through — the pack cannot stop it, because
`commitmentAttributes` is open. **The response mapping is an allow-list, not a passthrough.**

This is a deliberate break from the v1 flow, which showed the farmer their own name and
village back to them.

`application.blockers[].name` is the portal's own phrase, returned verbatim. It states why a
named farmer is ineligible or unpaid, so it carries the same `no-log` and `no-trace`
handling as the rest of the record.

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

## Examples

- [On-demand: the catalog entry](examples/on-demand-capability.json)
- [On-demand: request an OTP](examples/on-demand-request-otp.json)
- [On-demand: OTP issued](examples/on-demand-challenge-issued.json)
- [On-demand: read the status](examples/on-demand-read-status.json)
- [Direct: status, nothing blocking](examples/direct-status-clear.json)
- [Direct: status, two blockers](examples/direct-status-blocked.json)

Published examples show the logical form, every field inline; they are not wire payloads.
