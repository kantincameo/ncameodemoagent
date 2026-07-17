---
name: partoplay-services-importer
description: >-
  Parses an uploaded Partoplay Services CSV file, maps every row to the target Services JSON schema,
  and saves each record individually to Cosmos DB using cosmos_create_document. Use this skill
  whenever a user uploads a CSV with service data for Partoplay, mentions importing services,
  mapping service records, or saving services to Cosmos DB with partitionKey 'Services'.
---

# Partoplay Services Importer

You are processing a Partoplay Services CSV upload. Follow every step below in strict order. Do not skip any step.

## Step 1 — Parse the CSV

Read the uploaded CSV file in full. The expected headers are:

```
ServiceCode, ServiceName, Category, Sub Category, BusinessUnitName, ServiceType, OnlineBooking, TaxIncluded, TaxGroup, ServiceLength
```

Parse every row into a structured list. Ignore the `BusinessUnitName` column — it is not mapped to the target JSON.

---

## Step 2 — Map Each Row to the Target JSON Schema

For **every** row, produce a complete JSON document using these rules:

| Target Field             | Source Column   | Rule                                                                                      |
|--------------------------|-----------------|-------------------------------------------------------------------------------------------|
| `id`                     | Auto-generated  | Generate a new UUID v4 (e.g. `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`)                  |
| `partitionKey`           | Fixed           | Always `"Services"`                                                                       |
| `businessId`             | Not in CSV      | Always `""` (empty string)                                                                |
| `serviceId`              | Same as `id`    | Copy the same generated UUID used for `id`                                                |
| `serviceCode`            | `ServiceCode`   | Direct copy                                                                               |
| `serviceName`            | `ServiceName`   | Direct copy                                                                               |
| `serviceKind`            | `ServiceType`   | Direct copy                                                                               |
| `serviceCategory`        | `Category`      | Direct copy                                                                               |
| `serviceSubCategory`     | `Sub Category`  | Direct copy                                                                               |
| `isAddOn`                | Not in CSV      | Always `false`                                                                            |
| `durationMinutes`        | `ServiceLength` | Parse as integer. If empty → `0`                                                          |
| `price`                  | Not in CSV      | Always `0`                                                                                |
| `priceSource`            | Not in CSV      | Always `""`                                                                               |
| `taxIncluded`            | `TaxIncluded`   | If empty/missing/blank → `null`. If `"true"`/`"1"`/`"yes"` → `true`. Else → `false`     |
| `taxGroup`               | `TaxGroup`      | If empty/missing/blank → `null`. Else direct copy as string                               |
| `onlineBookingEnabled`   | `OnlineBooking` | Parse boolean: `"true"`/`"1"`/`"yes"` → `true`. All else → `false`                       |
| `requiresResource`       | Not in CSV      | Always `""`                                                                               |
| `requiresProvider`       | Not in CSV      | Always `""`                                                                               |
| `resourceTypeRequired`   | Not in CSV      | Always `""`                                                                               |
| `providerTypeRequired`   | Not in CSV      | Always `""`                                                                               |
| `isActive`               | Not in CSV      | Always `true`                                                                             |
| `createdAt`              | Auto-generated  | Current UTC timestamp in ISO 8601 format (e.g. `"2026-07-13T11:30:00Z"`)                 |
| `updatedAt`              | Auto-generated  | Same value as `createdAt`                                                                 |
| `_etag`                  | Not in CSV      | Always `null`                                                                             |
| `_ts`                    | Not in CSV      | Always `null`                                                                             |

### Example output for one row:

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "partitionKey": "Services",
  "businessId": "",
  "serviceId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "serviceCode": "1hrdon",
  "serviceName": "Bay rental 1 hour",
  "serviceKind": "SlotBooking",
  "serviceCategory": "Bay Rental",
  "serviceSubCategory": "Rental",
  "isAddOn": false,
  "durationMinutes": 60,
  "price": 0,
  "priceSource": "",
  "taxIncluded": null,
  "taxGroup": null,
  "onlineBookingEnabled": true,
  "requiresResource": "",
  "requiresProvider": "",
  "resourceTypeRequired": "",
  "providerTypeRequired": "",
  "isActive": true,
  "createdAt": "2026-07-13T11:30:00Z",
  "updatedAt": "2026-07-13T11:30:00Z",
  "_etag": null,
  "_ts": null
}
```

---

## Step 3 — Validate Before Saving

Before saving, verify each record:
- `id` is a non-empty UUID
- `partitionKey` is exactly `"Services"`
- `serviceCode` is non-empty
- `serviceName` is non-empty

If a record fails validation, log it as failed and skip saving it. Continue processing remaining rows.

---

## Step 4 — Save Each Record to Cosmos DB ⚠️ CRITICAL — DO NOT SKIP

For **every** validated record, invoke the tool `cosmos_create_document` with:
- `partitionKey` → `"Services"`
- Document body → the complete record JSON (pure JSON only — no markdown, no code block wrapping)

**Rules:**
- Process ALL rows. Do not stop after the first record.
- Do not batch — each row must be a separate `cosmos_create_document` call.
- If a save fails, record the error (serviceCode + error message) and continue to the next row.

---

## Step 5 — Report Results

After all records have been processed, provide a summary:

- ✅ **Total records successfully saved** (count)
- ❌ **Failed records** (list each with `serviceCode` and error reason)
- 📋 **Summary table** showing `serviceCode`, `serviceName`, and `status` for every row
