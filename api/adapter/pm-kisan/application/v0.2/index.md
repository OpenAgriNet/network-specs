---
layout: default
title: PM-KISAN application integration contract
---
# PM-KISAN application integration contract

[Adapter contracts](../../../) · [OpenAPI document](openapi.yaml)

Proposed OAN adapter payloads for this external service. Not an official provider API specification. Paths are illustrative; authentication, errors and Beckn wire bindings are not defined. Examples are synthetic.

## PMKISANApplicationInit

`POST /pmkisanapplication/init`

### Request

[Schema component](openapi.yaml#/components/schemas/PMKISANApplicationInitRequest)

| Field | Required | Meaning |
|---|---|---|
| `@context` | Yes | This pack's JSON-LD context, alone or inside a larger context array. |
| `@type` | Yes | This pack's OAN type, alone or alongside the Provider's own types. |
| `applicant` | Optional | The farmer, identified by registered mobile. |
| `enrolmentId` | Optional | The farmer's PM-KISAN registration number. Never an Aadhaar number. |
| `informationMode` | Yes | How this information is obtained. Always fetched from the scheme on demand. |
| `scheme` | Yes | The government scheme this payload is about. |

Nested requirements and conditional identifier choices are defined in the linked schema.

Example: [on-demand-request-otp.json](examples/on-demand-request-otp.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/SchemeApplication/v0.2/context.jsonld",
  "@type": "openagrinet:SchemeApplication",
  "informationMode": "OnDemand",
  "scheme": {
    "code": "PM-KISAN",
    "name": "Pradhan Mantri Kisan Samman Nidhi"
  },
  "applicant": {
    "mobile": "9876543210"
  }
}
```

### Response

[Schema component](openapi.yaml#/components/schemas/PMKISANApplicationInitResponse)

| Field | Required | Meaning |
|---|---|---|
| `@context` | Yes | This pack's JSON-LD context, alone or inside a larger context array. |
| `@type` | Yes | This pack's OAN type, alone or alongside the Provider's own types. |
| `challenge` | Yes | The portal's acknowledgement of the code it sent. Comes back in the reply, never in the request. |
| `informationMode` | Yes | How this information is obtained. Always fetched from the scheme on demand. |
| `scheme` | Yes | The government scheme this payload is about. |

Nested requirements and conditional identifier choices are defined in the linked schema.

Example: [PMKISANApplicationInit-response.json](examples/PMKISANApplicationInit-response.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/SchemeApplication/v0.2/context.jsonld",
  "@type": "openagrinet:SchemeApplication",
  "challenge": {
    "issued": {
      "channel": "SMS",
      "expiresAt": "2026-11-18T06:05:00Z",
      "length": 4,
      "method": "OTP",
      "valueType": "NUMERIC"
    }
  },
  "informationMode": "OnDemand",
  "scheme": {
    "code": "PM-KISAN"
  }
}
```

Example: [on-demand-challenge-issued.json](examples/on-demand-challenge-issued.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/SchemeApplication/v0.2/context.jsonld",
  "@type": "openagrinet:SchemeApplication",
  "informationMode": "OnDemand",
  "scheme": {
    "code": "PM-KISAN",
    "name": "Pradhan Mantri Kisan Samman Nidhi"
  },
  "challenge": {
    "issued": {
      "method": "OTP",
      "channel": "SMS",
      "length": 4,
      "valueType": "NUMERIC",
      "expiresAt": "2026-10-07T11:08:00Z"
    }
  }
}
```

## PMKISANApplicationStatus

`POST /pmkisanapplication/status`

### Request

[Schema component](openapi.yaml#/components/schemas/PMKISANApplicationStatusRequest)

| Field | Required | Meaning |
|---|---|---|
| `@context` | Yes | This pack's JSON-LD context, alone or inside a larger context array. |
| `@type` | Yes | This pack's OAN type, alone or alongside the Provider's own types. |
| `applicant` | Optional | The farmer, identified by registered mobile. |
| `challenge` | Yes | The OTP sent back to prove the request is the applicant's. |
| `enrolmentId` | Optional | The farmer's PM-KISAN registration number. Never an Aadhaar number. |
| `informationMode` | Yes | How this information is obtained. Always fetched from the scheme on demand. |
| `scheme` | Yes | The government scheme this payload is about. |

Nested requirements and conditional identifier choices are defined in the linked schema.

Example: [on-demand-read-status.json](examples/on-demand-read-status.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/SchemeApplication/v0.2/context.jsonld",
  "@type": "openagrinet:SchemeApplication",
  "informationMode": "OnDemand",
  "scheme": {
    "code": "PM-KISAN",
    "name": "Pradhan Mantri Kisan Samman Nidhi"
  },
  "applicant": {
    "mobile": "9876543210"
  },
  "challenge": {
    "response": {
      "method": "OTP",
      "value": "4821"
    }
  }
}
```

### Response

[Schema component](openapi.yaml#/components/schemas/PMKISANApplicationStatusResponse)

| Field | Required | Meaning |
|---|---|---|
| `@context` | Yes | This pack's JSON-LD context, alone or inside a larger context array. |
| `@type` | Yes | This pack's OAN type, alone or alongside the Provider's own types. |
| `application` | Yes | Where the farmer's application currently stands. |
| `enrolmentId` | Optional | The farmer's PM-KISAN registration number. Never an Aadhaar number. |
| `informationMode` | Yes | How this information is obtained. Always fetched from the scheme on demand. |
| `scheme` | Yes | The government scheme this payload is about. |

Nested requirements and conditional identifier choices are defined in the linked schema.

Example: [PMKISANApplicationStatus-response.json](examples/PMKISANApplicationStatus-response.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/SchemeApplication/v0.2/context.jsonld",
  "@type": "openagrinet:SchemeApplication",
  "application": {
    "registeredOn": "2026-11-18T06:05:00Z"
  },
  "informationMode": "OnDemand",
  "scheme": {
    "code": "PM-KISAN"
  }
}
```
