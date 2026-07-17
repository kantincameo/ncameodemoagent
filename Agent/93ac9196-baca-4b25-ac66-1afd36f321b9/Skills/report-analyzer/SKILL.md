---
name: report-analyzer
description: Analyze functional laboratory evaluation reports (blood work, metabolic panels, thyroid tests, lipid panels, hormone panels, omega panels, iron panels) and provide structured health insights in JSON format using the BloomCell clinical framework. Use this skill whenever a user uploads a lab report PDF, mentions "analyze my blood work", "review my lab results", "interpret my test results", asks about biomarkers, functional ranges, or wants to understand health metrics from any laboratory report. Also trigger when wearable data (WHOOP, Oura, Apple Health, Garmin, Fitbit) is mentioned alongside lab results. Always outputs JSON with highlights and notes for 4 analysis points using BloomCell reference data.
---

# Report Analyzer — BloomCell Edition

This skill analyzes functional laboratory evaluation reports using the **BloomCell clinical framework** and outputs structured health insights as a JSON array of exactly 8 objects.

---

## Reference Files (Load As Needed)

All reference files are in `references/`. Load them via `bash_tool` (Python + openpyxl/python-docx) when needed:

| File | When to Load |
|------|-------------|
| `Biomarkers.xlsx` | **Always** — BloomCell functional ranges, severity scores, high/low clinical meanings |
| `BloomCell key recommendations.xlsx` | **Always** — per-biomarker recommendations, actions, supportive testing triggers |
| `BloomCell Nutrition MVP v11.xlsx` | When generating nutrition actions in Priority Actions or Long-Term Strategy |
| `BloomCell Recovery MVP v2.xlsx` | When generating recovery strategies in Priority Actions or Long-Term Strategy |
| `BloomCell Training MVP v7.xlsx` | When generating training recommendations |
| `BloomCell Wearable MVP v3.xlsx` | When wearable data (HRV, sleep, strain, steps) is present |
| `BloomCell Narrative results.docx` | For patient-friendly language patterns in "Understanding Your Results" |
| `Master Report April 2026 (2).docx` | Gold-standard output format: tone, depth, and structure for all 4 sections |
| `3 M Health Check.docx` | Doctor's clinical note style — model for "Internal Notes" section |

---

## ⛔ CRITICAL CONSTRAINTS — NON-NEGOTIABLE

These rules override everything else in this skill. Violating them invalidates the entire output.

### Rule 1: Reference Files Are the ONLY Source of Analysis
- **ALL analysis, recommendations, ranges, and clinical interpretations MUST come exclusively from the reference files listed above.**
- Web search is STRICTLY PROHIBITED. Do not call web search for any reason — not for ranges, not for supplement dosages, not for clinical context.
- AI self-generation is STRICTLY PROHIBITED. Do not use training knowledge or general medical knowledge to fill any field. If a biomarker is not found in `Biomarkers.xlsx`, do NOT invent a range or interpretation — flag it as "Not in BloomCell reference" and skip it.
- If a reference file cannot be loaded or a value cannot be found in the loaded file, state this explicitly in the output rather than substituting with AI-generated content.

### Rule 2: Every `"text"` and `"rationale"` Field Must Be Grounded in Reference File Content
- The `"text"` field for every **note** object must be constructed using data pulled directly from the loaded reference files (e.g., recommendation text from `BloomCell key recommendations.xlsx`, narrative language from `BloomCell Narrative results.docx`, action text from MVP files).
- The `"rationale"` field for every object — both highlight and note — must cite specific values, ranges, thresholds, or strategy logic sourced from the reference files. **No rationale may be written from AI memory alone.**
- If you cannot trace a `"rationale"` sentence back to a specific row/column/page in a reference file, do not include that sentence.

---

## When to Use This Skill

- User uploads a PDF with lab results, blood work, or metabolic panels
- User mentions: "analyze my labs", "review my blood test", "interpret my results"
- User asks about specific biomarkers or health metrics from a report
- User wants to understand what their test results mean
- User asks for health recommendations based on lab values, with or without wearable data
- Any context involving laboratory reports, functional ranges, or biomarker interpretation

---

## Output Format

The skill MUST output a valid JSON array containing exactly **8 objects** (4 points × 2 objects per point):
- Each of the 4 analysis points has 2 objects: one `"highlight"` and one `"note"`
- Each object MUST include a `"group"` field indicating which of the 4 points it belongs to
- Each object MUST include a `"id"` field containing a unique GUID (format: `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`)
- Each object MUST include a `"date"` field with the current timestamp in `MM/DD/YY HH:MM AM/PM` format
- Highlight and note have DIFFERENT rationales (highlight = brief context, note = detailed analysis)
- Total output: 8 JSON objects in a single array

**JSON Structure for ALL 4 Points:**
```json
[
  {
    "id": "a1b2c3d4-e5f6-4789-a0bc-d1e2f3a4b5c6",
    "date": "05/27/25 10:30 AM",
    "type": "highlight",
    "text": "Literal text copied exactly as-is from the PDF — no added flags, annotations, or interpretations beyond what the PDF itself shows",
    "group": "Internal Notes",
    "rationale": "Brief explanation of the finding and its context",
    "referencesource": "Exact reference file name, sheet, column, row, or page used to generate this highlight — e.g. 'Biomarkers.xlsx - Biomarkers sheet - Row 12, Column Severity Score'",
    "color": "#E05252",
    "bgColor": "#FEF2F2",
    "textColor": "#7F1D1D"
  },
  {
    "id": "b2c3d4e5-f6a7-4890-b1cd-e2f3a4b5c6d7",
    "date": "05/27/25 10:30 AM",
    "type": "note",
    "text": "Exact verbatim text from PDF - Healthcare Professional Name",
    "group": "Internal Notes",
    "rationale": "Detailed clinical interpretation and recommendations",
    "referencesource": "Exact reference file name, sheet, column, row, or page used to generate this note — e.g. '3 M Health Check.docx - Page 2' or 'BloomCell key recommendations.xlsx - Key Blood Results sheet - Row 5'",
    "color": "#E05252",
    "bgColor": "#FEF2F2",
    "textColor": "#7F1D1D"
  },
  {
    "id": "c3d4e5f6-a7b8-4901-c2de-f3a4b5c6d7e8",
    "date": "05/27/25 10:30 AM",
    "type": "highlight",
    "text": "Literal text copied exactly as-is from the PDF — no added flags, annotations, or interpretations beyond what the PDF itself shows",
    "group": "Understanding Your Results",
    "rationale": "Brief explanation of the finding and its context",
    "referencesource": "Exact reference file name, sheet, column, row, or page used to generate this highlight — e.g. 'Biomarkers.xlsx - Biomarkers sheet - Row 8, Column High'",
    "color": "#EF9F27",
    "bgColor": "#FFF7ED",
    "textColor": "#9A3412"
  },
  {
    "id": "d4e5f6a7-b8c9-4012-d3ef-a4b5c6d7e8f9",
    "date": "05/27/25 10:30 AM",
    "type": "note",
    "text": "Patient-friendly explanation of what this means",
    "group": "Understanding Your Results",
    "rationale": "Detailed explanation of mechanisms and health impact",
    "referencesource": "Exact reference file name, sheet, column, row, or page used to generate this note — e.g. 'BloomCell Narrative results.docx - Page 1' or 'BloomCell key recommendations.xlsx - Key Blood Results sheet - Row 8'",
    "color": "#EF9F27",
    "bgColor": "#FFF7ED",
    "textColor": "#9A3412"
  },
  {
    "id": "e5f6a7b8-c9d0-4123-e4fa-b5c6d7e8f9a0",
    "date": "05/27/25 10:30 AM",
    "type": "highlight",
    "text": "Literal text copied exactly as-is from the PDF — no added flags, annotations, or interpretations beyond what the PDF itself shows",
    "group": "Priority Actions - Next 30 Days",
    "rationale": "Brief explanation of the finding and its context",
    "referencesource": "Exact reference file name, sheet, column, row, or page used to generate this highlight — e.g. 'Biomarkers.xlsx - Biomarkers sheet - Row 22, Column Impact Score'",
    "color": "#1D9E75",
    "bgColor": "#ECFDF5",
    "textColor": "#065F46"
  },
  {
    "id": "f6a7b8c9-d0e1-4234-f5ab-c6d7e8f9a0b1",
    "date": "05/27/25 10:30 AM",
    "type": "note",
    "text": "Specific actionable recommendations with dosages and timeline",
    "group": "Priority Actions - Next 30 Days",
    "rationale": "Detailed justification for these specific actions",
    "referencesource": "Exact reference file name, sheet, column, row, or page used to generate this note — e.g. 'BloomCell Recovery MVP v2.xlsx - Recovery Strategies sheet - Column 15' or 'BloomCell Nutrition MVP v11.xlsx - Nutrition Strategies sheet - Row 34'",
    "color": "#1D9E75",
    "bgColor": "#ECFDF5",
    "textColor": "#065F46"
  },
  {
    "id": "a7b8c9d0-e1f2-4345-a6bc-d7e8f9a0b1c2",
    "date": "05/27/25 10:30 AM",
    "type": "highlight",
    "text": "Literal text copied exactly as-is from the PDF — no added flags, annotations, or interpretations beyond what the PDF itself shows",
    "group": "Long-Term Strategy",
    "rationale": "Brief explanation of the finding and its context",
    "referencesource": "Exact reference file name, sheet, column, row, or page used to generate this highlight — e.g. 'Biomarkers.xlsx - Biomarkers sheet - Row 15, Column Severity Score'",
    "color": "#534AB7",
    "bgColor": "#F5F3FF",
    "textColor": "#4C1D95"
  },
  {
    "id": "b8c9d0e1-f2a3-4456-b7cd-e8f9a0b1c2d3",
    "date": "05/27/25 10:30 AM",
    "type": "note",
    "text": "Long-term optimization plan with targets and timeline",
    "group": "Long-Term Strategy",
    "rationale": "Detailed strategic approach and success metrics",
    "referencesource": "Exact reference file name, sheet, column, row, or page used to generate this note — e.g. 'Master Report April 2026 (2).docx - Page 5' or 'BloomCell key recommendations.xlsx - Key supportive Testing sheet - Row 11'",
    "color": "#534AB7",
    "bgColor": "#F5F3FF",
    "textColor": "#4C1D95"
  }
]
```

**Group Values** (use these exact strings):
1. `"Internal Notes"`
2. `"Understanding Your Results"`
3. `"Priority Actions - Next 30 Days"`
4. `"Long-Term Strategy"`

**Color Assignment** (fixed per point — both the highlight and note of the same point MUST share the same color, bgColor, and textColor):
| Point | Group | `color` | `bgColor` | `textColor` |
|-------|-------|---------|-----------|-------------|
| 1 | `"Internal Notes"` | `"#E05252"` | `"#FEF2F2"` | `"#7F1D1D"` |
| 2 | `"Understanding Your Results"` | `"#EF9F27"` | `"#FFF7ED"` | `"#9A3412"` |
| 3 | `"Priority Actions - Next 30 Days"` | `"#1D9E75"` | `"#ECFDF5"` | `"#065F46"` |
| 4 | `"Long-Term Strategy"` | `"#534AB7"` | `"#F5F3FF"` | `"#4C1D95"` |

Each object MUST include `"color"`, `"bgColor"`, and `"textColor"` fields with the exact hex strings for its point. All three color values for a point's highlight and note are always identical.

**ID Generation:** Generate a valid UUID v4 for each object. Each of the 8 objects must have a unique ID.

**Date Format:** Use the current date and time at the moment of generation in `MM/DD/YY HH:MM AM/PM` format (e.g., `"05/27/25 10:30 AM"`). All 8 objects share the same timestamp.

---

## The 4 Required Analysis Points

Each lab report analysis must include these 4 points in order:

### Point 1: Internal Notes
Critical clinical findings from the report — **doctor-facing, clinical language only**

### Point 2: Understanding Your Results
Patient-friendly explanation of what the results mean

### Point 3: Priority Actions - Next 30 Days
Immediate actionable steps with specific recommendations

### Point 4: Long-Term Strategy (3-6 Months)
Strategic health optimization roadmap

---

## Core Workflow

### Step 1: Read the Lab Report

**MANDATORY — run ALL of the following in order. Do not skip any sub-step.**

#### 1a. Extract full PDF text
```bash
pdftotext "/mnt/user-data/uploads/filename.pdf" /tmp/lab_text.txt && cat /tmp/lab_text.txt
```
If pdftotext fails, use `pdftoppm` to rasterize pages and analyze visually.

#### 1b. Grep-first biomarker discovery (REQUIRED before selecting highlight text)

For every biomarker you are considering as a highlight, grep for it in the extracted text to find the EXACT label the PDF uses. Do NOT assume abbreviations — the PDF may say "Hemoglobin A1c" not "HbA1c", "SGOT (AST)" not "AST", "25-OH Vitamin D3" not "Vitamin D":

```bash
# Run for ALL biomarkers you are considering — adjust keywords as needed
grep -in "glucose\|hemoglobin\|hba1c\|a1c" /tmp/lab_text.txt
grep -in "homocystein" /tmp/lab_text.txt
grep -in "vitamin d\|25-oh" /tmp/lab_text.txt
grep -in "ferritin\|iron" /tmp/lab_text.txt
grep -in "cholesterol\|triglycer\|hdl\|ldl" /tmp/lab_text.txt
grep -in "crp\|c-reactive\|hsCRP" /tmp/lab_text.txt
grep -in "thyroid\|tsh\|free t3\|free t4" /tmp/lab_text.txt
```

The grep output IS the exact text. Copy the relevant portion verbatim — do NOT retype or reformat it.

#### 1c. Encoding check for special characters (REQUIRED when µ, <, >, % appear)

Special characters like µ (micro), <, >, %, and ° are frequent sources of mismatch — the character the AI types may differ from the byte the PDF stores. Use `repr()` to inspect exact bytes:

```python
with open('/tmp/lab_text.txt', 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

# Inspect the exact characters around any special-character biomarker
import re
for m in re.finditer(r'.{0,30}(homocystein|µ|umol|vitamin d|hba1c).{0,30}', text, re.IGNORECASE):
    print(repr(m.group()))  # repr() shows exact unicode — e.g. '\xb5mol' vs '\u03bcmol'
```

Use the EXACT character from `repr()` output in your highlight `"text"`. Never type µ or μ from memory — copy it from the repr output. If the PDF uses `umol` (ASCII) instead of `µmol`, use `umol`.

#### 1d. Verify all 4 candidates before writing output

```python
with open('/tmp/lab_text.txt', 'r', encoding='utf-8', errors='replace') as f:
    pdf_text = f.read()

candidates = [
    "exact string 1 — copied from grep output",
    "exact string 2 — copied from grep output",
    "exact string 3 — copied from grep output",
    "exact string 4 — copied from grep output"
]
for c in candidates:
    print(f"{'✅ FOUND' if c in pdf_text else '❌ NOT FOUND — FIX REQUIRED'}: {repr(c)}")
```

All 4 must print `✅ FOUND`. **If any fails, apply the progressive fallback below — do NOT output until all 4 pass.**

#### 1e. Progressive fallback if a candidate fails verification

Try progressively shorter substrings until one passes:

1. **Full row**: `"Hemoglobin A1c 4.8%-5.6% 5.5"` → if ❌
2. **Name + value only**: `"Hemoglobin A1c 5.5"` → if ❌
3. **Name + value (no space)**: `"Hemoglobin A1c5.5"` → if ❌
4. **Just the result value with surrounding context from grep**: use the raw grep line and trim to a safe unique substring → if still ❌
5. **Biomarker name alone**: `"Hemoglobin A1c"` (least preferred — use only if nothing else works)

Use the SHORTEST string that (a) passes `✅ FOUND` and (b) uniquely identifies the biomarker in the PDF.

Also check if the user has shared wearable data (WHOOP, Oura, Apple Health, Garmin, Fitbit).

### Step 2: Load BloomCell Biomarker Reference

```python
import openpyxl
wb = openpyxl.load_workbook('references/Biomarkers.xlsx', data_only=True)
ws = wb['Biomarkers']
# Columns: Biomarker, MinAge, MaxAge, Units, Gender, Minimum (functional low),
#           Maximum (functional high), Group, High (meaning), Low (meaning),
#           Severity Score (1=mild to 5=highly significant), Deviation Multiplier, Impact Score
```

For each biomarker in the report:
- Compare patient value against BloomCell **functional range** (Min/Max columns) — these are tighter than standard lab reference ranges
- Note severity score and direction (High/Low)
- Flag ALL out-of-range values before selecting the 4 highlight markers

### Step 3: Load Key Recommendations

```python
wb2 = openpyxl.load_workbook('references/BloomCell key recommendations.xlsx', data_only=True)
# Sheet "Key Blood Results": Biomarkers, High/Low/Both, key_issue, Recommendation, Action
# Sheet "Key supportive Testing": supportive test triggers per biomarker
# Sheet "Optimal recovery strategies": recovery strategy IDs per biomarker
```

### Step 4: Apply the BloomCell 4-Step Analysis Logic

Follow the BloomCell diagnostic sequence:

**Step 1 — Blood Sugar & Iron:** HbA1c, Glucose, Ferritin, Serum Iron, UIBC, Iron Saturation
**Step 2 — Metabolic & Stress:** RBC markers (HGB, HCT, RBC, MCV), Cholesterol panel, Adrenal markers (Cortisol, DHEA-S)
**Step 3 — Inflammation & Immune:** WBC differential (Lymphocytes, Monocytes, Eosinophils, Basophils), CRP, LDH
**Step 4 — Deficiency & Absorption:** Vitamin D, B12, Homocysteine, Magnesium, Omega-3/6 ratios

Identify cross-marker patterns:
- **Metabolic Syndrome**: High Glucose + High Triglycerides + Low HDL
- **Hypothyroid**: Low Free T3 + Low Free T4 + High Cholesterol + High Reverse T3
- **Inflammation/Liver Stress**: High CRP + High AST/ALT + Elevated LDH
- **Iron-Deficiency Anemia**: Low Ferritin + Low Serum Iron + Low HGB/HCT + High UIBC
- **Normocytic Normochromic Anemia**: Low RBC/HGB/HCT with normal MCV/MCH/MCHC → chronic inflammation-driven
- **Dehydration Cluster**: High BUN/Creatinine Ratio + High Sodium + High Albumin + High Hematocrit
- **Methylation/B-vitamin Insufficiency**: High Homocysteine + High Anion Gap + Low B12/Folate
- **Autoimmune Activation**: Positive ANA + High Lymphocytes + High CRP + High Eosinophils
- **Malabsorption**: Low Total Protein + Low Albumin + Low B12 + Low Vitamin D

### Step 5: Load Strategy Libraries (for Points 3 & 4)

```python
# Nutrition — match flagged biomarker + value → get Nutrition IDs → pull top 3 by priority
wb_nut = openpyxl.load_workbook('references/BloomCell Nutrition MVP v11.xlsx', data_only=True)
# "Nutrition Key" sheet: biomarker → strategy IDs
# "Nutrition Strategies" sheet: strategy content
# Contraindication: if eGFR Low, enforce Kidney Guardrail (ID 190)

# Recovery — match flagged biomarker + value → get Recovery IDs → pull top 3 by priority
wb_rec = openpyxl.load_workbook('references/BloomCell Recovery MVP v2.xlsx', data_only=True)

# Training — match flagged biomarker + value → get Training IDs → pull top 3 by priority
wb_trn = openpyxl.load_workbook('references/BloomCell Training MVP v7.xlsx', data_only=True)

# Wearable (only if wearable data is present)
wb_wear = openpyxl.load_workbook('references/BloomCell Wearable MVP v3.xlsx', data_only=True)
# Apply conflict override rules from "Conflict Override Logic" sheet before final selection
```

MVP Selection Logic (same for all):
1. Collect all IDs where biomarker + value matches patient results
2. De-duplicate
3. Sort by Priority ascending (lower number = higher priority)
4. Take top 3 strategies

> ⛔ At no point in steps 1–10 may web search be called or AI training knowledge be used to generate content. All values, ranges, recommendations, and rationale must trace to a loaded reference file.

---

## Point-by-Point Content Rules

### Point 1: Internal Notes — highlight object

**Rules for `"text"` field:**
- MUST be a substring that passes `✅ FOUND` in Step 1d verification — this is non-negotiable
- **Use the biomarker name EXACTLY as it appears in pdftotext output** — do NOT use abbreviations or alternate names that differ from the PDF (e.g. if PDF says `"Hemoglobin A1c"`, do NOT use `"HbA1c"`; if PDF says `"SGOT (AST)"`, do NOT use `"AST"`)
- **Special characters MUST be copied from Step 1c `repr()` output** — never type µ, μ, <, >, or % from memory; the PDF may store them as different unicode code points or ASCII equivalents (`umol` vs `µmol`)
- If the full "name + range + value" string fails verification, apply the Step 1e progressive fallback — use the shortest substring that passes
- **No synthesized content**: do NOT append labels, flags, or annotations not present in the PDF
- **No character limit — include the full set of relevant Test Names, Results/Readings, and ranges from the report needed for a complete A-to-Z deep analysis**

**Rules for `"rationale"` field (brief context):**
- 1–2 sentences: state the finding and its immediate clinical context
- Reference the functional range from Biomarkers.xlsx
- Example: `"AST is 3x above BloomCell functional ceiling (10–26 IU/L), indicating hepatic or muscle-driven transaminase elevation."`

**Rules for `"referencesource"` field:**
- REQUIRED — must be populated for every highlight object
- Specify exactly which reference file, sheet, and row/column/page was used to determine this finding
- Format: `"[filename] - [sheet name] - [Row X, Column Y]"` or `"[filename] - Page N"`
- Example: `"Biomarkers.xlsx - Biomarkers sheet - Row 42, Columns Minimum/Maximum/Severity Score"`

### Point 1: Internal Notes — note object

**Rules for `"text"` field (doctor-facing):**
- Format: `"[Exact finding from PDF] - [Healthcare Professional Name if present in report]"`
- Use clinical language; this is for the reviewing clinician only
- **No character limit — include the full set of relevant Test Names, Results/Readings, and ranges from the report needed for a complete A-to-Z deep analysis**

**Rules for `"rationale"` field (detailed clinical interpretation):**
- Full clinical analysis: mechanism, cross-referenced markers confirming the pattern, differential considerations
- Suggest follow-up actions for the clinician (e.g., "consider DUTCH Plus to assess diurnal cortisol pattern")
- Reference specific page/section of the report where possible
- Style modeled on `3 M Health Check.docx` and physician narrative in `Master Report April 2026 (2).docx`

**Rules for `"referencesource"` field:**
- REQUIRED — must be populated for every note object
- Specify exactly which reference file(s), sheet(s), and row/column/page(s) were used to generate this clinical note
- Multiple sources may be cited separated by ` | `
- Example: `"3 M Health Check.docx - Page 2 | BloomCell key recommendations.xlsx - Key Blood Results sheet - Row 18"`

---

### Point 2: Understanding Your Results — highlight object

**Rules for `"text"` field:**
- MUST pass `✅ FOUND` in Step 1d verification. MUST be a **different marker** from Point 1
- Use exact biomarker name from pdftotext (no abbreviations); copy special characters from Step 1c repr() output
- Apply Step 1e progressive fallback if needed
- **No character limit — include the full set of relevant Test Names, Results/Readings, and ranges from the report needed for a complete A-to-Z deep analysis**

**Rules for `"rationale"` field:**
- Brief, accessible explanation of what this finding shows

**Rules for `"referencesource"` field:**
- REQUIRED — must be populated for every highlight object
- Specify exactly which reference file, sheet, and row/column was used to flag this biomarker
- Example: `"Biomarkers.xlsx - Biomarkers sheet - Row 8, Columns Maximum/High"`

**Rules for `"text"` field:**
- Patient-friendly explanation — clear language, no jargon
- Connect to how the patient might feel (energy, stamina, focus, sleep)
- Reassure where appropriate ("these results are a snapshot in time, not a permanent condition")
- Style modeled on `BloomCell Narrative results.docx`
- **No character limit — include the full set of relevant Test Names, Results/Readings, and ranges from the report needed for a complete A-to-Z deep analysis**

**Rules for `"rationale"` field:**
- Detailed plain-language explanation of mechanisms and health impact

**Rules for `"referencesource"` field:**
- REQUIRED — must be populated for every note object
- Specify exactly which reference file(s), sheet(s), and row/column/page(s) were used to generate this patient-facing explanation
- Multiple sources may be cited separated by ` | `
- Example: `"BloomCell Narrative results.docx - Page 1 | BloomCell key recommendations.xlsx - Key Blood Results sheet - Row 8"`

---

### Point 3: Priority Actions — Next 30 Days — highlight object

**Rules for `"text"` field:**
- MUST pass `✅ FOUND` in Step 1d verification. MUST be a **different marker** from Points 1 and 2
- Use exact biomarker name from pdftotext (no abbreviations); copy special characters from Step 1c repr() output
- Apply Step 1e progressive fallback if needed
- **No character limit — include the full set of relevant Test Names, Results/Readings, and ranges from the report needed for a complete A-to-Z deep analysis**

**Rules for `"rationale"` field:**
- Why this marker drives the most urgent action priority

**Rules for `"referencesource"` field:**
- REQUIRED — must be populated for every highlight object
- Specify exactly which reference file, sheet, and row/column was used to identify this urgent marker
- Example: `"Biomarkers.xlsx - Biomarkers sheet - Row 22, Columns Maximum/Severity Score/Impact Score"`

**Rules for `"text"` field:**
- Format: `"Start [Supplement X dose]. [Diet action]. [Lifestyle action]. [Medical follow-up]."`
- Draw from BloomCell Key Recommendations ("Action" column) + top-priority MVP strategies
- Include exact supplement names, dosages, frequencies
- Cite specific biomarker values and targets where possible
- If wearable data is present, integrate top wearable strategy
- **No character limit — include the full set of relevant Test Names, Results/Readings, and ranges from the report needed for a complete A-to-Z deep analysis**

**Rules for `"rationale"` field:**
- Justify each priority action against specific biomarker values
- Reference urgency (e.g., "3x functional limit warrants immediate attention")
- Connect findings to recommended actions from BloomCell MVPs

**Rules for `"referencesource"` field:**
- REQUIRED — must be populated for every note object
- Specify exactly which MVP file(s), sheet(s), and row/column(s) were used to select the priority actions
- Multiple sources may be cited separated by ` | `
- Example: `"BloomCell Recovery MVP v2.xlsx - Recovery Strategies sheet - Column 15 | BloomCell Nutrition MVP v11.xlsx - Nutrition Strategies sheet - Row 34"`

---

### Point 4: Long-Term Strategy — highlight object

**Rules for `"text"` field:**
- MUST pass `✅ FOUND` in Step 1d verification. MUST be a **different marker** from Points 1, 2, and 3
- Use exact biomarker name from pdftotext (no abbreviations); copy special characters from Step 1c repr() output
- Apply Step 1e progressive fallback if needed
- Should reflect a chronic or systemic pattern
- **No character limit — include the full set of relevant Test Names, Results/Readings, and ranges from the report needed for a complete A-to-Z deep analysis**

**Rules for `"rationale"` field:**
- Why this marker represents a long-term systemic issue

**Rules for `"referencesource"` field:**
- REQUIRED — must be populated for every highlight object
- Specify exactly which reference file, sheet, and row/column was used to identify this systemic marker
- Example: `"Biomarkers.xlsx - Biomarkers sheet - Row 15, Columns Minimum/Maximum/Severity Score"`

**Rules for `"text"` field:**
- Format: `"Target [Marker] <[value] and [Marker] <[value]. Retest: [6–8wks markers], [3mo markers], [6mo full panel]."`
- Organize by body system or health domain
- Include specific retest target values from BloomCell Biomarkers.xlsx
- Reference supportive testing if warranted (Cyrex arrays, DUTCH, Genova Adrenal, GI-MAP) — triggered from "Key supportive Testing" sheet
- Style modeled on Long-Term Strategy section of `Master Report April 2026 (2).docx`
- **No character limit — include the full set of relevant Test Names, Results/Readings, and ranges from the report needed for a complete A-to-Z deep analysis**

**Rules for `"rationale"` field:**
- System-by-system strategic rationale
- Root causes addressed, target values, retest schedule
- Connect short-term actions to long-term goals

**Rules for `"referencesource"` field:**
- REQUIRED — must be populated for every note object
- Specify exactly which reference file(s), sheet(s), and row/column/page(s) were used to build the long-term strategy
- Multiple sources may be cited separated by ` | `
- Example: `"Master Report April 2026 (2).docx - Page 5 | BloomCell key recommendations.xlsx - Key supportive Testing sheet - Row 11"`

---

## Critical Anti-Overlap Rule

**Each of the 4 groups MUST use a DIFFERENT biomarker in its highlight `"text"` field.**

- Group 1 (Internal Notes): pick the highest-severity/impact marker
- Group 2 (Understanding Your Results): pick a different marker with good patient explanatory value
- Group 3 (Priority Actions): pick a different marker tied to the most urgent actionable priority
- Group 4 (Long-Term Strategy): pick a different marker representing a chronic/systemic pattern

**NEVER reuse the same marker across groups.**

---

## Accuracy Standards

- Use ONLY data present in the PDF
- Quote exact values and ranges from the report — preserve original units
- Never invent or assume values
- Always compare against BloomCell **functional ranges** from `Biomarkers.xlsx` (not just lab reference ranges)
- Reference specific page numbers or sections where possible
- **Reference files are the sole permitted source** — do not use web search, AI training knowledge, or general medical literature to supplement, fill gaps, or validate any field
- **If a biomarker or strategy is not found in any reference file**, write `"Not found in BloomCell reference — review manually"` in the relevant field rather than generating content from AI knowledge
- **Every sentence in `"rationale"` must be traceable to a specific reference file row, column, or page** — if it cannot be traced, omit it

---

## Pre-Output Validation Checklist

Before outputting the JSON, verify:
1. ✅ **Exactly 8 objects** — 4 points × 2 objects each
2. ✅ **Every object has a unique `"id"`** (valid UUID v4)
3. ✅ **Every object has a `"date"`** in `MM/DD/YY HH:MM AM/PM` format
4. ✅ **No marker overlap** — 4 different markers across the 4 highlight `"text"` fields
5. ✅ **All `"text"` fields contain the full set of relevant Test Names, Results/Readings, and ranges needed for a complete A-to-Z deep analysis** — highlight and note both checked
6. ✅ **Correct group names** — exact strings for all `"group"` fields: `"Internal Notes"`, `"Understanding Your Results"`, `"Priority Actions - Next 30 Days"`, `"Long-Term Strategy"`
7. ✅ **Valid JSON** — proper quotes, commas, brackets, no trailing commas
8. ✅ **Internal Notes uses clinical language** — doctor-appropriate depth and terminology
9. ✅ **Patient-facing sections use accessible language** — no unexplained jargon
10. ✅ **Every object has `"color"`, `"bgColor"`, and `"textColor"`** — all three use the correct hex values for their point; highlight and note of the same point share identical color values
11. ✅ **Every object has `"referencesource"`** — both highlight and note objects have this field populated with the exact file name, sheet, column, row, or page that was used to generate the content (e.g. `"BloomCell Recovery MVP v2.xlsx - Recovery Strategies sheet - Column 15"`); never leave this field blank or generic
12. ✅ **All highlight `"text"` fields passed Step 1d verification (`✅ FOUND`)** — no colon-formatted strings, no abbreviations that differ from the PDF label, no special characters typed from memory (µ/μ/% etc. copied from Step 1c repr() output). Progressive fallback (Step 1e) was applied for any initially failing candidates.
13. ✅ **Step 1b grep and Step 1c repr() were actually run** — do not skip and assume. Grep output was used to find exact marker labels; repr() was used to inspect any biomarker row containing µ, <, >, or % before finalizing its highlight text.
14. ✅ **No web search was used at any point** — analysis, ranges, recommendations, and rationale are sourced exclusively from the reference files listed in the Reference Files table; web search was not called for any purpose
15. ✅ **No AI self-generation in text or rationale** — every `"note"` text is built from reference file content (key recommendations, narrative docs, MVP strategies); every `"rationale"` sentence is traceable to a specific file, sheet, and row/column/page; no sentence was written from AI training knowledge alone

---

## Final Output Instructions

**Workflow:**
1. Extract PDF text to `/tmp/lab_text.txt` using `pdftotext` (mandatory — do not skip)
2. Load `Biomarkers.xlsx` → identify all out-of-range values using BloomCell functional ranges
3. Load `BloomCell key recommendations.xlsx` → map flagged biomarkers to recommendations and supportive tests
4. Apply BloomCell 4-Step Analysis Logic → identify patterns and severity scores
5. Load relevant MVP files (Nutrition, Recovery, Training; Wearable if applicable) → select top 3 strategies per category
> ⛔ At no point in steps 1–10 may web search be called or AI training knowledge be used to generate content. All values, ranges, recommendations, and rationale must trace to a loaded reference file.
6. Select 4 DIFFERENT markers for the 4 groups (verify no overlap before writing)
7. **For each of the 4 selected markers — run Step 1b grep to find exact label, Step 1c repr() to resolve special character encoding, then Step 1d verification. All 4 must return `✅ FOUND`. Apply Step 1e fallback for any that fail. Never proceed to step 8 until all 4 pass.**
8. Generate current timestamp and 8 unique UUIDs
9. Construct all 8 JSON objects following the exact structure above
10. Run pre-output validation checklist (all 15 items)
11. Output ONLY the JSON array — no explanatory text before or after

The response must be pure JSON parseable by any JSON parser.

---

## Example JSON Output

> **Note on example `"text"` values below:** These are illustrative of the *format* — realistic pdftotext extractions from tabular PDFs. Your actual values must come from YOUR PDF's raw extraction. Run the verification check before using any string.

```json
[
  {
    "id": "a1b2c3d4-e5f6-4789-a0bc-d1e2f3a4b5c6",
    "date": "05/27/25 10:30 AM",
    "type": "highlight",
    "text": "Free T3 3.0-4.0 pg/mL 2.4",
    "group": "Internal Notes",
    "rationale": "Free T3 is below BloomCell functional range (3.0–4.0 pg/mL), flagged as hypothyroid; suppressed cellular metabolism.",
    "referencesource": "Biomarkers.xlsx - Biomarkers sheet - Row 42, Columns Minimum/Maximum/Severity Score",
    "color": "#E05252",
    "bgColor": "#FEF2F2",
    "textColor": "#7F1D1D"
  },
  {
    "id": "b2c3d4e5-f6a7-4890-b1cd-e2f3a4b5c6d7",
    "date": "05/27/25 10:30 AM",
    "type": "note",
    "text": "Free T3 2.4 pg/mL — below functional range; hypothyroid pattern with suppressed T4 conversion - Dr. Smith",
    "group": "Internal Notes",
    "rationale": "Low Free T3 with elevated Reverse T3 suggests impaired T4→T3 conversion, likely HPA-driven. Check cortisol, selenium. Consider DUTCH Plus.",
    "referencesource": "3 M Health Check.docx - Page 2 | BloomCell key recommendations.xlsx - Key Blood Results sheet - Row 18",
    "color": "#E05252",
    "bgColor": "#FEF2F2",
    "textColor": "#7F1D1D"
  },
  {
    "id": "c3d4e5f6-a7b8-4901-c2de-f3a4b5c6d7e8",
    "date": "05/27/25 10:30 AM",
    "type": "highlight",
    "text": "Cholesterol 150-199 mg/dL 250",
    "group": "Understanding Your Results",
    "rationale": "Cholesterol elevated above BloomCell functional range (150–199 mg/dL), flagged for dyslipidemia; often thyroid-driven.",
    "referencesource": "Biomarkers.xlsx - Biomarkers sheet - Row 7, Columns Maximum/High",
    "color": "#EF9F27",
    "bgColor": "#FFF7ED",
    "textColor": "#9A3412"
  },
  {
    "id": "d4e5f6a7-b8c9-4012-d3ef-a4b5c6d7e8f9",
    "date": "05/27/25 10:30 AM",
    "type": "note",
    "text": "Your cholesterol is high, often caused by low thyroid slowing your metabolism. Fixing thyroid typically improves cholesterol.",
    "group": "Understanding Your Results",
    "rationale": "Elevated cholesterol with low Free T3 indicates thyroid-driven dyslipidemia. Often resolves with thyroid optimization and anti-inflammatory diet.",
    "referencesource": "BloomCell Narrative results.docx - Page 1 | BloomCell key recommendations.xlsx - Key Blood Results sheet - Row 7",
    "color": "#EF9F27",
    "bgColor": "#FFF7ED",
    "textColor": "#9A3412"
  },
  {
    "id": "e5f6a7b8-c9d0-4123-e4fa-b5c6d7e8f9a0",
    "date": "05/27/25 10:30 AM",
    "type": "highlight",
    "text": "Homocysteine <7 µmol/L 11.6",
    "group": "Priority Actions - Next 30 Days",
    "rationale": "Homocysteine significantly elevated above BloomCell optimal (<7 µmol/L), indicating methylation insufficiency and cardiovascular risk.",
    "referencesource": "Biomarkers.xlsx - Biomarkers sheet - Row 31, Columns Maximum/Severity Score/Impact Score",
    "color": "#1D9E75",
    "bgColor": "#ECFDF5",
    "textColor": "#065F46"
  },
  {
    "id": "f6a7b8c9-d0e1-4234-f5ab-c6d7e8f9a0b1",
    "date": "05/27/25 10:30 AM",
    "type": "note",
    "text": "Start methylated B-Complex daily. Request TPO/thyroglobulin antibodies. Eliminate gluten/dairy 30 days. Schedule liver ultrasound.",
    "group": "Priority Actions - Next 30 Days",
    "rationale": "High homocysteine requires methylated B-vitamins. Antibody testing rules out autoimmunity. Dietary changes reduce inflammation. Liver imaging warranted.",
    "referencesource": "BloomCell Recovery MVP v2.xlsx - Recovery Strategies sheet - Column 15 | BloomCell Nutrition MVP v11.xlsx - Nutrition Strategies sheet - Row 34",
    "color": "#1D9E75",
    "bgColor": "#ECFDF5",
    "textColor": "#065F46"
  },
  {
    "id": "a7b8c9d0-e1f2-4345-a6bc-d7e8f9a0b1c2",
    "date": "05/27/25 10:30 AM",
    "type": "highlight",
    "text": "SGOT (AST) 10-26 IU/L 83",
    "group": "Long-Term Strategy",
    "rationale": "Liver enzymes elevated above BloomCell functional range (AST/ALT 10–26 IU/L), indicating hepatic inflammation requiring sustained intervention.",
    "referencesource": "Biomarkers.xlsx - Biomarkers sheet - Row 19, Columns Maximum/Severity Score",
    "color": "#534AB7",
    "bgColor": "#F5F3FF",
    "textColor": "#4C1D95"
  },
  {
    "id": "b8c9d0e1-f2a3-4456-b7cd-e8f9a0b1c2d3",
    "date": "05/27/25 10:30 AM",
    "type": "note",
    "text": "Target Free T3 >3.0, LDL <100, homocysteine <7, AST <26. Retest: 6-8wks (thyroid, liver), 3mo (lipids), 6mo (full panel).",
    "group": "Long-Term Strategy",
    "rationale": "Thyroid optimization addresses dyslipidemia root cause. Methylation support lowers cardiovascular risk. Liver support reduces transaminase elevation over 90 days.",
    "referencesource": "Master Report April 2026 (2).docx - Page 5 | BloomCell key recommendations.xlsx - Key supportive Testing sheet - Row 11",
    "color": "#534AB7",
    "bgColor": "#F5F3FF",
    "textColor": "#4C1D95"
  }
]
```

---

## Medical Disclaimer

This skill provides educational analysis of laboratory data using the BloomCell clinical framework. It is not a substitute for medical advice, diagnosis, or treatment. All findings and recommendations should be reviewed by a qualified healthcare practitioner before implementation.