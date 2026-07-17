---
name: csv-provider-mapper
description: >-
  Reads an uploaded CSV file, intelligently maps its columns to a Provider target JSON
  structure, applies validation and defaults, and returns a fully formed Provider JSON
  object ready for persistence. Use this skill whenever the user uploads or references a
  CSV and wants it converted to Provider JSON, mapped to provider fields, transformed into
  the target provider structure, or says things like "map this CSV", "convert CSV to
  provider", "process this staff file", "import providers from CSV", or "generate provider
  JSON from this file". Always invoke this skill before any Cosmos DB save operation.
---

# CSV Provider Mapper Skill

Parse an uploaded CSV, intelligently map every column to the Provider target schema,
apply field-level validation and defaults, and return a list of fully formed Provider
JSON objects.

---

## Step 1 — Parse the CSV

- Read the uploaded CSV file exactly as provided. Do not ask the user to paste data.
- Identify the header row and all data rows.
- Treat the first row as column headers.
- Handle common variants: comma-separated, semicolon-separated. Auto-detect the delimiter.
- Strip whitespace from all header names and values.

---

## Step 2 — Intelligent Column Mapping

For every column in the CSV, find the best matching field in the Provider schema below.
Matching is **semantic and fuzzy** — do not require exact name matches.

### Provider Schema Fields & Aliases

| Target Field | Accepted CSV Column Aliases (examples, not exhaustive) |
|---|---|
| `firstName` | first_name, fname, given_name, forename, first |
| `lastName` | last_name, lname, surname, family_name, last |
| `nickName` | nick, nickname, preferred_name, alias |
| `role` | role, position, job_title, title, type, designation |
| `specialization` | specialization, specialty, expertise, department, area |
| `email` | email, email_address, e-mail, mail, contact_email |
| `phone` | phone, phone_number, mobile, cell, contact_phone, telephone |
| `providerCode` | provider_code, emp_id, employee_id, staff_id, code, employee_code, empCode |
| `locationId` | location_id, location, loc_id, site_id, branch_id |
| `businessId` | business_id, biz_id, company_id, org_id |
| `providerId` | provider_id, pid, staff_uid |
| `isConsultant` | is_consultant, consultant, is_freelance, freelance |
| `onlineBookingEnabled` | online_booking, booking_enabled, online_booking_enabled, bookable |
| `isActive` | is_active, active, status, enabled |

Mapping rules:
- Use **case-insensitive**, **underscore/space/camelCase-tolerant** comparison.
- If a column name contains the target keyword (e.g. "Package Name" contains "name"), consider it a candidate.
- When multiple columns could match one field, pick the closest match and note it.
- Columns with no mapping are silently ignored (do not error).
- Log the final mapping as a brief note before the output (e.g. "Mapped: CSV 'emp_code' → providerCode").

---

## Step 3 — Apply Validation & Defaults

For each row, build a Provider object applying these rules in order:

### ID Fields
- `id`: Generate a new UUID v4 (random GUID) for every row.
- `providerId`: Use CSV value if present; otherwise generate a new UUID v4.
- `businessId`: Use CSV value if present; otherwise use empty string `""`.
- `locationId`: Use CSV value if present; otherwise use empty string `""`.
- `providerCode`: Use CSV value if present; otherwise use empty string `""`.

### Name Fields
- `firstName`: Use CSV value; default to `""` if missing.
- `lastName`: Use CSV value; default to `""` if missing.
- `nickName`: Use CSV value; default to `""` if missing.

### Role & Contact
- `role`: Use CSV value (uppercase it); default to `"PROVIDER"` if missing.
- `specialization`: Use CSV value; default to `null` if missing.
- `email`: Use CSV value; default to `null` if missing.
- `phone`: Use CSV value; default to `""` if missing.

### Boolean Fields
- `isConsultant`: Parse truthy strings ("true", "yes", "1", "y") → `true`; everything else or missing → `false`.
- `onlineBookingEnabled`: Same parsing as above; default `false`.
- `isActive`: Same parsing; default `true` (providers are active by default).

### Timestamps
- `createdAt`: Set to the **current UTC datetime** in ISO 8601 format with timezone offset.
- `updatedAt`: Set to the **same value** as `createdAt`.

### Nullable / System Fields
- `_etag`: Always `null`.
- `_ts`: Always `null`.

---

## Step 4 — Output Format

Produce a **JSON array** of Provider objects. Each object must exactly match this structure:

```json
{
  "id": "<generated-uuid>",
  "businessId": "<from CSV or empty string>",
  "providerId": "<from CSV or generated-uuid>",
  "providerCode": "<from CSV or empty string>",
  "locationId": "<from CSV or empty string>",
  "firstName": "<value>",
  "lastName": "<value>",
  "nickName": "<value or empty string>",
  "role": "<UPPERCASED value or PROVIDER>",
  "specialization": "<value or null>",
  "email": "<value or null>",
  "phone": "<value or empty string>",
  "isConsultant": false,
  "onlineBookingEnabled": false,
  "isActive": true,
  "createdAt": "<current UTC ISO8601>",
  "updatedAt": "<current UTC ISO8601>",
  "_etag": null,
  "_ts": null
}
```

Return **only** the JSON array — no extra prose after the array. Precede the array with a one-paragraph summary of:
- How many rows were processed
- The column mapping applied
- Any fields that used defaults because they were absent from the CSV
