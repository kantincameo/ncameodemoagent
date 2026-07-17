# doc-data-extractor

A Claude Skill that extracts structured data from **any** uploaded document
(PDF, image, Word, Excel, CSV, TXT, etc.) and returns it as **pure JSON**
matching a fixed schema — no explanations, no markdown fences, no extra text.

## Folder Structure

```
doc-data-extractor/
├── SKILL.md                      # Main skill instructions (required, read first)
├── README.md                     # This file
├── scripts/
│   ├── detect_filetype.py        # Routes a file to the right reading strategy
│   ├── fetch_source.py           # Downloads a URL (Drive/Dropbox/OneDrive link rewriting)
│   ├── validate_output.py        # Validates final JSON against the schema
│   └── read_spreadsheet.py       # Helper to dump CSV/XLSX rows as JSON
├── references/
│   ├── source_resolution.md      # Handling uploads, URLs (incl. Drive/Dropbox), paths, base64
│   ├── extraction_rules.md       # Label-mapping rules & multi-record heuristics
│   └── examples.md               # Sample input → output pairs
└── assets/                        # (reserved for future templates/samples)
```

## How It Works (high level)

1. Claude reads `SKILL.md` when this skill triggers.
2. It resolves the source — an **uploaded file**, a **URL** (direct file
   link, webpage, or Google Drive/Dropbox/OneDrive share link), a **file
   path**, or **base64** data — per `references/source_resolution.md`,
   fetching/downloading/decoding as needed to get real local content.
3. It runs `scripts/detect_filetype.py` (optional) to decide the read
   strategy for that resolved file.
4. It reads the actual content using the right tool for the file type
   (pdf/docx/xlsx skills, or native vision for images).
5. It extracts the 23 fixed customer-record fields (businessId, customerId,
   firstName, lastName, email, phone, dob, etc.) per the rules in
   `references/extraction_rules.md`.
6. It builds the output — **one plain JSON object** for a single record,
   or **multiple standalone JSON objects separated by commas** (no `[ ]`
   array wrapper) for multiple records — and optionally checks it with
   `scripts/validate_output.py`.
7. It responds with **only** that JSON content. Nothing else.

## Current Output Schema

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

**Multiple records** are returned like this — comma-separated, **not** a
JSON array:
```
{ "businessId": "", ... }, { "businessId": "", ... }, { "businessId": "", ... }
```

This is the confirmed schema. To change it again:

1. Edit the "Output Schema" section and field-types table in `SKILL.md`.
2. Update `FIELD_TYPES` in `scripts/validate_output.py` to match.
3. Update the field-mapping table in `references/extraction_rules.md`.

## Running the Helper Scripts Standalone

```bash
# Figure out how to read a file
python3 scripts/detect_filetype.py /path/to/file.pdf

# Dump a spreadsheet's rows as JSON (requires pandas, openpyxl)
pip install pandas openpyxl --break-system-packages
python3 scripts/read_spreadsheet.py /path/to/contacts.xlsx

# Validate output text against the schema (accepts single object,
# comma-separated objects, or an array — flags array-wrapping as an error)
python3 scripts/validate_output.py '{"businessId":"","customerId":"C1","externalCustomerId":"","firstName":"A","lastName":"B","email":"a@x.com","phone":"","dob":"","gender":"","address":"","primaryLocationId":"","joinedDate":"","lastVisitDate":"","totalVisits":0,"totalSpend":0,"lifetimeValue":0,"activeMembershipId":"","activeMembershipTier":"","activePackageIds":[],"tags":[],"preferredContactMethod":"","marketingOptInEmail":false,"marketingOptInSms":false,"customAttributes":{}}'
```

## Installing

Import the `.skill` file (or this unzipped folder) into your Claude
environment/skills directory. Once installed, upload any document and
ask Claude to "extract the data from this file" — the skill will trigger
automatically based on its description in `SKILL.md`.
