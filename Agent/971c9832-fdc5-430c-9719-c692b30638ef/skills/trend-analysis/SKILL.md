---
name: trend-analysis
description: Compare any document or return line across the past three years for one household — find forms seen before but missing now, new issuers, and changes of 25% or more — and turn missing items into checklist requests. Use for "what changed", "anything missing compared to last year", "show me the Vanguard 1099-DIV over three years", and in every review packet.
---

# Trend analysis

**Screens:** C6 History (client), O7 Scan & trend, O4 Review (office).
**Tools:** `trend_compare` (0), `document_history` (0), `checklist_add_from_trend` (1).

## What it compares
Because documents are stored by client and year, the same document type from the same issuer lines up across years. For each, the key figure is compared:

| Document | Key figure |
| --- | --- |
| W-2 | Box 1 wages |
| 1099-INT | Box 1 interest |
| 1099-DIV | Box 1a ordinary dividends |
| 1099-B | Box 1d proceeds |
| 1098 | Box 1 mortgage interest |
| 1099-R | Box 1 distribution |
| 1040 (filed) | line 9 total income, plus every captured line |

## Flags and what to do with them
| Flag | Meaning | Action |
| --- | --- | --- |
| seen in prior years, missing this year | The household had this form in 2023 and/or 2024 and nothing yet for 2025 | Ask the client (`checklist_add_from_trend`, then client-notifications). The IRS almost certainly has it. |
| missing, not on checklist | Same, and nobody has asked yet | Add it unless a known life event explains it (job change, account closed). |
| new this year | First time this type from this issuer | Confirm it is the household's; check for a related missing form (a new W-2 often means an old one is missing). |
| ±25% vs last year | Large change in the key figure | Reviewer: needs a reason tied to a document in the packet. |

## Steps
1. `trend_compare(return_id)` → `documents` (each with a 3-year series and flags), `flagged`, `return_lines`.
2. For the preparer: turn "missing" flags into requests with `checklist_add_from_trend`, then say what was added.
3. For the reviewer: each ±25% flag becomes a line in "What moved, and why", with its cause.
4. For a client asking about one document: `document_history(doc_type=…, issuer=…)` and show the three values plainly. No interpretation of what it means for their taxes.

## Limits
- A new client has history only from the prior returns they brought in (onboarding captures the 1040 lines, not the underlying forms). Say when a comparison is thin.
- Trend flags are prompts, never conclusions. A missing form is "we don't have it yet", not "you forgot".
