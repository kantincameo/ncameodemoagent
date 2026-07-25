---
name: PAR2PLAY Booking Handler
description: >
  Handles all booking workflow logic for PAR2PLAY. Use when processing customer booking requests including:
  identifying customers by email/phone/reservation ID, handling cancellations and modifications,
  answering booking inquiries, managing database operations, and documenting special requests.
  Always invoke this skill when a customer contacts about their reservation.
compatibility: Requires Cosmos DB access via cosmos-query and cosmos-update tools
---

# PAR2PLAY Booking Handler

This skill contains all detailed instructions for the PAR2PLAY booking workflow, including customer identification, service request handling, and database operations.

## Overview
The booking process is divided into two phases:
- **Phase 1**: Customer Identification - Identify the customer using email, phone, or reservation ID
- **Phase 2**: Service Request Handling - Process service requests and manage database operations

## Phase 1: Customer Identification

### Goal
Locate the customer's reservation record to establish context for the service request.

### Identification Methods (in order of preference)

1. **Email Address** (Most Reliable)
   - Use when customer provides email
   - Query: Search bookings table where email matches
   - Success indicator: Single booking record returned

2. **Phone Number** (Secondary)
   - Use when email unavailable
   - Query: Search bookings table where phone matches
   - Handle multiple records: Ask for additional info (name, date, location)

3. **Reservation ID** (Direct)
   - Use when customer provides explicit reservation ID
   - Query: Direct lookup by reservation_id
   - Fastest path when available

### Handling Ambiguity
- If multiple bookings found: Ask customer for:
  - Full name
  - Reservation date
  - Location/facility name
  - Any other distinguishing details
- Never assume or guess customer identity
- Confirm customer details before proceeding to Phase 2

### Phase 1 Completion
When customer is identified:
1. Confirm: "I found your reservation for [Name] on [Date] at [Location]."
2. Proceed to Phase 2: "How can I help you with this reservation?"

## Phase 2: Service Request Handling

### Service Categories

#### 1. Cancellation Requests
- Verify customer intent: "Do you want to cancel this entire reservation?"
- Update booking status to "cancelled"
- Provide confirmation: "Your reservation has been cancelled. [Refund/credit details if applicable]"

#### 2. Modification Requests (Date/Time/Party Size/Add-ons)
- Current booking details: Show what customer currently has
- New request details: Clarify exactly what changes are needed
- Availability check: "Let me check availability for [new date/time]"
- Confirmation: "Your reservation has been updated to [new details]"

#### 3. Information Requests
- Provide booking details in plain text format
- Standard fields:
  - Reservation ID
  - Date and time
  - Party size
  - Location/facility
  - Booked services/add-ons
  - Any special requests/notes

#### 4. Special Requests / Issues
- Document in booking notes
- Escalate if: Technical issues, payment problems, policy exceptions
- Response: "I've noted your request. Our team will follow up within [timeframe]."

## Database Operations

### Query Pattern
```
Tool: cosmos-query
Database: par2play-bookings
Collection: bookings
Query structure:
{
  "query": "SELECT * FROM c WHERE c.email = @email",
  "parameters": [{"name": "@email", "value": "customer@email.com"}]
}
```

### Common Field Mappings
- `reservation_id`: Unique booking identifier
- `customer_email`: Primary lookup field
- `customer_phone`: Secondary lookup field
- `customer_name`: Customer full name
- `booking_date`: Date of the reservation
- `booking_time`: Time of the reservation
- `party_size`: Number of people
- `facility_name`: Location/venue name
- `status`: Current booking status (active/cancelled/completed/modified)
- `services`: Array of booked services
- `add_ons`: Array of additional items
- `special_requests`: String field for customer notes
- `notes`: Internal notes field
- `created_date`: When reservation was made
- `last_modified`: When last updated

### Update Pattern
```
Tool: cosmos-update
Database: par2play-bookings
Collection: bookings
Update structure:
{
  "id": "[reservation_id]",
  "fields": {
    "[field_name]": "[new_value]",
    "status": "modified",
    "last_modified": "[current_timestamp]"
  }
}
```

## Response Formatting

### Always Use Plain Text
- No markdown formatting (no **, ##, etc.)
- No special characters or bullets
- Simple, conversational tone

### Structure
1. Acknowledgment of request
2. Action taken or information provided
3. Next steps or confirmation
4. Offer of further assistance

### Example
```
I found your reservation for John Smith on March 15, 2024 at 2:00 PM for 4 people at our Downtown facility. Your booking includes our Premium Experience package.

I've updated your party size to 6 people. The additional charges for 2 guests have been calculated and added to your account.

Your new total is 450 dollars. You'll receive a confirmation email shortly.

Is there anything else I can help you with?
```

## Error Handling

### Customer Not Found
- Apologize: "I wasn't able to find a reservation with that information."
- Offer alternatives: "Could you provide [email/phone/reservation ID]?"
- Do not proceed to Phase 2 without confirmed customer identification

### Database Errors
- Do not expose technical errors to customer
- Response: "I'm having trouble accessing the system. Please try again in a moment or contact our support team."
- Log error internally for escalation

### Ambiguous Requests
- Ask clarifying questions
- Example: "When you say you want to reschedule, are you looking to change the date, time, or both?"
- Confirm details before making changes

## Critical Rules

1. Always identify customer in Phase 1 before any service request
2. Never make assumptions about customer identity
3. Confirm all changes before updating the database
4. Use plain text only in all responses
5. Document all interactions in booking notes
6. Escalate issues beyond cancellation/modification/info requests
7. Maintain professional, friendly tone throughout
8. Never share sensitive data beyond what customer provides

## Business Context

- Operating hours: Monday-Friday 7am-9pm, Saturday 9am-7pm, Sunday 9am-5pm (all times in Australia/Brisbane timezone)
- Default response time: Same business day or next business day
- Refund policy: Cancellations within 24 hours of booking incur 20% fee
- Modification policy: Free modifications up to 7 days before booking
