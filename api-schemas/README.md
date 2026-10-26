# OpenAgriNet API Schema Packs

A domain schema says what a thing *is* in the agriculture domain. An API schema says what one named Provider's API will take and give back, so an experience layer can call it from the schema alone without reading adapter mapping files.

Each pack carries the same seven artifacts as a domain pack. The difference is scope, not shape: a domain pack is written once for the whole network, an API pack is written for one provider.

Where a pack attaches depends on the call, not on the pack. A catalog entry rides on `Resource.resourceAttributes`, `init` and `status` ride on `Commitment.commitmentAttributes`, and `support` rides on a `Support` channel. Each root schema records the whole mapping in `x-beckn-container-by-action`, so one lookup answers "where does this payload sit" for every call the pack serves.

## Every pack names its actions

`informationMode` says where the answer comes from. `OnDemand` is its only value: the external system answers, so the caller makes the `init`, `status` and `support` calls that follow discovery.

What a *particular* action must carry is stated by the pack, not left to the adapter. Each root schema carries `x-oan-schema-by-action`, which names one schema per action:

```yaml
x-oan-schema-by-action:
  catalog/publish: GrievanceCatalog
  init:            GrievanceInit
  status:          GrievanceStatus
  support:         GrievanceSupport
```

The validator reads the action off `context.action` and checks the payload against that schema alone. A `status` payload sent to `support` is refused, because the `support` schema is a different set of leaves with different requirements. An action the key does not name falls back to the root `oneOf`, which is the union of every leaf — a wider gate, and a vaguer refusal.

## Three layers, and no more

A pack is the same shape all the way down:

1. **Root** — `x-oan-schema-by-action`, `x-beckn-container-by-action`, `x-jsonld`, and a `oneOf` over every leaf.
2. **Per-call schema** — one per action, a `oneOf` over the leaves that serve it.
3. **Leaf** — one per (scheme, call). An `allOf` of a guard, a closed flat body, and, where the call has one, a gate.

The guard is a `const` on `scheme.code` in its own conjunct. It is what makes the leaves mutually exclusive, and what makes a refusal name a field: the validator rules out every arm whose guard fails, and reports against the one that remains.

```yaml
IsPMFBY:
  type: object
  required: [scheme]
  properties:
    scheme:
      type: object
      required: [code]
      properties:
        code: { const: PMFBY }
```

A guard is always `const`, never `enum` — the validator rules an arm out on `const` alone. `enum` is for stating a value space inside a body.

The body is flat and closed: every field the call accepts sits at the top level or in one named band, `additionalProperties: false` throughout. Nothing is inherited, so adding a scheme is adding a leaf and a `oneOf` member, and changing one scheme cannot reach another.

A gate is a `oneOf` over the combinations the portal accepts, used where "one of these two, not both" cannot be said with `required`. It is written as an exclusive `oneOf` and never as an `anyOf`: an `anyOf` swallows the reasons its members failed, so the caller gets "matches no schema" and no field name.

## What a leaf tells an integrator

Each leaf carries `x-oan-fields`, four lists that read as the call's contract:

| list | means |
|---|---|
| `mustSend` | drop any one of these and the validator refuses the request |
| `maySend` | optional on the way in; the call still passes without them |
| `oneOf` | exactly one of these, enforced by the leaf's gate |
| `comesBack` | what the answer carries |

The lists are documentation — no code reads them — but they are kept true against the schema, and the published page is generated from the same file.

## Two profile values these packs introduce

Both are new with `api-schemas/`; the eight domain packs use neither.

| Key | Value | Why |
|---|---|---|
| `semantic_model` | `provider-api` | The domain packs are `generalised` — written once for the whole network. A provider API pack is scoped to one provider, which is the distinction this folder exists to make. |
| `interaction_type` | `Transact` | These packs describe calls that change state upstream — a grievance is lodged, not looked up. The domain packs describe retrieval. |

## One pack, two schemes

`Grievance/v0.1` covers PMFBY and PM-KISAN in a single pack rather than one pack each. The two desks share a capability — file a grievance, read it back — and differ in what they accept, so each call's schema is a `oneOf` over one leaf per desk, pinned by `scheme.code`. A caller reads one pack to learn the capability and one leaf to learn the desk.

`SchemeApplication` stays its own pack because checking where an application stands is a different capability, not a different scheme: nothing is filed, nothing has a lifecycle, and nothing comes back with a case number. It borrows nothing from `Grievance` and `Grievance` borrows nothing from it — neither pack `$ref`s across the folder boundary, so neither can break the other.

## Shared and unshared terms

The packs share a vocabulary without sharing a schema. `informationMode`, `provider`, `scheme`, `enrolmentId` and `grievance.description` resolve to the same `openagrinet:` IRIs in both packs, so two payloads from different packs mean the same thing in a graph even though no file references the other. `applicantMobile` is shared across a placement difference: PMFBY's grievance desk carries it at the top level, `SchemeApplication` carries it as `applicant.mobile`, and both resolve to the same term.

Where two desks classify differently, the difference is carried by the value space, not by a second term. `grievance.category` is one property in both leaves; PMFBY pins the numeric codes its portal issues, PM-KISAN pins `G001`–`G010`.

A leaf simply does not declare what its desk has no equivalent for. PM-KISAN's grievance leaves carry no `subCategory`, because that desk classifies at one level; PMFBY's carry no `challenge`, because that desk asks for no OTP. Because every body is closed, sending either is refused by name — there is nothing to inherit and therefore nothing to refuse explicitly.

## Packs

- [Grievance](Grievance/v0.1/README.md) — lodging and reading a grievance at a scheme desk. Two desks today: PMFBY crop insurance and PM-KISAN income support.
- [Scheme Application](SchemeApplication/v0.1/README.md) — reading where a farmer's application to a scheme stands: instalments paid, eKYC standing, and what is blocking payment. PM-KISAN today.

OAN terms use `openagrinet:` for `https://openagrinet.github.io/network-specs/vocab#`. Versioned artifacts are published under `https://openagrinet.github.io/network-specs/api-schemas/`.
