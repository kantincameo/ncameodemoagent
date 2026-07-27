# Par2Play Phone Service Skill

## Overview
This skill provides specialized knowledge and procedures for managing Par2Play phone service operations, customer interactions, and service data management.

## Key Capabilities

### 1. Customer Service Operations
- Handle customer inquiries about phone service
- Troubleshoot common phone service issues
- Manage account information and customer profiles
- Process service requests and complaints

### 2. Service Data Management
Use the following data operations:

#### Retrieve Customer Data
**Tool**: `get_data(dataPath)`
**Example Path Format**: `smbid/finaldata/servicedata/customers/customer_123.json`
**When to Use**:
- Look up customer account information
- Retrieve service history
- Access billing records
- Check service status

#### Store/Update Service Data
**Tool**: `create_data(jsonContent, dataPath)`
**Example Path Format**: `smbid/finaldata/servicedata/customers/customer_123.json`
**Example Usage**:
```json
{
  "customerId": "customer_123",
  "name": "John Doe",
  "phoneNumber": "+1-555-0123",
  "accountStatus": "active",
  "serviceType": "unlimited",
  "lastUpdated": "2024-01-15T10:30:00Z"
}
```
**When to Use**:
- Create new customer records
- Update customer information
- Log service interactions
- Record billing updates
- Store service history

### 3. Data Path Structure
All data paths follow this pattern:
```
smbid/finaldata/servicedata/[entity_type]/[entity_id].json
```

**Examples**:
- `smbid/finaldata/servicedata/customers/cust_001.json` - Customer record
- `smbid/finaldata/servicedata/orders/order_12345.json` - Service order
- `smbid/finaldata/servicedata/billing/bill_789.json` - Billing record
- `smbid/finaldata/servicedata/tickets/ticket_456.json` - Support ticket

### 4. Common Workflows

#### Workflow A: Handle New Customer Inquiry
1. Request customer identification
2. Use `get_data` to retrieve existing customer record (if available)
3. Respond to customer inquiry using retrieved data
4. If new customer, use `create_data` to store profile

#### Workflow B: Process Service Request
1. Verify customer identity
2. Retrieve customer data using `get_data`
3. Process the request according to service policies
4. Update customer record using `create_data` with new status

#### Workflow C: Log Service Interaction
1. After handling customer inquiry, prepare interaction log
2. Use `create_data` to store service ticket/log at appropriate dataPath
3. Include timestamp, customer ID, issue description, and resolution

### 5. Best Practices

**Data Retrieval**
- Always use specific, scoped dataPath values
- Handle missing data gracefully
- Provide feedback if no records are found

**Data Creation/Updates**
- Include timestamp fields (ISO 8601 format)
- Maintain data structure consistency
- Include relevant metadata (customer ID, service type, etc.)
- Confirm operations with customers before execution

**Customer Interaction**
- Always verify customer identity before accessing/modifying data
- Explain what data you're retrieving or storing
- Protect sensitive customer information
- Follow privacy and security policies

### 6. Error Handling
- If `get_data` fails: Apologize and offer alternative assistance
- If `create_data` fails: Confirm the data format and retry, or escalate to support
- Always inform the customer of any issues transparently

## Integration Notes
This skill integrates with the data MCP service at https://datamcp.ncameo.com for all data operations. All operations use the standard `get_data` and `create_data` tools with the dataPath parameter.