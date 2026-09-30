# PM-KISAN Grievance

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

Describes what the PM-KISAN grievance API accepts and what it returns, so an experience layer can call it from the schema alone without reading adapter mapping files.

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

Direction is carried by `informationMode`, never by the Beckn action. `OnDemand` is the ask; `Direct` is an answer carrying a real case. The same attributes therefore serve `confirm`, `select`, `status`, or any later action without change — nothing in this pack names an action.

`Direct` payloads must carry `caseStatus`, `filedOn` and `source`. That is the whole of it, because it is the whole of what a lodge reply and a case read have in common: the lodge reply echoes the category, the case read carries the officer's reply instead, and neither has a case identifier at all.

There is deliberately no matching `OnDemand` requirement. Lodging a grievance sends the identity, the category and the complaint; reading sends the identity and `filedOn`. Requiring the lodge fields here would reject a legitimate read. What each action must carry is enforced by that action's mapping guard, not by this pack.

## No case identifier

The lodge reply carries a success flag and a human-readable message, and nothing else — no case id, no reference, not even a date. A status record carries no identifier either: it names the registration number the grievance was filed under, which is shared by every grievance on that farmer. This pack therefore has no field corresponding to PMFBY's `ticketNo`, and that absence shapes everything downstream.

A grievance is retrieved by the identity it was filed under, and the portal returns **every** grievance on that identity rather than one named case. There is no way to ask the portal for a single one. `filedOn` is what closes the gap: it is returned when the grievance is lodged, sent back on the read, and matched against each record's date to pick the one the caller means. Two grievances filed on the same identity on the same day are therefore indistinguishable.

**One piece of evidence points the other way and is unresolved.** The existing v1 BAP client reads a `grievance-id` value out of the BPP's response tags and prints it as "Grievance ID". Nothing in the portal client produces such a value, and no sample payload in the legacy tree shows one, so it is not established whether `grievance-id` comes from the portal, is assigned by the v1 BPP, or is a field the portal client silently drops. If it turns out to be portal-issued, this pack needs a case-identifier field and the retrieval story above changes. Resolve against a live response before v1.0.

## Composition

`PMKISANGrievance` is self-contained. It does not compose the Agriculture Resource
field set: that set is framed around a Resource holding information, which this
pack is not. It reuses Beckn `Descriptor` objects for `scheme`,
`grievanceCategory` and `caseStatus`, and the shared `SourceReference` for
`source`.

## Fields

"Required when" describes a complete OAN Resource. It does not make the field mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@type` | Always | Identifies the commitment as `openagrinet:PMKISANGrievance` |
| `informationMode` | Always | `OnDemand` is the ask; `Direct` carries a real case. Defined by this pack rather than inherited |
| `scheme` | Always | Scheme the grievance is raised against; present in both directions |
| `applicantId` | Every ask | The farmer's PM-KISAN registration number, the only identity this pack accepts. `writeOnly`; never echoed |
| `grievanceCategory` | Ask, when lodging | One of ten published codes, `G001`–`G010`. Echoed on a lodge response; absent from a case read, whose per-record payload carries no category field |
| `grievanceDescription` | Ask, when lodging | The farmer's account of the problem, minimum ten characters. Returned verbatim on a case read |
| `caseStatus` | `Direct` | Where the grievance stands. The portal's own status where it publishes one, the adapter's summary otherwise — see below |
| `filedOn` | `Direct` | Date the grievance was filed. Read from the portal on a case read; generated on a lodge |
| `officerReply`, `repliedOn` | Optional in `Direct` | Absent rather than null while no reply exists |
| `source` | `Direct` | Authoritative upstream source |

## Grievance categories

Unlike PMFBY, the portal publishes a closed list, so the pack enumerates it and an unknown code is refused at the network edge rather than upstream. The code goes to the portal verbatim.

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

## Category term

The JSON key is `grievanceCategory` in both grievance packs, but it resolves to `openagrinet:pmkisanGrievanceCategory` here and to `openagrinet:pmfbyGrievanceCategory` in the PMFBY pack. The two schemes publish incompatible value spaces — a closed `G001`–`G010` list against a dotted `3.10` — so one IRI could not hold both. Payloads are unaffected; only the context mapping differs.

## Case status

A status record carries the portal's own `GrievanceStatus`. Where it is present, `caseStatus.name` holds it verbatim and `caseStatus.code` is derived from it by upper-casing and replacing spaces — the same treatment PMFBY gives its status text, so an unrecognised phrase yields an unfamiliar code rather than a failure.

Where it is absent, and on a lodge reply where there is no status of any kind, the adapter asserts one:

- `REGISTERED` — the lodge call did not report failure.
- `REPLIED` — a status record with an officer reply but no `GrievanceStatus`.
- `UNDER_REVIEW` — a status record with neither.

So `caseStatus` is the portal's word when the portal has one, and the network's summary otherwise. A caller cannot tell which from the payload; that is a known weakness of carrying both in one field.

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

`applicantId` is `writeOnly`: it travels inbound only and is never echoed in a response, written to a log, attached to a trace, or included in an error body. The farmer supplied it and does not need it read back.

The v1 adapter does the opposite: it returns `identity-no` and `lookup-type` tags, echoing the farmer's registration number straight back to the caller. A v2 adapter must not carry that behaviour over — `applicantId` is `writeOnly` precisely to forbid it.

The portal returns the registration number with every record on a case read. It is consumed rather than surfaced: it names the resource and appears in no attribute.

`grievanceDescription` is free text that may contain personal details the schema cannot constrain.

**The status record carries far more about the farmer than this pack surfaces.** Alongside the grievance itself it returns the farmer's name, father's name, gender, mobile number, and state, district, block and village. None of it is modelled here and none of it is emitted, which is deliberate: it is not part of a grievance, the caller already knows who they asked about, and publishing it would disclose more than the identity the pack goes to some trouble to withhold. An adapter must drop these fields rather than pass them through — the pack cannot stop it, because `commitmentAttributes` is open.

## Stricter than the upstream client

Three constraints are tighter than what the upstream client would pass through:

- `grievanceCategory.code` is closed to the ten published codes; the client checks the label it was handed, not the code, so a code reaching it by any other route is forwarded unchecked.
- `grievanceDescription` requires ten characters; the portal takes an empty string.
- `applicantId` must be **ASCII** alphanumeric. The upstream accepts Devanagari, Bengali and Tamil digits and forwards them to the portal unconverted. The pattern refuses them at the edge instead.

Two places the pack is deliberately *not* stricter:

- The registration number is checked only for "non-empty alphanumeric". Eleven alphanumeric characters is the documented shape, but nothing upstream enforces it and the only source is a tool docstring; a length rule built on that would reject a valid grievance before the farmer's complaint reached the portal.
- `grievanceDescription`'s length is measured on the raw string. The upstream client measures it after trimming, so ten characters of whitespace pass here and fail there. Tightening it would need a regex that rejects payloads the portal accepts, so the adapter trims and re-checks instead.


## Non-goals

This pack does not describe the transport envelope. The portal payload travels encrypted and the response arrives wrapped; both belong to the adapter, and neither the ciphertext nor the service token appears here or in any payload this pack describes.

Two fields the portal returns are absent because the mapping consumes them: `Responce` is the upstream success flag — misspelled, string-valued, and sometimes missing on a lodge, always present on a status check — which decides between a response and an error, and `message` is transport chatter. The farmer and address fields listed under Privacy are absent because they are withheld, which is a different thing.


It also does not define credentials. Those live in the adapter configuration, where credentials are named by environment variable and never held.

## Examples

The two `Direct` examples show the derived form of `caseStatus`. No sample of the portal's own `GrievanceStatus` text exists anywhere in the legacy tree, so rather than invent one the examples demonstrate the fallback branch only.

- [On-demand: lodge a grievance](examples/on-demand-lodge-grievance.json)
- [On-demand: read a case](examples/on-demand-read-cases.json)
- [Direct: grievance registered](examples/direct-grievance-registered.json)
- [Direct: grievance with officer reply](examples/direct-grievance-replied.json)
