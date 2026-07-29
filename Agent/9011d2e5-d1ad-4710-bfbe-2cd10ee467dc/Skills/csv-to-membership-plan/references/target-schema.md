# Membership Plan Target Schema (JSON)

This is the fixed target structure every membership CSV must map to. All fields listed here are required to be present in the output JSON, with defaults applied per the column-mapping.md rules.

```json
{
  "memberships": [
    {
      "id": "string (UUID or plan_<code>)",
      "businessId": "string",
      "planId": "string (defaults to id)",
      "locationId": "string",
      "externalMembershipId": "string",
      "membershipName": "string (required)",
      "membershipCode": "string or null",
      "membershipTypeKind": "string (default: 'Recurring')",
      "descriptionRaw": "string",
      "price": "number >= 0 (required)",
      "priceSource": "string (default: 'FromSourceFile')",
      "billingCycle": "string (default: 'Monthly')",
      "membershipDuration": "string (required, e.g. '1 Month', '12 Months', 'Ongoing')",
      "isUnlimited": "boolean (default: false)",
      "setupFee": "number >= 0 (default: 0)",
      "annualFee": "number >= 0 (default: 0)",
      "declineFee": "number >= 0 (default: 0)",
      "buyOutFee": "number >= 0 (default: 0)",
      "freezeFee": "number >= 0 (default: 0)",
      "downgradeFee": "number or null (default: null)",
      "upgradeFee": "number or null (default: null)",
      "guestPassFee": "number >= 0 (default: 0)",
      "guestPassVisits": "integer >= 0 (default: 0)",
      "numVisits": "integer >= 0 (default: 0)",
      "advanceBookingDays": "integer >= 0 (default: 0)",
      "saleStartDate": "ISO 8601 string or null (default: null)",
      "centerAssigned": "boolean (default: true)",
      "soldInCenter": "boolean (default: true)",
      "benefits": [
        {
          "serviceNameRaw": "string (the name as it appeared in the source CSV)",
          "serviceId": "string (UUID from Service Knowledge Base) or null if unmatched",
          "totalCredits": "integer >= 0 (default: 0)"
        }
      ],
      "isActive": "boolean (default: true)",
      "createdAt": "ISO 8601 timestamp",
      "updatedAt": "ISO 8601 timestamp",
      "_etag": null,
      "_ts": null
    }
  ],
  "membershipKnowledge": [
    {
      "membershipId": "string (must match a membership.id)",
      "membershipName": "string (copy from membership.membershipName)",
      "summary": "string (1–2 sentence overview of the membership)",
      "valueProposition": "string (what problem does it solve? who should buy it?)",
      "idealFor": "string (describe the target member or use case)",
      "includedServiceNames": "string (comma-separated list of service names from benefits)",
      "commonQuestions": "string (likely FAQ entries, e.g. 'Can I pause it? Yes, for $X fee')",
      "keywords": "string (comma-separated tags for search/filtering)",
      "notes": "string (any special conditions, warnings, or internal notes)",
      "createdAt": "ISO 8601 timestamp",
      "updatedAt": "ISO 8601 timestamp"
    }
  ]
}
```

## Mandatory Fields for a "Complete" Membership

Before a membership is marked as ready/complete, these four fields must all be present and valid:
1. **membershipName** — non-empty string
2. **price** — number ≥ 0
3. **membershipDuration** — non-empty string
4. **benefits** — non-empty array (at least one service)

If any of these are missing or invalid, the membership is flagged as a "gap" and held for user review/correction.

## Note on Defaults

All other fields (setupFee, annualFee, billingCycle, etc.) have sensible defaults applied per the column-mapping.md rules. If a field is missing in the source CSV and has a default, it is automatically filled; the user is NOT required to provide every field for every membership.
