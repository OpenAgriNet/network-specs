# Weather Advisory

## Purpose

Defines the weather fields added to an advisory capability that produces agricultural guidance from weather information.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource` listed in a Provider catalog.

## Composition

`WeatherAdvisory` combines the Agriculture Resource, Agriculture Capability, Advisory Capability, and Weather Advisory field sets with `allOf`.

## Fields

| Field | Meaning |
|---|---|
| `weatherParameters` | Weather parameters used to produce advice |
| `forecastHorizon` | Maximum supported forecast horizon |
| `updateFrequency` | Expected refresh interval |
| `geographicGranularity` | Smallest supported geographic unit |

## Non-goals

This schema does not represent a live weather reading. Use `WeatherObservation` for that outcome.

## Examples

- [District and village advisory](examples/district-village-advisory.json)
- [Point, short-horizon advisory](examples/point-short-horizon-advisory.json)
