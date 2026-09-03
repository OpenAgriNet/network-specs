# Weather Advisory

## Purpose

Defines weather-informed agricultural guidance that a Provider can supply on demand or make directly available.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. An `OnDemand` Resource describes the advisory scope a Provider supports. A `Direct` Resource carries specific advice.

## Composition

`WeatherAdvisory` combines the Agriculture Resource and Weather Advisory field sets with `allOf`.

## Fields

| Field | Meaning |
|---|---|
| `informationMode` | `OnDemand` requires a Provider invocation; `Direct` contains specific advice |
| `topics` | Topics addressed by the advisory |
| `supportedWeatherParameters` | Weather parameters available as the basis for on-demand advice |
| `forecastHorizon` | Maximum supported forecast horizon |
| `updateFrequency` | Expected refresh interval |
| `geographicGranularities` | Geographic levels at which advice is available |
| `location` | Place to which the advice applies |
| `issuedAt` | Time at which the Provider issued the advice |
| `validity` | Period during which the advice applies |
| `recommendations` | Localized guidance, weather severity, and suggested actions |
| `weatherBasis` | Weather parameters and supporting Resource identifiers used to produce the advice |
| `source` | Provider or authoritative source that issued the advice |

## Non-goals

This schema does not replace `WeatherObservation`, which carries measured or forecast values. Weather Advisory interprets weather information and recommends an agricultural action.

`OnDemand` is the Weather Advisory capability declaration. It carries supported parameters, horizon, update frequency, geographic granularities, language, topics, and coverage. `Direct` carries the place-specific advisory. There is no separate `WeatherAdvisoryCapability` schema.

## Examples

- [District crop advisory](examples/district-village-advisory.json)
- [Point irrigation advisory](examples/point-short-horizon-advisory.json)
- [On-demand weather advisory](examples/on-demand-weather-advisory.json)
