# Package Knowledge Builder — README

This Claude skill turns a business's service packages (session packs, prepaid bundles,
one-time purchase packages, etc.) into a "knowledge base" JSON — a clean transactional record
for each package, plus a rich AI-written knowledge profile for each one. It follows the exact
same two-stage flow as `membership-knowledge-builder`, with one difference: a package has an
**expiry** (how long it stays valid before it expires) where a membership has a **duration**.
It's designed to pair with `service-knowledge-builder`: a package's included services get
linked to that skill's real service records instead of staying as plain text.

---

## How it works (2 Stages)

**Stage 1 — Collect package data**

1. Claude first asks whether you already have a Service Knowledge Builder output (the JSON
   with `businessKnowledge` + `services`) for this business. If you do, it uses that to link
   packages to real services and to inform extra questions. If not, it continues without it —
   included services just stay as plain text.
2. Claude asks whether you want to **upload a Package CSV** or **enter packages manually**.
   - **Manual entry:** Claude asks for the four mandatory fields per package — name, price,
     expiry, and services included — plus a few optional extras if relevant to your business.
   - **CSV upload:** Claude reads the file, maps whatever column names it uses to the fixed
     schema, and matches each mentioned service against your Service Knowledge Base to link
     it properly.
3. If anything mandatory is missing for a specific package, Claude asks only for that missing
   detail (or asks you to upload a services file if service links can't be resolved) — it
   won't re-ask things it already has.

**Stage 2 — Knowledge base creation & confirmation**

4. Claude generates a `packageKnowledge` profile for every package — summary, value
   proposition, who it's ideal for, an expiry reminder, common questions, keywords, etc. —
   grounded in the package's actual price/expiry/linked services and, if available, your
   business context.
5. It shows you a table of packages plus sample knowledge entries for review.
6. You confirm or ask for changes.
7. Once confirmed, Claude produces the final combined JSON file and validates its structure
   before handing it to you.

---

## What you get (Final Output)

A single `.json` file with this fixed structure:

```json
{
  "packages": [
    {
      "id": "...",
      "packageName": "10 Session Pack",
      "price": 750.0,
      "expiryDuration": "6 Months",
      "benefits": [
        { "serviceNameRaw": "Massage", "serviceId": "uuid-or-empty", "totalCredits": 10 }
      ],
      "...": "plus the rest of the transactional fields (booking flags, has* flags, etc.)"
    }
  ],
  "packageKnowledge": [
    {
      "packageId": "matches packages[].id",
      "packageName": "...",
      "summary": "2-4 line plain description",
      "valueProposition": "...",
      "idealFor": "...",
      "includedServiceNames": ["Massage"],
      "expirySummary": "...",
      "commonQuestions": ["...", "..."],
      "keywords": ["...", "..."],
      "notes": "..."
    }
  ]
}
```

- `packages` and `packageKnowledge` are always 1:1 matched (joinable via `packageId`).
- `expiryDuration` (how long the package stays valid) is the package-side equivalent of a
  membership's `membershipDuration` — packages are normally one-time purchases, not recurring
  subscriptions, so there's no `billingCycle` here.
- Every service a package includes is matched against your Service Knowledge Base where
  possible, so `serviceId` points to a real service instead of a loose text string.
- The full field-by-field explanation is in `references/target-schema.md`.
- The full CSV column-mapping and validation rules are in `references/column-mapping.md`.
- You can check the final JSON yourself using `scripts/validate_output.py`:
  ```bash
  python3 scripts/validate_output.py output.json
  ```

---

## How to use the skill

1. Install the skill on your Claude profile (via the "Save skill" button on the zip/`.skill`
   file).
2. In a new chat, say something like: *"set up packages for [Business Name]"* or *"import
   this package CSV and link it to my services."*
3. Claude will follow the two stages above and give you the final JSON file at the end.

This skill works best alongside `service-knowledge-builder` — build the service knowledge
base first (or have it ready to upload) so package benefits link to real services.
