# Provider contracts

- Keep one versioned OpenAPI file per provider service. Describe the HTTP call the provider accepts: method, route, parameters, media type, and original field names. Do not substitute the consumer tool route for the provider route.
- Use a documented service URL in `servers`, or a clearly labeled non-routable placeholder when the provider supplies the URL privately. Preserve a service-path prefix and operation-specific server overrides. Do not publish environment variable names or configuration values.
- Describe credentials with their scheme and exact header or query parameter name. Apply security requirements to the operations that use them. Never include a usable credential, private record or OTP.
- Give each documented payload shape a named schema in `components/schemas` and a synthetic example where the shape is known. For GET, document the parameters rather than inventing a request body. Preserve differences between payload variants, errors, and bodyless responses; explicitly identify unknown results.
- In a provider publication, `descriptor.docs` points to the OpenAPI document and each action’s `operationRef` identifies the operation. That operation references its own input and output schemas. Do not repeat schema links in the catalog.
- Update the provider inventory when adding a service or closing a capability gap. A handler name or mapping draft alone is not enough evidence for a native API. From the repo root, run `python3 scripts/check-api-separation.py` in the validation environment.
- Edit `<provider>/catalog.json` to add catalogs or resources. Keep native contracts in their capability folders. Mark partial mappings incomplete and list missing steps.

## Provider layout

Keep one provider-level `catalog.json` for listings and one `<capability>/<version>/openapi.yaml` for each evidenced native service. Place action YAMLs under that version’s `mappings/`. Use an inactive example catalog for a documented service with an incomplete network binding. If only a proposed handler exists, keep its draft mapping and record the missing native contract in the inventory. Do not invent an endpoint or publish an empty catalog.

For mapping-only capabilities, use `openapi-draft.yaml` with empty `paths` and list what the provider must confirm. A provider without any confirmed service uses `catalog-placeholder.json` as an inventory note, not a publication. Replace these drafts when the native contract is verified.

Keep generic validation examples inside the schema pack. Complete provider resources belong in the provider catalog. Leave published v0.1 fixtures at their original paths.
