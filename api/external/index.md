---
layout: default
title: External APIs
---
# External APIs

These files describe two different interfaces: proposed OAN integrations for scheme operations, and upstream operations as used by a provider adapter. Neither is an official provider specification. Examples are synthetic.

| Provider | Service | Contract and examples |
|---|---|---|
| PMFBY | Grievance | [Grievance operations](pmfby/grievance/v0.2/) |
| PMFBY | Private policy and claim lookup | [Policy and claim reads](pmfby/insurance/v0.2/openapi.yaml) |
| PM-KISAN | Grievance | [Grievance operations](pm-kisan/grievance/v0.2/) |
| PM-KISAN | Application status | [Application operations](pm-kisan/application/v0.2/) |
| SATHI | Crop groups and crops by group | [Master-data reads](sathi/master/v0.2/openapi.yaml) |
| SATHI | Certified seed stock | [Stock lookup](sathi/stock/v0.2/openapi.yaml) |
| GFR | Crop registry | [Registry query](gfr/crop-registry/v0.2/openapi.yaml) |
| Soil Health Card | Private reports | [Report query](shc/reports/v0.2/openapi.yaml) |
| FFS | Allowance, products, retailers and fertilizer booking | [Booking operations](ffs/booking/v0.2/openapi.yaml) |
| IMD | Mausamgram coordinate forecasts | [Daily forecast](imd/mausamgram/v0.2/openapi.yaml) |
| IMD | District Agromet bulletin | [Dated feed](imd/agromet/v0.2/openapi.yaml) |
| Agmarknet | Nearby mandi prices | [Price lookup](agmarknet/nearby-prices/v0.2/openapi.yaml) |
| Agmarknet | Prices by market and date range | [Selected-market lookup](agmarknet/market-prices/v0.2/openapi.yaml) |
| SMAM | Private benefit application status | [Status lookup](smam/benefit-status/v0.2/openapi.yaml) |

A catalog Resource links its contract through `descriptor.docs`. See the [Grievance](../../schema/examples/grievance-api-resource.json) and [SchemeApplication](../../schema/examples/schemeapplication-api-resource.json) examples. A document link does not define the Beckn invocation binding.
