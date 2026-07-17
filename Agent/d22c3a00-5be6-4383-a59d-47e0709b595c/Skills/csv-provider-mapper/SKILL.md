---
name: csv-provider-mapper
description: >  
  Parse an uploaded CSV file, intelligently map its columns to Provider JSON fields using  
  fuzzy/semantic matching, apply validation with sensible defaults, inject current UTC  
  timestamps, and return a JSON array of Provider objects ready for persistence.  
  Use this skill whenever a user uploads a CSV and wants it converted to Provider records,  
  regardless of how the CSV columns are named — e.g. 'packName', 'Title', 'emp_first',  
  'fname', 'contact_email', 'mobile', 'active_flag', etc. Also triggers for phrases like  
  'import CSV', 'map this CSV', 'convert CSV to Provider', 'process provider data from CSV'.
---

# CSV Provider Mapper

Convert any CSV file into a validated JSON array of Provider objects, no matter what the source columns are called.

## Target Provider Schema

Every output record must conform to this exact shape:

```json
{
  "businessId": "<string — from CSV if present, else empty string>",
  "providerId": "<string — from CSV if present, else empty string>",
  "providerCode": "<string — from CSV if present, else empty string>",
  "locationId": "<string — from CSV if present, else empty string>",
  "firstName": "<string — from CSV, else empty string>",
  "lastName": "<string — from CSV, else empty string>",
  "nickName": "<string — from CSV, else empty string>",
  "role": "<string — from CSV, else empty string>",
  "specialization": "<string or null — from CSV, else null>",
  "email": "<string or null — from CSV, else null>",
  "phone": "<string — from CSV, else empty string>",
  "isConsultant": "<boolean — from CSV, else false>",
  "onlineBookingEnabled": "<boolean — from CSV, else false>",
  "isActive": "<boolean — from CSV, else true>",
  "createdAt": "<current UTC ISO8601 datetime>",
  "updatedAt": "<current UTC ISO8601 datetime>",
  "_etag": null,
  "_ts": null
}
```

## Step 1 — Read the CSV

Read the full content of the uploaded CSV file. Parse every row including the header row. Identify all column names exactly as they appear.

## Step 2 — Intelligent Column Mapping

Map each CSV column to the nearest Provider field using semantic understanding. Column names in the wild are messy — match by meaning, not by exact string.

### Mapping Reference Table

| Provider Field | Likely CSV column names (non-exhaustive) |
|---|---|
| `businessId` | businessId, business_id, biz_id, org_id, organisation_id, company_id |
| `providerId` | providerId, provider_id, emp_id, employeeId, employee_id, staff_id, worker_id |
| `providerCode` | providerCode, provider_code, emp_code, employee_code, code, emplo_code, staff_code |
| `locationId` | locationId, location_id, loc_id, site_id, branch_id, office_id |
| `firstName` | firstName, first_name, fname, given_name, forename, first |
| `lastName` | lastName, last_name, lname, surname, family_name, last |
| `nickName` | nickName, nick_name, nickname, alias, preferred_name, display_name |
| `role` | role, job_role, position, job_title, title, designation, rank |
| `specialization` | specialization, specialisation, specialty, expertise, department, dept |
| `email` | email, email_address, e_mail, contact_email, work_email, mail |
| `phone` | phone, phone_number, mobile, cell, contact_number, telephone, tel |
| `isConsultant` | isConsultant, is_consultant, consultant, consulting, is_contractor |
| `onlineBookingEnabled` | onlineBookingEnabled, online_booking, booking_enabled, can_book_online |
| `isActive` | isActive, is_active, active, status, enabled, active_flag |

If a CSV column does not map to any Provider field, ignore it.
If multiple CSV columns could map to the same field, pick the closest match and note it.

## Step 3 — Value Transformation & Validation

Apply these rules to each value before writing it to the output:

### String fields (`firstName`, `lastName`, `nickName`, `role`, `providerCode`, `locationId`, `businessId`, `providerId`, `phone`)
- Trim leading/trailing whitespace.
- If the value is empty, null, or missing → use `""` (empty string).

### Nullable string fields (`specialization`, `email`)
- Trim whitespace.
- If empty, null, or missing → use `null`.
- For `email`: if a value is present, do a basic format check (must contain `@` and `.`). If invalid, set to `null` and note the issue.

### Boolean fields (`isConsultant`, `onlineBookingEnabled`, `isActive`)
- Accept: `true`, `false`, `1`, `0`, `yes`, `no`, `y`, `n`, `TRUE`, `FALSE` (case-insensitive).
- Map `true`/`1`/`yes`/`y` → `true`; `false`/`0`/`no`/`n` → `false`.
- If missing or unrecognisable:
  - `isConsultant` → `false`
  - `onlineBookingEnabled` → `false`
  - `isActive` → `true`

### `id` field
- Always generate a new UUID v4. Never read from CSV.

### `createdAt` and `updatedAt`
- Always set to the **current UTC datetime** in ISO 8601 format, e.g. `"2026-07-13T11:25:00Z"`.
- Never use a value from the CSV for these fields — always generate fresh.

### `_etag` and `_ts`
- Always set to `null`. Never read from CSV.

## Step 4 — Build Output Array

For every data row in the CSV (excluding the header), produce one Provider object following the schema above with all mappings and transformations applied.

Return the complete JSON array.

## Step 5 — Mapping Summary

After generating the JSON, produce a concise mapping summary in this format:

```
📋 Column Mapping Summary
──────────────────────────────────────────
CSV Column          → Provider Field
──────────────────────────────────────────
fname               → firstName
lname               → lastName
contact_email       → email
mobile              → phone
active_flag         → isActive
... (all mapped columns)
──────────────────────────────────────────
Ignored columns: col_x, col_y
Records processed: 42
Validation warnings: email invalid for row 7 (set to null)
```

## Edge Cases

| Situation | Behaviour |
|---|---|
| CSV has no header row | Treat first row as data, use positional labels (col_1, col_2…), map by position if possible, warn user |
| CSV is empty | Return `[]` and inform the user |
| A row has fewer columns than the header | Fill missing columns with defaults |
| A row has more columns than the header | Ignore extra columns |
| Duplicate column names in CSV | Use the first occurrence |
| Non-UTF-8 encoding | Process what can be decoded, warn about any rows skipped |

## Output Format

Return:
1. The mapping summary (as above)
2. The full JSON array of Provider objects

Do not add any commentary between the mapping summary and the JSON — the agent will immediately use the JSON array to call Cosmos DB.
