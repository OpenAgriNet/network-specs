---
layout: default
title: Grievance API review
---
# Grievance operation contracts

[All API contracts](../../) · [OpenAPI document](openapi.yaml)

Consumer-review proposal. Paths are synthetic adapter-facing operations, not deployed endpoints or complete Beckn envelopes. Authentication and errors remain open. Response examples are synthetic minimum valid outcomes, not actual portal responses.

## PMFBYStatus

`POST /pmfby/status`

### Request

[Schema component](openapi.yaml#/components/schemas/PMFBYStatusRequest)

| Field | Required | Meaning |
|---|---|---|
| `@context` | Yes | This pack's JSON-LD context, alone or inside a larger context array. |
| `@type` | Yes | This pack's OAN type, alone or alongside the Provider's own types. |
| `applicantMobile` | Yes | The farmer's mobile, which the portal files the ticket against. |
| `case` | Yes | The case opened for this grievance. |
| `cropYear` | Optional | The crop year of the enrolment. |
| `enrolmentId` | Optional | The enrolment the grievance is about, as the scheme numbers it. Never an Aadhaar number. |
| `informationMode` | Yes | How this information is obtained. Always fetched from the scheme on demand. |
| `scheme` | Yes | The government scheme this payload is about. |
| `season` | Optional | The season of the enrolment. |

Nested requirements and conditional identifier choices are defined in the linked schema.

Example: [pmfby-on-demand-read-case.json](examples/pmfby-on-demand-read-case.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.1/context.jsonld",
  "@type": "openagrinet:Grievance",
  "informationMode": "OnDemand",
  "scheme": {
    "code": "PMFBY",
    "name": "Pradhan Mantri Fasal Bima Yojana"
  },
  "applicantMobile": "9876543210",
  "case": {
    "ticketNo": "100626000099001"
  }
}
```

### Response

[Schema component](openapi.yaml#/components/schemas/PMFBYStatusResponse)

| Field | Required | Meaning |
|---|---|---|
| `@context` | Yes | This pack's JSON-LD context, alone or inside a larger context array. |
| `@type` | Yes | This pack's OAN type, alone or alongside the Provider's own types. |
| `case` | Yes | The case opened for this grievance. |
| `cropYear` | Optional | The crop year of the enrolment. |
| `enrolmentId` | Optional | The enrolment the grievance is about, as the scheme numbers it. Never an Aadhaar number. |
| `grievance` | Optional | The grievance itself. |
| `informationMode` | Yes | How this information is obtained. Always fetched from the scheme on demand. |
| `scheme` | Yes | The government scheme this payload is about. |
| `season` | Optional | The season of the enrolment. |

Nested requirements and conditional identifier choices are defined in the linked schema.

Example: [PMFBYStatus-response.json](examples/PMFBYStatus-response.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.1/context.jsonld",
  "@type": "openagrinet:Grievance",
  "case": {
    "status": {
      "code": "Registered"
    }
  },
  "informationMode": "OnDemand",
  "scheme": {
    "code": "PMFBY"
  }
}
```

## PMFBYSupport

`POST /pmfby/support`

### Request

[Schema component](openapi.yaml#/components/schemas/PMFBYSupportRequest)

| Field | Required | Meaning |
|---|---|---|
| `@context` | Yes | This pack's JSON-LD context, alone or inside a larger context array. |
| `@type` | Yes | This pack's OAN type, alone or alongside the Provider's own types. |
| `applicantMobile` | Yes | The farmer's mobile, which the portal files the ticket against. |
| `complaintDate` | Optional | The caller's own filing date, where case.filedOn is the portal's. |
| `cropYear` | Yes | The crop year of the enrolment. |
| `enrolmentId` | Yes | The enrolment the grievance is about, as the scheme numbers it. Never an Aadhaar number. |
| `grievance` | Yes | The grievance itself. |
| `informationMode` | Yes | How this information is obtained. Always fetched from the scheme on demand. |
| `provider` | Yes | The desk the grievance is filed with. |
| `receiptSourceId` | Optional | The channel the complaint arrived through. Names the channel, not the farmer. |
| `scheme` | Yes | The government scheme this payload is about. |
| `season` | Yes | The season of the enrolment. |

Nested requirements and conditional identifier choices are defined in the linked schema.

Example: [pmfby-on-demand-file-grievance.json](examples/pmfby-on-demand-file-grievance.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.1/context.jsonld",
  "@type": "openagrinet:Grievance",
  "informationMode": "OnDemand",
  "provider": {
    "id": "pmfby",
    "descriptor": {
      "name": "PMFBY Grievance Portal"
    }
  },
  "scheme": {
    "code": "PMFBY",
    "name": "Pradhan Mantri Fasal Bima Yojana"
  },
  "enrolmentId": "KA2026KH00123456",
  "applicantMobile": "9876543210",
  "cropYear": "2026",
  "season": "Kharif",
  "complaintDate": "2026-09-28",
  "receiptSourceId": "4",
  "grievance": {
    "category": {
      "code": "3"
    },
    "subCategory": {
      "code": "10"
    },
    "description": "Cannot log in to the PMFBY portal to view my Kharif 2026 enrolment."
  }
}
```

### Response

[Schema component](openapi.yaml#/components/schemas/PMFBYSupportResponse)

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

Example: [PMFBYSupport-response.json](examples/PMFBYSupport-response.json)

```json
{
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.1/context.jsonld",
  "@type": "openagrinet:Grievance",
  "case": {
    "ticketNo": "123456789"
  },
  "informationMode": "OnDemand",
  "scheme": {
    "code": "PMFBY"
  }
}
```

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
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.1/context.jsonld",
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
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.1/context.jsonld",
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
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.1/context.jsonld",
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
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.1/context.jsonld",
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
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.1/context.jsonld",
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
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.1/context.jsonld",
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
  "@context": "https://openagrinet.github.io/network-specs/schema/Grievance/v0.1/context.jsonld",
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
