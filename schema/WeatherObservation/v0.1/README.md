# Weather Observation

<nav class="artifact-links" aria-label="Schema artifacts">
  <a href="../../">All schemas</a>
  <a href="attributes.yaml">attributes.yaml</a>
  <a href="context.jsonld">context.jsonld</a>
  <a href="vocab.jsonld">vocab.jsonld</a>
  <a href="profile.json">profile.json</a>
  <a href="renderer.json">renderer.json</a>
  <a href="#examples">Examples</a>
</nav>

## Purpose

Defines weather observations and forecasts that a Provider can supply on demand or make directly available.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. An `OnDemand` Resource describes supported observation types, parameters, coverage, and granularity. A `Direct` Resource carries specific measured or forecast values.

## Composition

`WeatherObservation` combines the Agriculture Resource and Weather Observation field sets with `allOf`.

## Fields

"Required when" describes a complete OAN Resource. It does not make the field mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@type` | Always | Identifies the Resource as `openagrinet:WeatherObservation` |
| `informationMode` | Always | `OnDemand` requires a Provider invocation; `Direct` contains specific weather information |
| `subjectCategories` | Optional | Broad agriculture classification inherited from Agriculture Resource |
| `agricultureSubjects` | Optional | Governed subjects when the weather information is explicitly subject-specific |
| `languages` | Optional | Languages used by textual descriptors |
| `coverageAreas` | Optional | Geographic applicability or supported coverage |
| `supportedObservationTypes` | `OnDemand` | Observation forms available on demand |
| `supportedParameters` | `OnDemand` | Weather parameters available on demand |
| `forecastHorizon` | Optional | Maximum available forecast horizon |
| `updateFrequency` | Optional | Expected refresh interval |
| `geographicGranularities` | `OnDemand` | Geographic levels supported by the Provider |
| `observationType` | `Direct` | Measured observation or forecast |
| `source` | `Direct` | Authoritative upstream source |
| `location` | `Direct` | Beckn GeoJSON geometry to which the result applies |
| `generatedAt` | `Direct` | Result-generation time |
| `observedAt` | `Direct` observation | Measurement time |
| `modelRunAt` | `Direct` forecast | Forecast model run time |
| `validity` | `Direct` forecast | Bounded applicability period |
| `parameters` | `Direct` | Weather values, units, and an optional aggregation type |

### Aggregation types

`aggregationType` qualifies how a parameter value was calculated over its applicable reporting period, normally the Resource's validity period. It is optional because a point-in-time observation may be unqualified. A Provider should supply `validity` when a non-instantaneous aggregation would otherwise have no clear period.

| Value | Meaning | Example |
|---|---|---|
| `Instantaneous` | Value at a particular instant | Temperature observed at 09:00 |
| `Minimum` | Lowest value over the applicable period | Daily minimum temperature |
| `Maximum` | Highest value over the applicable period | Daily maximum temperature |
| `Mean` | Arithmetic mean over the applicable period | Mean relative humidity for three hours |
| `Sum` | Accumulated total over the applicable period | Total rainfall during a forecast day |

## Non-goals

An `OnDemand` Resource must describe what the Provider can supply, but it may also carry current or representative values. `Direct` identifies a Resource whose specific information is usable without a further Provider invocation. The modes define minimum requirements; they do not prohibit additional fields. Spatial indexes such as H3 are implementation projections and are not part of the portable domain contract.

A measured observation requires `observedAt`. A forecast requires `modelRunAt` and a validity window with both `startsAt` and `endsAt`. `generatedAt` records when the normalized Resource was produced and does not replace either domain timestamp.

## Naming open item

This pack currently covers measured observations and forecasts. `WeatherInformation` is a clearer candidate name if both remain in one pack. `AgriWeatherInformation` and `AgriWeatherAdvisory` are not recommended because the `openagrinet:` namespace and the selected OAN schema already establish the agricultural context.

## Examples

- [Point forecast](examples/point-forecast.json)
- [District observation](examples/district-observation.json)
- [Live weather observation](examples/live-weather-observation.json)
- [On-demand weather information](examples/on-demand-weather-information.json)
