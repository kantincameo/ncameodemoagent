---
name: doc-data-extractor
description: >
  Extracts structured customer data from any uploaded document (PDF, Word, Excel, CSV, image, webpage, or base64-encoded file)
  and maps the data to a fixed 23-field customer schema. Use this skill whenever you need to parse customer records from a
  document, file, or data payload — including cases where field names vary, data is unstructured, or multiple customers
  appear in a single file. Always invoke this skill before attempting to save customer data to any database or storage system.
---

# doc-data-extractor

Extracts all customer records from a document and maps them to the canonical 23-field customer schema.

## When to Use

Invoke this skill whenever:
- A document (PDF, Word, Excel, CSV, image, URL, base64) contains customer data that must be persisted.
- The source payload field name for the document is unknown or variable.
- Customer data is unstructured, semi-structured, or spread across multiple rows/sections.

## Fixed 23-Field Customer Schema

Every extracted record MUST contain exactly these fields:

```json
{
  "businessId": "",
  "customerId": "",
  "externalCustomerId": "",
  "firstName": "",
  "lastName": "",
  "email": "",
  "phone": "",
  "dob": "",
  "gender": "",
  "address": "",
  "primaryLocationId": "",
  "joinedDate": "",
  "lastVisitDate": "",
  "totalVisits": 0,
  "totalSpend": 0,
  "lifetimeValue": 0,
  "activeMembershipId": "",
  "activeMembershipTier": "",
  "activePackageIds": [],
  "tags": [],
  "preferredContactMethod": "",
  "marketingOptInEmail": false,
  "marketingOptInSms": false,
  "customAttributes": {}
}
```

## Extraction Rules

1. **Scan the entire document** for every distinct customer entity — do not stop at the first match.
2. **Map all available data** to the schema fields above using best-effort inference on column headers, labels, and context.
3. **Type coercion** (strictly enforced — never use `null`):
   - Missing / unknown string → `""`
   - Missing / unknown number → `0`
   - Missing / unknown boolean → `false`
   - Missing / unknown array → `[]`
   - Missing / unknown object → `{}`
   - Missing / unknown address → `""`
4. **Address format**: Combine all address parts into a single string: `"street, city, state, postalCode, country"` (e.g., `"123 Main St, Springfield, IL 62701, US"`). If any part is missing, omit it from the string gracefully.
5. **Date normalization**: Convert all dates to ISO 8601 `YYYY-MM-DD` where possible.
6. **Phone normalization**: Convert to E.164 format (e.g., `+15550001234`) where possible.
7. **Do not invent data**: If a field cannot be confidently mapped, use the empty default — do not guess.
8. **No markdown wrapping**: Return raw JSON arrays only.
9. **Empty document**: If no customer data is found, return `[]`.

## Output Format

Return a JSON array of customer record objects:

```json
[
  {
    "businessId": "biz-001",
    "customerId": "cust-123",
    "externalCustomerId": "",
    "firstName": "Jane",
    "lastName": "Doe",
    "email": "jane.doe@example.com",
    "phone": "+15550001234",
    "dob": "1990-06-15",
    "gender": "female",
    "address": "123 Main St, Springfield, IL 62701, US",
    "primaryLocationId": "loc-01",
    "joinedDate": "2021-03-10",
    "lastVisitDate": "2024-11-20",
    "totalVisits": 14,
    "totalSpend": 420.50,
    "lifetimeValue": 500.00,
    "activeMembershipId": "mem-gold",
    "activeMembershipTier": "Gold",
    "activePackageIds": ["pkg-001", "pkg-003"],
    "tags": ["vip", "returning"],
    "preferredContactMethod": "email",
    "marketingOptInEmail": true,
    "marketingOptInSms": false,
    "customAttributes": {
      "referralSource": "website"
    }
  }
]
```

## Field Mapping Hints

| Common source label variants | Maps to schema field |
|---|---|
| `first name`, `fname`, `given name` | `firstName` |
| `last name`, `lname`, `surname`, `family name` | `lastName` |
| `email`, `email address`, `e-mail` | `email` |
| `phone`, `mobile`, `cell`, `telephone` | `phone` |
| `date of birth`, `birthday`, `DOB` | `dob` |
| `address`, `street address`, `location`, `city`, `state`, `zip`, `postal code`, `country` | `address` (combined string: "street, city, state, postalCode, country") |
| `joined`, `registered`, `sign-up date` | `joinedDate` |
| `last visit`, `last seen`, `recent visit` | `lastVisitDate` |
| `visits`, `visit count`, `# visits` | `totalVisits` |
| `spend`, `total spend`, `revenue` | `totalSpend` |
| `LTV`, `lifetime value`, `CLV` | `lifetimeValue` |
| `membership`, `plan`, `subscription` | `activeMembershipId` / `activeMembershipTier` |
| `packages`, `package IDs` | `activePackageIds` |
| `tags`, `labels`, `segments` | `tags` |
| `contact preference`, `preferred contact` | `preferredContactMethod` |
| `email opt-in`, `email consent` | `marketingOptInEmail` |
| `SMS opt-in`, `SMS consent`, `text opt-in` | `marketingOptInSms` |
