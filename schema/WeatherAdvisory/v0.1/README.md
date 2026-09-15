# Weather Advisory

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

Defines weather-informed agricultural guidance that a Provider can supply on demand or make directly available.

## Attachment point

The schema is applied to `resourceAttributes` of a Beckn `Resource`. An `OnDemand` Resource describes the advisory scope a Provider supports. A `Direct` Resource carries specific advice.

## Composition

`WeatherAdvisory` combines the Agriculture Resource and Weather Advisory field sets with `allOf`.

## Fields

"Required when" describes a complete OAN Resource. It does not make the field mandatory in a Beckn `Intent` or an identifier-only protocol reference.

| Field | Required when | Meaning |
|---|---|---|
| `@type` | Always | Identifies the Resource as `openagrinet:WeatherAdvisory` |
| `informationMode` | Always | `OnDemand` requires a Provider invocation; `Direct` contains specific advice |
| `subjectCategories` | Always | Required by the composed Agriculture Resource field set; this pack additionally requires `Weather` |
| `agricultureSubjects` | Optional | Governed crop, pest, disease, or practice references when relevant |
| `languages` | `OnDemand`; optional in `Direct` | Supported response languages; each Direct recommendation declares its own language |
| `coverageAreas` | Optional | Geographic applicability or supported coverage |
| `topics` | Both modes | Topics addressed by the advisory |
| `supportedWeatherParameters` | `OnDemand` | Weather parameters available as the basis for on-demand advice |
| `forecastHorizon` | Optional | Maximum supported forecast horizon |
| `updateFrequency` | Optional | Expected refresh interval |
| `geographicGranularities` | `OnDemand` | Geographic levels at which advice is available |
| `location` | `Direct` | Beckn Location whose required `geo` member identifies where the advice applies |
| `issuedAt` | `Direct` | Time at which the Provider issued the advice |
| `validity` | `Direct` | Period during which the advice applies |
| `recommendations` | `Direct` | Localized guidance, weather severity, and suggested actions |
| `weatherBasis` | `Direct` | Weather parameters and supporting Resource identifiers used to produce the advice |
| `source` | `Direct` | Provider or authoritative source that issued the advice |

## Non-goals

This schema does not replace `WeatherObservation`, which carries measured or forecast values. Weather Advisory interprets weather information and recommends an agricultural action.

`OnDemand` is the Weather Advisory capability declaration. It carries supported parameters, horizon, update frequency, geographic granularities, language, topics, and coverage. `Direct` carries the place-specific advisory. There is no separate `WeatherAdvisoryCapability` schema.

## Examples

- [District crop advisory](examples/district-village-advisory.json)
- [Point irrigation advisory](examples/point-short-horizon-advisory.json)
- [On-demand weather advisory](examples/on-demand-weather-advisory.json)
