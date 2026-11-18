# SchemeApplication

Public catalog metadata describing the available service.

[Attributes](attributes.yaml) · [Context](context.jsonld) · [Vocabulary](vocab.jsonld) · [Profile](profile.json) · [API specification](../../../api/external/pm-kisan/application/v0.2/)

## Fields

| Field | Required | Meaning |
|---|---|---|
| @context | Yes | JSON-LD context |
| @type | Yes | SchemeApplication |
| informationMode | Yes | OnDemand |
| scheme | Yes | Scheme code and name |
| actions | Yes | Advertised operations |
| challenge | Optional | Public verification methods; if supplied, methods is required |

Scheme codes are Provider-defined non-empty strings, not a PM-KISAN-only enumeration. Each action advertises its request-schema URI and Beckn attachment path. Other Providers can publish their own codes and API links without a schema release. Verification method, channel and code length are not fixed to four-digit SMS OTPs. The linked API contract defines the actual verification and operation requirements.

## Examples

[Catalog attributes](examples/) · [Complete Resource linking the API specification](../../examples/schemeapplication-api-resource.json)

The complete Resource keeps its identity and API-document link in the Beckn wrapper. Its resourceAttributes contain the catalog metadata only.

## Validation

Validate catalog attributes against SchemeApplication. It applies SchemeApplicationFields without a Provider allow-list. Validate operation inputs and outcomes against the separate request and response components in the linked API contract. A syntactically valid URI does not prove that the target exists or is the correct request contract. Historical named payload components remain compatibility references, not branches of the generic catalog contract.
