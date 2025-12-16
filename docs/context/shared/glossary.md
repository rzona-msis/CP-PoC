# Campus Resource Hub - Glossary

## Domain Terms

**Resource**: Any campus asset that can be booked or reserved (study rooms, equipment, event spaces, etc.)

**Booking**: A reservation of a resource for a specific time period

**Owner**: The user or department that manages a resource

**Requester**: A user who requests to book a resource

**Approval Workflow**: Process where bookings require staff/admin approval before confirmation

**Conflict Detection**: System check to prevent double-booking of resources

**Availability Rules**: JSON-encoded rules defining when a resource can be booked

## User Roles

**Student**: Basic user who can search, book resources, and leave reviews

**Staff**: Elevated user who can manage department resources and approve bookings

**Admin**: Full access user who can manage all resources, users, and moderate content

## Technical Terms

**MVC**: Model-View-Controller architectural pattern

**DAL**: Data Access Layer - encapsulates all database operations

**CRUD**: Create, Read, Update, Delete operations

**ORM**: Object-Relational Mapping (not used in this project; using direct SQL)

**CSRF**: Cross-Site Request Forgery protection

**XSS**: Cross-Site Scripting protection

## Status Values

### Booking Status
- `pending`: Awaiting approval
- `approved`: Confirmed booking
- `rejected`: Denied by owner/admin
- `cancelled`: Cancelled by requester
- `completed`: Booking time has passed

### Resource Status
- `draft`: Not yet published
- `published`: Active and bookable
- `archived`: No longer available

## Abbreviations

**PRD**: Product Requirements Document

**ERD**: Entity-Relationship Diagram

**API**: Application Programming Interface

**UI/UX**: User Interface / User Experience

**MCP**: Model Context Protocol (for AI integration)

