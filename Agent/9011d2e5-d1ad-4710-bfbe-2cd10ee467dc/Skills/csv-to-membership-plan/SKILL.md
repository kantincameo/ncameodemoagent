---
name: membership-knowledge-builder
description: >
  Builds a business's Membership Knowledge Base JSON by collecting membership plan details
  (via CSV upload or manual entry), linking each membership's included services to the
  business's existing Service Knowledge Builder data, and generating a rich AI knowledge
  profile for every membership. Use this skill whenever a user wants to set up, import, or
  build membership plans / membership tiers for a business, mentions uploading a "membership
  CSV" or "membership list", asks to generate a "membership knowledge base", wants
  memberships prepared for Cosmos DB, or says things like "set up my membership plans" or
  "import my memberships and link them to my services." Works for any business/vertical and
  pairs with the service-knowledge-builder skill (memberships reference that skill's
  services list to link "services included").
---

# Membership Knowledge Builder

This skill turns a business's membership plans (gym memberships, salon packages, subscription
tiers, etc.) into one finished JSON file: a clean transactional record for each membership
plan, plus a rich AI-written knowledge profile for each one. It follows the same two-stage
shape as the companion `service-knowledge-builder` skill, and the two are meant to work
together — a membership's "services included" should link back to real services from that
skill's output whenever possible, rather than staying as free-text names.

The final JSON always has the exact same shape — see `references/target-schema.md` — so it
never changes structure between businesses.

Don't invent concrete facts (prices, durations, fees) the user hasn't given you. It's fine to
write descriptive/marketing text for the knowledge profiles (that's the point), but never
guess a specific number or a service link — leave it `null`/`[]` and ask instead.

## Stage 1 — Collect membership data

### 1a. Check for existing Service Knowledge Base

Ask the user whether they already have a Service Knowledge Builder output for this business
(the JSON containing `businessKnowledge` and `services`). This matters because membership
"services included" should link to real, verified services rather than free text.

- If yes ⇒ ask them to upload/paste that JSON. Keep its `businessKnowledge` and `services`
  list on hand for the rest of this skill: `businessKnowledge` informs which extra questions
  are worth asking (Stage 1b), and `services` is the lookup list for linking included
  services (Stage 1c/1d).
- If no ⇒ continue without it. Included services will stay as plain text (`serviceId: null`)
  since there's nothing to verify them against, and skip the business-context follow-up
  questions in manual entry.

### 1b. Choose entry mode

Ask the user whether they want to:
- Upload a Membership CSV, or
- Enter membership details manually

#### Manual entry

Ask for these **mandatory** fields for each membership:
1. Membership name
2. Price
3. Duration (how long the membership lasts, e.g. "1 Month", "Annual", "Ongoing" — this is
   separate from billing cycle/frequency)
4. Services included

If a Service Knowledge Base is available (Stage 1a), match whatever they say for "services
included" against its `services` list (by name, case/whitespace-insensitive, allowing close
matches) and attach the real `serviceId`. If something doesn't match any known service, keep
it as free text and flag it to the user rather than silently dropping it.

You may also ask a handful of additional relevant questions (billing cycle, setup fee, guest
passes, whether it auto-renews, etc.) informed by the `businessKnowledge` industry/type if one
is available — but never require more than the four mandatory fields above to proceed.

#### CSV upload

Read `references/column-mapping.md` before touching the CSV — it has the alias table for
resolving arbitrary column headers to the fixed target fields (this covers the full
MembershipPlan schema, not just the four mandatory ones), plus the per-field validation/
default rules. CSV column names vary between businesses, so always run raw headers through
the mapping step first, and log the resolved `"<raw>" ⇒ "<target>"` mapping.

Produce one membership record per valid CSV row. For the "services included" / benefits
column specifically: split it into individual service names and match each one against the
Service Knowledge Base's `services` list (Stage 1a) the same way as in manual entry, attaching
`serviceId` wherever there's a confident match.

### 1c. Fill gaps

After parsing (CSV or manual), check every membership against the four mandatory fields:
membership name, price, duration, services included (with as many linked `serviceId`s as
possible).

- If a membership is missing one of these fields entirely ⇒ ask the user only for that
  specific missing detail, for that specific membership (don't re-collect fields you already
  have).
- If "services included" references services that don't exist anywhere in the Service
  Knowledge Base and you don't have one loaded yet (or the one you have seems incomplete) ⇒
  ask the user whether they'd like to upload a Service Knowledge Builder CSV/JSON to resolve
  the links, or confirm they're fine leaving those as unlinked free text.

Don't move to Stage 2 until every membership has all four mandatory fields.

## Stage 2 — Knowledge base creation & confirmation

### 2a. Generate membership knowledge

For every membership record, write a `membershipKnowledge` entry — a knowledge profile
covering what the membership is, who it's for, and why someone would choose it. Ground it in
the membership's actual fields (price, duration, linked services, fees) and, if available,
the business's `businessKnowledge` (industry, audience, tone) so the writing fits the
business. Field definitions are in `references/target-schema.md`. As with the Service
Knowledge Builder, this is the one place to write like a domain expert rather than a
data-mapper — avoid generic filler that could apply to any membership at any business.

### 2b. Show for review

Present a summary for the user to confirm:
- A table of parsed memberships (name, price, duration, linked services, any unlinked
  service names flagged)
- One or two sample `membershipKnowledge` entries so they can see the style/quality

Ask them to confirm or tell you what to fix. Apply corrections and re-summarize as needed.
Do not produce the final file until they confirm.

### 2c. Produce the final JSON

Once confirmed, assemble the final combined JSON exactly as structured in
`references/target-schema.md` (`memberships` + `membershipKnowledge` — this top-level shape
never changes) and save it as a file for the user. Validate it first:

```bash
python3 scripts/validate_output.py <path-to-output.json>
```

It checks required top-level keys, that every `memberships[].id` has a matching
`membershipKnowledge[].membershipId`, and that required fields aren't missing — it does not
judge writing quality, only structure. Fix anything it flags, then deliver the file to the
user.