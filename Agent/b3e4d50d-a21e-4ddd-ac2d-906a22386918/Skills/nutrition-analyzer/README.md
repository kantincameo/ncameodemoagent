# Nutrition Analyzer — Skill Package

## What's inside

```
nutrition-analyzer/
├── SKILL.md                          ← main instructions (read this first)
├── README.md                         ← this file
├── references/
│   ├── BloomCell_Nutrition.xlsx      ← ground-truth sheet (59 markers)
│   └── output_schema_example.json    ← one worked example of the 8-object output
└── scripts/
    ├── read_markers.py               ← loads the Excel sheet into clean JSON
    ├── extract_report.py             ← reliable PDF text extraction (pdftotext -layout)
    ├── build_output.py               ← scaffolds the 8-object shell (GUIDs + timestamps)
    └── validate_output.py            ← validates a finished output before showing the human
```

This package mirrors the `bloodwork-analyzer` skill structure exactly — same hard rules,
same scripts, same output schema — just pointed at the nutrition ground-truth sheet instead
of the bloodwork one.

## How this skill uses the Excel sheet

`references/BloomCell_Nutrition.xlsx` has 5 columns per marker: **Marker Name, Internal
Notes, Explanation, 30-Day Plan, Long-Term Plan** — covering 59 markers across protein status,
fatty acids (omega-3/omega-6), inflammation (CRP), minerals (calcium), hormones (cortisol,
testosterone), iron studies (ferritin), and the full thyroid panel (TSH, T3, T4, Reverse T3).
These map directly to the 4 output groups:

| Excel column | Output group |
|---|---|
| Internal Notes | `Internal Notes` |
| Explanation | `Understanding Your Results` |
| 30-Day Plan | `Priority Actions - Next 30 Days` |
| Long-Term Plan | `Long-Term Strategy` |

**No internet, no outside medical/nutrition knowledge is used anywhere in this skill.** Every
clinical sentence in the output must trace back to a row in this sheet.

Some `Internal Notes` rows contain clinical dosing or protocol detail explicitly marked
"retained internal" in the sheet (e.g. protein g/kg dosing, contraindication-sensitive fasting
windows) — SKILL.md instructs Claude to keep that detail only in the `Internal Notes` group and
keep the patient-facing groups general, matching how the sheet itself is written.

## Updating the ground-truth sheet

If you edit the sheet or have a newer version:

1. Just replace `references/BloomCell_Nutrition.xlsx` with your new file (keep the same
   filename).
2. That's it — `read_markers.py` and `validate_output.py` always read whatever `.xlsx` is
   currently sitting in `references/`, so the skill automatically uses your latest version on the
   very next run. Nothing else needs to change.

## Running it end-to-end (what Claude does under the hood)

```bash
python3 scripts/read_markers.py                    # load ground truth
python3 scripts/extract_report.py report.pdf        # extract report text (PDF only — use
                                                      # native vision for screenshots)
python3 scripts/build_output.py > shell.json         # scaffold 8 objects with valid IDs/dates
#  ...fill in text/rationale/referencesource per SKILL.md's matching rules...
python3 scripts/validate_output.py shell.json        # must PASS before showing the human
```
