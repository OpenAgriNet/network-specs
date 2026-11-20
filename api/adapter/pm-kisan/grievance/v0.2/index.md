---
layout: default
title: PM-KISAN grievance integration contract
---
# PM-KISAN grievance integration contract

[Adapter contracts](../../../) · [OpenAPI document](openapi.yaml)

Proposed OAN adapter payloads for this external service. Not an official provider API specification. Paths are illustrative; authentication, errors and Beckn wire bindings are not defined. Examples are synthetic.

## PMKISANInit

`POST /pmkisan/init`

### Request

[Schema component](openapi.yaml#/components/schemas/PMKISANInitRequest)

| Field | Required | Meaning |
|---|---|---|
| `@context` | Yes | This pack's JSON-LD context, alone or inside a larger context array. |
| `@type` | Yes | This pack's OAN type, alone or alongside the Provider's own types. |
| `enrolmentId` | Yes | The enrolment the grievance is about, as the scheme numbers it. Never an Aadhaar number. |
| `informationMode` | Yes | How this information is obtained. Always fetched from the scheme on demand. |
| `scheme` | Yes | The government scheme this payload is about. |

Nested requirements and conditional identifier choices are defined in the linked schema.

Example: [pmkisan-on-demand-request-otp.json](examples/pmkisan-on-demand-request-otp.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.2/context.jsonld",
  "@type": "openagrinet:Grievance",
  "informationMode": "OnDemand",
  "scheme": {
    "code": "PM-KISAN",
    "name": "Pradhan Mantri Kisan Samman Nidhi"
  },
  "enrolmentId": "UP12345678A"
}
```

### Response

[Schema component](openapi.yaml#/components/schemas/PMKISANInitResponse)

| Field | Required | Meaning |
|---|---|---|
| `@context` | Yes | This pack's JSON-LD context, alone or inside a larger context array. |
| `@type` | Yes | This pack's OAN type, alone or alongside the Provider's own types. |
| `challenge` | Yes | The portal's acknowledgement of the code it sent. Comes back in the reply, never in the request. |
| `informationMode` | Yes | How this information is obtained. Always fetched from the scheme on demand. |
| `scheme` | Yes | The government scheme this payload is about. |

Nested requirements and conditional identifier choices are defined in the linked schema.

Example: [PMKISANInit-response.json](examples/PMKISANInit-response.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.2/context.jsonld",
  "@type": "openagrinet:Grievance",
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

Example: [pmkisan-on-demand-challenge-issued.json](examples/pmkisan-on-demand-challenge-issued.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.2/context.jsonld",
  "@type": "openagrinet:Grievance",
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
      "expiresAt": "2026-09-28T11:08:00Z"
    }
  }
}
```

## PMKISANStatus

`POST /pmkisan/status`

### Request

[Schema component](openapi.yaml#/components/schemas/PMKISANStatusRequest)

| Field | Required | Meaning |
|---|---|---|
| `@context` | Yes | This pack's JSON-LD context, alone or inside a larger context array. |
| `@type` | Yes | This pack's OAN type, alone or alongside the Provider's own types. |
| `case` | Yes | The case the reply concerns. |
| `challenge` | Yes | The OTP sent back to prove the request is the applicant's. |
| `enrolmentId` | Yes | The enrolment the grievance is about, as the scheme numbers it. Never an Aadhaar number. |
| `informationMode` | Yes | How this information is obtained. Always fetched from the scheme on demand. |
| `scheme` | Yes | The government scheme this payload is about. |

Nested requirements and conditional identifier choices are defined in the linked schema.

Example: [pmkisan-on-demand-read-cases.json](examples/pmkisan-on-demand-read-cases.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.2/context.jsonld",
  "@type": "openagrinet:Grievance",
  "informationMode": "OnDemand",
  "scheme": {
    "code": "PM-KISAN",
    "name": "Pradhan Mantri Kisan Samman Nidhi"
  },
  "challenge": {
    "response": {
      "method": "OTP",
      "value": "7390"
    }
  },
  "enrolmentId": "UP12345678A",
  "case": {
    "filedOn": "2026-09-28"
  }
}
```

### Response

[Schema component](openapi.yaml#/components/schemas/PMKISANStatusResponse)

| Field | Required | Meaning |
|---|---|---|
| `@context` | Yes | This pack's JSON-LD context, alone or inside a larger context array. |
| `@type` | Yes | This pack's OAN type, alone or alongside the Provider's own types. |
| `case` | Yes | The case the reply concerns. |
| `grievance` | Optional | The grievance itself. |
| `informationMode` | Yes | How this information is obtained. Always fetched from the scheme on demand. |
| `scheme` | Yes | The government scheme this payload is about. |

Nested requirements and conditional identifier choices are defined in the linked schema.

Example: [PMKISANStatus-response.json](examples/PMKISANStatus-response.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.2/context.jsonld",
  "@type": "openagrinet:Grievance",
  "case": {
    "status": {
      "code": "Registered"
    }
  },
  "informationMode": "OnDemand",
  "scheme": {
    "code": "PM-KISAN"
  }
}
```

## PMKISANSupport

`POST /pmkisan/support`

### Request

[Schema component](openapi.yaml#/components/schemas/PMKISANSupportRequest)

| Field | Required | Meaning |
|---|---|---|
| `@context` | Yes | This pack's JSON-LD context, alone or inside a larger context array. |
| `@type` | Yes | This pack's OAN type, alone or alongside the Provider's own types. |
| `challenge` | Yes | The OTP sent back to prove the request is the applicant's. |
| `enrolmentId` | Yes | The enrolment the grievance is about, as the scheme numbers it. Never an Aadhaar number. |
| `grievance` | Yes | The grievance itself. |
| `informationMode` | Yes | How this information is obtained. Always fetched from the scheme on demand. |
| `provider` | Yes | The desk the grievance is filed with. |
| `scheme` | Yes | The government scheme this payload is about. |

Nested requirements and conditional identifier choices are defined in the linked schema.

Example: [pmkisan-on-demand-lodge-grievance.json](examples/pmkisan-on-demand-lodge-grievance.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.2/context.jsonld",
  "@type": "openagrinet:Grievance",
  "informationMode": "OnDemand",
  "provider": {
    "id": "pmkisan",
    "descriptor": {
      "name": "PM-KISAN Portal"
    }
  },
  "scheme": {
    "code": "PM-KISAN",
    "name": "Pradhan Mantri Kisan Samman Nidhi"
  },
  "challenge": {
    "response": {
      "method": "OTP",
      "value": "4821"
    }
  },
  "enrolmentId": "UP12345678A",
  "grievance": {
    "category": {
      "code": "G003"
    },
    "description": "Third instalment for 2026 has not been credited."
  }
}
```

### Response

[Schema component](openapi.yaml#/components/schemas/PMKISANSupportResponse)

| Field | Required | Meaning |
|---|---|---|
| `@context` | Yes | This pack's JSON-LD context, alone or inside a larger context array. |
| `@type` | Yes | This pack's OAN type, alone or alongside the Provider's own types. |
| `case` | Yes | The case opened for this grievance. |
| `enrolmentId` | Optional | The enrolment the grievance is about, as the scheme numbers it. Never an Aadhaar number. |
| `grievance` | Optional | The grievance itself. |
| `informationMode` | Yes | How this information is obtained. Always fetched from the scheme on demand. |
| `provider` | Optional | The desk the grievance is filed with. |
| `scheme` | Yes | The government scheme this payload is about. |

Nested requirements and conditional identifier choices are defined in the linked schema.

Example: [PMKISANSupport-response.json](examples/PMKISANSupport-response.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.2/context.jsonld",
  "@type": "openagrinet:Grievance",
  "case": {
    "ticketNo": "EXAMPLE"
  },
  "informationMode": "OnDemand",
  "scheme": {
    "code": "PM-KISAN"
  }
}
```
