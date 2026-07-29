# Customer Knowledge Builder — README

This Claude skill turns a business's customer list — plus what each customer has bought
(memberships and/or packages) — into a "knowledge base" JSON: clean transactional records
for customers and their purchases, plus a rich AI-written knowledge profile for every
customer. It pairs with `service-knowledge-builder`, `membership-knowledge-builder`, and
`package-knowledge-builder` — purchases link back to real membership/package plans, and their
benefits link back to real services, wherever possible.

---

## How it works (3 Stages)

**Stage 1 — Collect customer profiles**

1. Claude asks whether you want to **upload a Customer CSV** or **enter customers manually**.
2. Mandatory per customer: first name + last name, and at least one contact method (email or
   phone). Everything else (visits, spend, tags, etc.) is optional.

**Stage 2 — Collect membership/package purchases**

3. Claude asks whether you already have a Membership Knowledge Builder output and/or a
   Package Knowledge Builder output for this business — these are what purchases get matched
   against.
4. Claude asks whether you want to **upload a Customer Membership/Package CSV** or **enter
   purchases manually**.
5. For each purchase, Claude:
   - links it to the right customer (by email, phone, or name),
   - matches the plan name against your known memberships/packages — **if nothing matches,
     it's labeled `"Other"` rather than guessed**,
   - links included services back to your Service Knowledge Base where possible.
6. If anything mandatory is missing (customer link, plan name/"Other", start date, or
   benefits), Claude asks only for that specific missing detail.

**Stage 3 — Knowledge base creation & confirmation**

7. Claude generates a `customerKnowledge` profile for every customer — engagement level,
   value segment, active plans, preferred services, common questions, etc. — grounded in
   their actual profile and purchase history.
8. It shows you a table of customers plus sample knowledge entries for review.
9. You confirm or ask for changes.
10. Once confirmed, Claude produces the final combined JSON file and validates its structure
    before handing it to you.

---

## What you get (Final Output)

A single `.json` file with this fixed structure:

```json
{
  "customers": [
    {
      "id": "...",
      "firstName": "Michael",
      "lastName": "Turner",
      "email": "...",
      "activeMemberships": [
        { "membershipId": "...", "membershipName": "Silver Membership", "benefits": [...] }
      ],
      "...": "plus the rest of the profile fields (visits, spend, tags, etc.)"
    }
  ],
  "customerMemberships": [
    {
      "id": "...",
      "customerId": "matches customers[].id",
      "membershipPlanId": "real plan id, or null if unmatched",
      "membershipName": "real plan name, or \"Other\"",
      "planKind": "Membership | Package | Other",
      "startDate": "...",
      "membershipStatus": "Active",
      "benefits": [
        { "serviceNameRaw": "Bay rental 1 hour", "serviceId": "...", "totalCredits": 2, "redeemedCredits": 1, "...": "credit tracking" }
      ],
      "...": "plus the rest of the purchase fields (invoice, amounts, recurrence, etc.)"
    }
  ],
  "customerKnowledge": [
    {
      "customerId": "matches customers[].id",
      "customerName": "...",
      "summary": "2-4 line plain description",
      "engagementLevel": "...",
      "valueSegment": "...",
      "activePlans": ["Silver Membership"],
      "preferredServices": ["Bay rental 1 hour"],
      "commonQuestions": ["...", "..."],
      "keywords": ["...", "..."],
      "notes": "..."
    }
  ]
}
```

- `customers` and `customerKnowledge` are always 1:1 matched (joinable via `customerId`).
- `customerMemberships` can have several records per customer (one per plan they've bought),
  each linked back via `customerId`.
- Any purchase whose plan name doesn't match a known membership or package is labeled
  `"Other"` instead of being guessed or dropped.
- The full field-by-field explanation is in `references/target-schema.md`.
- The full CSV column-mapping and validation rules (for both the customer CSV and the
  membership/package CSV) are in `references/column-mapping.md`.
- You can check the final JSON yourself using `scripts/validate_output.py`:
  ```bash
  python3 scripts/validate_output.py output.json
  ```

---

## How to use the skill

1. Install the skill on your Claude profile (via the "Save skill" button on the zip/`.skill`
   file).
2. In a new chat, say something like: *"import my customers and link their memberships"* or
   *"build a customer knowledge base for [Business Name]."*
3. Claude will follow the three stages above and give you the final JSON file at the end.

This skill works best alongside `service-knowledge-builder`, `membership-knowledge-builder`,
and `package-knowledge-builder` — build those first (or have their outputs ready to upload)
so customer purchases link to real plans and services instead of falling back to "Other".
