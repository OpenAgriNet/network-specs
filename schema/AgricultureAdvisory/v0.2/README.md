# Agriculture Advisory

Use `AgricultureAdvisory` for actionable guidance. Use `WeatherObservation` for the forecast or measurement itself. A farmer's booking allowance and confirmed order are provider transaction data, not recommendations.

An OnDemand catalog Resource declares topics and supported languages; an issued Direct Resource includes topics, issuance timestamp, recommendations with message and language, and source. The shared AgricultureResource fields apply in both modes. Optional applicability conditions describe the crops, seasons, stages and timing to which advice applies.

Set `weatherInformed: true` to declare the stronger weather contract. Include Weather in subjectCategories. An OnDemand weather service also declares supported weather parameters and geographic granularities. A Direct weather advisory also supplies its location, bounded validity and weather basis. Do not infer these fields from a publisher name or bulletin date.
