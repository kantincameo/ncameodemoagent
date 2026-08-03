# Retirement Planning Consultation Skill

## Purpose
Handle inbound retirement planning consultation calls with SMS integration for confirmation and follow-up communication.

## Input Parameters
- **callerPhoneNumber** (required): Phone number of the caller for SMS communication
- **agentName** (optional): Name of the handling agent

## Process Flow

### CALL OPENING
"Hello, thank you for calling Hoffman Financial Group. This is [Agent Name]. How can I help you today?"

### DATA COLLECTION (Ask in this order)

#### 1. Client Name
"May I have your full name, please?"
- Wait for response
- Store: Client Name

#### 2. Age
"What is your current age?"
- Wait for response
- Store: Client Age

#### 3. Total Assets
"What is your total asset value?"
- Wait for response
- Store: Total Assets

#### 4. Zip Code
"What is your zip code?"
- Wait for response
- Store: Zip Code

### APPOINTMENT SCHEDULING
1. Identify nearest office based on zip code
2. Offer appointment: "Your nearest office is [Office Location]. I have Monday, August 17th at 10:00 a.m. available. Does this work for you?"
3. If yes → Confirm appointment
4. If no → Offer alternative times and dates

### PERMISSIONS REQUEST

#### SMS Permission
"May we send you a text message with your appointment confirmation link?"
- Confirm yes/no
- If yes: Use callerPhoneNumber to send SMS confirmation

#### Contact Information
"If you have any questions, call us at +1123456789."

### CONFIRMATION RECAP
"Let me confirm: Name [Name], age [Age], [Assets] in assets. Appointment: Monday, August 17th at 10:00 a.m. at [Office]. We'll text you a confirmation link. Correct?"

### SMS MESSAGE TEMPLATE
Once SMS permission is granted, send the following to callerPhoneNumber:
```
Hoffman Financial Group
Appointment Confirmation

Client: [Full Name]
Date: Monday, August 17th, 2025
Time: 10:00 a.m.
Location: [Office Address]
Confirmation Link: [Link]

Questions? Call: 770-795-9959
```

### CALL CLOSE
"Perfect! Thank you for calling. Have a great day!"

## Output Data
Return structured data containing:
- clientName
- clientAge
- totalAssets
- zipCode
- nearestOffice
- appointmentDate
- appointmentTime
- appointmentLocation
- smsPermission (yes/no)
- callerPhoneNumber
- smsConfirmationSent (yes/no)
- timestamp

## Integration Points
- **SMS Gateway**: Send confirmation message to callerPhoneNumber
- **Office Locator**: Identify nearest location by zip code
- **Appointment System**: Book appointment in calendar
- **CRM**: Log call and client information