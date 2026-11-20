# Grievance

Public catalog metadata describing the available service.

[Attributes](attributes.yaml) · [Context](context.jsonld) · [Vocabulary](vocab.jsonld) · [Profile](profile.json) · [PMFBY API](../../../api/external/pmfby/grievance/v0.2/openapi.yaml) · [PM-KISAN API](../../../api/external/pm-kisan/grievance/v0.2/openapi.yaml)

## Fields

| Field | Required | Meaning |
|---|---|---|
| @context | Yes | JSON-LD context |
| @type | Yes | Grievance |
| informationMode | Yes | OnDemand |
| scheme | Yes | Scheme code and name |
| actions | Yes | Advertised operations |
| challenge | Optional | Public verification methods; if supplied, methods is required |
| grievanceOptions | Yes | Available complaint categories |

Scheme codes and complaint category codes are non-empty strings supplied by the Provider, not a fixed enumeration. Adding a new scheme or category does not require a schema release. Each action carries a request-schema URI and its Beckn attachment path. A URI passing catalog validation does not prove that the target exists or is the correct request contract; consumers must resolve and validate the linked API contract.

For example, `scheme.code: "LOCAL-SUPPORT"` and a category with `code: "PAYMENT-DELAY"` are valid identifiers. PMFBY numeric categories and PM-KISAN G001-style codes remain examples of Provider-specific values. Verification method, channel and code length are also Provider-defined. Private inputs, OTP responses and case records do not belong in this public catalog.

## Examples

[Catalog attributes](examples/) · [Complete Resource linking the API specification](examples/network/grievance-api-resource.json)

The complete Resource keeps its identity and API-document link in the Beckn wrapper. Its resourceAttributes contain the catalog metadata only.

## Validation

Validate catalog attributes against Grievance. It applies GrievanceFields without a Provider allow-list. The linked API contracts retain their own fixed codes and requirements. Validate operation inputs and outcomes against those separate request and response components.
