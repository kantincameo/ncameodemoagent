---
name: document-lake-scanning
description: Store every client document in Azure Data Lake by client and year, and run the AI scanner on every upload — classify, extract fields with confidence, check readability, match the checklist and compare with the past three years. Use for any upload ("I uploaded my W-2"), a rescan ("re-extract this 1099-B"), or questions about where a file is kept.
---

# Document lake and scanning

**Screens:** C2 Documents (client), O3 Workbench and O7 Scan & trend (office).
**Tools:** `document_ingest` (1), `document_scan` (1), `storage_manifest` (0).

## Where things live
One path, everywhere — Azure Data Lake Storage Gen2, filesystem `taxpilot`:

```
clients/{household_id}/{tax_year}/{document_id}/original.<ext>    the upload, as received
clients/{household_id}/{tax_year}/{document_id}/extraction.json   scanner output, identifiers masked
clients/{household_id}/{tax_year}/{document_id}/manifest.json     hash, size, mime, uploader, version
```

The path *is* the client and the year, so "everything we hold for the Patels", retention and legal holds are directory operations. A prior-year return a new client brings in is stored under *its* year, not this year's folder. Agents never hold storage credentials; only the ops server does.

## Every upload, the same pipeline
`document_ingest(return_id, filename, mime, content_base64 | source_path)` does all of this in one call:
1. **Scan** — the AI scanner reads the file and returns the document type, issuer, owner, tax year, readability, each field with its box and confidence, and any identifiers. Identifiers are masked *inside the scanner* and hashed to a vault reference; the raw value is never written.
2. **Match** — if the checklist expects this type from this issuer, the upload fills that slot (same document id); otherwise a new document is added.
3. **Store** — original, extraction and manifest go to the lake; the document row gets the URI, hash and version.
4. **Quality** — unreadable → status `retake` with the specific reason, and a retake request to the client. Readable → `received` and a receipt.
5. **Trend** — the key figure is compared with the same document from the two prior years; the result comes back with the upload (`trend.series`, `trend.flags`).

`document_scan(document_id)` reruns steps 1, 4 and 5 on a stored file (new scanner version, disputed field). Fields already written to the draft are kept; unwritten ones are replaced.

## Reading the result
- Report the classification and the match in one line: "Scanned as 1099-DIV from Fidelity, 2025 — fills the item we were waiting for."
- Call out quality problems with the exact fix the scanner named.
- Mention a trend flag only if it changes what someone should do ("36% higher than last year — worth a look" or "new this year").
- Never repeat a raw identifier. The scanner returns masked values; if you ever see a full one, stop and report it (rule P-2).

## Scanner configuration
`TAXPILOT_SCANNER=claude` (production: Claude reads PDFs and images with a fixed JSON schema) or `fixture` (development: JSON already in the output shape). `TAXPILOT_STORE=adls` or `local` (same layout on disk).
