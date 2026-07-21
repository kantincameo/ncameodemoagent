# Wearable Analyzer — Skill Package

## What's inside

```
wearable-analyzer/
├── SKILL.md                          ← main instructions (read this first)
├── README.md                         ← this file
├── references/
│   ├── BloomCell_Wearable_markers.xlsx    ← ground-truth sheet (32 markers)
│   └── output_schema_example.json         ← one worked example of the 8-object output
└── scripts/
    ├── read_markers.py               ← loads the Excel sheet into clean JSON
    ├── extract_report.py             ← reliable PDF text extraction (pdftotext -layout)
    ├── build_output.py               ← scaffolds the 8-object shell (GUIDs + timestamps)
    └── validate_output.py            ← validates a finished output before showing the human
```

This package mirrors the `bloodwork-analyzer` skill structure exactly — same hard rules,
same scripts, same output schema — just pointed at the wearable ground-truth sheet, with a
few wearable-specific rules layered in (see below).

## How this skill uses the Excel sheet

`references/BloomCell_Wearable_markers.xlsx` has 5 columns per marker: **Marker Name, Internal
Notes, Explanation, 30-Day Plan, Long-Term Plan** — covering 32 markers across Cardiovascular
(Resting/Max Heart Rate, HR Recovery), Movement (Steps, Active Minutes, Distance, Floors,
Sedentary Time), Recovery (HRV, HRV Trend, Readiness/Recovery Score, Overnight HR, Temperature),
Respiratory (Respiratory Rate, SpO2), Sleep (Deep/REM/Total Sleep, Efficiency, Consistency,
Latency, WASO), Training Load (Strain, Training Load, Avg Exercise HR), Fitness (VO2 Max), and
Stress (Stress Score). These map directly to the 4 output groups:

| Excel column | Output group |
|---|---|
| Internal Notes | `Internal Notes` |
| Explanation | `Understanding Your Results` |
| 30-Day Plan | `Priority Actions - Next 30 Days` |
| Long-Term Plan | `Long-Term Strategy` |

**No internet, no outside knowledge is used anywhere in this skill.** Every statement in the
output must trace back to a row in this sheet.

### Wearable-specific quirks handled in SKILL.md

- **No fixed reference ranges.** Nearly every marker here is baseline/device-relative, not a
  universal number — the skill is told to never invent a numeric cutoff.
- **Device-specific markers.** Strain (Whoop-only), Recovery Score (Whoop-only), Readiness Score
  (Oura/Garmin) etc. — the skill cross-checks the source device against the sheet's `Devices:`
  list per row as an extra match-verification signal.
- **Context-only markers.** Max Heart Rate, Calories Burned, Light Activity Minutes, and
  Moderate/Vigorous Minutes are marked "Relevance: None (context only)" with no strategy — the
  skill won't manufacture action items for these.
- **Clinical-language routing.** Rows like Resting Heart Rate, Overnight Heart Rate, Temperature,
  Respiratory Rate, and SpO2 mark certain "Clinical (internal)" framing (illness-detection
  language) as internal-only — that stays in `Internal Notes`, never in the patient-facing
  groups, matching how the sheet itself is written.

## Updating the ground-truth sheet

If you edit the sheet or have a newer version:

1. Just replace `references/BloomCell_Wearable_markers.xlsx` with your new file (keep the same
   filename).
2. That's it — `read_markers.py` and `validate_output.py` always read whatever `.xlsx` is
   currently sitting in `references/`, so the skill automatically uses your latest version on the
   very next run. Nothing else needs to change.

## Running it end-to-end (what Claude does under the hood)

```bash
python3 scripts/read_markers.py                    # load ground truth
python3 scripts/extract_report.py export.pdf         # extract export text (PDF only — use
                                                      # native vision for screenshots)
python3 scripts/build_output.py > shell.json         # scaffold 8 objects with valid IDs/dates
#  ...fill in text/rationale/referencesource per SKILL.md's matching rules...
python3 scripts/validate_output.py shell.json        # must PASS before showing the human
```
