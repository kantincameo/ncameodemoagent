# Target JSON Schema (fixed)

This is the **only** shape the final output ever takes. Every field listed here must be
present in the output (use `null`, `""`, `[]`, or the stated default for unknowns — never
omit a key). It mirrors the two-array pattern used by `service-knowledge-builder` and
`membership-knowledge-builder` (a transactional list + a generated knowledge list, 1:1 linked
by id). The transactional `packages[]` fields follow the user's existing `PackagePlan`
structure, plus one addition — `expiryDuration` — which plays the role
`membershipDuration` plays for memberships.

```json
{
  "packages": [
    {
      "id": "guid",
      "businessId": "string",
      "packageId": "string",
      "locationId": "string",
      "packageCode": "string",
      "packageName": "string",
      "description": "string",
      "packageCategory": "Default",
      "businessName": "Default",

      "price": 0.0,
      "priceSource": "FromSourceFile",
      "expiryDuration": "string",

      "onlineBookingEnabled": true,
      "taxGroup": null,
      "centerTaxId": null,

      "hasPackageSales": true,
      "hasServices": true,
      "hasServiceDiscount": true,
      "hasFreeProducts": false,
      "hasBundledProducts": false,
      "hasForms": false,
      "hasClasses": false,
      "hasWorkshops": false,
      "hasDayPackage": false,

      "benefits": [
        {
          "serviceNameRaw": "string",
          "serviceId": "uuid or \"\" — matches a service-knowledge-builder services[].id when linked",
          "totalCredits": 0
        }
      ],

      "ownerType": "Organization",
      "ownerName": "string",
      "isActive": true,
      "createdAt": "ISO 8601 timestamp",
      "updatedAt": "ISO 8601 timestamp",
      "_etag": null,
      "_ts": null
    }
  ],
  "packageKnowledge": [
    {
      "packageId": "string — matches the corresponding packages[].id",
      "packageName": "string",
      "summary": "string — 2-4 sentence plain-language description of the package",
      "valueProposition": "string — why a customer would choose this over paying per-visit",
      "idealFor": "string — who this package is best suited for",
      "includedServiceNames": ["string — resolved names of the linked services"],
      "expirySummary": "string — plain-language reminder of when/how the package expires",
      "commonQuestions": ["string — plausible customer questions about this package"],
      "keywords": ["string — search/discovery terms for this package"],
      "notes": "string — anything a customer should know before buying, or \"\" if none",
      "createdAt": "ISO 8601 timestamp",
      "updatedAt": "ISO 8601 timestamp"
    }
  ]
}
```

## Field notes

**packages** — this is the transactional record, produced deterministically from the CSV or
manual entry per `references/column-mapping.md`. Don't add creative content here; that
belongs in `packageKnowledge`.

- `expiryDuration` vs a membership's `membershipDuration`: same idea, different context — a
  package is normally a one-time purchase, and `expiryDuration` says how long it stays valid
  before unused credits/sessions are lost (e.g. "30 Days", "6 Months"). There's no
  `billingCycle` equivalent here since packages don't recur the way memberships do.
- `benefits[].serviceId` should be a real id from the linked Service Knowledge Base's
  `services` list whenever a confident match was found (see column-mapping.md); otherwise
  `""`, with `serviceNameRaw` preserving whatever text was given.
- The `has*` boolean flags (`hasPackageSales`, `hasServices`, `hasServiceDiscount`,
  `hasFreeProducts`, `hasBundledProducts`, `hasForms`, `hasClasses`, `hasWorkshops`,
  `hasDayPackage`) describe what kind of package this is / what it bundles — keep their
  defaults from column-mapping.md unless the CSV or user says otherwise.

**packageKnowledge** — the generated layer. `packageId` must exactly match the `id` of its
corresponding entry in `packages`, so the two arrays stay the same length and joinable 1:1.
`includedServiceNames` should reflect the resolved/linked service names (falling back to
`serviceNameRaw` for anything that couldn't be linked).
