---
name: wearable-analyzer
description: Analyzes human-uploaded wearable device data/export (PDF or screenshot — e.g. Oura, Whoop, Garmin, Apple Watch, Fitbit summaries) strictly against the bundled BloomCell_Wearable_markers.xlsx ground-truth sheet and produces the fixed 8-object JSON output (Internal Notes, Understanding Your Results, Priority Actions - Next 30 Days, Long-Term Strategy). Use this skill whenever the user asks to run the "Wearable agent" / "Wearable markers agent" / "Fitness report agent", analyze wearable/fitness-tracker data for the LEGO-piece pipeline, or generate provider/patient notes and 30-day/long-term plans from wearable metrics (HRV, sleep, resting heart rate, readiness, strain, steps, etc.). NO internet access, no external knowledge, and no model prior knowledge may be used for clinical/coaching content — every statement must trace back to a row in the bundled Excel sheet. If the user supplies an updated version of BloomCell_Wearable_markers.xlsx, replace the file in references/ with the new one and always use the latest file present there.
---

# Wearable Analyzer

Generates the "Wearable/Fitness Analysis" LEGO piece for the NCAMEO multi-agent health-report pipeline. Takes one human-selected wearable-data file (PDF export or screenshot from an app/device dashboard) as input, and the bundled `references/BloomCell_Wearable_markers.xlsx` sheet as the ONLY source of interpretation rules, coaching language, and ground truth. Produces exactly 8 JSON objects for human-in-the-loop review.

## Hard rules — read first

1. **Zero internet / zero external knowledge.** Never call web_search, never fetch a URL, never fill in a marker's interpretation, threshold, or recommendation from general knowledge. If a marker found in the wearable data is NOT present in `references/BloomCell_Wearable_markers.xlsx`, do not invent content for it — list it in a `"skipped_markers"` note to the human instead of guessing (see Step 5).
2. **The Excel sheet is the only source of interpretation language.** All `Explanation`, `Internal Notes`, `30-Day Plan`, and `Long-Term Plan` text in the output must be drawn from — or a faithful synthesis of — the matching row(s) in the sheet. Do not paraphrase in a way that changes meaning; do not add recommendations, targets, or claims that aren't grounded in that row.
3. **No fixed reference ranges — this sheet is baseline-relative.** Unlike blood/urine/nutrition sheets, almost every wearable marker here is explicitly "no fixed range — baseline/device-relative." Never state or imply a universal numeric cutoff (e.g. "HRV should be X ms") beyond what a row's own `30-Day Plan` tiers (Starting out / Building / Advanced) say. Flag a marker as notable based on the report's own framing (device flag, a stated deviation from the person's baseline, or a value the report itself calls out) — not against an invented normal range.
4. **Some rows are "Relevance: None (context only)."** Max Heart Rate, Calories Burned, Light Activity Minutes, and Moderate/Vigorous Minutes are marked context-only with no strategy — don't manufacture action items for these; use them for background context only if directly relevant to another notable marker.
5. **Clinical-language routing.** A few rows mark certain framing as "Clinical (internal)" — e.g. Resting Heart Rate, Overnight Heart Rate, Temperature, Respiratory Rate, SpO2 explicitly say the internal/clinical framing (illness detection, "take seriously") stays in `Internal Notes` only, and the user-facing groups must stay to general recovery/readiness/wellness language, never illness-detection claims. Follow that routing exactly as the sheet specifies per marker.
6. **"Latest file always."** Before every run, list `references/` and use whichever `.xlsx` file is there. If the user gives you an updated sheet, overwrite the old one (same filename, or tell the user to keep the filename `BloomCell_Wearable_markers.xlsx`) — never keep two versions around, never fall back to a cached/older copy.
7. **Human-in-the-loop only.** This skill only produces the draft 8-object JSON for a human to review, edit, and approve. It never auto-submits or pushes the output anywhere.

## Workflow

### Step 1 — Load the ground truth
Run `scripts/read_markers.py` to load every row of `references/BloomCell_Wearable_markers.xlsx` into a clean structure: `{marker_name, internal_notes, explanation, plan_30_day, long_term_plan}`. This gives you the exact list of marker names the sheet recognizes (32 markers across Cardiovascular, Movement, Recovery, Respiratory, Sleep, Training Load, Fitness, and Stress categories) — use these as your match targets, don't rely on memory of the sheet.

### Step 2 — Extract the report/export text
Never eyeball a PDF or screenshot for numbers. Run `scripts/extract_report.py <path-to-export>`:
- For a PDF export, it runs `pdftotext -layout` and prints the raw extracted text.
- For an image/screenshot (e.g. an app dashboard screenshot), view it directly (native vision) and transcribe every marker name, value/score, unit, and device-stated flag or trend arrow you see, verbatim, before doing anything else.

### Step 3 — Match markers (verification loop)
For each marker name found in the data:
1. Try an exact (case-insensitive) match against the sheet's `marker_name` list.
2. If no exact match, try a normalized match (strip units/parentheses, common aliases e.g. "RHR" ↔ "Resting Heart Rate", "HRV" stays "HRV", "Readiness" ↔ "Readiness Score", "Recovery %" ↔ "Recovery Score", "VO2max" ↔ "VO2 Max", "WASO" ↔ "Wake After Sleep Onset (WASO)").
3. Note which device the data came from (Oura, Whoop, Garmin, Apple Watch, Fitbit, Google Fit, etc.) and cross-check against the sheet's `Devices:` list for that marker — some markers are device-specific (e.g. Strain is Whoop-only, Recovery Score is Whoop-only, Readiness Score is Oura/Garmin). A marker name from a device the sheet doesn't list for that row is a mismatch signal — recheck the match.
4. `grep -i` the raw extracted text for the matched sheet marker name to confirm it's really present before using it — never trust a fuzzy match you haven't verified against the actual extracted text with `repr()` around the matched substring (catches invisible/Unicode whitespace mismatches).
5. Any marker that cannot be confidently matched to a sheet row goes on a "not covered by ground truth sheet" list — do NOT generate content for it.

### Step 4 — Decide what's notable
Since there are no fixed ranges, "notable" means: the device/report itself flags it (low/high badge, red/yellow indicator, a stated downward trend), or the value is explicitly called out in the source data as a deviation from the person's own baseline. Use the sheet's `Relevance: High/Moderate/None` language to prioritize among candidates — High-relevance markers with device-flagged deviations should drive the 4 summary points over Moderate or None-relevance markers.

### Step 5 — Build the 8 JSON objects
Produce **exactly 8 objects**, 2 per group, using the groups below in this exact order and exact string values. Run `scripts/build_output.py` to scaffold valid GUIDs and ISO-8601 UTC timestamps, then fill in content per these rules:

| Group (exact string) | highlight object `text` | note object `text` |
|---|---|---|
| `Internal Notes` | Literal text/value copied exactly as-is from the wearable data (the flagged marker line) — no interpretation added | Clinical/coaching-language synthesis drawn only from the matched rows' `Internal Notes` column content — provider-facing, may include the "Clinical (internal)" framing the sheet marks as internal-only |
| `Understanding Your Results` | Literal text/value copied exactly as-is from the wearable data | Patient-friendly synthesis drawn only from the matched rows' `Explanation` column content |
| `Priority Actions - Next 30 Days` | Literal text/value copied exactly as-is from the wearable data | Actionable synthesis drawn only from the matched rows' `30-Day Plan` column content (respect the Starting out / Building / Advanced tiers where the row has them — pick the tier appropriate to the data if inferable, otherwise present the general guidance) |
| `Long-Term Strategy` | Literal text/value copied exactly as-is from the wearable data | Strategic synthesis drawn only from the matched rows' `Long-Term Plan` column content |

Every object must include:
- `id`: unique UUID v4 (script generates these)
- `date`: current timestamp, UTC ISO 8601, exactly `YYYY-MM-DDTHH:MM:SSZ`
- `type`: `"highlight"` or `"note"`
- `text`
- `group`: one of the 4 exact strings above
- `rationale`: 1–2 sentences — for highlight, brief context on why this line was pulled; for note, brief explanation of which sheet rows/logic produced this synthesis
- `referencesource`: exact source — for highlight text this is the export file name + page/section (or "screenshot" + app name); for note text this is `"BloomCell_Wearable_markers.xlsx - Wearable Markers sheet - Row N, Marker: <name>"` (list every row used if more than one marker feeds a note)

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
