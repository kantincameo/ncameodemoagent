---
name: partoplay-services-importer
description: >-
  Parses an uploaded Partoplay Services CSV file and maps every row to the target Services JSON schema.
  Returns a validated JSON array of mapped records ready for saving. Use this skill whenever a user
  uploads a CSV with service data for Partoplay, mentions importing services, mapping service records,
  or preparing services data for Cosmos DB with partitionKey 'Services'.
---

# Partoplay Services Importer

You are processing a Partoplay Services CSV upload. Follow every step below in strict order. Do not skip any step.

## Step 1 — Parse the CSV

Read the uploaded CSV file in full. Extract the raw header row exactly as it appears — do not assume headers match any specific naming convention.

Parse every row into a structured list keyed by the raw column headers.

---

## Step 1.5 — Intelligent Column Mapping

The uploaded CSV may use any column naming convention. Before mapping rows to the target schema, resolve each raw CSV header to its target field using the alias table below. Matching is **case-insensitive** and **whitespace-insensitive**.

| Target Field | Accepted CSV Column Names (aliases) |
|---|---|
| `serviceId` | ServiceId, Service Id, SvcId, Id |
| `serviceCode` | ServiceCode, Service Code, Code, Svc Code, SvcCode |
| `serviceName` | ServiceName, Service Name, Name, Svc Name, SvcName, Service Title, Title |
| `serviceCategory` | Category, ServiceCategory, Service Category, Cat, Svc Category |
| `serviceSubCategory` | Sub Category, SubCategory, Sub-Category, ServiceSubCategory, Sub Cat, SubCat |
| `businessUnitName` | BusinessUnitName, Business Unit, Business Unit Name, BU Name, BUName *(ignored — not mapped to schema)* |
| `serviceKind` | ServiceType, Service Type, Type, Kind, ServiceKind, Svc Type |
| `onlineBookingEnabled` | OnlineBooking, Online Booking, Online Book, Booking, IsOnline, OnlineEnabled |
| `taxIncluded` | TaxIncluded, Tax Included, Tax Inc, IncludesTax, IsTaxIncluded |
| `taxGroup` | TaxGroup, Tax Group, Tax Grp, TaxGrp, TaxCategory |
| `durationMinutes` | ServiceLength, Service Length, Duration, DurationMinutes, Minutes, ServiceTime, Length, Time, Mins |

**Mapping rules:**
1. For each raw CSV header, find the best match in the alias table (case-insensitive, ignore extra spaces).
2. If a header matches an alias, map all values in that column to the corresponding target field.
3. If a header has **no match** in the alias table, ignore that column entirely.
4. If a target field has **no matching column** in the CSV, apply its default value as defined in Step 2.
5. If two or more CSV columns resolve to the same target field, use the first one encountered and ignore the rest.
6. Before proceeding to Step 2, log the resolved mapping as: `CSV column "<raw>" → target field "<target>"` for every matched column.

---

## Step 2 — Map Each Row to the Target JSON Schema

Using the resolved column mapping from Step 1.5, produce a complete JSON document for **every** row:

| Target Field | Source | Rule |
|---|---|---|
| `id` | Auto-generated | Generate a new UUID v4 |
| `businessId` | Not in CSV | Always `""` (empty string) |
| `serviceId` | Mapped column | Direct copy from CSV; may be empty or null |
| `serviceCode` | Mapped column | Direct copy; may be empty or null |
| `serviceName` | Mapped column | Direct copy |
| `serviceKind` | Mapped column | Direct copy; may be blank or null |
| `serviceCategory` | Mapped column | Direct copy; may be blank or null |
| `serviceSubCategory` | Mapped column | Direct copy; may be blank or null |
| `isAddOn` | Not in CSV | Always `false` |
| `durationMinutes` | Mapped column | Parse as integer. If empty or missing → `0` |
| `price` | Not in CSV | Always `0` |
| `taxIncluded` | Mapped column | If empty/missing/blank → `null`. If `"true"`/`"1"`/`"yes"` → `true`. Else → `false` |
| `taxGroup` | Mapped column | If empty/missing/blank → `null`. Else direct copy as string |
| `onlineBookingEnabled` | Mapped column | `"true"`/`"1"`/`"yes"` → `true`; empty/missing → `true` (default); else → `false` |
| `requiresResource` | Not in CSV | Always `null` |
| `requiresProvider` | Not in CSV | Always `null` |
| `resourceType` | Not in CSV | Always `null` |
| `providerType` | Not in CSV | Always `null` |
| `isActive` | Not in CSV | Always `true` |
| `createdAt` | Auto-generated | Current UTC timestamp in ISO 8601 format |
| `updatedAt` | Auto-generated | Same value as `createdAt` |
| `_etag` | Not in CSV | Always `null` |
| `_ts` | Not in CSV | Always `null` |

---

## Step 3 — Validate & Return JSON Output

Validate each mapped record:
- `id` is a non-empty UUID
- `serviceName` is non-empty

If a record fails validation, log it as failed and exclude it from the output. Continue processing remaining rows.

**Return** the final validated records as a JSON array to the agent. Do not save or call any tools. The agent will handle saving each record to Cosmos DB.
