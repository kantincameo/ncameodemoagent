---
name: nutrition-analyzer
description: Analyzes a human-uploaded nutritional/biomarker-nutrition report (PDF or screenshot) strictly against the bundled BloomCell_Nutrition.xlsx ground-truth sheet and produces the fixed 8-object JSON output (Internal Notes, Understanding Your Results, Priority Actions - Next 30 Days, Long-Term Strategy). Use this skill whenever the user asks to run the "Nutrition agent" / "Nutrition analysis agent", analyze a nutrition-related lab PDF or screenshot for the LEGO-piece pipeline, or generate provider/patient notes and 30-day/long-term nutrition plans from a report. NO internet access, no external medical/nutrition knowledge, and no model prior knowledge may be used for clinical content — every clinical statement must trace back to a row in the bundled Excel sheet. If the user supplies an updated version of BloomCell_Nutrition.xlsx, replace the file in references/ with the new one and always use the latest file present there.
---

# Nutrition Analyzer

Generates the "Nutrition Analysis" LEGO piece for the NCAMEO multi-agent health-report pipeline. Takes one human-selected nutrition/biomarker report file (PDF or screenshot) as input, and the bundled `references/BloomCell_Nutrition.xlsx` sheet as the ONLY source of clinical rules, language, and ground truth. Produces exactly 8 JSON objects for human-in-the-loop review.

## Hard rules — read first

1. **Zero internet / zero external knowledge.** Never call web_search, never fetch a URL, never fill in a marker's interpretation, nutrition strategy, or recommendation from general knowledge. If a marker found in the report is NOT present in `references/BloomCell_Nutrition.xlsx`, do not invent content for it — list it in a `"skipped_markers"` note to the human instead of guessing (see Step 5).
2. **The Excel sheet is the only source of clinical/nutrition language.** All `Explanation`, `Internal Notes`, `30-Day Plan`, and `Long-Term Plan` text in the output must be drawn from — or a faithful synthesis of — the matching row(s) in the sheet. Do not paraphrase in a way that changes meaning; do not add recommendations, dosages, or claims that aren't grounded in that row. Several rows explicitly mark content as "retained internal" (e.g. clinical dosing ranges, contraindication-sensitive fasting protocols) — that internal-only language belongs in `Internal Notes` group content, never in the patient-facing `Understanding Your Results` / `Priority Actions` / `Long-Term Strategy` groups; keep the user-facing version general as the sheet itself does.
3. **"Latest file always."** Before every run, list `references/` and use whichever `.xlsx` file is there. If the user gives you an updated sheet, overwrite the old one (same filename, or tell the user to keep the filename `BloomCell_Nutrition.xlsx`) — never keep two versions around, never fall back to a cached/older copy.
4. **Human-in-the-loop only.** This skill only produces the draft 8-object JSON for a human to review, edit, and approve. It never auto-submits or pushes the output anywhere.

## Workflow

### Step 1 — Load the ground truth
Run `scripts/read_markers.py` to load every row of `references/BloomCell_Nutrition.xlsx` into a clean structure: `{marker_name, internal_notes, explanation, plan_30_day, long_term_plan}`. This gives you the exact list of marker names the sheet recognizes (59 markers spanning protein/nutrition status, fatty acids, inflammation, minerals, hormones, iron studies, and thyroid panel) — use these as your match targets, don't rely on memory of the sheet.

### Step 2 — Extract the report text
Never eyeball a PDF for numbers. Run `scripts/extract_report.py <path-to-report>`:
- For a PDF, it runs `pdftotext -layout` and prints the raw extracted text.
- For an image/screenshot, view it directly (native vision) and transcribe every marker name + value + flag (H/L/normal) you see, verbatim, before doing anything else.

### Step 3 — Match markers (verification loop)
For each marker name found in the report:
1. Try an exact (case-insensitive) match against the sheet's `marker_name` list.
2. If no exact match, try a normalized match (strip units/parentheses, common abbreviation aliases e.g. "hs-CRP" ↔ "CRP (High Sensitivity) (mg/L)", "Free T4" ↔ "Free T4 (ng/dL)", "TSH" ↔ "TSH – Thyroid Stimulating Hormone (mIU/L)").
3. `grep -i` the raw extracted text for the matched sheet marker name to confirm it's really present before using it — never trust a fuzzy match you haven't verified against the actual extracted text with `repr()` around the matched substring (catches invisible/Unicode whitespace mismatches, and this sheet has several en-dash "–" characters in marker names that plain string equality can silently miss).
4. Any report marker that cannot be confidently matched to a sheet row goes on a "not covered by ground truth sheet" list — do NOT generate clinical content for it.

### Step 4 — Decide what's notable
Only markers that are flagged abnormal in the report (H/L flags, out-of-range, or explicitly called out by the report) are candidates for detailed synthesis. Use the sheet's own "Nutrition relevance: High/Moderate" language (embedded in the `internal_notes` column) to prioritize which findings drive the 4 summary points — High-relevance markers with an actionable Strategy line (e.g. Protein Optimization, Omega-3 Emphasis, Iron Repletion) should generally be favored over Moderate-relevance markers with "No dedicated strategy" when several abnormal markers compete for space. Normal-range markers generally don't need individual mention unless the report itself highlights them.

### Step 5 — Build the 8 JSON objects
Produce **exactly 8 objects**, 2 per group, using the groups below in this exact order and exact string values. Run `scripts/build_output.py` to scaffold valid GUIDs and ISO-8601 UTC timestamps, then fill in content per these rules:

| Group (exact string) | highlight object `text` | note object `text` |
|---|---|---|
| `Internal Notes` | Literal text copied exactly as-is from the report (the flagged value/marker line) — no interpretation added | Clinical-language synthesis drawn only from the matched rows' `Internal Notes` column content — doctor-facing, may include the "retained internal" clinical dosing/strategy detail the sheet marks as internal-only |
| `Understanding Your Results` | Literal text copied exactly as-is from the report | Patient-friendly synthesis drawn only from the matched rows' `Explanation` column content |
| `Priority Actions - Next 30 Days` | Literal text copied exactly as-is from the report | Actionable synthesis drawn only from the matched rows' `30-Day Plan` column content |
| `Long-Term Strategy` | Literal text copied exactly as-is from the report | Strategic synthesis drawn only from the matched rows' `Long-Term Plan` column content |

Every object must include:
- `id`: unique UUID v4 (script generates these)
- `date`: current timestamp, UTC ISO 8601, exactly `YYYY-MM-DDTHH:MM:SSZ`
- `type`: `"highlight"` or `"note"`
- `text`
- `group`: one of the 4 exact strings above
- `rationale`: 1–2 sentences — for highlight, brief context on why this line was pulled; for note, brief explanation of which sheet rows/logic produced this synthesis
- `referencesource`: exact source — for highlight text this is the report file name + page/line; for note text this is `"BloomCell_Nutrition.xlsx - Nutritional Markers sheet - Row N, Marker: <name>"` (list every row used if more than one marker feeds a note)

### Step 6 — Validate before showing the human
Run `scripts/validate_output.py <output.json>`. It checks:
- Exactly 8 objects, 2 per group, correct group strings
- Valid UUID v4 format, no duplicate IDs
- Valid `YYYY-MM-DDTHH:MM:SSZ` timestamp
- Every `referencesource` on a note object actually references a row that exists in the currently-loaded sheet
- No object's `text` is empty

Fix any failures, then present the JSON to the human along with the "not covered by ground truth sheet" list from Step 3 so they can see what was excluded and why.

## Output format reference

See `references/output_schema_example.json` for a fully-worked example of the exact shape expected.

## Notes on the "date" field naming clash

Two conventions for `date` were mentioned when the sibling bloodwork-analyzer skill was defined: `MM/DD/YY HH:MM AM/PM` and UTC ISO 8601 (`2026-06-24T14:20:00Z`). This skill uses **UTC ISO 8601** for consistency with the other sibling skills and the actual JSON template — flag to the human if a different format is actually wanted so the script can be adjusted.
