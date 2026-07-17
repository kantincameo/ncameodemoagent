# Example Input → Output Pairs

Use these as a mental reference for how extraction should behave with
the current 23-field customer schema.

---

## Example 1: Single record, plain text

**Input document (customer_note.txt):**
```
Customer Registration

Name: Ananya Verma
Email: ananya.verma@clinic.com
Mobile: +91-9998887771
DOB: 1990-04-12
Gender: Female
Membership: Gold Tier
Email marketing: Subscribed
SMS marketing: Not subscribed
```

**Expected output:**
```json
{
  "businessId": "",
  "customerId": "",
  "externalCustomerId": "",
  "firstName": "Ananya",
  "lastName": "Verma",
  "email": "ananya.verma@clinic.com",
  "phone": "+91-9998887771",
  "dob": "1990-04-12",
  "gender": "Female",
  "address": "",
  "primaryLocationId": "",
  "joinedDate": "",
  "lastVisitDate": "",
  "totalVisits": 0,
  "totalSpend": 0,
  "lifetimeValue": 0,
  "activeMembershipId": "",
  "activeMembershipTier": "Gold Tier",
  "activePackageIds": [],
  "tags": [],
  "preferredContactMethod": "",
  "marketingOptInEmail": true,
  "marketingOptInSms": false,
  "customAttributes": {}
}
```

Note: this is a **single** record, so it's returned as one plain object
— no comma, no brackets.

---

## Example 2: Multiple records — comma-separated, NO array brackets

**Input document (customers.csv):**
```
Customer ID,Full Name,Email,Mobile,Total Visits,Total Spend
C001,Rajesh Patel,rajesh.patel@example.com,9876543210,12,15000
C002,Sneha Iyer,sneha.iyer@test.in,,3,2500
```

**Expected output (exactly this shape — comma between objects, no `[` `]`):**
```
{
  "businessId": "",
  "customerId": "C001",
  "externalCustomerId": "",
  "firstName": "Rajesh",
  "lastName": "Patel",
  "email": "rajesh.patel@example.com",
  "phone": "9876543210",
  "dob": "",
  "gender": "",
  "address": "",
  "primaryLocationId": "",
  "joinedDate": "",
  "lastVisitDate": "",
  "totalVisits": 12,
  "totalSpend": 15000,
  "lifetimeValue": 0,
  "activeMembershipId": "",
  "activeMembershipTier": "",
  "activePackageIds": [],
  "tags": [],
  "preferredContactMethod": "",
  "marketingOptInEmail": false,
  "marketingOptInSms": false,
  "customAttributes": {}
},
{
  "businessId": "",
  "customerId": "C002",
  "externalCustomerId": "",
  "firstName": "Sneha",
  "lastName": "Iyer",
  "email": "sneha.iyer@test.in",
  "phone": "",
  "dob": "",
  "gender": "",
  "address": "",
  "primaryLocationId": "",
  "joinedDate": "",
  "lastVisitDate": "",
  "totalVisits": 3,
  "totalSpend": 2500,
  "lifetimeValue": 0,
  "activeMembershipId": "",
  "activeMembershipTier": "",
  "activePackageIds": [],
  "tags": [],
  "preferredContactMethod": "",
  "marketingOptInEmail": false,
  "marketingOptInSms": false,
  "customAttributes": {}
}
```

Notice: two complete `{ ... }` objects, separated by a single comma,
with **no** surrounding `[` and `]`. This is NOT a JSON array.

---

## Example 3: Document with no matching customer data at all

**Input document (invoice.pdf):** an invoice with amounts, item lines,
and a company address, but no personal customer info anywhere.

**Expected output (all fields at type-appropriate empty values):**
```json
{
  "businessId": "",
  "customerId": "",
  "externalCustomerId": "",
  "firstName": "",
  "lastName": "",
  "email": "",
  "phone": "",
  "dob": "",
  "gender": "",
  "address": "",
  "primaryLocationId": "",
  "joinedDate": "",
  "lastVisitDate": "",
  "totalVisits": 0,
  "totalSpend": 0,
  "lifetimeValue": 0,
  "activeMembershipId": "",
  "activeMembershipTier": "",
  "activePackageIds": [],
  "tags": [],
  "preferredContactMethod": "",
  "marketingOptInEmail": false,
  "marketingOptInSms": false,
  "customAttributes": {}
}
```

---

## Example 4: customAttributes and tags/arrays populated

**Input document (member_card.txt):**
```
Member: Priya Nair
Tags: VIP, Referral, Corporate
Active Packages: Yoga-10, Spa-5
Referral Source: Instagram
Preferred Contact: SMS
```

**Expected output (relevant excerpt):**
```json
{
  "firstName": "Priya",
  "lastName": "Nair",
  "activePackageIds": ["Yoga-10", "Spa-5"],
  "tags": ["VIP", "Referral", "Corporate"],
  "preferredContactMethod": "SMS",
  "customAttributes": {
    "referralSource": "Instagram"
  }
}
```
(Other fields omitted here for brevity — the real output must still
include all 23 keys.)

---

## Example 5: Scanned image of a form (vision-based reading)

**Input:** a photo of a printed customer intake form.

Process: view the image directly, read the printed text visually, then
extract the same way as any text document. Output format is identical
to the examples above — single object or comma-separated objects, with
all 23 keys, correct types, no markdown fences, no array brackets for
multiple records.
