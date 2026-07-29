# Target JSON Schema (fixed)

This is the **only** shape the final output ever takes. Every field listed here must be
present in the output (use `null`, `""`, or `[]` for unknowns — never omit a key). It mirrors
the two-array pattern used by `service-knowledge-builder` (a transactional list + a generated
knowledge list, 1:1 linked by id).

```json
{
  "memberships": [
    {
      "id": "string",
      "businessId": "string",
      "planId": "string",
      "locationId": "string",
      "externalMembershipId": "string",

      "membershipName": "string",
      "membershipCode": "string|null",
      "membershipTypeKind": "string",
      "descriptionRaw": "string",

      "price": 0,
      "priceSource": "string",
      "billingCycle": "string",
      "membershipDuration": "string",
      "isUnlimited": false,

      "setupFee": 0,
      "annualFee": 0,
      "declineFee": 0,
      "buyOutFee": 0,
      "freezeFee": 0,
      "downgradeFee": "number|null",
      "upgradeFee": "number|null",
      "guestPassFee": 0,
      "guestPassVisits": 0,
      "numVisits": 0,
      "advanceBookingDays": 0,
      "saleStartDate": "string|null",

      "centerAssigned": true,
      "soldInCenter": true,

      "benefits": [
        {
          "serviceNameRaw": "string",
          "serviceId": "uuid|null — matches a service-knowledge-builder services[].id when linked",
          "totalCredits": 0
        }
      ],

      "isActive": true,
      "createdAt": "ISO 8601 timestamp",
      "updatedAt": "ISO 8601 timestamp",
      "_etag": null,
      "_ts": null
    }
  ],
  "membershipKnowledge": [
    {
      "membershipId": "string — matches the corresponding memberships[].id",
      "membershipName": "string",
      "summary": "string — 2-4 sentence plain-language description of the membership",
      "valueProposition": "string — why a customer would choose this over paying per-service",
      "idealFor": "string — who this membership is best suited for",
      "includedServiceNames": ["string — resolved names of the linked services"],
      "commonQuestions": ["string — plausible customer questions about this membership"],
      "keywords": ["string — search/discovery terms for this membership"],
      "notes": "string — anything a customer should know before signing up, or \"\" if none",
      "createdAt": "ISO 8601 timestamp",
      "updatedAt": "ISO 8601 timestamp"
    }
  ]
}
```

## Field notes

**memberships** — this is the transactional record, produced deterministically from the CSV
or manual entry per `references/column-mapping.md`. Don't add creative content here; that
belongs in `membershipKnowledge`.

- `membershipDuration` vs `billingCycle`: these are different things. `billingCycle` is how
  often the customer is charged (e.g. "Monthly"); `membershipDuration` is how long the
  membership/commitment lasts (e.g. "12 Months", "Ongoing"). Both matter — don't collapse one
  into the other.
- `benefits[].serviceId` should be a real id from the linked Service Knowledge Base's
  `services` list whenever a confident match was found (see column-mapping.md); otherwise
  `null`, with `serviceNameRaw` preserving whatever text was given.

**membershipKnowledge** — the generated layer. `membershipId` must exactly match the `id` of
its corresponding entry in `memberships`, so the two arrays stay the same length and joinable
1:1. `includedServiceNames` should reflect the resolved/linked service names (falling back to
`serviceNameRaw` for anything that couldn't be linked).