# Target JSON Schema (fixed)

This is the **only** shape the final output ever takes. Every field listed here must be
present in the output (use `null`, `""`, `[]`, or the stated default for unknowns — never
omit a key). It follows the same pattern as the other knowledge-builder skills, but with
**two** transactional arrays (`customers` and `customerMemberships`) plus one generated
knowledge array (`customerKnowledge`), because a customer and their purchases are distinct
records that get linked together.

```json
{
  "customers": [
    {
      "id": "uuid",
      "businessId": "string",
      "firstName": "string",
      "lastName": "string",
      "email": "string|null",
      "phone": "string|null",
      "dob": "string|null",
      "gender": "string|null",
      "address": "string|null",
      "locationId": "string",
      "joinedDate": "string|null",
      "lastVisitDate": "string|null",
      "totalVisits": 0,
      "totalSpend": 0.0,
      "lifetimeValue": 0.0,
      "tags": ["string"],
      "preferredContactMethod": "string|null",
      "activeMemberships": [
        {
          "membershipId": "uuid|null — the linked customerMemberships[] record's membershipPlanId",
          "membershipName": "string — real plan name, or \"Other\" if unmatched",
          "benefits": [
            {
              "serviceNameRaw": "string",
              "serviceId": "uuid|null"
            }
          ]
        }
      ],
      "createdAt": "ISO 8601 timestamp",
      "updatedAt": "ISO 8601 timestamp",
      "_etag": null,
      "_ts": null
    }
  ],
  "customerMemberships": [
    {
      "id": "uuid",
      "businessId": "string",
      "customerId": "uuid — matches a customers[].id",
      "membershipPlanId": "uuid|null — matches a membership-knowledge-builder memberships[].id or a package-knowledge-builder packages[].id when matched, else null",
      "membershipName": "string — the real plan name when matched, else \"Other\"",
      "planKind": "string — \"Membership\", \"Package\", or \"Other\"",
      "locationId": "string",
      "invoiceNo": "string|null",
      "benefitType": "string — e.g. \"ServiceBenefit\"",
      "saleDate": "string|null",
      "startDate": "string",
      "endDate": "string|null",
      "salesAmount": 0.0,
      "salesAmountInclTax": 0.0,
      "balanceValue": 0.0,
      "cancelledValue": 0,
      "expiredValue": 0,
      "membershipStatus": "string — e.g. \"Active\", \"Expired\", \"Cancelled\"",
      "recurrenceStatus": "string|null — e.g. \"Active\", \"None\"",
      "nextRecurrenceDate": "string|null",
      "benefits": [
        {
          "serviceNameRaw": "string",
          "serviceId": "uuid|null",
          "totalCredits": 0,
          "redeemedCredits": 0,
          "refundedCredits": 0,
          "expiredCredits": 0,
          "balanceCredits": 0
        }
      ],
      "createdAt": "ISO 8601 timestamp",
      "updatedAt": "ISO 8601 timestamp",
      "_etag": null,
      "_ts": null
    }
  ],
  "customerKnowledge": [
    {
      "customerId": "string — matches the corresponding customers[].id",
      "customerName": "string",
      "summary": "string — 2-4 sentence plain-language profile of this customer",
      "engagementLevel": "string — e.g. \"High\", \"Moderate\", \"Low\", \"New\" — based on visits/spend/recency actually on record",
      "valueSegment": "string — e.g. \"Top spender\", \"Regular\", \"Occasional\" — based on totalSpend/lifetimeValue actually on record",
      "activePlans": ["string — names of currently active memberships/packages"],
      "preferredServices": ["string — services this customer uses most, from their benefits history"],
      "commonQuestions": ["string — plausible questions this customer might ask staff"],
      "keywords": ["string — search/discovery/segmentation terms for this customer"],
      "notes": "string — anything staff should know when serving this customer, or \"\" if none",
      "createdAt": "ISO 8601 timestamp",
      "updatedAt": "ISO 8601 timestamp"
    }
  ]
}
```

## Field notes

**customers** — the base profile record, produced deterministically from the CSV/manual entry
per `references/column-mapping.md`. `activeMemberships` is derived, not independently
collected: after `customerMemberships` is built (Stage 2), populate each customer's
`activeMemberships` by filtering that customer's records where `membershipStatus == "Active"`
and projecting the lightweight view (`membershipId`, `membershipName`, `benefits` without the
credit-tracking numbers). Don't add creative/analytical content here — that belongs in
`customerKnowledge`.

**customerMemberships** — one record per purchase/enrollment (a customer can have several:
one per membership or package they've bought). This is the transactional record; it mirrors
the fields a real membership/package sale would have (credits, balances, recurrence). Two
extra fields not in the user's original sample were added for clarity:
- `membershipName`: kept alongside `membershipPlanId` so the record is human-readable even
  when the plan couldn't be matched (in which case it's literally `"Other"`).
- `planKind`: distinguishes whether the linked plan came from a Membership Knowledge Base, a
  Package Knowledge Base, or matched neither (`"Other"`).

**customerKnowledge** — the generated layer, one entry per customer. `customerId` must
exactly match the `id` of its corresponding entry in `customers`, so `customers` and
`customerKnowledge` stay the same length and joinable 1:1. Base `engagementLevel` and
`valueSegment` only on the customer's actual recorded visits/spend/dates — don't invent a
segment scheme the data doesn't support.
