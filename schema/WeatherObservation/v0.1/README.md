# Weather Observation

## Purpose

Defines measured or forecast weather information returned for a requested place and time.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource` produced by a live Provider invocation.

## Composition

`WeatherObservation` combines the Agriculture Resource and Weather Observation field sets with `allOf`.

## Fields

| Field | Meaning |
|---|---|
| `observationType` | Measured observation or forecast |
| `source` | Authoritative upstream source |
| `location` | Beckn GeoJSON geometry to which the result applies |
| `generatedAt` | Result-generation time |
| `modelRunAt` | Forecast model run time |
| `validity` | Applicability period |
| `parameters` | Weather values and units |

## Non-goals

Location-specific values do not belong in Provider onboarding metadata. They are returned by the live capability.
Spatial indexes such as H3 are implementation projections and are not part of the portable domain contract.

## Examples

- [Point forecast](examples/point-forecast.json)
- [District observation](examples/district-observation.json)
- [Live weather observation](examples/live-weather-observation.json)
