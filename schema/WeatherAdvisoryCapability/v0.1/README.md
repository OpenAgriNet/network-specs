# Weather Advisory Capability

## Purpose

Defines the metadata a Provider publishes when it can produce weather-informed agricultural advice. The profile fixes the interaction type as `Advise` and the outcome type as `WeatherAdvisory`.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource` listed in a Provider catalog.

## Composition

`WeatherAdvisoryCapability` combines the Agriculture Resource, Agriculture Capability, Advisory Capability, and Weather Advisory Capability field sets with `allOf`.

## Fields

| Field | Meaning |
|---|---|
| `weatherParameters` | Weather parameters the Provider can use to produce advice |
| `forecastHorizon` | Maximum supported forecast horizon |
| `updateFrequency` | Expected refresh interval |
| `geographicGranularity` | Smallest supported geographic unit |

## Non-goals

This schema does not carry advice for a specific place, time, or agriculture subject. `WeatherAdvisory` carries that outcome.

## Examples

- [District and village capability](examples/district-village-capability.json)
- [Point, short-horizon capability](examples/point-short-horizon-capability.json)
