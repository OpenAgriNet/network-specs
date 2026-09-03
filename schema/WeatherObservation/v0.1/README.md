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
| `observedAt` | Measurement time, required for an observation |
| `modelRunAt` | Forecast model run time |
| `validity` | Bounded applicability period, required for a forecast |
| `parameters` | Weather values and units |

## Non-goals

An `OnDemand` Resource never carries location-specific values. A `Direct` Resource does. Spatial indexes such as H3 are implementation projections and are not part of the portable domain contract.

A measured observation requires `observedAt`. A forecast requires `modelRunAt` and a validity window with both `startsAt` and `endsAt`. `generatedAt` records when the normalized Resource was produced and does not replace either domain timestamp.

## Naming open item

This pack currently covers measured observations and forecasts. `WeatherInformation` is a clearer candidate name if both remain in one pack. `AgriWeatherInformation` and `AgriWeatherAdvisory` are not recommended because the `openagrinet:` namespace and the selected OAN schema already establish the agricultural context.

## Examples

- [Point forecast](examples/point-forecast.json)
- [District observation](examples/district-observation.json)
- [Live weather observation](examples/live-weather-observation.json)
- [On-demand weather information](examples/on-demand-weather-information.json)
