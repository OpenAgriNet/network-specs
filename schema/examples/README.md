# Complete OpenAgriNet schema examples

These examples show OAN domain attributes inside complete Beckn objects. They complement the smaller validation fixtures stored with each schema pack.

## Read the examples

| Example | Complete Beckn object | What it demonstrates |
|---|---|---|
| [Knowledge and market Provider catalog](knowledge-and-mandi-provider-catalog.json) | Catalog | One Provider advertises KnowledgeResource, KnowledgeAdvisory, MandiPrice, and MarketIntelligence information available `OnDemand` |
| [Weather Provider catalog](weather-provider-catalog.json) | Catalog | One Provider advertises WeatherObservation and WeatherAdvisory information available `OnDemand` |
| [Published knowledge catalog](published-knowledge-catalog.json) | Catalog | One Provider publishes general and crop-specific KnowledgeResource information in `Direct` mode |
| [Direct knowledge advisory Resource](direct-knowledge-advisory-resource.json) | Resource | Crop-specific guidance and its supporting Knowledge Resource returned in `Direct` mode |
| [Direct weather Resource](live-weather-resource.json) | Resource | Location-specific weather information returned in `Direct` mode |
| [Direct mandi-price Resource](live-mandi-price-resource.json) | Resource | Market, commodity, date, and price information returned in `Direct` mode |
| [Direct weather advisory Resource](live-weather-advisory-resource.json) | Resource | Location- and time-specific weather guidance returned in `Direct` mode |
| [Direct market intelligence Resource](direct-market-intelligence-resource.json) | Resource | Price trends, a demand forecast, and a nearby market opportunity returned in `Direct` mode |

The Catalog examples use the complete Beckn [Catalog](https://github.com/beckn/schemas/tree/draft/schema/Catalog), [Provider](https://github.com/beckn/schemas/tree/draft/schema/Provider), and [Resource](https://github.com/beckn/schemas/tree/draft/schema/Resource) boundaries. Their `resourceAttributes` values use the selected OAN schema pack.

The Direct examples are complete Beckn Resources, not protocol request or response envelopes. The selected Provider and signed transport interaction establish their source. The Resource does not repeat `providerId` or `participantId`. Protocol actions, context, correlation, signatures, synchronous responses, and callbacks belong to the protocol specification.

## On-demand and direct information

An `OnDemand` Resource advertises stable scope such as subject category, language, coverage, forecast horizon, supported parameters, or supported commodities. It does not contain the requested location, observation time, current value, or actual advice.

A `Direct` Resource contains those specific values. Discovery may index `OnDemand` Resources, `Direct` Resources, or both. Whether information is current, historical, or forecast is independent of its information mode.

## Validation boundary

Each full example has two validation layers:

1. The outer object follows the linked Beckn Catalog, Provider, Resource, Descriptor, Attributes, and GeoJSONGeometry contracts.
2. Each `resourceAttributes` object follows the OAN pack named by its `@context` and `@type`.

Pack-local examples remain the direct fixtures for validating only an OAN contract.
