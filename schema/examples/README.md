# Complete OpenAgriNet Schema Examples

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
| [FFS booking service](ffs-booking-api-resource.json) | Resource | The catalog advertises a service. The [provider contract](../../api/external/ffs/booking/v0.2/openapi.yaml) describes the private steps that lead to a booking. |
| [Seed availability](seedavailability-api-resource.json), [crop registry](cropregistry-api-resource.json), [soil report lookup](soilhealthcard-api-resource.json) | Resource | Three different services use the same public AgricultureResource fields and link to different provider contracts. |

## Publish and discover a v0.2 catalog

These are synthetic catalog entries, not live provider addresses. Send the publish examples to `POST /publish` and the search examples to `POST /discover`. Filters match the versioned resource type and public attributes such as subject category or scheme. Several providers may qualify. The example responses show matching catalog resources, not live availability.

| Capability | Publish | Filter | Example response |
|---|---|---|---|
| District advisory | [Catalog](providers/v0.2/publish/imd.json) | [Request](providers/v0.2/discover/imd-agromet.json) | [Matches](providers/v0.2/on-discover/imd-agromet.json) |
| Fertilizer booking | [Catalog](providers/v0.2/publish/ffs.json) | [Request](providers/v0.2/discover/ffs-booking.json) | [Matches](providers/v0.2/on-discover/ffs-booking.json) |
| Scheme grievance | [Catalog](providers/v0.2/publish/pmfby.json) | [Request](providers/v0.2/discover/pmfby-grievances.json) | [Matches](providers/v0.2/on-discover/pmfby-grievances.json) |

The public result carries the provider, resource and advertised contract references. Farmer identifiers, login challenges, case contents and bookings belong in the subsequent authorized interaction, not the published catalog. All request files under `providers/v0.2/` follow the same arrangement.

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
