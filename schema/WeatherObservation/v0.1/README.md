# Weather Observation

## Purpose

Defines weather observations and forecasts that a Provider can supply on demand or make directly available.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. An `OnDemand` Resource describes supported observation types, parameters, coverage, and granularity. A `Direct` Resource carries specific measured or forecast values.

## Composition

`WeatherObservation` combines the Agriculture Resource and Weather Observation field sets with `allOf`.

## Fields

| Field | Meaning |
|---|---|
| `informationMode` | `OnDemand` requires a Provider invocation; `Direct` contains specific weather information |
| `supportedObservationTypes` | Observation forms available on demand |
| `supportedParameters` | Weather parameters available on demand |
| `forecastHorizon` | Maximum available forecast horizon |
| `updateFrequency` | Expected refresh interval |
| `geographicGranularities` | Geographic levels supported by the Provider |
| `observationType` | Measured observation or forecast |
| `source` | Authoritative upstream source |
| `location` | Beckn GeoJSON geometry to which the result applies |
| `generatedAt` | Result-generation time |
| `modelRunAt` | Forecast model run time |
| `validity` | Applicability period |
| `parameters` | Weather values and units |

## Non-goals

An `OnDemand` Resource never carries location-specific values. A `Direct` Resource does. Spatial indexes such as H3 are implementation projections and are not part of the portable domain contract.

## Examples

- [Point forecast](examples/point-forecast.json)
- [District observation](examples/district-observation.json)
- [Live weather observation](examples/live-weather-observation.json)
- [On-demand weather information](examples/on-demand-weather-information.json)
