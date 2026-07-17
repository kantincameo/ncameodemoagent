---
name: csv-to-membership-plan
description: >-
  Read an uploaded CSV file, intelligently map its columns to the MembershipPlan target JSON
  structure, apply validation rules, and generate a ready-to-save JSON document. Use this skill
  whenever a user uploads a CSV and wants to convert it into a MembershipPlan JSON, map membership
  data from a spreadsheet, transform CSV columns to a target plan structure, or says things like
  "I uploaded a CSV", "map this CSV to the membership plan", "convert this spreadsheet to JSON",
  "process this membership data", "import membership plans", or "here is my CSV file". Always
  invoke this skill before saving to Cosmos DB. Never skip this skill when a CSV file is present.
---

# CSV to MembershipPlan Mapper

You are responsible for reading an uploaded CSV file, intelligently mapping its columns to the
MembershipPlan target JSON structure, applying validations, and producing a final output JSON.
You do NOT save to Cosmos DB — that is handled by the agent after you return the JSON.

---

## Target JSON Structure

```json
{
  "id": "plan_silver_loc001",
  "businessId": "b_8f3a2e10-4c21-4b7a-9d2e-1a2b3c4d5e6f",
  "planId": "plan_silver_loc001",
  "locationId": "loc_001",
  "externalMembershipId": "66962067-80fa-4275-9071-3d95dacbb8a5",

  "membershipName": "Silver Membership",
  "membershipCode": "SLVMEM",
  "membershipTypeKind": "Recurring",
  "descriptionRaw": "30% discount on Bay rental",

  "price": 200.0000,
  "priceSource": "FromSourceFile",
  "billingCycle": "Monthly",
  "isUnlimited": false,

  "setupFee": 0.0000,
  "annualFee": 0.0000,
  "declineFee": 0.0000,
  "buyOutFee": 0.0000,
  "freezeFee": 0.0000,
  "downgradeFee": null,
  "upgradeFee": null,
  "guestPassFee": 0.0000,
  "guestPassVisits": 0,
  "initialRecognition": 0,
  "monthlyRecognition": 200,
  "freeServiceRecognition": 0,
  "creditAmount": 0.0,
  "serviceCreditAmount": 0.0,
  "productCreditAmount": 0.0,
  "otherCreditAmount": 0.0,
  "serviceCreditEqualanceAmount": 0.0,
  "numVisits": 0,
  "advanceBookingDays": 0,
  "saleStartDate": null,
  "membershipInvoiceDate": null,
  "addOnMemberTemplateId": null,
  "membershipCancelTemplateId": null,
  "redemptionCenterTemplateId": null,
  "centerTaxId": null,
  "centerAssigned": true,
  "soldInCenter": true,

  "benefits": [
    {
      "serviceNameRaw": "Bay rental 1 hour",
      "serviceId": "svc_001",
      "totalCredits": 2
    }
  ],

  "isActive": true,
  "createdAt": "2026-07-13T11:35:00Z",
  "updatedAt": "2026-07-13T11:35:00Z",
  "_etag": null,
  "_ts": null
}
```

---

## Step 1 — Read the CSV

Parse the uploaded CSV file in full. Extract all column headers and all row data.
If multiple rows exist, generate one JSON document per row.
Handle quoted fields, commas within fields, and UTF-8 encoding gracefully.

---

## Step 2 — Intelligent Column Mapping

Map each CSV column to its target field using semantic similarity — not exact name matching.
A column does not need to match exactly. Use your understanding of naming conventions,
abbreviations, and domain context to find the best match.

Use this mapping guide:

| Target Field                    | Likely CSV Column Names (examples, not exhaustive)                                        |
|---------------------------------|-------------------------------------------------------------------------------------------|
| `id`                            | id, planId, plan_id, uid, identifier, record_id                                           |
| `planId`                        | planId, plan_id, id, uid, plan_identifier                                                 |
| `businessId`                    | businessId, business_id, biz_id, orgId, organization_id, company_id                      |
| `locationId`                    | locationId, location_id, loc_id, site_id, branch_id                                      |
| `externalMembershipId`          | externalMembershipId, external_id, ext_membership_id, external_membership_id             |
| `membershipName`                | membershipName, name, title, planName, plan_name, MemName, membership                    |
| `membershipCode`                | membershipCode, code, plan_code, short_code, sku, abbreviation                           |
| `membershipTypeKind`            | membershipTypeKind, type, kind, membershipType, plan_type, category                      |
| `descriptionRaw`                | descriptionRaw, description, desc, details, summary, notes, about                        |
| `price`                         | price, cost, amount, fee, rate, monthly_price, plan_price, value                         |
| `priceSource`                   | priceSource, price_source, pricing_type, source                                          |
| `billingCycle`                  | billingCycle, billing_cycle, frequency, interval, period, cycle, term                    |
| `isUnlimited`                   | isUnlimited, unlimited, is_unlimited, no_limit                                           |
| `setupFee`                      | setupFee, setup_fee, initiation_fee, enrollment_fee                                      |
| `annualFee`                     | annualFee, annual_fee, yearly_fee                                                        |
| `declineFee`                    | declineFee, decline_fee, failed_payment_fee                                              |
| `buyOutFee`                     | buyOutFee, buyout_fee, buy_out_fee, cancellation_fee                                     |
| `freezeFee`                     | freezeFee, freeze_fee, hold_fee, pause_fee                                               |
| `downgradeFee`                  | downgradeFee, downgrade_fee                                                              |
| `upgradeFee`                    | upgradeFee, upgrade_fee                                                                  |
| `guestPassFee`                  | guestPassFee, guest_pass_fee, guest_fee, visitor_fee                                     |
| `guestPassVisits`               | guestPassVisits, guest_pass_visits, guest_visits, visitor_count                          |
| `initialRecognition`            | initialRecognition, initial_recognition, upfront_recognition                             |
| `monthlyRecognition`            | monthlyRecognition, monthly_recognition, recurring_recognition                           |
| `freeServiceRecognition`        | freeServiceRecognition, free_service_recognition, free_recognition                       |
| `creditAmount`                  | creditAmount, credit_amount, total_credit                                                |
| `serviceCreditAmount`           | serviceCreditAmount, service_credit_amount, service_credit                               |
| `productCreditAmount`           | productCreditAmount, product_credit_amount, product_credit                               |
| `otherCreditAmount`             | otherCreditAmount, other_credit_amount, other_credit                                     |
| `serviceCreditEqualanceAmount`  | serviceCreditEqualanceAmount, service_credit_equivalence, credit_equivalence             |
| `numVisits`                     | numVisits, num_visits, visit_count, visits, allowed_visits                               |
| `advanceBookingDays`            | advanceBookingDays, advance_booking_days, booking_advance, booking_days                  |
| `saleStartDate`                 | saleStartDate, sale_start_date, start_date, available_from                               |
| `membershipInvoiceDate`         | membershipInvoiceDate, invoice_date, billing_date, membership_invoice_date               |
| `addOnMemberTemplateId`         | addOnMemberTemplateId, add_on_template_id, addon_template                                |
| `membershipCancelTemplateId`    | membershipCancelTemplateId, cancel_template_id, cancellation_template                    |
| `redemptionCenterTemplateId`    | redemptionCenterTemplateId, redemption_template_id, redemption_template                  |
| `centerTaxId`                   | centerTaxId, center_tax_id, tax_id, tax_code                                             |
| `centerAssigned`                | centerAssigned, center_assigned, assigned_to_center                                      |
| `soldInCenter`                  | soldInCenter, sold_in_center, center_sale, in_center_sale                                |
| `isActive`                      | isActive, active, status, enabled, is_active, live, published                            |
| `benefits`                      | benefits, defaultBenefits, services, perks, inclusions, extras                           |
| `serviceNameRaw`                | serviceNameRaw, service_name, serviceName, benefit_name, service                         |
| `serviceId`                     | serviceId, service_id, svc_id, benefit_id, service_code                                  |
| `totalCredits`                  | totalCredits, credits, total_credits, credit_count, sessions, uses                       |

If a column name is ambiguous, use context from surrounding columns and row values to determine
the best mapping. If a column clearly cannot map to any target field, discard it gracefully
without error.

---

## Step 3 — Validation Rules

Apply these rules to every mapped record before generating output:

| Field                          | Rule                                                                                                      |
|--------------------------------|-----------------------------------------------------------------------------------------------------------|
| `price`                        | Must be a number ≥ 0. If missing, empty, or non-numeric → default to `0`.                                |
| `isActive`                     | Must be boolean. Map "true"/"yes"/"1"/"active"/"enabled" → `true`; anything else → `false`.              |
| `membershipTypeKind`           | If missing or empty → default to `"Recurring"`.                                                           |
| `billingCycle`                 | If missing or empty → default to `"Monthly"`.                                                             |
| `priceSource`                  | If missing or empty → default to `"FromSourceFile"`.                                                      |
| `isUnlimited`                  | Must be boolean. If missing → default to `false`.                                                         |
| `setupFee`                     | Must be a number ≥ 0. If missing → default to `0`.                                                        |
| `annualFee`                    | Must be a number ≥ 0. If missing → default to `0`.                                                        |
| `declineFee`                   | Must be a number ≥ 0. If missing → default to `0`.                                                        |
| `buyOutFee`                    | Must be a number ≥ 0. If missing → default to `0`.                                                        |
| `freezeFee`                    | Must be a number ≥ 0. If missing → default to `0`.                                                        |
| `downgradeFee`                 | If missing or empty → default to `null`.                                                                  |
| `upgradeFee`                   | If missing or empty → default to `null`.                                                                  |
| `guestPassFee`                 | Must be a number ≥ 0. If missing → default to `0`.                                                        |
| `guestPassVisits`              | Must be an integer ≥ 0. If missing → default to `0`.                                                      |
| `initialRecognition`           | Must be a number ≥ 0. If missing → default to `0`.                                                        |
| `monthlyRecognition`           | Must be a number ≥ 0. If missing → default to `0`.                                                        |
| `freeServiceRecognition`       | Must be a number ≥ 0. If missing → default to `0`.                                                        |
| `creditAmount`                 | Must be a number ≥ 0. If missing → default to `0`.                                                        |
| `serviceCreditAmount`          | Must be a number ≥ 0. If missing → default to `0`.                                                        |
| `productCreditAmount`          | Must be a number ≥ 0. If missing → default to `0`.                                                        |
| `otherCreditAmount`            | Must be a number ≥ 0. If missing → default to `0`.                                                        |
| `serviceCreditEqualanceAmount` | Must be a number ≥ 0. If missing → default to `0`.                                                        |
| `numVisits`                    | Must be an integer ≥ 0. If missing → default to `0`.                                                      |
| `advanceBookingDays`           | Must be an integer ≥ 0. If missing → default to `0`.                                                      |
| `saleStartDate`                | If missing or empty → default to `null`.                                                                  |
| `membershipInvoiceDate`        | If missing or empty → default to `null`.                                                                  |
| `addOnMemberTemplateId`        | If missing or empty → default to `null`.                                                                  |
| `membershipCancelTemplateId`   | If missing or empty → default to `null`.                                                                  |
| `redemptionCenterTemplateId`   | If missing or empty → default to `null`.                                                                  |
| `centerTaxId`                  | If missing or empty → default to `null`.                                                                  |
| `centerAssigned`               | Must be boolean. If missing → default to `true`.                                                          |
| `soldInCenter`                 | Must be boolean. If missing → default to `true`.                                                          |
| `totalCredits`                 | Must be an integer ≥ 0. If missing or invalid → default to `0`.                                           |
| `_etag`                        | Always set to `null`.                                                                                     |
| `_ts`                          | Always set to `null`.                                                                                     |
| `createdAt`                    | Always set to current UTC datetime in ISO 8601 format (e.g. `"2025-01-15T10:30:00Z"`).                   |
| `updatedAt`                    | Always set to the exact same value as `createdAt`.                                                        |
| `id`                           | If missing → generate as `"plan_" + membershipCode.toLowerCase()` or a short UUID-like key.              |
| `planId`                       | If missing → use the same value as `id`.                                                                  |
| `benefits`                     | If no benefits data is found in the CSV → set to `[]`.                                                    |
| `businessId`                   | If missing → keep as empty string `""`.                                                                   |
| `locationId`                   | If missing → keep as empty string `""`.                                                                   |
| `externalMembershipId`         | If missing → keep as empty string `""`.                                                                   |

---

## Step 4 — Output

Produce the final JSON for each CSV row. Format it cleanly and completely.

- If the CSV had **multiple rows** → output a JSON **array** of objects.
- If the CSV had a **single row** → output a single JSON **object**.

Present the output inside a code block labeled `json`.

After presenting the output, state clearly:
> ✅ Mapping complete. [N] record(s) ready.

Do NOT invoke `cosmos_create_document` or any Cosmos DB tool yourself.
The agent handles saving — your job is only to produce the mapped and validated JSON.
