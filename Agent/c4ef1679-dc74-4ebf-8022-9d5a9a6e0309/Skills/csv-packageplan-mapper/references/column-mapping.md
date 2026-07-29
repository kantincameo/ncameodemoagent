# CSV Column Mapping & Validation Rules

This mirrors the target `PackagePlan` structure the user's existing CSV mapper already uses,
with one addition: `expiryDuration` (packages don't recur like memberships, but they do
expire — this is a package's equivalent of a membership's `membershipDuration`).

Package CSVs come from many different systems, so headers are never standardized. Before
mapping rows to the target schema, resolve every raw CSV header to a target field using the
alias table below. Matching is **case-insensitive** and **whitespace-insensitive**, and
should use semantic judgement, not just exact string matching — a column doesn't need to
match an alias exactly; use context (naming conventions, abbreviations, neighboring columns,
sample values) to find the best match.

| Target Field | Likely CSV Column Names (examples, not exhaustive) |
|---|---|
| `packageId` | id, Id, ID, sourceId, source_id, packageId, package_id |
| `packageName` | packageName, packName, Name, Title, PkgName, pkg_name |
| `description` | description, desc, details, about, summary |
| `price` | price, cost, amount, fee, rate, Price |
| `packageCode` | packageCode, code, pkgCode, pkg_code, Code |
| `packageCategory` | packageCategory, category, type, Category |
| `expiryDuration` | expiry, expiryDuration, expiry_duration, validity, valid_for, expiration, expiration_period, valid_until_period |
| `businessId` | businessId, bizId, orgId, business_id |
| `businessName` | businessName, bizName, company, Business |
| `locationId` | locationId, location, locId, loc_id |
| `ownerName` | ownerName, owner, org, organization |
| `ownerType` | ownerType, orgType, owner_type |
| `isActive` | isActive, active, status, enabled |
| `onlineBookingEnabled` | onlineBookingEnabled, onlineBooking, booking, online, canBook, bookingType, isOnlineBooking |
| `benefits[].serviceNameRaw` | serviceName, serviceNameRaw, service |
| `benefits[].serviceId` | serviceId, svcId, service_id |
| `benefits[].totalCredits` | totalCredits, credits, lessons, sessions, qty |
| `hasPackageSales` | hasPackageSales, packageSales |
| `hasServices` | hasServices, services |
| `hasServiceDiscount` | hasServiceDiscount, serviceDiscount, discount |
| `hasFreeProducts` | hasFreeProducts, freeProducts |
| `hasBundledProducts` | hasBundledProducts, bundledProducts |
| `hasForms` | hasForms, forms |
| `hasClasses` | hasClasses, classes |
| `hasWorkshops` | hasWorkshops, workshops |
| `hasDayPackage` | hasDayPackage, dayPackage |

For boolean fields, accept these values (case-insensitive):
- True: `true`, `1`, `yes`, `y`, `on`
- False: `false`, `0`, `no`, `n`, `off`

For columns that cannot be confidently matched to any target field, skip them and note them
in an unmapped-columns list rather than erroring.

## Linking "services included" to the Service Knowledge Base

The benefits columns (`serviceNameRaw` / `serviceId` / `totalCredits`) typically describe one
or more services per package. For each service name found:

1. Try to match it against the `serviceName` field of the Service Knowledge Base's `services`
   list (see Stage 1a in SKILL.md), case/whitespace-insensitive, allowing close/fuzzy matches
   (e.g. "Massage" ↔ "60-Min Massage").
2. If matched → set `benefits[].serviceId` to that service's real `id` (a UUID from the
   Service Knowledge Base) and `serviceNameRaw` to the name as it appeared in the package CSV.
3. If no confident match → keep `serviceNameRaw` as-is, set `serviceId` to `""`, and flag it
   to the user during the gap-filling step rather than silently guessing.

## Example: Service Linking in Action

**Setup:** Your Service Knowledge Base has these services registered:
```json
{
  "services": [
    { "id": "d1d5a13b-8306-4c3c-b36f-493a02ba1378", "serviceName": "Single Lesson 30 min", ... },
    { "id": "0201e4fc-5f8b-4e64-a7d4-bb9e5f91d3c1", "serviceName": "Bay rental 1 hour", ... }
  ]
}
```

**Scenario 1: Confident Match**
- CSV provides: `serviceName = "Single Lesson"`
- Fuzzy match → finds "Single Lesson 30 min" in SKB ✓
- Result:
  ```json
  {
    "serviceNameRaw": "Single Lesson",
    "serviceId": "d1d5a13b-8306-4c3c-b36f-493a02ba1378",
    "totalCredits": 10
  }
  ```

**Scenario 2: Partial Match**
- CSV provides: `serviceName = "Lesson 30min"`
- Fuzzy match → fuzzy-matches to "Single Lesson 30 min" (close enough) ✓
- Result:
  ```json
  {
    "serviceNameRaw": "Lesson 30min",
    "serviceId": "d1d5a13b-8306-4c3c-b36f-493a02ba1378",
    "totalCredits": 5
  }
  ```

**Scenario 3: No Match Found**
- CSV provides: `serviceName = "Private Coaching"`
- Fuzzy match → no confident match in SKB ✗
- Action: **FLAG TO USER** (don't silently skip it)
  - "Could not match 'Private Coaching' to any known service. Should I keep it as-is?"
- Result (if user confirms):
  ```json
  {
    "serviceNameRaw": "Private Coaching",
    "serviceId": "",
    "totalCredits": 0
  }
  ```

**Decision Rule for Matching:**
- If match confidence > 80% (e.g., "30-Min Lesson" ↔ "Single Lesson 30 min") → link it
- If confidence 50-80% (e.g., "Lesson" ↔ "Single Lesson 30 min") → ASK user to confirm
- If confidence < 50% → keep as free text, flag to user

## Row → JSON validation & default rules

Apply these to every mapped package record, in order:

### Identity fields
- `id`: always auto-generate a new GUID (never take this from the CSV)
- `packageId`: use the CSV `id`/`packageId` column value; if missing/empty → generate a new GUID

### Pricing
- `price`: must be numeric ≥ 0. Strip currency symbols ($, £, €) before parsing. If missing,
  empty, or non-numeric → **flag as a gap** (price is one of the four mandatory fields — do
  not silently default it to 0)
- `priceSource`: always `"FromSourceFile"`

### Expiry (mandatory, new field)
- `expiryDuration`: how long the package stays valid before it expires (e.g. "30 Days",
  "6 Months", "1 Year"). If missing/empty → **flag as a gap**

### String fields with defaults
- `packageCategory`: missing/empty → default `"Default"`
- `businessName`: missing/empty → default `"Default"`
- `ownerType`: missing/empty → default `"Organization"`
- `packageName`: **required** — record is invalid without it (do not silently substitute
  "Unknown Package"; flag as a gap instead so the user can supply it)
- `description`: missing → `""`
- `packageCode`: missing → `""`
- `businessId`: missing → `""`
- `locationId`: missing → `""`
- `ownerName`: missing → `""`

### Boolean fields
- `isActive`: missing → default `true`
- `onlineBookingEnabled`: missing → default `true`
- `hasPackageSales`: missing → default `true`
- `hasServices`: missing → default `true`
- `hasServiceDiscount`: missing → default `true`
- `hasFreeProducts`: missing → default `false`
- `hasBundledProducts`: missing → default `false`
- `hasForms`: missing → default `false`
- `hasClasses`: missing → default `false`
- `hasWorkshops`: missing → default `false`
- `hasDayPackage`: missing → default `false`

### Timestamps (auto-generated, current UTC time)
- `createdAt`: Generate current UTC datetime in ISO 8601 format
  Format example: `"2026-07-22T23:43:00.143057+00:00"`
  (Use Python: `datetime.utcnow().isoformat() + "+00:00"` or equivalent)
- `updatedAt`: Same value as `createdAt` for new packages (both `packages` and `packageKnowledge`)

### Null fields (always null, do not collect from user)
- `taxGroup`: null (reserved for future tax configuration)
- `centerTaxId`: null (reserved for future tax configuration)
- `_etag`: null (Cosmos DB internal field; auto-managed)
- `_ts`: null (Cosmos DB internal field; auto-managed)

**Note:** These fields should never be populated from the CSV or user input. Always set to `null`.

### Benefits array (mandatory: must have at least 1 entry)
Default: `benefits` is `[]` unless benefits-related columns are present **and** have
non-empty values for that row.

1. No benefits columns in the CSV at all → `benefits: []`.
2. Benefits columns exist but are blank for a row → `benefits: []` for that row (flag as gap if mandatory).
3. At least one benefits value present for a row → build one entry per distinct service
   mentioned:
   ```json
   { "serviceNameRaw": "<name or \"\">", "serviceId": "<linked id or \"\">", "totalCredits": 0 }
   ```
   - `totalCredits` missing/non-numeric → default `0`
   - `serviceNameRaw`/`serviceId` missing but `totalCredits` present → still include the entry with empty strings for the missing parts
   - A package can have multiple services in the benefits array (one entry per service)

### Multiple Services Per Package

A package may include multiple distinct services:
```json
{
  "benefits": [
    { "serviceNameRaw": "Single Lesson 30 min", "serviceId": "d1d5a13b-...", "totalCredits": 10 },
    { "serviceNameRaw": "Group Session 1 hour", "serviceId": "e2e6b24c-...", "totalCredits": 2 }
  ]
}
```

However, each entry must have a distinct service. If the same service is listed multiple times 
with different credit counts, merge them into a single entry with the total.

**Important:** A package is only "complete" once `packageName`, `price`, `expiryDuration`, and at least one
entry in `benefits` are all present — these are the four mandatory fields called out in
Stage 1 of SKILL.md. Everything else missing gets a sensible default per the rules above
rather than blocking progress.
