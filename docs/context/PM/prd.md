# Product Requirements Document (PRD)
## Campus Resource Hub

**Version**: 1.0  
**Date**: November 10, 2025  
**Team**: AiDD Final Project Team  

---

## 1. Objective

Build a full-stack web application that enables university departments, student organizations, and individuals to efficiently list, discover, and book campus resources including study rooms, AV equipment, lab instruments, event spaces, and tutoring sessions.

## 2. Background & Problem Statement

Currently, campus resources are managed through disparate systems (email requests, paper sign-ups, department-specific portals), leading to:
- Inefficient resource discovery
- Double-bookings and scheduling conflicts
- Lack of visibility into resource availability
- Manual approval processes
- No feedback mechanism for resource quality

## 3. Stakeholders

**Primary Users**:
- Students seeking study spaces, equipment, and services
- Staff managing departmental resources
- Administrators overseeing campus-wide resource allocation

**Secondary Stakeholders**:
- Department heads (usage analytics)
- Facilities management (space utilization)
- IT department (system maintenance)

## 4. Success Metrics

- **Adoption**: 200+ active users within first month
- **Utilization**: 70%+ resource booking rate
- **Efficiency**: 90%+ reduction in booking response time
- **Satisfaction**: 4.0+ average resource rating
- **Conflict Rate**: <5% booking conflicts

## 5. Core Features (MVP)

### 5.1 User Management & Authentication
- Email/password registration and login
- Role-based access (Student, Staff, Admin)
- Profile management with department affiliation

### 5.2 Resource Listings
- Create, read, update, delete resource listings
- Rich metadata: title, description, images, category, location, capacity
- Resource lifecycle: draft → published → archived

### 5.3 Search & Discovery
- Keyword search across resources
- Filters: category, location, date/time availability, capacity
- Sort options: recent, most booked, top-rated

### 5.4 Booking & Scheduling
- Calendar-based booking interface
- Start/end time selection
- Real-time conflict detection
- Status workflow: pending → approved → completed
- Email/in-app notifications for booking confirmations

### 5.5 Messaging System
- Direct messages between requesters and resource owners
- Threaded conversations linked to bookings
- Notification system for new messages

### 5.6 Reviews & Ratings
- Post-booking review capability
- 1-5 star ratings with text comments
- Aggregate ratings displayed on resource pages
- Top-rated badges for high-quality resources

### 5.7 Admin Dashboard
- User management (view, suspend, delete)
- Resource moderation (approve, edit, archive)
- Booking oversight (approve, reject, cancel)
- Review moderation (hide inappropriate content)
- Usage analytics and reports

## 6. Non-Goals (Out of Scope for MVP)

- Mobile native applications (mobile-responsive web only)
- Payment processing for paid resources
- Real-time chat functionality
- Integration with existing campus ID systems
- Multi-language support
- Calendar sync with external services (stretch goal)

## 7. User Flows

### Flow 1: Student Books Study Room
1. Student searches "study room" with date filter
2. Views available rooms with photos and ratings
3. Selects room and desired time slot
4. System checks for conflicts
5. Booking auto-approved (for open resources)
6. Student receives confirmation

### Flow 2: Staff Manages Equipment
1. Staff creates resource listing for lab equipment
2. Sets availability rules and requires_approval flag
3. Publishes listing
4. Reviews incoming booking requests
5. Approves after verifying prerequisites
6. System notifies requester

### Flow 3: Admin Moderates Content
1. Admin views flagged review or reported message
2. Reviews content for policy violations
3. Takes action (hide, delete, warn user)
4. Action logged in admin audit trail

## 8. Technical Requirements

- **Response Time**: <2 seconds for page loads
- **Availability**: 99% uptime during business hours
- **Security**: HTTPS, password hashing, CSRF protection, input validation
- **Accessibility**: WCAG 2.1 Level A compliance minimum
- **Browser Support**: Chrome, Firefox, Safari, Edge (latest 2 versions)

## 9. Privacy & Security

- Store only necessary user information
- Hash all passwords with bcrypt
- Implement CSRF tokens on all forms
- Sanitize all user inputs to prevent XSS
- Restrict file uploads (type, size validation)
- Admin audit logging for sensitive operations

## 10. Future Enhancements (Post-MVP)

- Google Calendar integration
- Waitlist functionality for popular resources
- Department-level analytics dashboards
- Mobile applications (iOS/Android)
- Advanced search with natural language queries
- AI-powered booking recommendations
- Automated reminder notifications
- Resource usage forecasting

## 11. Dependencies & Risks

**Dependencies**:
- Flask framework and Python ecosystem
- Bootstrap 5 for UI components
- Email service for notifications

**Risks**:
- Low initial adoption (mitigation: campus marketing campaign)
- Complex booking conflicts (mitigation: robust testing)
- Data privacy concerns (mitigation: minimal data collection, clear policies)

## 12. Timeline

- **Week 1**: Planning, design, database schema
- **Week 2**: Authentication, resource CRUD, search
- **Week 3**: Booking logic, messaging, reviews, admin panel
- **Week 3**: Testing, documentation, deployment preparation

## 13. Open Questions

- Should we integrate with existing campus authentication (SSO)?
- What is the maximum booking duration allowed?
- How far in advance can users book resources?
- Should there be booking limits per user?

---

**Approval**:  
Product Lead: _______________  
Backend Engineer: _______________  
Frontend Engineer: _______________  
QA/DevOps: _______________  

