# Weather Advisory

## Purpose

Defines actual weather-informed agricultural guidance returned by a Provider for a place and validity period.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource` returned as the outcome of invoking a `WeatherAdvisoryCapability`.

## Composition

`WeatherAdvisory` combines the Agriculture Resource and Weather Advisory outcome field sets with `allOf`.

## Fields

| Field | Meaning |
|---|---|
| `topics` | Topics addressed by the advisory |
| `location` | Place to which the advice applies |
| `issuedAt` | Time at which the Provider issued the advice |
| `validity` | Period during which the advice applies |
| `recommendations` | Localized guidance, urgency, and suggested actions |
| `weatherBasis` | Weather parameters and supporting Resource identifiers used to produce the advice |
| `source` | Provider or authoritative source that issued the advice |

## Non-goals

This schema does not advertise Provider coverage or supported forecast horizons. `WeatherAdvisoryCapability` carries that catalog metadata. It also does not replace `WeatherObservation`, which carries measured or forecast values.

## Examples

- [District crop advisory](examples/district-village-advisory.json)
- [Point irrigation advisory](examples/point-short-horizon-advisory.json)
