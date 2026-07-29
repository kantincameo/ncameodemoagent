# CSV Column Mapping & Validation Rules

Two different CSVs are handled by this skill — a **Customer CSV** (Stage 1) and a **Customer
Membership/Package CSV** (Stage 2). Their mapping tables and rules are kept separate below.
As with the other knowledge-builder skills, matching is case/whitespace-insensitive and
should use semantic judgement, not just exact string matching — a column doesn't need to
match an alias exactly. Columns that don't map to anything are skipped gracefully, not
errored on, and logged as unmapped.

---

## Part A — Customer CSV (Stage 1)

| Target Field | Likely CSV Column Names (examples, not exhaustive) |
|---|---|
| `id` | id, customerId, customer_id, uid |
| `businessId` | businessId, business_id, biz_id, orgId |
| `firstName` | firstName, first_name, FName, given_name |
| `lastName` | lastName, last_name, LName, surname, family_name |
| `email` | email, Email, email_address, e-mail |
| `phone` | phone, Phone, phone_number, mobile, contact_number, cell |
| `dob` | dob, DOB, date_of_birth, birthdate, birthday |
| `gender` | gender, Gender, sex |
| `address` | address, Address, street_address, mailing_address |
| `locationId` | locationId, location_id, loc_id, site_id, branch_id |
| `joinedDate` | joinedDate, joined_date, signup_date, member_since, created_date |
| `lastVisitDate` | lastVisitDate, last_visit_date, last_visit, most_recent_visit |
| `totalVisits` | totalVisits, total_visits, visit_count, num_visits |
| `totalSpend` | totalSpend, total_spend, lifetime_spend, total_purchases |
| `lifetimeValue` | lifetimeValue, lifetime_value, LTV, ltv |
| `tags` | tags, Tags, labels, segments |
| `preferredContactMethod` | preferredContactMethod, preferred_contact_method, contact_preference, contact_method |

### Row → JSON validation & default rules

| Field | Rule |
|---|---|
| `id` | Always auto-generate a new UUID (never take from CSV) |
| `businessId` | Missing → `""` |
| `firstName`, `lastName` | **Required together** — a row needs at least a first and last name to be valid |
| `email`, `phone` | **At least one required.** A row with neither is invalid — flag it |
| `dob`, `gender`, `address` | Missing → `null` |
| `locationId` | Missing → `""` |
| `joinedDate`, `lastVisitDate` | Missing → `null` |
| `totalVisits` | Integer ≥ 0. Missing/non-numeric → `0` |
| `totalSpend`, `lifetimeValue` | Number ≥ 0. Strip currency symbols. Missing/non-numeric → `0.0` |
| `tags` | Split on comma/semicolon into a list. Missing → `[]` |
| `preferredContactMethod` | Missing → `null` |
| `activeMemberships` | Always `[]` at this stage — populated later in Stage 3a from `customerMemberships` |
| `createdAt` / `updatedAt` | Current UTC timestamp, ISO 8601 (same value for both) |
| `_etag`, `_ts` | Always `null` |

A customer row is only valid if it has both `firstName`+`lastName` **and** at least one of
`email`/`phone`. Anything else missing just gets its default.

---

## Part B — Customer Membership/Package CSV (Stage 2)

| Target Field | Likely CSV Column Names (examples, not exhaustive) |
|---|---|
| `id` | id, recordId, record_id |
| `businessId` | businessId, business_id, biz_id |
| `customerId` / customer link | customerId, customer_id, customer_email, email, phone, customer_name, customer |
| `membershipPlanId` / plan name | membershipPlanId, packageId, planId, membershipName, packageName, planName, plan |
| `locationId` | locationId, location_id, loc_id |
| `invoiceNo` | invoiceNo, invoice_no, invoice_number, invoice |
| `benefitType` | benefitType, benefit_type, type |
| `saleDate` | saleDate, sale_date, purchase_date |
| `startDate` | startDate, start_date, effective_date, activation_date |
| `endDate` | endDate, end_date, expiry_date, expiration_date |
| `salesAmount` | salesAmount, sales_amount, amount, price, cost |
| `salesAmountInclTax` | salesAmountInclTax, sales_amount_incl_tax, amount_incl_tax, total_amount |
| `balanceValue` | balanceValue, balance_value, balance |
| `cancelledValue` | cancelledValue, cancelled_value, cancelled_amount |
| `expiredValue` | expiredValue, expired_value, expired_amount |
| `membershipStatus` | membershipStatus, status, plan_status |
| `recurrenceStatus` | recurrenceStatus, recurrence_status, billing_status |
| `nextRecurrenceDate` | nextRecurrenceDate, next_recurrence_date, next_billing_date, next_charge_date |
| `benefits[].serviceNameRaw` | serviceName, serviceNameRaw, service |
| `benefits[].serviceId` | serviceId, svcId, service_id |
| `benefits[].totalCredits` | totalCredits, total_credits, credits, sessions |
| `benefits[].redeemedCredits` | redeemedCredits, redeemed_credits, used_credits, redeemed |
| `benefits[].refundedCredits` | refundedCredits, refunded_credits, refunded |
| `benefits[].expiredCredits` | expiredCredits, expired_credits, expired |
| `benefits[].balanceCredits` | balanceCredits, balance_credits, remaining_credits, remaining |

### Linking rules

**Customer link:** resolve `customerId` by matching, in priority order: (1) an explicit
customer id column if present, (2) email, (3) phone, (4) full name — against the customers
already collected in Stage 1. No confident match → flag for the user rather than guessing.

**Plan link:** resolve `membershipPlanId` and `membershipName`/`planKind` by matching the
given plan name against the loaded Membership Knowledge Base's `memberships[]` (by
`membershipName`) and/or the Package Knowledge Base's `packages[]` (by `packageName`),
case/whitespace-insensitive, close matches allowed.
- Matched a membership → `membershipPlanId` = that membership's `id`, `membershipName` = its
  real name, `planKind` = `"Membership"`.
- Matched a package → `membershipPlanId` = that package's `id`, `membershipName` = its real
  name, `planKind` = `"Package"`.
- No match, or no plan knowledge base loaded at all → `membershipPlanId` = `null`,
  `membershipName` = `"Other"`, `planKind` = `"Other"`. Never invent a plan name or guess a
  close-enough id.

**Service links (benefits):** same approach as the other knowledge-builder skills — match
each benefit's service name against service-knowledge-builder's `services` list; linked
`serviceId` where confident, else keep as free text with `serviceId: null`.

### Row → JSON validation & default rules

| Field | Rule |
|---|---|
| `id` | Always auto-generate a new UUID |
| `businessId` | Missing → `""` |
| `customerId` | **Required** — resolved via the linking rules above; row is invalid if it can't be linked |
| `membershipPlanId` / `membershipName` / `planKind` | Resolved via plan-link rules above; `"Other"` is a valid, complete value |
| `locationId` | Missing → `""` |
| `invoiceNo` | Missing → `null` |
| `benefitType` | Missing/empty → default `"ServiceBenefit"` |
| `saleDate` | Missing → `null` |
| `startDate` | **Required** — flag as a gap if missing |
| `endDate` | Missing → `null` |
| `salesAmount`, `salesAmountInclTax`, `balanceValue` | Number ≥ 0. Missing/non-numeric → `0.0` |
| `cancelledValue`, `expiredValue` | Number ≥ 0. Missing → `0` |
| `membershipStatus` | Missing/empty → default `"Active"` |
| `recurrenceStatus` | Missing → `null` |
| `nextRecurrenceDate` | Missing → `null` |
| `benefits` | **Required — at least one entry** (linked or free-text). Missing entirely → flag as a gap |
| `totalCredits`, `redeemedCredits`, `refundedCredits`, `expiredCredits`, `balanceCredits` (per benefit) | Integer ≥ 0. Missing/non-numeric → `0` |
| `createdAt` / `updatedAt` | Current UTC timestamp, ISO 8601 |
| `_etag`, `_ts` | Always `null` |

A purchase record is only "complete" once it has a resolved `customerId`, a `membershipName`
(real or `"Other"`), a `startDate`, and at least one `benefits` entry — these are the four
mandatory fields called out in Stage 2 of SKILL.md.
