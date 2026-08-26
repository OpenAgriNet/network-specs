# Complete OpenAgriNet schema examples

These examples show OAN domain attributes inside complete Beckn objects. They complement the smaller validation fixtures stored with each schema pack.

## Read the examples

| Example | Complete Beckn object | What it demonstrates |
|---|---|---|
| [Knowledge and mandi Provider catalog](knowledge-and-mandi-provider-catalog.json) | Catalog | One Provider advertises multiple invokable capabilities |
| [Weather Provider catalog](weather-provider-catalog.json) | Catalog | One Provider advertises live weather observation and weather advisory capabilities without publishing location-specific values |
| [Published knowledge catalog](published-knowledge-catalog.json) | Catalog | One Provider publishes both general and crop-specific knowledge Resources for discovery |
| [Live weather Resource](live-weather-resource.json) | Resource | A location-specific weather result returned after invoking a discovered capability |
| [Live mandi-price Resource](live-mandi-price-resource.json) | Resource | A market, commodity, date, and price result returned after invoking a discovered capability |
| [Live weather advisory Resource](live-weather-advisory-resource.json) | Resource | Actual location- and time-specific guidance returned after invoking a weather advisory capability |

The Catalog examples use the complete Beckn [Catalog](https://github.com/beckn/schemas/tree/draft/schema/Catalog), [Provider](https://github.com/beckn/schemas/tree/draft/schema/Provider), and [Resource](https://github.com/beckn/schemas/tree/draft/schema/Resource) boundaries. Their `resourceAttributes` values use the selected OAN schema pack.

The two live examples are complete Beckn Resources, not protocol request or response envelopes. The selected Provider and signed transport interaction establish their source. The Resource does not repeat `providerId` or `participantId`. Protocol actions, context, correlation, signatures, synchronous responses, and callbacks belong to the protocol specification.

## Catalog metadata and live values

Provider catalogs advertise stable capability metadata such as capability type, subject category, language, coverage, forecast horizon, and geographic granularity. The governed capability profile supplies the interaction type. Catalogs do not contain the requested location, observation time, market, commodity, current value, or actual advice.

Live Resources contain those request-specific values. Discovery can index the capability or a published knowledge Resource without treating a live observation as stored catalog metadata.

## Validation boundary

Each full example has two validation layers:

1. The outer object follows the linked Beckn Catalog, Provider, Resource, Descriptor, Attributes, and GeoJSONGeometry contracts.
2. Each `resourceAttributes` object follows the OAN pack named by its `@context` and `@type`.

Pack-local examples remain the direct fixtures for validating only an OAN contract.
