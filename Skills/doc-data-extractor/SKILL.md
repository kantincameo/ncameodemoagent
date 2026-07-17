---
name: doc-data-extractor
description: Extract structured data from ANY document — uploaded file, URL/link (document or webpage, incl. Google Drive/Dropbox/OneDrive), file path, or base64 data — and return pure JSON matching a fixed customer-record schema (businessId, customerId, firstName, lastName, email, phone, etc.). Use whenever the user uploads a file, pastes a link, gives a path, or provides base64 and asks to "extract data", "convert to json", "get customer info from this", or similar, for any document type (PDF, image, Word, Excel, CSV, TXT, webpage) and any source. Must fetch/read the real referenced content — never fabricate. Output is ALWAYS raw JSON only, no explanations or code fences. Multiple records → individual JSON objects separated by commas, not wrapped in an array. Trigger even on a bare link or path with no other explanation.
---

# Document Data Extractor

Extracts a fixed set of fields from any uploaded document and returns **only** raw JSON — nothing else.

## Output Schema (FIXED)

Every extraction must produce object(s) with exactly these keys, in this order, with these exact JSON types:

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

### Field types — respect these exactly

| Field | Type | Empty/missing value |
|---|---|---|
| businessId, customerId, externalCustomerId | string | `""` |
| firstName, lastName, email, phone | string | `""` |
| dob, joinedDate, lastVisitDate | string (date, keep as found in source; ISO `YYYY-MM-DD` if the source is unambiguous, otherwise as-written) | `""` |
| gender | string | `""` |
| address | string | `""` |
| primaryLocationId | string | `""` |
| totalVisits | number (integer) | `0` |
| totalSpend, lifetimeValue | number (can be decimal) | `0` |
| activeMembershipId, activeMembershipTier | string | `""` |
| activePackageIds | array of strings | `[]` |
| tags | array of strings | `[]` |
| preferredContactMethod | string | `""` |
| marketingOptInEmail, marketingOptInSms | boolean | `false` |
| customAttributes | object (free-form key-value) | `{}` |

- Keep this exact key order and exact key names every time.
- If a field cannot be found in the document, use the "Empty/missing value" from the table above for that field's type — **never** use `null`, and never omit the key.
- Do not invent, guess, or hallucinate values. Only fill a field if the document actually contains that information (directly or very clearly implied by a labeled field).
- **firstName / lastName**: if the document only has one combined "Name" field, split it into first and last name as best as possible (first word(s) → firstName, last word → lastName). If it truly can't be split (single-word name, company name, etc.), put the whole value in `firstName` and leave `lastName` as `""`.
- **customAttributes**: only populate this with data that clearly doesn't map to any other field but is still clearly structured key-value info in the source (e.g. "Referral Source: Instagram"). If nothing like that exists, leave it as `{}` — don't force unrelated text into it.

## Output Format — Single vs Multiple Records

- **Single record** (one person found in the document): output exactly **one** JSON object. Nothing else.
- **Multiple records** (document has more than one person — a list, table, or multiple entries): output each record as its **own individual JSON object**, separated by a comma, **one after another** — like this:

  ```
  { "businessId": "", "customerId": "", ... }, { "businessId": "", "customerId": "", ... }, { "businessId": "", "customerId": "", ... }
  ```

  **Do NOT wrap them in `[` and `]` square brackets.** This is not a JSON array — it is a sequence of standalone JSON objects separated by commas. Each `{ ... }` is complete and independent.
- Whether formatting each object compact (one line) or pretty-printed (multi-line, indented) is fine either way — just keep the comma between consecutive objects and never add the outer `[`/`]` brackets.

## Workflow

1. **Resolve the source.** The document can arrive in any of these forms — figure out which one applies, in this priority order:
   - **Uploaded file present in this conversation** → use the real path under `/mnt/user-data/uploads/` (list the directory if unsure of the exact name). This is the most common case — treat any file the user attached as this.
   - **URL / link given** (e.g. a direct file link ending in `.pdf`/`.docx`/`.xlsx`/`.csv`/image extension, a Google Drive/Dropbox share link, or a plain webpage URL) → use `web_fetch` to retrieve it.
     - If it's a **direct file link**, fetch it and treat the retrieved bytes/content exactly like an uploaded file of that type (download it locally first if it needs a format-specific tool like the `pdf`/`docx`/`xlsx` skills — see `references/source_resolution.md` for the download-then-read pattern).
     - If it's a **webpage** (not a raw file), fetch the page and extract the fields directly from its rendered text/HTML content — no separate file-type step needed.
     - Google Drive/Dropbox/OneDrive share links: convert to a direct-download form first if possible (see `references/source_resolution.md`), then fetch. `scripts/fetch_source.py <url>` automates this rewrite + download when network access is available (it needs internet access — if the sandbox has none, use the `web_fetch` tool instead).
   - **File path given** (e.g. `/mnt/...`, `C:\...`, or any absolute/relative path the user typed) → use that path directly with `view`/`bash`/read tools. Verify it exists before reading; if it doesn't, say so plainly instead of guessing.
   - **Base64 data given** (pasted inline or in a variable) → decode it to a temporary file (matching the stated/inferred file type) before reading, using the same type-specific reading strategy below.
   - **Nothing usable found** (no upload, no URL, no path, no base64) → do not fabricate output. Tell the user plainly (in normal chat, not JSON) that no document/source was found and ask them to upload a file, or paste a URL/path.
   - Full step-by-step handling for each source type (including the Google Drive conversion trick and the download-then-read pattern for URLs) is in `references/source_resolution.md` — consult it whenever the source isn't a plain local upload.
2. **Detect the file type.** Optionally run `scripts/detect_filetype.py <path>` to get a suggested reading strategy, or just infer from the extension/content-type.
3. **Read the file based on type** — consult the relevant skill/tool for reading, don't guess blindly:
   - PDF → use the `pdf` or `pdf-reading` skill/tools to extract text (handles both text PDFs and scanned/OCR cases).
   - Word (.docx) → use the `docx` skill to read content.
   - Excel/CSV (.xlsx, .csv, .tsv) → use the `xlsx` skill, or run `scripts/read_spreadsheet.py <path>` to dump rows as JSON for easy scanning.
   - Image (.jpg, .png, etc., including photos of documents/business cards) → view the image directly and read the text visually (vision), since Claude can read images natively.
   - Plain text (.txt, .md, etc.) → read directly.
   - Any other/unknown type → use the `file-reading` skill as a router to figure out the right approach.
4. **Extract the fields.** Scan the full content for all 23 schema fields (or clearly equivalent labels — e.g. "Full Name" splits into firstName/lastName, "Mobile" → phone, "Date of Birth" → dob). See `references/extraction_rules.md` for the full label-mapping table, type-conversion rules, and multi-record detection heuristics — read this file whenever the document's labels aren't an exact match to the schema keys, or when unsure how to convert a value to the required type (number/boolean/array/object).
5. **Build the output.** Construct the JSON object(s) exactly matching the schema and types above. One record → single object. Multiple records → individual objects separated by commas, no `[`/`]` array wrapper (see "Output Format" above). See `references/examples.md` for worked input → output examples.
6. **(Optional) Validate.** Run `scripts/validate_output.py '<your-json>'` to double-check the JSON has exactly the right keys, order, and string types before responding.
7. **Output ONLY the JSON.** Your entire response must be the raw JSON — no ```json code fences, no leading/trailing text, no "Here is the extracted data:", no notes about missing fields. Just the JSON value itself, valid and parseable.

## Critical Rules

- **Always work from the actual fetched/read content of the real source the user gave** — the specific uploaded file, the specific URL, the specific path, or the decoded base64. Never answer from assumption, memory of a similar document, or a guess about what the file probably contains.
- If a URL fails to fetch, a path doesn't exist, or base64 fails to decode, **say so plainly in normal chat** — do not invent plausible-looking JSON to fill the gap.
- **Never** wrap the output in markdown code fences (no ` ```json ... ``` `).
- **Never** add a preamble or postamble sentence — the JSON is the entire response.
- **Never** use `null` for missing fields — use the type-appropriate empty value from the field-types table (`""`, `0`, `false`, `[]`, or `{}`).
- **Never** skip a key even if empty.
- **Never** put a number as a string or a string as a number — respect the exact type per field (e.g. `totalVisits` must be `5` not `"5"`; `marketingOptInEmail` must be `true`/`false` not `"true"`/`"yes"`).
- **Multiple records → comma-separated individual objects, NOT a `[...]` array.** Single record → one plain object.
- If literally no relevant data exists anywhere in the document, return one object with all fields at their type-appropriate empty value.

## Updating the Schema

The current schema (23 customer fields: businessId, customerId, externalCustomerId, firstName, lastName, email, phone, dob, gender, address, primaryLocationId, joinedDate, lastVisitDate, totalVisits, totalSpend, lifetimeValue, activeMembershipId, activeMembershipTier, activePackageIds, tags, preferredContactMethod, marketingOptInEmail, marketingOptInSms, customAttributes) is the confirmed schema as of the last update. If the user changes it again, update:
1. The "Output Schema" section and field-types table above with the real field names/types.
2. `REQUIRED_FIELDS` / `FIELD_TYPES` in `scripts/validate_output.py`.
3. The field-mapping table in `references/extraction_rules.md`.

## Bundled Resources

```
doc-data-extractor/
├── SKILL.md                      # this file
├── README.md                     # human-readable overview
├── scripts/
│   ├── detect_filetype.py        # routes a file to the right reading strategy
│   ├── fetch_source.py           # downloads a URL (incl. Drive/Dropbox/OneDrive rewrite)
│   ├── validate_output.py        # validates final JSON against the schema
│   └── read_spreadsheet.py       # dumps CSV/XLSX rows as JSON for scanning
├── references/
│   ├── source_resolution.md      # handling uploads, URLs, paths, base64, Drive links
│   ├── extraction_rules.md       # label-mapping table + multi-record heuristics
│   └── examples.md               # worked input -> output examples
└── assets/                        # reserved for future templates/samples
```

Read `references/source_resolution.md`, `references/extraction_rules.md`, and `references/examples.md` whenever you need more detail than what's in this file — they are not auto-loaded, so consult them explicitly during extraction.
