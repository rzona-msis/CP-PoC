# Product Requirements Document (PRD)
## Campus Resource Hub

**Version:** 1.0  
**Date:** November 9, 2025  
**Project:** AiDD 2025 Capstone - AI-Driven Development  
**Team:** Reid Zona

---

## 1. Executive Summary

Campus Resource Hub is a full-stack web application designed to facilitate the sharing and booking of campus resources among students and staff. The platform enables efficient resource management, reduces scheduling conflicts, and promotes collaboration within the campus community.

### Objectives
- Provide a centralized platform for campus resource discovery and booking
- Streamline resource allocation and reduce scheduling conflicts
- Enable communication between resource owners and requesters
- Implement WCAG 2.1 AA accessibility standards as an advanced feature
- Ensure secure user authentication and data protection

### Success Metrics
- User registration and active usage rates
- Number of successful bookings completed
- Reduction in booking conflicts and cancellations
- Positive user feedback on accessibility features
- System uptime and performance benchmarks

---

## 2. Stakeholders

### Primary Users
- **Students**: Browse and book study rooms, equipment, tutoring sessions
- **Staff**: Create and manage resources, approve booking requests
- **Administrators**: Oversee platform operations, moderate content, manage users

### Technical Stakeholders
- Development Team
- Database Administrators
- Accessibility Compliance Team
- Security Team

---

## 3. Core Features

### 3.1 User Authentication & Authorization
- User registration with email validation
- Secure login with password hashing (bcrypt)
- Role-based access control (student, staff, admin)
- Session management with Flask-Login

### 3.2 Resource Management
- CRUD operations for resources
- Resource categorization (study rooms, equipment, labs, event spaces, tutoring)
- Image uploads and gallery display
- Draft/published/archived status workflow
- Approval requirements for sensitive resources

### 3.3 Search & Discovery
- Keyword search across titles and descriptions
- Category-based filtering
- Location-based filtering
- Featured resources on homepage

### 3.4 Booking System
- Calendar-based booking interface
- Conflict detection and prevention
- Booking approval workflow for restricted resources
- Booking status management (pending, approved, rejected, cancelled)
- Email notifications (future enhancement)

### 3.5 Messaging System
- Direct messaging between users
- Thread-based conversations
- Unread message indicators
- Contact resource owners directly

### 3.6 Review & Rating System
- 5-star rating system
- Text reviews and comments
- One review per user per resource
- Average rating display and distribution

### 3.7 Admin Dashboard
- User management (promote, demote, delete)
- Resource moderation
- System statistics and analytics
- Activity monitoring

---

## 4. Advanced Feature: WCAG 2.1 AA Accessibility

### 4.1 Semantic HTML Structure
- Proper heading hierarchy (h1-h6)
- Semantic elements (header, nav, main, article, aside, footer)
- ARIA landmarks for screen reader navigation

### 4.2 Keyboard Navigation
- Skip navigation links
- Focus indicators on all interactive elements
- Keyboard-accessible dropdown menus and modals
- Tab order optimization

### 4.3 Screen Reader Support
- Alt text for all images
- ARIA labels and descriptions
- ARIA live regions for dynamic content
- Meaningful link text

### 4.4 Visual Accessibility
- Color contrast ratio 4.5:1 for text (AA standard)
- Color contrast ratio 3:1 for UI components
- Sufficient touch target size (minimum 44x44px)
- No information conveyed by color alone

### 4.5 Responsive Design
- Mobile-first approach with Bootstrap 5
- Flexible layouts for various screen sizes
- Reduced motion support for animations

### 4.6 Testing & Validation
- Automated accessibility testing with axe-selenium-python
- Manual testing with screen readers (NVDA, JAWS)
- Keyboard-only navigation testing
- Color contrast validation tools

---

## 5. Technical Architecture

### 5.1 Technology Stack
- **Backend**: Python 3.10+, Flask 3.0.0
- **Database**: SQLite (development), PostgreSQL-ready (production)
- **ORM**: SQLAlchemy 3.1.1
- **Authentication**: Flask-Login 0.6.3, bcrypt 4.1.1
- **Frontend**: Jinja2 templates, Bootstrap 5, vanilla JavaScript
- **Testing**: pytest 7.4.3, Selenium 4.15.2

### 5.2 Architecture Pattern
- **MVC Pattern**: Clear separation of concerns
- **Data Access Layer**: Abstraction for database operations
- **Blueprint Structure**: Modular route organization
- **Application Factory**: Flexible configuration management

### 5.3 Database Schema
- Users: user_id, name, email, password_hash, role, department
- Resources: resource_id, owner_id, title, description, category, location, capacity, status
- Bookings: booking_id, resource_id, requester_id, start_datetime, end_datetime, status
- Messages: message_id, thread_id, sender_id, receiver_id, content
- Reviews: review_id, resource_id, reviewer_id, rating, comment

---

## 6. Security Considerations

### 6.1 Authentication Security
- Password hashing with bcrypt (cost factor 12)
- CSRF protection on all forms (Flask-WTF)
- Session security with secure cookies
- Password complexity recommendations

### 6.2 Authorization
- Role-based access control (RBAC)
- Resource ownership verification
- Admin-only route protection
- Authorization checks before all sensitive operations

### 6.3 Input Validation & Sanitization
- Server-side form validation
- SQL injection prevention via ORM
- XSS prevention via template escaping
- File upload validation and size limits

---

## 7. Future Enhancements

- Email notifications for booking status changes
- SMS notifications for urgent updates
- Calendar integration (Google Calendar, Outlook)
- Payment processing for premium resources
- Analytics dashboard with usage insights
- Mobile native applications (iOS, Android)
- Real-time availability updates with WebSockets
- Advanced search with filters and sorting
- Resource recommendations based on user history

---

## 8. Development Timeline

**Phase 1 (Completed)**: Core Infrastructure
- Database models and relationships
- Data Access Layer implementation
- Flask application setup

**Phase 2 (Completed)**: Controllers & Views
- All controller blueprints
- Accessible HTML templates
- WCAG compliance implementation

**Phase 3 (In Progress)**: Testing & Documentation
- Test suite development
- Documentation completion
- Accessibility testing

**Phase 4 (Upcoming)**: Deployment
- Production database setup
- Server configuration
- CI/CD pipeline setup

---

## 9. Acceptance Criteria

### Functional Requirements
- ✅ Users can register and login securely
- ✅ Resources can be created, edited, and deleted
- ✅ Search and filtering work correctly
- ✅ Bookings are created without conflicts
- ✅ Messaging system enables user communication
- ✅ Reviews can be submitted with ratings

### Non-Functional Requirements
- ✅ All pages meet WCAG 2.1 AA standards
- ⏳ 95%+ automated test coverage
- ⏳ Page load time < 2 seconds
- ✅ Responsive design for mobile/tablet/desktop
- ✅ Secure password storage and CSRF protection

### Accessibility Requirements
- ✅ Keyboard navigation for all features
- ✅ Screen reader compatibility
- ✅ Color contrast ratio compliance
- ✅ ARIA labels and landmarks
- ⏳ Automated accessibility test suite

---

**Document Status**: Draft  
**Next Review Date**: November 15, 2025  
**Approved By**: [Pending]
