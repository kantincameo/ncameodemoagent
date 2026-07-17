# Extraction Rules & Field Mapping Reference

This file documents how to map messy real-world document labels onto the
fixed 23-field customer-record JSON schema, and how to convert raw text
into the correct JSON type for each field.

## Current Schema Fields & Common Label Variants

| JSON Key | Type | Common source labels |
|---|---|---|
| `businessId` | string | "Business ID", "Org ID", "Company ID" — usually only present in exports that already carry internal IDs; often not present in a plain form/document |
| `customerId` | string | "Customer ID", "Client ID", "Patient ID", "Member ID", "ID" |
| `externalCustomerId` | string | "External ID", "CRM ID", "Reference ID", "Ext. Customer ID" |
| `firstName` | string | "First Name", "Given Name" — or split from a combined "Name" field |
| `lastName` | string | "Last Name", "Surname", "Family Name" — or split from a combined "Name" field |
| `email` | string | "Email", "E-mail", "Email Address", "Email ID" |
| `phone` | string | "Phone", "Phone Number", "Contact No", "Mobile", "Mobile No", "Cell", "WhatsApp Number" |
| `dob` | string (date) | "DOB", "Date of Birth", "Birth Date" |
| `gender` | string | "Gender", "Sex" |
| `address` | string | "Address", "Home Address", "Residential Address" — combine street/city/state/zip into one string if they're separate fields, comma-separated |
| `primaryLocationId` | string | "Location ID", "Branch ID", "Clinic ID", "Preferred Location" |
| `joinedDate` | string (date) | "Joined Date", "Registration Date", "Signup Date", "Member Since", "Created On" |
| `lastVisitDate` | string (date) | "Last Visit", "Last Appointment Date", "Last Seen" |
| `totalVisits` | number | "Total Visits", "Visit Count", "No. of Visits" |
| `totalSpend` | number | "Total Spend", "Total Amount Spent", "Lifetime Spend" (if distinct from lifetimeValue) |
| `lifetimeValue` | number | "Lifetime Value", "LTV", "Customer Lifetime Value" |
| `activeMembershipId` | string | "Membership ID", "Active Membership", "Plan ID" |
| `activeMembershipTier` | string | "Membership Tier", "Plan", "Tier", "Membership Level" (e.g. "Gold", "Platinum") |
| `activePackageIds` | array of strings | "Package IDs", "Active Packages" — if the document lists multiple package names/IDs, put each as a string in this array |
| `tags` | array of strings | "Tags", "Labels", "Categories" — split comma/semicolon-separated tag lists into array items |
| `preferredContactMethod` | string | "Preferred Contact Method", "Contact Preference" (e.g. "email", "sms", "phone") |
| `marketingOptInEmail` | boolean | "Email Opt-in", "Marketing Emails", "Subscribe to Emails" — map yes/true/checked/subscribed → `true`, no/false/unchecked/unsubscribed → `false` |
| `marketingOptInSms` | boolean | "SMS Opt-in", "Marketing SMS", "Text Messages" — same yes/no → true/false mapping |
| `customAttributes` | object | Any other clearly-labeled key-value data that doesn't map to the fields above (e.g. "Referral Source: Instagram" → `{"referralSource": "Instagram"}`) |

> This table must be kept in sync with the "Output Schema" section of
> SKILL.md. When the user updates the schema, update this table too.

## Type Conversion Rules

- **Strings**: keep as written in the source. Don't reformat unless the
  field is explicitly a date (see below).
- **Dates** (`dob`, `joinedDate`, `lastVisitDate`): if the source date is
  unambiguous (e.g. "March 5, 2020" or "05/03/2020" with clear
  day/month/year context), convert to ISO `YYYY-MM-DD`. If the format is
  ambiguous (e.g. "03/05/2020" with no locale clue) or partial (only a
  year), keep the value exactly as written in the source rather than
  guessing which part is month vs day.
- **Numbers** (`totalVisits`, `totalSpend`, `lifetimeValue`): parse to
  a real JSON number, not a string. Strip currency symbols/commas
  (e.g. "$1,200.50" → `1200.5`). If not found, use `0`.
- **Booleans** (`marketingOptInEmail`, `marketingOptInSms`): map
  affirmative words/checkboxes (yes, true, checked, subscribed, opted-in,
  ✓) to `true`; negative/absent ones (no, false, unchecked, unsubscribed,
  opted-out) to `false`. If the document says nothing about a channel at
  all, default to `false` (don't assume opt-in).
- **Arrays** (`activePackageIds`, `tags`): if the source has a
  comma/semicolon/bullet-separated list, split it into individual string
  array items. If nothing is present, use `[]`.
- **Object** (`customAttributes`): only add keys here for genuinely
  extra structured info with no home elsewhere in the schema. Use
  camelCase keys inside it, consistent with the rest of the schema
  style. If nothing qualifies, use `{}`.

## Name Splitting

If the source has a single combined "Name" field instead of separate
first/last:
- Split on the last space: everything before the last word → `firstName`,
  the last word → `lastName`.
- Handle common prefixes/suffixes sensibly (e.g. "Dr. Ananya Verma" →
  firstName: "Dr. Ananya", lastName: "Verma" — keep the title attached
  to firstName rather than dropping it).
- If truly a single word or a non-personal name (e.g. a company name in
  a B2B context), put the whole value in `firstName` and leave
  `lastName` as `""`.

## Multi-Record Detection Heuristics

Treat a document as **multi-record** (→ multiple comma-separated
objects, no array brackets) when you see:
- A numbered or bulleted list of people
- A table/grid with a row per person and columns matching schema fields
- A spreadsheet where each row is clearly a different customer
- Multiple clearly delimited "cards"/sections, each describing one person

Treat a document as **single-record** (→ one plain object) when there is
exactly one person's information anywhere in the document.

## When a Field Genuinely Isn't Present

Use the type-appropriate empty value (`""`, `0`, `false`, `[]`, `{}` —
see the Field Types table in SKILL.md). Do not:
- Guess/hallucinate a plausible-looking value
- Use `null`, `"N/A"`, `"-"`, or omit the key
- Put a string in a numeric/boolean/array/object field "just to fill it"

## Output Discipline Checklist (apply before responding)

1. Is the entire response valid JSON content and nothing else (no prose, no fences)?
2. Every object has exactly the 23 schema keys, in schema order?
3. Every value matches its required type (string/number/boolean/array/object) — never a mismatched type, never `null`?
4. Multiple people → comma-separated standalone objects, **no `[`/`]` wrapper**? One person → a single plain object?

Run `scripts/validate_output.py` against your output before returning it
to double check keys, types, structure, and the no-array-brackets rule.
