---
layout: default
title: External APIs
---
# External APIs

[Full provider and capability inventory](README.md)

Read one OpenAPI document per provider capability. The path, method and payload describe the upstream interface used by a caller or adapter. These are source-derived contracts, not claims of live availability. Synthetic examples use the upstream field names. Where present, `x-oan-binding` describes how the operation fits a network flow; it is not part of the HTTP request.

For example, PMFBY grievance status calls `POST /krphapi/FGMS/GetGrievenceTicketsStatus`. The network action is `status`; it does not rename the provider path to `/pmfby/status`. An encrypted operation distinguishes the on-wire envelope from the plaintext fields inside it.

| Provider | Service | Contract and examples |
|---|---|---|
| PMFBY | Grievance | [Grievance operations](pmfby/grievance/v0.2/openapi.yaml) |
| PMFBY | Private policy and claim lookup | [Policy and claim reads](pmfby/insurance/v0.2/openapi.yaml) |
| PM-KISAN | Grievance | [Grievance operations](pm-kisan/grievance/v0.2/openapi.yaml) |
| PM-KISAN | Application status | [Application operations](pm-kisan/application/v0.2/openapi.yaml) |
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
| NPSS | Crop image analysis (multipart) | [Image request and observed response](npss/diagnosis/v0.2/openapi.yaml) |
| PoCRA | Facility aggregator (legacy Beckn) | [Facility search](pocra/facilities/v0.2/openapi.yaml) |
| Knowledge Provider | Ranked passages | [Search](knowledge/search/v0.2/openapi.yaml) |
