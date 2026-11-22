# Provider API inventory

Edit each provider’s `catalog.json` directly. Its `message.catalogs[]` holds the catalogs and resources that provider publishes.

## Documented services

Provider-supplied means that the document uses a non-routable placeholder. An undocumented header scheme does not establish anonymous access: check the operation for OTP, encryption, body fields, or other requirements. No live integration is asserted.

| Provider / service | Operations | Server | HTTP authentication |
|---|---:|---|---|
| [agmarknet/market-prices](agmarknet/market-prices/v0.2/openapi.yaml) | 1 | Provider-supplied | query: `token` |
| [agmarknet/nearby-prices](agmarknet/nearby-prices/v0.2/openapi.yaml) | 1 | Provider-supplied | query: `token` |
| [ffs/booking](ffs/booking/v0.2/openapi.yaml) | 4 | Provider-supplied | bearer |
| [gfr/crop-registry](gfr/crop-registry/v0.2/openapi.yaml) | 1 | Provider-supplied | No header scheme documented |
| [imd/agromet](imd/agromet/v0.2/openapi.yaml) | 1 | `https://agromet.imd.gov.in` | No header scheme documented |
| [imd/mausamgram](imd/mausamgram/v0.2/openapi.yaml) | 1 | `https://mausamgram.imd.gov.in/nwpapi` | No header scheme documented |
| [knowledge/search](knowledge/search/v0.2/openapi.yaml) | 1 | Provider-supplied | bearer |
| [npss/diagnosis](npss/diagnosis/v0.2/openapi.yaml) | 2 | `https://npss.dac.gov.in/api3.0` | bearer |
| [pm-kisan/application](pm-kisan/application/v0.2/openapi.yaml) | 4 | Provider-supplied | No header scheme documented |
| [pm-kisan/grievance](pm-kisan/grievance/v0.2/openapi.yaml) | 4 | Provider-supplied | No header scheme documented |
| [pmfby/grievance](pmfby/grievance/v0.2/openapi.yaml) | 2 | Provider-supplied | header: `Authorization` |
| [pmfby/insurance](pmfby/insurance/v0.2/openapi.yaml) | 2 | Provider-supplied | header: `token` |
| [pocra/facilities](pocra/facilities/v0.2/openapi.yaml) | 1 | Provider-supplied | No header scheme documented |
| [sathi/master](sathi/master/v0.2/openapi.yaml) | 2 | Provider-supplied | query: `apiKey` |
| [sathi/stock](sathi/stock/v0.2/openapi.yaml) | 1 | Provider-supplied | No header scheme documented |
| [shc/reports](shc/reports/v0.2/openapi.yaml) | 1 | Provider-supplied | bearer |
| [smam/benefit-status](smam/benefit-status/v0.2/openapi.yaml) | 1 | Provider-supplied | header: `Token` |

## Catalog capabilities

Knowledge search uses `discover`, not a follow-up selection. An authorized discovery handler maps `message.intent.textSearch` to the provider’s `POST /search` query and returns ranked Direct resources via `on_discover`. The same intent can be routed to multiple eligible responders, each returning its own catalog with the original correlation IDs. The sample does not enable fanout, grant access to a corpus or change the base protocol.

A publication links only the operations currently backed by a native contract. Other entries explain what is missing; they are not invocation instructions.

| Provider | Capability | Schema | Catalog or gap |
|---|---|---|---|
| agmarknet | agmarknet-market-prices | MandiPrice | [Catalog](agmarknet/catalog.json) |
| agmarknet | agmarknet-nearby-prices | MandiPrice | [Catalog](agmarknet/catalog.json) · [Partial mapping](agmarknet/nearby-prices/v0.2/mappings/select.yaml) |
| agristack | agristack-consent | AgricultureResource | Consent and authorized read endpoints are unverified. |
| aif | aif-loan | SchemeApplication | [Source-traced requests](aif/loan/v0.2/openapi-draft.yaml); adapter binding not yet deployed. |
| aif | aif-tickets | Grievance | [Source-traced requests](aif/tickets/v0.2/openapi-draft.yaml); adapter binding not yet deployed. |
| amul | amul-schemes | KnowledgeResource | Uses network search or cached results; no native scheme endpoint is confirmed. |
| ffs | ffs-booking | AgricultureResource | [Catalog](ffs/catalog.json) |
| gfr | gfr-advice | AgricultureAdvisory | [Source-traced requests](gfr/advice/v0.2/openapi-draft.yaml); adapter binding not yet deployed. |
| gfr | gfr-registry | AgricultureResource | [Catalog](gfr/catalog.json) |
| icar | icar-field-advice | AgricultureAdvisory | Material lookup does not establish a field-advice endpoint. |
| icar | icar-materials | KnowledgeResource | Reads internal storage; no native HTTP endpoint is confirmed. |
| imd | imd-agromet | AgricultureAdvisory | [Catalog](imd/catalog.json) |
| imd | imd-district-forecast | WeatherObservation | Station lookup is known; the forecast route is unverified. |
| imd | imd-mausamgram | WeatherObservation | [Catalog](imd/catalog.json) |
| kcc | kcc-loan | SchemeApplication | [Source-traced requests](kcc/loan/v0.2/openapi-draft.yaml); adapter binding not yet deployed. |
| khc | khc-tickets | Grievance | [Source-traced requests](khc/tickets/v0.2/openapi-draft.yaml); adapter binding not yet deployed. |
| knowledge | knowledge-search | KnowledgeResource | [Catalog](knowledge/catalog.json) · [discover](knowledge/search/v0.2/examples/discover.json) · [native search](knowledge/search/v0.2/examples/search-exchange.json) · [on_discover](knowledge/search/v0.2/examples/on_discover.json). |
| knowledge | knowledge-answers | AgricultureAdvisory | Passage search is documented; advisory output is unverified. |
| knowledge | knowledge-documents | KnowledgeResource | Passage search does not establish whole-document or scheme-filter support. |
| knowledge | knowledge-schemes | KnowledgeResource | Scheme aliases use catalog search; no native endpoint is confirmed. |
| mahavistaar | mahavistaar-schemes | KnowledgeResource | Caller and handler use different scheme fields; the binding is unverified. |
| market-insights | market-insights-outlook | MarketIntelligence | Price history is available; no outlook endpoint is confirmed. |
| npss | npss-diagnosis | AgricultureResource | [Inactive example catalog](npss/catalog.json); image transfer and response are unverified. |
| pm-kisan | pm-kisan-benefits | SchemeApplication | [Catalog](pm-kisan/catalog.json) |
| pm-kisan | pm-kisan-grievances | Grievance | [Catalog](pm-kisan/catalog.json) |
| pmfby | pmfby-grievances | Grievance | [Catalog](pmfby/catalog.json) |
| pmfby | pmfby-insurance | AgricultureResource | [Catalog](pmfby/catalog.json) |
| pocra | pocra-facilities | AgricultureFacility | [Catalog](pocra/catalog.json) |
| sathi | sathi-stock | AgricultureResource | [Catalog](sathi/catalog.json) |
| shc | shc-reports | AgricultureResource | [Catalog](shc/catalog.json) |
| smam | smam-benefits | SchemeApplication | [Catalog](smam/catalog.json) |
| video | video-library | KnowledgeResource | Searches an internal collection; no native video API is confirmed. |
