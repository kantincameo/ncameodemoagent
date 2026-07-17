# Source Resolution Reference

The document to extract from can arrive in **four** different forms. This
file explains exactly how to resolve each one to actual, real content
before extracting anything. The core rule: **always read the real file/
page the user pointed to — never guess or fabricate based on the filename
or URL alone.**

---

## 1. Uploaded File (most common)

If the user attached/uploaded a file in the conversation, its real path
is under `/mnt/user-data/uploads/`.

```bash
ls -la /mnt/user-data/uploads/
```

Use the exact filename found there. Do not assume a name — list the
directory first if there's any doubt, especially if multiple files were
uploaded (in which case, ask the user which one, or process all of them
if the request implies "all files").

Then read it per its type (see "Type-Specific Reading" below).

---

## 2. URL / Link

Two sub-cases:

### 2a. Direct file link
A URL that points straight at a file — ends in `.pdf`, `.docx`, `.xlsx`,
`.csv`, `.jpg`, `.png`, etc., or is otherwise clearly a raw file
(e.g. an S3/CDN link, an attachment link from an email system).

**Pattern: fetch → save locally → read with the type-specific tool.**

```python
# Example for a PDF link
import urllib.request
urllib.request.urlretrieve(
    "https://example.com/report.pdf",
    "/tmp/downloaded_source.pdf"
)
```
Or use the `web_fetch` tool directly if it can return the file content;
for binary formats (pdf/docx/xlsx/images) that need a dedicated skill to
parse (tables, styling, OCR, etc.), download to a local temp path first
so the `pdf`/`docx`/`xlsx` skill tools can operate on it as a normal file.

### 2b. Webpage (not a raw file)
A normal URL that renders an HTML page containing the info (e.g. a
profile page, a contact page, an online form response, a Google Doc
"view" link converted to something readable).

Use `web_fetch` on the URL, then extract fields directly from the
returned text/HTML — no need to download or run it through a
format-specific skill.

### 2c. Cloud storage share links (Google Drive, Dropbox, OneDrive)
These share-page URLs are usually **not** directly downloadable as-is.
Convert them to a direct-download form first:

- **Google Drive**: a share link like
  `https://drive.google.com/file/d/FILE_ID/view?usp=sharing`
  becomes a direct-download link:
  `https://drive.google.com/uc?export=download&id=FILE_ID`
  Extract `FILE_ID` from the original URL, build the direct link, then
  fetch/download that instead.
- **Dropbox**: a share link ending in `?dl=0` becomes downloadable by
  changing the query param to `?dl=1` (or `?raw=1`).
- **OneDrive**: share links usually need `download=1` appended, or use
  the "embed"/"download" variant of the link if the standard one 404s
  on direct fetch.

If none of these conversions work (e.g. the file needs sign-in / isn't
publicly shared), tell the user plainly that the link isn't publicly
accessible and ask them to upload the file directly instead — do not
guess its contents.

---

## 3. File Path

The user may type a path directly (`/mnt/user-data/uploads/x.pdf`,
`/home/user/docs/report.docx`, a Windows-style path, a relative path,
etc.).

1. Check the path exists before reading:
   ```bash
   ls -la "<the path>"
   ```
2. If it exists, read it per its type (see below).
3. If it doesn't exist, say so plainly — don't fabricate output. Common
   reasons: typo in the path, file is on the user's local machine (not
   accessible to Claude) rather than in this environment, or the file
   was never actually uploaded/saved there. Ask the user to upload the
   file directly if the path isn't reachable.

---

## 4. Base64 Data

If the user pastes raw base64 content (or it's embedded in a JSON blob,
a code block, etc.), decode it to a temporary file first, then read
that file per its type.

```python
import base64

with open("/tmp/decoded_source.pdf", "wb") as f:
    f.write(base64.b64decode(base64_string))
```

Infer the file type from context (the user usually says what it is, or
there's a data URI prefix like `data:application/pdf;base64,...` /
`data:image/png;base64,...` which tells you the MIME type directly —
strip the prefix before decoding the rest).

---

## Type-Specific Reading (applies after source is resolved to a real local file)

Once you have a real local path (uploaded, downloaded, or decoded),
reading follows the same rules regardless of how you got it:

| Type | How to read |
|------|-------------|
| PDF | `pdf` / `pdf-reading` skill |
| Word (.docx) | `docx` skill |
| Excel/CSV/TSV | `xlsx` skill, or `scripts/read_spreadsheet.py` |
| Image (jpg/png/etc.) | View directly, read visually (vision) |
| Plain text/markdown | Read directly |
| Webpage (fetched HTML) | Extract from fetched text directly, no extra tool needed |
| Unknown type | `file-reading` skill as a router |

---

## Summary Decision Tree

```
Does the user's message contain...
├── An uploaded file in this conversation?
│     → read from /mnt/user-data/uploads/
├── A URL?
│     ├── Direct file link → fetch/download → read per type
│     ├── Cloud share link (Drive/Dropbox/OneDrive) → convert to direct link → fetch/download → read per type
│     └── Plain webpage → web_fetch → extract from returned text directly
├── A file path?
│     → verify it exists → read per type
├── Base64 data?
│     → decode to temp file → read per type
└── None of the above?
      → do NOT fabricate. Ask the user to upload a file or provide a URL/path.
```
