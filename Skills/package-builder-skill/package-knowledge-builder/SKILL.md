---
name: package-knowledge-builder
description: >-
  Builds a business's Package Knowledge Base JSON by collecting service package details (via
  CSV upload or manual entry), linking each package's included services to the business's
  existing Service Knowledge Builder data, and generating a rich AI knowledge profile for
  every package. Use this skill whenever a user wants to set up, import, or build service
  packages / session packs / prepaid bundles for a business, mentions uploading a "package
  CSV" or "packages list", asks to generate a "package knowledge base", wants packages
  prepared for Cosmos DB, or says things like "set up my packages" or "import my packages and
  link them to my services." Works for any business/vertical, mirrors the same flow as the
  membership-knowledge-builder skill (with package expiry playing the role membership
  duration plays there), and pairs with service-knowledge-builder (packages reference that
  skill's services list to link "services included").
---

# Package Knowledge Builder

This skill turns a business's service packages (session packs, prepaid bundles, one-time
purchase packages, etc.) into one finished JSON file: a clean transactional record for each
package, plus a rich AI-written knowledge profile for each one. It follows the exact same
two-stage shape as `membership-knowledge-builder` — the one structural difference is that a
package has an **expiry** (how long it stays valid before unused credits/sessions are lost)
in the place where a membership has a **duration**. A package is typically a one-time
purchase (not a recurring subscription), while a membership recurs — that's the core
distinction to keep in mind while working through this skill.

The final JSON always has the exact same shape — see `references/target-schema.md` — so it
never changes structure between businesses.

Don't invent concrete facts (prices, expiry periods, fees) the user hasn't given you. It's
fine to write descriptive/marketing text for the knowledge profiles (that's the point), but
never guess a specific number or a service link — leave it `null`/`[]` and ask instead.

### Critical: Mandatory Field Validation

**NEVER invent or skip:**
- ❌ Prices, expiry, credit counts, or service links
- ❌ Ask instead of guessing

**ALWAYS do:**
- ✅ Flag missing mandatory fields with clear messages
- ✅ Ask user for missing data (e.g., "**Price is missing for 'Three Pack'. Please provide the price.**")
- ✅ Flag unmatched services, don't silently drop them

## Stage 1 — Collect package data

### 1a. Check for existing Service Knowledge Base

Ask the user whether they already have a Service Knowledge Builder output for this business
(the JSON containing `businessKnowledge` and `services`). This matters because a package's
"services included" should link to real, verified services rather than free text.

- If yes → ask them to upload/paste that JSON. Keep its `businessKnowledge` and `services`
  list on hand: `businessKnowledge` informs which extra questions are worth asking
  (Stage 1b), and `services` is the lookup list for linking included services (Stage 1c/1d).
- If no → continue without it. Included services stay as plain text (`serviceId: null`) since
  there's nothing to verify them against, and skip the business-context follow-up questions
  in manual entry.

### 1b. Choose entry mode

Ask the user whether they want to:
- Upload a Package CSV, or
- Enter package details manually

#### Manual entry

Collect these **four mandatory fields** per package:

1. **Package Name** (e.g., "10 lesson Pack", "5 Bay rental Bundle")
2. **Price** (numeric, strip $£€; e.g., 400, 750.00)
3. **Expiry** (e.g., "Never Expires", "30 Days", "6 Months", "Unlimited")
4. **Services Included** (at least one; e.g., "Single Lesson 30 min", "Bay rental 1 hour")

If a Service Knowledge Base is available (Stage 1a), match whatever they say for "services
included" against its `services` list (by name, case/whitespace-insensitive, allowing close
matches) and attach the real `serviceId`. If something doesn't match any known service, keep
it as free text and flag it to the user rather than silently dropping it.

**Optional:** Ask about online booking (`onlineBookingEnabled`: true for online, false for in-person only).
Default to `true` if user doesn't specify.

#### CSV upload

Read `references/column-mapping.md` for column aliases and validation rules. Map raw headers 
to target fields, then produce one package record per CSV row.

#### CSV Validation — Checking for Missing Data

**After parsing the CSV, check each package for the four mandatory fields:**

If any package is missing `packageName`, `price`, `expiryDuration`, or `services`, 
**ask the user explicitly:**

```
❌ MISSING DATA FOUND:

Package [packageName or "Row X"]:
  • Price is missing — please provide the price for this package
  • Expiry is missing — how long is this package valid? (e.g., "Never Expires", "30 Days")
  • Services are missing — which service(s) does this package include?

Please provide the missing information to continue.
```

**Do NOT proceed to Stage 2 until all four mandatory fields are complete for every package.**

### 1c. Fill gaps

After parsing (CSV or manual), check every package against the four mandatory fields:
package name, price, expiry, services included (with as many linked `serviceId`s as
possible).

- If a package is missing one of these fields entirely → ask the user only for that specific
  missing detail, for that specific package (don't re-collect fields you already have).
- If "services included" references services that don't exist anywhere in the Service
  Knowledge Base and you don't have one loaded yet (or the one you have seems incomplete) →
  ask the user whether they'd like to upload a Service Knowledge Builder CSV/JSON to resolve
  the links, or confirm they're fine leaving those as unlinked free text.

Don't move to Stage 2 until every package has all four mandatory fields.

## Stage 2 — Knowledge base creation & confirmation

### 2a. Generate package knowledge

For every package record, write a `packageKnowledge` entry — a knowledge profile covering
what the package is, who it's for, and why someone would choose it over paying per-visit.
Ground it in the package's actual fields (price, expiry, linked services, session counts)
and, if available, the business's `businessKnowledge` (industry, audience, tone) so the
writing fits the business. Field definitions are in `references/target-schema.md`. As with
the other knowledge-builder skills, write like a domain expert rather than a data-mapper —
avoid generic filler that could apply to any package at any business.

#### Field-by-Field Generation Guide

Write grounded, domain-specific text (not generic filler).

**summary** (2-4 sentences): Describe what package is, include quantity/price/expiry. Example: "A prepaid bundle of three 30-minute lessons at Par2Play, for $240, never expires."

**valueProposition** (1-2 sentences): Answer "Why buy instead of paying per-visit?" Reference package size.

**idealFor** (1-2 sentences): Target customer/use case. Avoid "everyone".

**includedServiceNames** (array): Linked service names from Service Knowledge Base.

**expirySummary** (1 sentence): Plain-language expiry reminder (e.g., "Never expires", "30-day window").

**commonQuestions** (3-4 questions): Plausible customer questions specific to this package type.

**keywords** (3-5 terms): Searchable terms customers use (e.g., "lesson package", "bundle", quantity).

**notes** (optional): Critical info (booking method, composition, unusual details). Leave empty if none.

### 2b. Show for review

Present a summary for the user to confirm:
- A table of parsed packages (name, price, expiry, linked services, any unlinked service
  names flagged)
- One or two sample `packageKnowledge` entries so they can see the style/quality

Ask them to confirm or tell you what to fix. Apply corrections and re-summarize as needed.
Do not produce the final file until they confirm.

### 2c. Produce the final JSON

Once confirmed, assemble the final combined JSON exactly as structured in
`references/target-schema.md` (`packages` + `packageKnowledge` — this top-level shape never
changes) and save it as a file for the user. Validate it first:

```bash
python3 scripts/validate_output.py <path-to-output.json>
```

It checks required top-level keys, that every `packages[].id` has a matching
`packageKnowledge[].packageId`, and that required fields aren't missing — it does not judge
writing quality, only structure. Fix anything it flags, then deliver the file to the user.

### Encoding & Format Validation

Before delivering the JSON file:
- **Character Encoding:** Ensure the file is saved as UTF-8 (no BOM unless the platform requires it)
- **Timestamps:** All `createdAt` and `updatedAt` fields must be ISO 8601 format 
  (e.g., `"2026-07-22T23:43:00.143057+00:00"`)
- **Validation:** The Python script checks structure only, not content quality. If the script passes, 
  the file is ready to use.
