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

Applied to `resourceAttributes` of a Beckn `Resource`, the same as every OAN domain pack.

## Direction, not action

Direction is carried by `informationMode`, never by the Beckn action. `OnDemand` is the ask; `Direct` is an answer carrying a real case. The same attributes therefore serve `init`, `confirm`, `select`, `status`, or any later action without change — nothing in this pack names an action.

`Direct` payloads must carry `ticketNo`, `caseStatus`, `filedOn` and `source`, which is true of `on_confirm` and `on_status` alike.

There is deliberately no matching `OnDemand` requirement. The ask side has no field common to every payload: filing a grievance sends the phone, the application, the season and the OTP; reading a case sends the phone and the ticket; an OTP acknowledgement sends neither, because it must not echo the phone. Requiring any of them here would reject a legitimate payload of some other action. What each action must carry is enforced by that action's mapping guard, not by this pack.

## Composition

`PMFBYGrievance` combines the Agriculture Resource field set with the PMFBY grievance fields using `allOf`, and reuses Beckn `Descriptor` objects for `scheme`, `grievanceCategory` and `caseStatus`.

## Fields

"Required when" describes a complete OAN Resource. It does not make the field mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@type` | Always | Identifies the Resource as `openagrinet:PMFBYGrievance` |
| `informationMode` | Always | `OnDemand` is the ask; `Direct` carries a real case |
| `subjectCategories` | Always | Required by the composed Agriculture Resource field set; this pack additionally requires `Scheme` |
| `scheme` | Always | Scheme the grievance is raised against; present in both directions |
| `applicantPhone` | Every ask | Ten-digit mobile of the farmer. It is the number the OTP goes to when filing, and the portal matches a ticket to the phone it was filed from, so reading a case needs it too |
| `applicationNo` | Ask, when filing; also returned in `Direct` | Crop insurance application number the grievance concerns |
| `cropYear`, `season` | Ask, when filing | Four-digit crop year, and one of `Kharif`, `Rabi`, `Zaid` |
| `grievanceCategory` | Ask, when filing | Category and sub-category joined by a dot; the adapter splits on that dot, so the shape is load-bearing |
| `grievanceDescription` | Ask, when filing | The farmer's account of the problem, minimum ten characters |
| `otp` | Ask, when filing | Six-digit one-time password proving the phone number; `writeOnly` |
| `ticketNo` | `Direct`; also the ask when reading a case, alongside `applicantPhone` | Portal grievance ticket number |
| `caseStatus` | `Direct` | Where the grievance stands; `name` verbatim from the portal, `code` derived from it |
| `filedOn` | `Direct` | Date the grievance was filed |
| `officerReply`, `repliedOn` | Optional in `Direct` | Absent rather than null while no reply exists |
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

## Stricter than the portal

Three constraints are tighter than what the portal itself would take, and are deliberate:

- `applicantPhone` requires an Indian mobile series (`^[6-9]`); the portal checks only that ten digits arrived.
- `cropYear` requires four digits; the portal takes any digit string.
- `season` is closed to three values; the portal takes the numeric codes the adapter produces.

Each rejects at the network edge something the portal would have rejected later, or would have accepted as nonsense.

## Non-goals

This pack does not define the grievance category list. The portal publishes none — only category `3` / sub-category `10` is in use today, and no names for them are published, which is why the examples carry a code and no `name`. The `code` pattern constrains only the dotted shape the adapter splits on.

Two fields the portal requires are absent by design, because a caller never supplies them: `complaint_date` is generated by the adapter at lodge time, and `receipt_source_id` is a constant identifying the Vistaar channel. Two fields the portal returns are absent for the same reason: `ticket_id` is an internal portal key the farmer never quotes, and `message` is transport chatter.

It also does not define credentials or transport. Those live in the adapter configuration, where credentials are named by environment variable and never held.

## Examples

- [On-demand: file a grievance](examples/on-demand-file-grievance.json)
- [On-demand: read an existing case](examples/on-demand-read-case.json)
- [On-demand: OTP challenge acknowledgement](examples/on-demand-otp-challenge.json)
- [Direct: grievance with officer reply](examples/direct-grievance-replied.json)
