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

The `Resource` does not disappear — `Commitment.resources` requires at least one,
each with an `id` and a `quantity`. It stays thin: a pointer to the catalogable
"grievance handling" entry the offer references. The case itself sits beside it
on the commitment.

This is deliberately unlike the OAN domain packs. A forecast or a mandi price
genuinely is a resource, and those packs stay on `resourceAttributes`.

## Direction, not action

Direction is carried by `informationMode`, never by the Beckn action. `OnDemand` is the ask; `Direct` is an answer carrying a real case. The same attributes therefore serve `init`, `confirm`, `select`, `status`, or any later action without change — nothing in this pack names an action.

`Direct` payloads must carry `ticketNo`, `caseStatus`, `filedOn` and `source`, which is true of `on_confirm` and `on_status` alike. A case read returns more than that — the application number, the category, the farmer's own description — and those are optional here because `on_confirm` does not repeat them.

There is deliberately no matching `OnDemand` requirement. The ask side has no field common to every payload: filing a grievance sends the phone, the application, the season and the OTP; reading a case sends the phone and the ticket; an OTP acknowledgement sends neither, because it must not echo the phone. Requiring any of them here would reject a legitimate payload of some other action. What each action must carry is enforced by that action's mapping guard, not by this pack.

## Composition

`PMFBYGrievance` is self-contained. It does not compose the Agriculture Resource
field set: that set is framed around a Resource holding information, which this
pack is not. It reuses Beckn `Descriptor` objects for `scheme`,
`grievanceCategory` and `caseStatus`, and the shared `SourceReference` for
`source`.

## Fields

"Required when" describes a complete OAN Resource. It does not make the field mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@type` | Always | Identifies the commitment as `openagrinet:PMFBYGrievance` |
| `informationMode` | Always | `OnDemand` is the ask; `Direct` carries a real case. Defined by this pack rather than inherited |
| `scheme` | Always | Scheme the grievance is raised against; present in both directions |
| `applicantPhone` | Every ask | Ten-digit mobile of the farmer. It is the number the OTP goes to when filing, and the portal matches a ticket to the phone it was filed from, so reading a case needs it too |
| `applicationNo` | Ask, when filing; also returned in `Direct` | Crop insurance application number the grievance concerns |
| `cropYear`, `season` | Ask, when filing | Four-digit crop year, and one of `Kharif`, `Rabi`, `Zaid` |
| `grievanceCategory` | Ask, when filing; also returned in `Direct` | Category and sub-category joined by a dot; the adapter splits on that dot, so the shape is load-bearing. Names come back on a case read and are joined with a slash |
| `grievanceDescription` | Ask, when filing; also returned in `Direct` | The farmer's account of the problem, minimum ten characters |
| `otp` | Ask, when filing | Six-digit one-time password proving the phone number; `writeOnly` |
| `ticketNo` | `Direct`; also the ask when reading a case, alongside `applicantPhone` | Portal grievance ticket number |
| `caseStatus` | `Direct` | Where the grievance stands; `name` verbatim from the portal, `code` derived from it |
| `filedOn` | `Direct` | Date the grievance was filed |
| `officerReply` | Optional in `Direct` | The portal's latest remark. Absent rather than empty while no reply exists. PMFBY publishes no reply date, so there is no `repliedOn` |
| `source` | `Direct` | Authoritative upstream source |
| `otpChallenge` | Answer to an OTP request | Masked destination and expiry; carries no secret |

## Category term

The JSON key is `grievanceCategory` in both grievance packs, but it resolves to `openagrinet:pmfbyGrievanceCategory` here and to `openagrinet:pmkisanGrievanceCategory` in the PM-KISAN pack. The two schemes publish incompatible value spaces — a dotted `3.10` against a closed `G001`–`G010` list — so one IRI could not hold both. Payloads are unaffected; only the context mapping differs.

## Privacy

Every field carrying personal data is marked in `attributes.yaml` with `x-oan-pii`:

```yaml
x-oan-pii:
  class: contact
  handling: [no-log, no-trace, no-echo, mask-on-echo]
```

`class` is one of `identifier`, `contact`, `credential` or `freetext`. `handling` draws on
`no-log`, `no-trace`, `no-echo`, `no-forward` and `mask-on-echo`.

The marking is inert — the extended-schema validator ignores `x-` keys, exactly as it
ignores the `if`/`then` branches. It exists so the rule can be read by a tool rather than
only by a person: a CI check can assert that no property marked `no-echo` appears in any
`Direct` example, which is the class of mistake the v1 `identity-no` echo was.

`otp` is `writeOnly`: it travels inbound only and must never be returned in a response, written to a log, attached to a trace, or forwarded to the lodge call.

`applicantPhone` is never echoed. An OTP acknowledgement returns `otpChallenge.sentTo`, masked to first two and last two digits, so the farmer can confirm which number was used.

`applicationNo` identifies a named farmer's policy, and `grievanceDescription` is free text that may contain personal details the schema cannot constrain. Neither belongs in a payload dump.

The portal's case record carries far more about the farmer than this pack surfaces: name, mobile number, email, and the full state / district / sub-district / panchayat / village hierarchy, alongside the insurance policy number and insurer. The adapter must drop all of it and map only the fields listed above. None of it may reach `commitmentAttributes`, a log, or a trace. This is the same class of mistake as the v1 `identity-no` echo, and it is the reason the response mapping is an allow-list rather than a passthrough.

## Stricter than the portal

Three constraints are tighter than what the portal itself would take, and are deliberate:

- `applicantPhone` requires an Indian mobile series (`^[6-9]`); the portal checks only that ten digits arrived.
- `cropYear` requires four digits; the portal takes any digit string.
- `season` is closed to three values; the portal takes the numeric codes the adapter produces.

Each rejects at the network edge something the portal would have rejected later, or would have accepted as nonsense.

## Non-goals

This pack does not define the grievance category list. The portal publishes no enumeration of valid pairs; it returns a name for whichever pair a case was filed under — `3` is `Enrollment`, `10` is `Portal Issues Login` — but there is no endpoint that lists them. The `code` pattern therefore constrains only the dotted shape the adapter splits on, and `name` is whatever came back.

Category `3.10` is the only pair in use today, because v1 hardcoded it for every grievance regardless of subject. That is a v1 defect carried in the data, not a portal constraint, and v2 does not repeat it: the category is a caller-supplied field.

Two fields the portal requires are absent by design, because a caller never supplies them: `complaint_date` is generated by the adapter at lodge time, and `receipt_source_id` is a constant identifying the Vistaar channel. Two fields the portal returns are absent for the same reason: `ticket_id` is an internal portal key the farmer never quotes, and the numeric status id is an opaque key whose name the pack already carries.

It also does not define credentials or transport. Those live in the adapter configuration, where credentials are named by environment variable and never held.

## Examples

- [On-demand: file a grievance](examples/on-demand-file-grievance.json)
- [On-demand: read an existing case](examples/on-demand-read-case.json)
- [On-demand: OTP challenge acknowledgement](examples/on-demand-otp-challenge.json)
- [Direct: grievance with officer reply](examples/direct-grievance-replied.json)
