---
name: service-knowledge-builder
description: >-
  Builds a business's complete "knowledge base" JSON by interviewing the user about their
  business (or reading their business URL), then importing a Services CSV and generating a
  detailed AI knowledge profile for every service. Use this skill whenever a user wants to
  onboard a business into a knowledge base, mentions uploading a "services CSV" or "services
  list" to build a profile/knowledge base, asks to generate "businessKnowledge" or
  "serviceKnowledge", wants services prepared for Cosmos DB or a similar document database,
  or says things like "set up my business profile and import my services." Works for any
  business/vertical (salons, clinics, gyms, spas, repair shops, consultancies, etc.) — it is
  not tied to any single client or CSV format, and intelligently maps whatever column names
  the uploaded CSV happens to use.
---

# Service Knowledge Builder

This skill turns a business + a raw services spreadsheet into one finished JSON file that
combines three things: who the business is, what each of its services literally is (the
transactional record), and a rich AI-written knowledge profile for each service (useful for
search, chatbots, or recommendation features). The final JSON always has the exact same
shape — see `references/target-schema.md` — so downstream systems can rely on it never
changing structure between businesses.

Follow the six stages below **in order**. Don't skip a stage or silently invent data the
user hasn't given you — if something is genuinely unknown, use `null` or an empty string/array
rather than guessing a specific fact (it's fine to write reasonable descriptive/marketing
text, since that's the point of "knowledge," but don't fabricate concrete facts like phone
numbers, addresses, or prices).

## Stage 1 — Collect business knowledge

Ask the user, in one message, to either:
- paste their business website URL, or
- describe their business in a few sentences (what it is, what it offers, who it serves)

If they give a URL, fetch and read it (and a couple of obvious sub-pages like "About" or
"Services" if linked) to understand the business. If they give a description instead, work
from that. Either way, use your judgement to also ask 1-2 short follow-ups only if something
important is missing and can't be inferred (e.g. industry is unclear) — don't interrogate them
with a long form.

From what you learn, produce a `businessKnowledge` object matching the fields in
`references/target-schema.md`. Anything you couldn't determine and the user didn't state
stays `null` (or `""`/`[]` for text/list fields) — never invent it.

## Stage 2 — Get the services CSV

Ask the user to upload their services CSV (or point you to it). Don't move on until you have
a file to read.

## Stage 3 — Parse & map the CSV

Read `references/column-mapping.md` before touching the CSV — it has the alias table for
resolving arbitrary column headers (e.g. "Svc Name", "Duration", "Tax Grp") to the fixed
target fields, plus the row → JSON mapping rules. CSV column names vary wildly between
businesses, so never assume the raw headers match the target field names directly; always run
them through the mapping step first, and log the resolved `"<raw>" → "<target>"` mapping so
the user (and you) can sanity-check it.

Produce one service record per valid CSV row, per the fixed schema in
`references/target-schema.md`. Skip and report any row missing a service name.

## Stage 4 — Generate serviceKnowledge

For every service record produced in Stage 3, write a `serviceKnowledge` entry: a short
plain-language profile of that specific service, informed by the service's own fields
(name, category, duration, etc.) **and** the `businessKnowledge` from Stage 1 (so the tone,
audience, and context match the business). Field definitions are in
`references/target-schema.md`.

This is the one place in the whole pipeline where you should think like a domain writer, not
a data-mapper — a generic one-line restatement of the service name isn't useful. Ground each
profile in what you actually know: the service's category/subcategory, typical duration, and
the business's stated industry and audience. Where you're inferring rather than being told
something (e.g. "commonQuestions" a customer might ask), that's expected and fine — it's
knowledge generation, not extraction — but keep it plausible for the specific service and
business, not generic filler that would apply to any business.

## Stage 5 — Confirm with the user

Before producing the final file, show the user a summary for review:
- The `businessKnowledge` object (or its key fields)
- A table of the parsed services (name, category, duration, price if any) — flag any skipped
  rows and why
- One or two sample `serviceKnowledge` entries so they can see the style/quality

Ask them to confirm, or tell you what to fix. Apply any corrections and re-summarize if
needed. Do not generate the final combined file until they confirm.

## Stage 6 — Produce the final JSON

Once confirmed, assemble the single combined JSON exactly as structured in
`references/target-schema.md` (`businessKnowledge`, `services`, `serviceKnowledge` — that
top-level shape never changes) and save it as a file for the user. Use
`scripts/validate_output.py` to sanity-check the structure before handing it over:

```bash
python3 scripts/validate_output.py <path-to-output.json>
```

It checks required top-level keys, that every `services[].id` has a matching
`serviceKnowledge[].serviceId`, and that required fields aren't missing — it does not judge
writing quality, only structure. Fix anything it flags, then deliver the file to the user.
