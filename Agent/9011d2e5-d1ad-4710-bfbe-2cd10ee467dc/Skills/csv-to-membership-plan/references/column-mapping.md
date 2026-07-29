# CSV Column Mapping & Validation Rules

Membership CSVs come from many different systems, so headers are never standardized. Before
mapping rows to the target schema, resolve every raw CSV header to a target field using the
alias table below.

Matching is **case-insensitive** and **whitespace-insensitive**, and should use semantic
judgement, not just exact string matching — a column doesn't need to match an alias exactly;
use context (naming conventions, abbreviations, neighboring columns, sample values) to find
the best match.

| Target Field | Likely CSV Column Names (examples, not exhaustive) |
|---|---|
| `id` | id, planId, plan_id, uid, identifier, record_id |
| `planId` | planId, plan_id, id, uid, plan_identifier |
| `businessId` | businessId, business_id, biz_id, orgId, organization_id, company_id |
| `locationId` | locationId, location_id, loc_id, site_id, branch_id |
| `externalMembershipId` | externalMembershipId, external_id, ext_membership_id, external_membership_id |
| `membershipName` | membershipName, name, title, planName, plan_name, MemName, membership |
| `membershipCode` | membershipCode, code, plan_code, short_code, sku, abbreviation |
| `membershipTypeKind` | membershipTypeKind, type, kind, membershipType, plan_type, category |
| `descriptionRaw` | descriptionRaw, description, desc, details, summary, notes, about |
| `price` | price, cost, amount, fee, rate, monthly_price, plan_price, value |
| `priceSource` | priceSource, price_source, pricing_type, source |
| `billingCycle` | billingCycle, billing_cycle, frequency, interval, period, cycle, term |
| `membershipDuration` | duration, membershipDuration, membership_duration, term_length, validity, length_of_membership, contract_length |
| `isUnlimited` | isUnlimited, unlimited, is_unlimited, no_limit |
| `setupFee` | setupFee, setup_fee, initiation_fee, enrollment_fee |
| `annualFee` | annualFee, annual_fee, yearly_fee |
| `declineFee` | declineFee, decline_fee, failed_payment_fee |
| `buyOutFee` | buyOutFee, buyout_fee, buy_out_fee, cancellation_fee |
| `freezeFee` | freezeFee, freeze_fee, hold_fee, pause_fee |
| `downgradeFee` | downgradeFee, downgrade_fee |
| `upgradeFee` | upgradeFee, upgrade_fee |
| `guestPassFee` | guestPassFee, guest_pass_fee, guest_fee, visitor_fee |
| `guestPassVisits` | guestPassVisits, guest_pass_visits, guest_visits, visitor_count |
| `numVisits` | numVisits, num_visits, visit_count, visits, allowed_visits |
| `advanceBookingDays` | advanceBookingDays, advance_booking_days, booking_advance, booking_days |
| `saleStartDate` | saleStartDate, sale_start_date, start_date, available_from |
| `centerAssigned` | centerAssigned, center_assigned, assigned_to_center |
| `soldInCenter` | soldInCenter, sold_in_center, center_sale, in_center_sale |
| `isActive` | isActive, active, status, enabled, is_active, live, published |
| `benefits` / services included | benefits, defaultBenefits, services, servicesIncluded, services_included, perks, inclusions, extras |

Columns that clearly don't map to anything in the target schema are discarded gracefully —
don't error, just skip them (and log that they were skipped).

## Linking "services included" to the Service Knowledge Base

The benefits/services-included column typically contains one or more service names (comma or
semicolon separated, or one per row depending on the CSV's shape). For each name found:

1. Try to match it against the `serviceName` field of the Service Knowledge Base's `services`
   list (see Stage 1a in SKILL.md), case/whitespace-insensitive, allowing close/fuzzy matches
   (e.g. "Haircut" ↔ "Hair Cut & Style").
2. If matched → set `serviceId` to that service's real `id` (a UUID from the Service
   Knowledge Base) and `serviceNameRaw` to the name as it appeared in the membership CSV.
3. If no confident match → keep `serviceNameRaw` as-is and set `serviceId` to `null`, and
   flag it to the user during the gap-filling step rather than silently guessing.

## Row → JSON validation & default rules

Apply these to every mapped membership record:

| Field | Rule |
|---|---|
| `id` | If missing → generate as `"plan_" + membershipCode.toLowerCase()`, or a short UUID if no code exists |
| `planId` | If missing → same value as `id` |
| `businessId` | If missing → `""` |
| `locationId` | If missing → `""` |
| `externalMembershipId` | If missing → `""` |
| `membershipName` | **Required** — record is invalid without it |
| `membershipCode` | Direct copy; may be null |
| `membershipTypeKind` | If missing/empty → default `"Recurring"` |
| `descriptionRaw` | Direct copy; may be `""` |
| `price` | **Required.** Must be a number ≥ 0. If missing/non-numeric → flag as a gap (don't silently default — price is mandatory) |
| `priceSource` | If missing/empty → default `"FromSourceFile"` |
| `billingCycle` | If missing/empty → default `"Monthly"` |
| `membershipDuration` | **Required.** How long the membership lasts (e.g. "1 Month", "12 Months", "Ongoing"). If missing → flag as a gap |
| `isUnlimited` | Boolean. If missing → default `false` |
| `setupFee`, `annualFee`, `declineFee`, `buyOutFee`, `freezeFee`, `guestPassFee` | Number ≥ 0. If missing → default `0` |
| `downgradeFee`, `upgradeFee` | If missing/empty → default `null` |
| `guestPassVisits`, `numVisits`, `advanceBookingDays` | Integer ≥ 0. If missing → default `0` |
| `saleStartDate` | If missing/empty → default `null` |
| `centerAssigned`, `soldInCenter` | Boolean. If missing → default `true` |
| `isActive` | Boolean. Map "true"/"yes"/"1"/"active"/"enabled" → `true`; anything else present → `false`; if missing → default `true` |
| `benefits` | **Required — at least one entry.** If none found in the CSV/manual entry → flag as a gap |
| `totalCredits` (within each benefit) | Integer ≥ 0. If missing/invalid → default `0` |
| `_etag`, `_ts` | Always `null` |
| `createdAt` | Current UTC timestamp, ISO 8601 |
| `updatedAt` | Same value as `createdAt` |

A membership is only "complete" once `membershipName`, `price`, `membershipDuration`, and at
least one entry in `benefits` are all present — these are the four mandatory fields called out
in Stage 1 of SKILL.md. Anything else missing gets a sensible default per the table above
rather than blocking progress.