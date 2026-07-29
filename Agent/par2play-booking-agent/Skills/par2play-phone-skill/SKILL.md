# Par2Play Phone Booking Skill

This skill enables the Par2Play Booking Agent to:
1. Check golf course availability
2. Create confirmed bookings
3. Cancel bookings if needed

## Core Functions

### check_availability
**Purpose:** Query available time slots for a given date and party size

**Input:**
```json
{
  "date": "YYYY-MM-DD",
  "numberOfGolfers": number,
  "timePreference": "morning|afternoon|evening|[specific time HH:MM]"
}
```

**Output:**
```json
{
  "date": "YYYY-MM-DD",
  "availableSlots": [
    {
      "startTime": "HH:MM",
      "endTime": "HH:MM",
      "resourceId": "string",
      "pricePerPerson": number,
      "totalPrice": number,
      "availableSpots": number
    }
  ],
  "message": "string describing availability"
}
```

### create_booking
**Purpose:** Create a confirmed booking record

**Input:**
```json
{
  "date": "YYYY-MM-DD",
  "startTime": "HH:MM",
  "endTime": "HH:MM",
  "numberOfGolfers": number,
  "resourceId": "string",
  "paymentMethod": "Confirmed",
  "membershipInstanceIdUsed": null,
  "customerPackageIdUsed": null,
  "creditsDeducted": 0,
  "amountCharged": number,
  "specialRequests": "string or null"
}
```

**Output:**
```json
{
  "bookingId": "string",
  "status": "confirmed",
  "appointmentDate": "YYYY-MM-DD",
  "startTime": "HH:MM",
  "endTime": "HH:MM",
  "resourceId": "string",
  "numberOfGolfers": number,
  "amountCharged": number,
  "paymentMethod": "Confirmed",
  "message": "Booking created successfully"
}
```

### cancel_booking
**Purpose:** Cancel an existing booking

**Input:**
```json
{
  "bookingId": "string",
  "reason": "string (optional)"
}
```

**Output:**
```json
{
  "bookingId": "string",
  "status": "cancelled",
  "message": "Booking cancelled successfully"
}
```

## Integration Notes
- All times are in 24-hour format (HH:MM)
- Dates must be in ISO format (YYYY-MM-DD)
- Prices are in the system's default currency
- Payment is marked as "Confirmed" - actual payment processing happens separately
- No membership discounts or package credits are applied during booking
- Booking confirmation is final once create_booking succeeds