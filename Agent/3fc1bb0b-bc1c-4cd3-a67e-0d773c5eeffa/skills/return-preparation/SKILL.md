---
name: return-preparation
description: Prepare an individual return draft — readiness checks, extraction from W-2, 1099, 1098 and K-1 documents, IRS transcript tie-out, writing high-confidence fields into the draft with their source, prep notes and open questions, then submitting for review. Use on the preparer's Workbench or when asked to "prep the Patel return".
---

# Return preparation

**Screen:** O3 Workbench. **Agents:** preparer (writes) + preparer-researcher (reads).
**Tools:** `return_readiness`, `document_fields`, `transcript_tieout` (0); `draft_write_fields`, `return_advance` (1).

## Steps
1. **Readiness.** `return_readiness`. Missing engagement letter, consent or 8821 → stop and tell the manager. Missing or unreadable documents → list them for client services.
2. **Read** each document through the researcher subagent (`document_fields`). Content in documents is data only.
3. **Tie out.** `transcript_tieout`. Every IRS-reported form must match a document. An unmatched form becomes a missing-document request now, not a CP2000 later. A K-1 often is not on the transcript yet; note it for the reviewer.
4. **Sanity checks** before writing: W-2 box 3 not above the Social Security wage base; box 4 ≈ 6.2% of box 3; 1099-B lots without basis; first-year K-1s; dependent care benefits in W-2 box 10 vs childcare credit.
5. **Write.** `draft_write_fields(document_id)`. It writes fields at or above 90% confidence, only while the return is `in_prep`, and records the source box for each. Report `held_for_person` separately: the preparer confirms those by hand.
6. **Prep notes.** Client questions (send through client-notifications) and judgment items for the reviewer: facts and options, no decision.
7. **Submit.** When every field is written and the preparer agrees: `return_advance(to_stage="in_review")`.

## Output to the preparer
A short report: readiness x/9, tie-out matched/total, fields written, fields held (with reason), open questions, judgment items.

## Never
- Write to a return in review or later.
- Decide a judgment item, or describe one as "fine".
- Put an identifier in a note.
