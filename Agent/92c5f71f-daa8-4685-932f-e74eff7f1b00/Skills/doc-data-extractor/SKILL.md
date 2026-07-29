---
name: customer-knowledge-builder
description: >-
  Builds a business's Customer Knowledge Base JSON by collecting customer profile data (CSV
  or manual entry), then each customer's membership/package purchases (CSV or manual entry),
  linking purchases to the right customer and plan (falling back to "Other" if a plan name
  doesn't match), and generating an AI knowledge profile per customer. Use whenever a user
  wants to set up, import, or build a customer database/knowledge base, mentions a "customer
  CSV" or "customer membership CSV", asks to generate "customerKnowledge", wants customers
  prepared for Cosmos DB, or says things like "import my customers and link their
  memberships." Mirrors the staged flow of service-knowledge-builder,
  membership-knowledge-builder, and package-knowledge-builder, and pairs with all three.
---

# Customer Knowledge Builder

This skill turns a business's customer list — plus what each customer has bought (memberships
and/or packages) — into one finished JSON file: clean transactional records, and a rich
AI-written knowledge profile for every customer. It follows the same staged shape as the
other knowledge-builder skills, but has two data-collection stages instead of one, because a
customer record and a customer's membership/package purchases are collected and validated
separately before being tied together.

The final JSON always has the exact same shape — see `references/target-schema.md` — so it
never changes structure between businesses.

Don't invent concrete facts (spend totals, dates, plan names) the user hasn't given you. It's
fine to write descriptive/analytical text for the knowledge profiles (that's the point), but
never guess a specific number or a plan/service link — leave it `null`/`[]`/`"Other"` and ask
instead.

## Stage 1 — Collect customer profiles

Ask the user whether they want to:
- Upload a Customer CSV, or
- Enter customers manually

For each customer, the **mandatory** fields are:
1. First name and last name
2. At least one contact method — email or phone

#### Manual entry
Ask for the mandatory fields above, then optionally the rest of the profile
(`references/target-schema.md` has the full field list) if the user wants to provide it —
never block on anything beyond the mandatory fields.

#### CSV upload
Read `references/column-mapping.md` before touching the CSV — it has the alias table for
resolving arbitrary column headers to the fixed customer fields, plus per-field
validation/default rules. Log the resolved `"<raw>" → "<target>"` mapping. Produce one
customer record per valid row; a row missing both name and any contact method is invalid —
skip it and report it to the user.

## Stage 2 — Collect membership/package purchases

### 2a. Check for existing plan knowledge bases

Ask the user whether they already have a Membership Knowledge Builder output and/or a
Package Knowledge Builder output for this business (the JSON containing `memberships[]` /
`packages[]`). These are the lookup lists used to link each purchase to a real plan. If
neither is available, purchases can still be recorded, but plan names will fall back to
`"Other"` (see 2c) since there's nothing to verify them against.

### 2b. Choose entry mode

Ask the user whether they want to:
- Upload a Customer Membership/Package CSV, or
- Enter purchases manually

**Mandatory** fields for each purchase record:
1. Which customer it belongs to (name, email, or phone — enough to match against Stage 1's
   customers)
2. Membership or package name (or confirmation that it doesn't match a known plan — see 2c)
3. Start date (when the membership/package began)
4. Benefits — the services included, ideally linked to real services

#### Manual entry
Ask for the mandatory fields above per purchase. Optionally ask a few more relevant fields
(sale amount, status, expiry/next recurrence, invoice number) if useful — never require more
than the four mandatory fields to proceed.

#### CSV upload
Read `references/column-mapping.md` for the purchase-record alias table and defaults. Produce
one purchase record per valid row.

### 2c. Link customer, plan, and services

For every purchase record:
- **Customer link:** match against Stage 1's customers by email, then phone, then full name
  (in that priority order). If no confident match → flag it and ask the user which customer
  it belongs to (or whether to add it as a new customer).
- **Plan link:** match the given membership/package name against the loaded
  `memberships[]`/`packages[]` lists (case/whitespace-insensitive, allowing close matches).
  If matched → use that plan's real id and name. **If no match is found (or no plan knowledge
  base was loaded at all) → set the plan name to `"Other"`** and leave the plan id `null`,
  rather than inventing or guessing a plan.
- **Service links (benefits):** match each benefit's service name against
  service-knowledge-builder's `services` list the same way as in the other knowledge-builder
  skills — linked `serviceId` where confident, otherwise kept as free text.

### 2d. Fill gaps

Check every purchase against the four mandatory fields. If something's missing or a link
couldn't be resolved, ask the user only for that specific missing detail on that specific
purchase — don't re-collect things you already have. Don't move to Stage 3 until every
purchase has all four mandatory fields (with "Other" counting as a valid, complete plan
name when nothing matched).

## Stage 3 — Knowledge base creation & confirmation

### 3a. Generate customer knowledge

For every customer, write a `customerKnowledge` entry summarizing who they are as a
customer: engagement level, what they tend to buy, how they use their memberships/packages,
and what might be relevant to know when serving them. Ground it in the customer's actual
profile fields and linked purchases (not invented specifics). Field definitions are in
`references/target-schema.md`. Write like a domain expert, not a data-mapper — avoid generic
filler that could apply to any customer.

### 3b. Show for review

Present a summary for the user to confirm:
- A table of parsed customers (name, contact, active memberships/packages, any unmatched
  "Other" purchases flagged)
- One or two sample `customerKnowledge` entries so they can see the style/quality

Ask them to confirm or tell you what to fix. Apply corrections and re-summarize as needed.
Do not produce the final file until they confirm.

### 3c. Produce the final JSON

Once confirmed, assemble the final combined JSON exactly as structured in
`references/target-schema.md` (`customers` + `customerMemberships` + `customerKnowledge` —
this top-level shape never changes) and save it as a file for the user. Validate it first:

```bash
python3 scripts/validate_output.py <path-to-output.json>
```

It checks required top-level keys, that every `customers[].id` has a matching
`customerKnowledge[].customerId`, that every `customerMemberships[].customerId` points to a
real customer, and that required fields aren't missing — it does not judge writing quality,
only structure. Fix anything it flags, then deliver the file to the user.
