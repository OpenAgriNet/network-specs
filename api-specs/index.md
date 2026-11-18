---
layout: default
title: API separation review
---
# API separation review

This branch separates public catalog resources from private operation payloads. It is a proposal for consumer feedback, not a deployed provider API. Main remains unchanged.

| Contract | Public catalog | Operation contracts |
|---|---|---|
| Grievance | [Catalog schema](../schema/Grievance/v0.1/) | [Operations and examples](Grievance/v0.1/) |
| SchemeApplication | [Catalog schema](../schema/SchemeApplication/v0.1/) | [Operations and examples](SchemeApplication/v0.1/) |

The schema root now validates discovery metadata only. Existing named payload components remain compatibility aliases, but consumers validating a private payload against the former pack root must migrate. This intentional preview change must not ship under existing production URLs without a version and migration decision.

OpenAPI requestBody and responses carry separate schemas. Responses no longer require incoming OTPs or contact details. Their property allowlists prohibit those values from being echoed. Documented possible output fields are not automatically all mandatory. Successful operations require an outcome, such as an issued challenge, case ticket or case status.

The paths and adapter.example.invalid server are review placeholders. They do not claim these upstream URLs exist and do not define a native Beckn action. The payloads here are attributes, not complete Beckn envelopes. Consumers must agree the transport binding, authentication, challenge lifecycle, errors, retries and response completeness before implementation.

API documentation can be linked through a Resource descriptor's docs entry with label, url and mimeType. A link advertises documentation; it does not authorise invocation. Existing actions declarations are retained for comparison and compatibility, not presented as a settled replacement for Beckn bindings.

The legacy x-oan privacy annotations remain handling guidance, not enforcement. Public profile index paths now include only resourceAttributes. Private enrolment, OTP, application and case payloads must never enter public discovery indexes.

## Consumer review checklist

- Can the consumer resolve external schema references and select request versus response schemas?
- Which adapter or Beckn operation carries each request, ACK and business outcome?
- Can a consumer advertise the API document through descriptor.docs without relying on the old root union?
- What are the actual provider authentication and error contracts?
- Which outputs are guaranteed, optional or absent when an upstream record is incomplete?
- Do OTP and applicant fields stay out of responses, logs, traces and public indexes?
- Which versioned URL transition avoids breaking current validators?

Run `uv run --with pyyaml --with jsonschema python scripts/check-api-separation.py` to check the proposed contracts and fixtures. This does not call live providers.
