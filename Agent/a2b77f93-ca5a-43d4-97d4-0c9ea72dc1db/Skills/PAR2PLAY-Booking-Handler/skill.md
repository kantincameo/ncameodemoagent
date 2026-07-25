# PAR2PLAY Booking Handler Skill

This skill contains all detailed logic for the PAR2PLAY Booking Assistant's two-phase booking flow: customer identification and service request handling.

## OVERVIEW

When the agent invokes this skill, execute the appropriate phase based on the customer interaction stage:

- **Phase 1:** Customer identification and system lookup
- **Phase 2:** Booking creation and confirmation

---

## PHASE 1: CUSTOMER IDENTIFICATION

### Purpose
Locate or create a customer record in the Cosmos database before proceeding to booking.

### Workflow

1. **Extract Customer Information from User Input**
   - Name (required)
   - Phone number (preferred)
   - Email (preferred)
   - Any other identifying details mentioned

2. **Search Cosmos Database**
   - Use `cosmos_search_documents` MCP tool
   - Query Template:
     ```
     SELECT * FROM customers c WHERE c.name LIKE @name OR c.phone = @phone OR c.email = @email
     ```
   - Database: `par2play`
   - Container: `customers`
   - Partition Key: `/customerId`

3. **Customer Found?**
   - **Yes:** Retrieve `customerId`, `name`, `phone`, `email`, `membershipStatus`
   - **No:** Create new customer record using `cosmos_upsert_document` (see below)

4. **Create New Customer (if needed)**
   - Use `cosmos_upsert_document` MCP tool
   - Document structure:
     ```json
     {
       "customerId": "<generate UUID or use phone-based ID>",
       "name": "<customer name>",
       "phone": "<phone number>",
       "email": "<email address>",
       "membershipStatus": "active" or "guest",
       "createdAt": "<current timestamp>",
       "updatedAt": "<current timestamp>"
     }
     ```
   - Database: `par2play`
   - Container: `customers`
   - Partition Key: `/customerId`

5. **Return to Agent**
   - Confirm customer identification to the user
   - Example: "Great! I found your account. Let's get you booked for a court or lesson."
   - Pass `customerId` to Phase 2

### Field Mapping
- `customerId`: Unique identifier (UUID or derived)
- `name`: Customer full name
- `phone`: Contact phone number
- `email`: Contact email
- `membershipStatus`: "active" for members, "guest" for walk-ins
- `createdAt`: ISO 8601 timestamp of account creation
- `updatedAt`: ISO 8601 timestamp of last update

---

## PHASE 2: SERVICE REQUEST HANDLING

### Purpose
Collect booking details and create a reservation in Cosmos.

### Workflow

1. **Determine Service Type**
   - **Court Rental:** "I'd like to book a court"
   - **Lesson:** "I'd like to book a lesson" or mention instructor name
   - Clarify if needed: "Are you looking to rent a court or book a lesson?"

2. **Collect Booking Details**

   **For Court Rental:**
   - Desired date (YYYY-MM-DD format)
   - Desired time slot (HH:MM AM/PM format)
   - Court type preference (indoor or outdoor, if available)
   - Duration (typically 1 hour)
   - Confirm cost: $50/hour for court rentals

   **For Lesson:**
   - Desired date (YYYY-MM-DD format)
   - Desired time slot (HH:MM AM/PM format)
   - Skill level (beginner, intermediate, advanced)
   - Lesson type (private or group)
   - Preferred instructor (if known)
   - Confirm pricing:
     - Private: $75/hour
     - Group: $35/person per hour

3. **Create Booking Record**
   - Use `cosmos_upsert_document` MCP tool
   - Document structure:
     ```json
     {
       "bookingId": "<generate UUID>",
       "customerId": "<from Phase 1>",
       "serviceType": "court_rental" or "lesson",
       "bookingDate": "<YYYY-MM-DD>",
       "startTime": "<HH:MM>",
       "endTime": "<HH:MM (typically 1 hour later)>",
       "courtType": "indoor" or "outdoor" (for court rentals),
       "skillLevel": "beginner|intermediate|advanced" (for lessons),
       "lessonType": "private" or "group" (for lessons),
       "instructor": "<instructor name>" (for lessons, optional),
       "status": "confirmed",
       "totalCost": "<numeric value>",
       "paymentStatus": "pending",
       "createdAt": "<current timestamp>",
       "updatedAt": "<current timestamp>"
     }
     ```
   - Database: `par2play`
   - Container: `bookings`
   - Partition Key: `/customerId`

4. **Generate Booking Confirmation**
   - Booking Reference: First 8 characters of `bookingId`
   - Confirmation should include:
     - Booking reference number
     - Service type (court rental or lesson)
     - Date and time
     - Location (court # if rental, instructor name if lesson)
     - Total cost
     - Payment instructions: "Please pay at check-in or online via our website"
   - Example: "Your booking reference is ABC12345. You've booked an indoor court on Friday, January 17th from 10:00 AM to 11:00 AM. Total cost is $50. Please pay at check-in."

5. **Return to Agent**
   - Provide booking confirmation details to the user
   - Offer further assistance (additional bookings, inquiries, etc.)

### Field Mapping for Bookings
- `bookingId`: Unique booking identifier (UUID)
- `customerId`: Reference to customer (from Phase 1)
- `serviceType`: "court_rental" or "lesson"
- `bookingDate`: Date in YYYY-MM-DD format
- `startTime`: Start time in HH:MM format (24-hour)
- `endTime`: End time in HH:MM format (typically start + 1 hour)
- `courtType`: "indoor" or "outdoor" (court rentals only)
- `skillLevel`: "beginner", "intermediate", or "advanced" (lessons only)
- `lessonType`: "private" or "group" (lessons only)
- `instructor`: Name of instructor (lessons, optional)
- `status`: "confirmed", "pending", "completed", or "cancelled"
- `totalCost`: Numeric value (e.g., 50, 75, 35)
- `paymentStatus`: "pending", "paid", or "cancelled"
- `createdAt`: ISO 8601 timestamp of booking creation
- `updatedAt`: ISO 8601 timestamp of last update

---

## ERROR HANDLING

### Cosmos Search Failures
- If `cosmos_search_documents` returns no results, proceed to create a new customer
- If query syntax errors occur, simplify the query and retry

### Booking Conflicts
- If the requested time slot is unavailable (already booked), offer alternative times
- Suggest 15-minute increments around the preferred time

### Invalid Input
- If date is in the past, ask for a future date
- If time is outside 8 AM - 6 PM, offer available slots
- If email/phone format is invalid, ask for clarification

### Database Errors
- If `cosmos_upsert_document` fails, inform the user: "We're experiencing a technical issue. Please try again in a moment."
- Do not expose Cosmos error messages to the customer

---

## MCP TOOL REFERENCE

### cosmos_search_documents
**Purpose:** Query customer or booking records
**Parameters:**
- `database`: "par2play"
- `container`: "customers" or "bookings"
- `query`: SQL-like query string with @parameters
- `parameters`: {"@name": "John Doe", "@phone": "5551234567"}

**Returns:** Array of matching documents

### cosmos_upsert_document
**Purpose:** Create or update a customer or booking record
**Parameters:**
- `database`: "par2play"
- `container`: "customers" or "bookings"
- `document`: Full document object (JSON)
- `partitionKey`: "/customerId" for customers, "/customerId" for bookings

**Returns:** Confirmation of upsert operation with document ID

---

## SUMMARY

This skill bridges the agent and Cosmos database:
1. **Phase 1** identifies/creates customers
2. **Phase 2** creates booking records and returns confirmation details

The agent should invoke this skill whenever a customer requests a booking, and simply relay the results back to the user in a friendly, conversational manner.