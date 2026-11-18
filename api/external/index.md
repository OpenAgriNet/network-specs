---
layout: default
title: External APIs
---
# External APIs

These are proposed OAN integration contracts for external services, not official provider-native API specifications. Provider ownership is unchanged. Endpoints are illustrative and examples are synthetic.

| Provider | Service | Contract and examples |
|---|---|---|
| PMFBY | Grievance | [Grievance operations](pmfby/grievance/v0.2/) |
| PM-KISAN | Grievance | [Grievance operations](pm-kisan/grievance/v0.2/) |
| PM-KISAN | Application status | [Application operations](pm-kisan/application/v0.2/) |

A catalog Resource links its contract through `descriptor.docs`. See the [Grievance](../../schema/examples/grievance-api-resource.json) and [SchemeApplication](../../schema/examples/schemeapplication-api-resource.json) examples. A document link does not define the Beckn invocation binding.
