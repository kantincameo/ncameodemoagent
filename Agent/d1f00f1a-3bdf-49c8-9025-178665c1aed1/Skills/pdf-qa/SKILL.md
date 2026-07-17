---
name: pdf-qa
description: >
  Use this skill whenever the user wants to ask questions about a PDF document whose text content
  has already been extracted and provided as plain text. Triggers when the user pastes or uploads
  PDF text and asks one or more questions about it, or when they say things like "here is the PDF
  text, answer my questions", "I extracted the text from a PDF, can you help me understand it",
  "summarize this document and answer questions", "find information in this PDF text", or any
  request to query, interrogate, search, or extract facts from extracted PDF/document text.
  Also trigger when the user asks follow-up questions on already-provided document text.
  Do NOT use for non-text PDF tasks (merging, splitting, form filling) — use the pdf skill instead.
---

# PDF QA Skill

Answer user questions accurately and thoroughly from PDF content that has been provided as plain text.

## Bundled Resources

- `references/examples.md` — Example interactions for common question types. Read when unsure how to format an answer.
- `scripts/chunk_pdf_text.py` — CLI utility to split very large PDF text into overlapping chunks. Run when the user provides a text file too large to process at once.

---

## Workflow

### Step 1 — Receive and Index the Document

When PDF text is provided:
- Acknowledge receipt and briefly state what the document appears to be about (title, topic, rough length).
- Identify structural signals: section headers, numbered lists, tables (as text), footnotes, page markers.
- Do NOT summarize the entire document unprompted — wait for the user's question(s).

### Step 2 — Understand the Question

Before answering, classify the question type:

| Type | Description | Strategy |
|------|-------------|----------|
| **Factual lookup** | Specific fact, number, date, name | Find exact location, quote or paraphrase |
| **Synthesis** | Combining info from multiple sections | Identify all relevant passages, then synthesize |
| **Comparison** | Compare two entities/options | Extract both sides, then compare |
| **Summary** | Overview of section or whole doc | Identify key points, prioritize by importance |
| **Inference** | Conclusion not stated explicitly | State it's an inference, show reasoning |
| **Out of scope** | Not covered in the document | Clearly say it's not in the provided text |

### Step 3 — Answer

Structure answers according to complexity:

**Simple factual questions** → Direct 1–3 sentence answer, with the relevant quote or page/section reference if available.

**Complex or multi-part questions** → Use this format:
```
**Answer:** [Direct answer to the question]

**Supporting evidence:** [Quote or paraphrase the relevant text passage(s)]

**Source location:** [Section name / page number / paragraph if identifiable]
```

**Summaries** → Use concise bullet points or short paragraphs, covering main themes, key findings, and any important data.

---

## Key Rules

1. **Ground every claim in the text.** Do not add information from outside the provided document.
2. **Be explicit when uncertain.** If the document is ambiguous or incomplete, say so.
3. **Cite location when possible.** Reference section headers, page numbers, or paragraph context.
4. **Distinguish inference from fact.** Label any conclusion you draw that isn't explicitly stated.
5. **Handle multi-question inputs.** If the user asks several questions at once, answer each in a numbered list.
6. **Out-of-scope questions.** If the question cannot be answered from the text, say: _"This information does not appear in the provided document."_ Offer to answer what is available.
7. **Preserve the user's terms.** If they refer to "the agreement" or "the report", use the same language.

---

## Follow-Up Handling

After answering, check if the user might need:
- Clarification on a term or concept from the document
- A deeper dive into a specific section
- A structured summary or table of key points

Offer these naturally — e.g., _"Would you like a summary of the key findings?"_ or _"I can also pull together all the dates mentioned if that would help."_

---

## Edge Cases

| Situation | Handling |
|-----------|----------|
| Text is garbled / OCR noise | Note the quality issue; do your best; flag uncertain passages |
| Document is very long | Use `scripts/chunk_pdf_text.py` to split; answer per chunk |
| Question is vague | Ask one targeted clarifying question before answering |
| Multiple PDFs provided | Confirm which document the question refers to |
| User asks to generate a quiz | Generate Q&A pairs drawn from the text, with answers |
