# SchemeApplication

Public catalog metadata describing the available service.

[Attributes](attributes.yaml) · [Context](context.jsonld) · [Vocabulary](vocab.jsonld) · [Profile](profile.json) · [API specification](../../../api/external/pm-kisan/application/v0.1/)

## Fields

| Field | Required | Meaning |
|---|---|---|
| @context | Yes | JSON-LD context |
| @type | Yes | SchemeApplication |
| informationMode | Yes | OnDemand |
| scheme | Yes | Scheme code and name |
| actions | Yes | Advertised operations |
| challenge | Where defined by the scheme | Supported verification methods |

The attributes schema defines the exact requirements for each scheme. Request and response fields are described in the linked API specification, not in the catalog schema.

## Examples

[Catalog attributes](examples/) · [Complete Resource linking the API specification](../../examples/schemeapplication-api-resource.json)

The complete Resource keeps its identity and API-document link in the Beckn wrapper. Its resourceAttributes contain the catalog metadata only.

## Validation

Validate catalog attributes against SchemeApplication. Validate operation inputs and outcomes against the separate request and response components in the API specification. Historical named payload components remain compatibility references.
