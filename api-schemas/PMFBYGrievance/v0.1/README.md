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

## Direction, not action

Direction is carried by `informationMode`, never by the Beckn action. `OnDemand` is the ask; `Direct` is an answer carrying a real case. The same attributes therefore serve `init` and `status` without change.

One action is an exception, and the pack names it. On `support` the payload has no `Commitment` to sit on, so it attaches through `Support.channels`, and three fields leave the attributes object for the `Support` object's own slots: `applicationNo` becomes `orderId`, and `grievanceCategory` and `grievanceDescription` become the `descriptor`'s `code`/`name` and `longDesc`. `x-beckn-container-by-action` on the root schema records which container each action uses; `x-beckn-path` on each of those three fields records where it goes. A field with no `x-beckn-path` never moves.

A fourth field exists only on that leg, and it is there so the request can be routed at
all. The adapter picks the upstream call from a binding key, `participantId|capabilityCode`,
and reads both halves out of the payload. On every other action the payload composes a
`Contract`, so the participant is read from `commitments[].offer.provider.id`. A
`SupportAction` composes no contract, and `Support` is sealed at three fields, none of
which names a participant — so the channel carries `providerId` instead. It is the same
value the contract legs supply and it resolves to the same registry record; only its
location differs. `scheme.code` is not a substitute: it names a scheme rather than a
participant, and it reads `PMFBY` where the registry holds `pmfby`.

`Support.orderId` means the same thing in both directions. The spec defines it as the thing "against which support is required", which is an ask-side meaning, and nothing about a reply changes what the complaint is against — so `on_support` echoes the application number back unchanged rather than overwriting it. The ticket the portal issues is a different thing and lives in a different place: `ticketNo` on the channel, with `ticketId` beside it. This is the same rule PM-KISAN follows, where `orderId` is the registration number on both legs because that scheme issues no ticket at all. One field, one meaning, both schemes.

The grievance is lodged through `support`, not `confirm` — the rationale is in `docs/grievance-support-variant.md` and the live flow in `docs/grievance-usecase.md`. `x-beckn-container-by-action` therefore has no `confirm` entry. The privacy markings travel with the field wherever it sits: a `no-echo` field is still `no-echo` in a `Support` slot.

`Direct` payloads must carry `ticketNo`, `caseStatus`, `filedOn` and `source`, which is true of `on_support` and `on_status` alike. A case read returns more than that — the application number, the category, the farmer's own description — and those are optional in the attributes because on `on_support` they come back in the `Support` object's own slots instead, not in the channel.

There is deliberately no matching `OnDemand` requirement. The ask side has no field common to every payload: filing a grievance sends the phone, the application, the season and the challenge; reading a case sends the phone and the ticket; a challenge acknowledgement sends neither, because it must not echo the phone. Requiring any of them here would reject a legitimate payload of some other action. What each action must carry is enforced by that action's mapping guard, not by this pack.

## Upstream response coverage

Every field the portal sends back, and where it goes. Nothing is left unaccounted for.

**Lodge reply** — the `grievance-response` group, four fields:

| upstream | here | note |
|---|---|---|
| `status` | `caseStatus` | `name` verbatim, `code` derived by upper-casing |
| `ticket-no` | `ticketNo` | the number the farmer is told |
| `ticket-id` | `ticketId` | the portal's own row id, returned only |
| `message` | *dropped* | the portal's own text. It may carry a stack trace, an internal hostname, or a quoted-back credential, so it is never returned. Log it redacted and return our own message. |

`filedOn` and `source` are not in the reply. The adapter asserts them — `filedOn` from the
request's own filing date, `source` from provider configuration. They are network-asserted,
not portal-reported, and a caller cannot tell the difference from the payload. That is a
known weakness, the same one `caseStatus` has on PM-KISAN.

**Case read** — the record is much richer than the lodge reply. Every field it carries.

**Read this table as a proposal, not as verified fact.** Of the names below only
`GrievenceSupportTicketNo` occurs anywhere we can check, and it occurs there as a *request*
tag rather than a response field. The legacy client renders the reply generically without
naming a single field, so the reply's shape is not observable from any source on disk.
Confirm these names against PMFBY's own API document before anything is built on them. See
`docs/grievance-upstream-contracts.md`, which is the master reference for what each portal
actually sends.

| upstream | here | note |
|---|---|---|
| `GrievenceSupportTicketNo` | `ticketNo` | the response carries its own, so nothing needs echoing |
| `ApplicationNo` | `applicationNo` | |
| `GrievenceDescription` | `grievanceDescription` | |
| `TicketCategoryID` + `TicketSubCategoryID` | `grievanceCategory.code` | joined with a dot |
| `TicketCategoryName` + `TicketSubCategoryName` | `grievanceCategory.name` | joined with ` / `, mirroring the dot |
| `RequestYear` | `cropYear` | arrives as a number, stringified |
| `RequestSeason` | `season` | the portal's code mapped back to the name |
| `TicketStatus` | `caseStatus` | `name` verbatim, `code` derived by upper-casing and replacing spaces |
| `ComplaintDate` | `filedOn` | already ISO, no conversion |
| `latestRemark` | `officerReply` | the portal sends `""` rather than omitting it; the adapter omits the field instead, so an absent `officerReply` reads as "not yet answered" |
| `TicketStatusID` | *dropped* | an opaque internal key; the derived `caseStatus.code` carries the same meaning in a form a consumer can read |
| `responseDynamic` | *consumed* | the success flag the guard tests; not a field |
| `RequestorMobileNo` | *dropped* | personal data, and `applicantPhone` is never echoed |
| `FarmerName` | *dropped* | personal data |
| `Email` | *dropped* | personal data |
| `StateMasterName` | *dropped* | personal data |
| `DistrictMasterName` | *dropped* | personal data |
| `SubDistrictName` | *dropped* | personal data |
| `GramPanchayat` | *dropped* | personal data |
| `NyayPanchayat` | *dropped* | personal data |
| `VillageName` | *dropped* | personal data |
| `InsurancePolicyNo` | *dropped* | personal data |
| `InsuranceCompany` | *dropped* | personal data |

Eleven of the record's fields are dropped and none of them may reach a payload, a log or a
trace; see "Privacy" below. The response mapping is an allow-list, not a passthrough.

The record carries no reply date anywhere, which is why this pack has no `repliedOn` —
unlike PM-KISAN's, which has one.

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
| `providerId` | `support` ask | Network participant id, so the adapter can route a payload that composes no `Contract`. Not returned |
| `applicantPhone` | Every ask | Ten-digit mobile of the farmer. It is the number the challenge goes to when filing, and the portal matches a ticket to the phone it was filed from, so reading a case needs it too |
| `applicationNo` | Ask, when filing; also returned in `Direct` | Crop insurance application number the grievance concerns |
| `cropYear`, `season` | Ask, when filing | Four-digit crop year, and one of `Kharif`, `Rabi`, `Zaid` |
| `grievanceCategory` | Ask, when filing; also returned in `Direct` | Category and sub-category joined by a dot; the adapter splits on that dot, so the shape is load-bearing. Names come back on a case read and are joined with a slash |
| `grievanceDescription` | Ask, when filing; also returned in `Direct` | The farmer's account of the problem, minimum ten characters |
| `challenge` | Ask, when filing | Proof of the phone number. The network-wide `Challenge` shape narrowed to what PMFBY offers: `method` is `SMS_OTP`, `value` is six digits. `writeOnly` as a whole object |
| `ticketNo` | `Direct`; also the ask when reading a case, alongside `applicantPhone` | Portal grievance ticket number |
| `caseStatus` | `Direct` | Where the grievance stands; `name` verbatim from the portal, `code` derived from it |
| `filedOn` | `Direct` | Date the grievance was filed |
| `officerReply` | Optional in `Direct` | The portal's latest remark. Absent rather than empty while no reply exists. PMFBY publishes no reply date, so there is no `repliedOn` |
| `source` | `Direct` | Authoritative upstream source |
| `challengeIssued` | Answer to a challenge request | Which mechanism was used, the masked destination and the expiry — all three required; carries no secret. `readOnly` |

## Challenge

`challenge` and `challengeIssued` are the network-wide [`Challenge` and `ChallengeIssued`](../../../schema/AgricultureResource/v0.1/README.md#challenge), narrowed here to what PMFBY offers:

```yaml
challenge:
  allOf:
    - $ref: ".../AgricultureResource/v0.1/attributes.yaml#/components/schemas/Challenge"
    - not: { required: [txnId] }
      properties:
        method: { enum: [SMS_OTP] }
        value:  { pattern: "^[0-9]{6}$" }
```

The portal issues a six-digit SMS OTP and nothing else, so that is all this pack accepts. The narrowing is `allOf`, which the validator evaluates, so the six-digit rule is enforced by the pack rather than deferred to a mapping guard.

The narrowing also refuses what PMFBY does not use: the shared `Challenge` offers a `txnId` for mechanisms whose upstream issues a correlator, and this pack rejects it outright rather than accept a field the adapter would ignore.

If PMFBY later offers a second mechanism, this pack widens the `enum` and pins the new format alongside it. Nothing else moves: the carrier is unchanged, the mapping reads `challenge.method` to pick a prerequisite, and the experience layer reads `challengeIssued.method` to know what to collect.

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

`challenge` is `writeOnly` as a whole object: it travels inbound only, and `challenge.value` must never be returned in a response, written to a log, attached to a trace, or forwarded to the lodge call. `challengeIssued` is `readOnly` — it is returned and never sent.

`applicantPhone` is never echoed. A challenge acknowledgement returns `challengeIssued.sentTo`, masked to first two and last two digits, so the farmer can confirm which number was used.

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
- [On-demand: challenge acknowledgement](examples/on-demand-challenge-issued.json)
- [Direct: lodge reply, as the portal sends it](examples/direct-grievance-registered.json)
- [Direct: grievance with officer reply](examples/direct-grievance-replied.json)
