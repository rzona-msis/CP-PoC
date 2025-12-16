# Campus Resource Hub

<<<<<<< HEAD
A full-stack web application for managing and booking campus resources including study rooms, equipment, lab spaces, and event venues.

**Course**: AI-Driven Development (AiDD) Final Project  
**Due Date**: Friday, November 15, 2025  
**Team**: Core Team (~4 students)

---

## 🎯 Project Overview

Campus Resource Hub enables university departments, student organizations, and individuals to efficiently discover, share, and reserve campus resources. The system provides comprehensive features including real-time availability, booking management, user reviews, administrative moderation, and AI-powered assistance.

### Key Features

✅ **User Management & Authentication**
- Role-based access control (Student, Staff, Admin)
- Secure password hashing with bcrypt
- Session management with Flask-Login

✅ **Resource Listings**
- CRUD operations for resources
- Rich metadata (title, description, category, location, capacity)
- Lifecycle management (draft → published → archived)

✅ **Search & Discovery**
- Keyword search across resources
- Advanced filtering (category, location, date/time)
- Multiple sort options (recent, top-rated, most booked)

✅ **Booking System**
- Calendar-based booking interface
- Real-time conflict detection
- Approval workflows (automatic or manual)
- Status tracking (pending → approved → completed)

✅ **Messaging**
- Direct communication between users
- Threaded conversations
- Booking-specific message threads

✅ **Reviews & Ratings**
- Post-booking review capability
- 5-star rating system
- Aggregate ratings and top-rated badges

✅ **Admin Dashboard**
- System-wide statistics and analytics
- User and resource management
- Content moderation
- Audit logging

---

## 🏗️ Architecture

### Technology Stack

- **Backend**: Python 3.10+ with Flask
- **Database**: SQLite (PostgreSQL-ready for production)
- **Frontend**: Jinja2 templates + Bootstrap 5
- **Authentication**: Flask-Login + bcrypt
- **Testing**: pytest
- **Version Control**: Git + GitHub

### Application Architecture

The application follows the **Model-View-Controller (MVC)** pattern with a dedicated **Data Access Layer (DAL)**:

```
src/
├── controllers/        # Flask routes and blueprints
│   ├── auth.py         # Authentication endpoints
│   ├── resources.py    # Resource CRUD
│   ├── bookings.py     # Booking management
│   ├── messages.py     # Messaging system
│   ├── dashboard.py    # User dashboard
│   └── admin_panel.py  # Admin functions
├── models/             # Data models
│   ├── database.py     # Schema and initialization
│   └── user.py         # User model for Flask-Login
├── data_access/        # Data Access Layer (DAL)
│   ├── user_dal.py     # User CRUD operations
│   ├── resource_dal.py # Resource operations
│   ├── booking_dal.py  # Booking operations
│   ├── message_dal.py  # Messaging operations
│   ├── review_dal.py   # Review operations
│   └── admin_dal.py    # Admin operations
├── views/              # Jinja2 HTML templates
│   ├── base.html       # Base template
│   ├── auth/           # Login, registration
│   ├── resources/      # Resource views
│   ├── bookings/       # Booking views
│   ├── dashboard/      # User dashboard
│   ├── messages/       # Messaging interface
│   ├── admin/          # Admin panel
│   └── errors/         # Error pages
├── static/             # Static files (CSS, JS, images)
├── forms.py            # WTForms form definitions
└── app.py              # Flask application factory
```

---

## 📊 Database Schema

### Core Tables

**users**
- `user_id` (PK)
- `name`, `email` (unique), `password_hash`
- `role` (student/staff/admin)
- `department`, `profile_image`, `created_at`

**resources**
- `resource_id` (PK)
- `owner_id` (FK → users)
- `title`, `description`, `category`, `location`, `capacity`
- `images`, `availability_rules` (JSON)
- `status` (draft/published/archived)
- `requires_approval`, `created_at`

**bookings**
- `booking_id` (PK)
- `resource_id` (FK → resources)
- `requester_id` (FK → users)
- `start_datetime`, `end_datetime`
- `status` (pending/approved/rejected/cancelled/completed)
- `notes`, `created_at`, `updated_at`

**messages**
- `message_id` (PK)
- `thread_id`, `sender_id` (FK), `receiver_id` (FK)
- `booking_id` (FK, optional)
- `content`, `is_read`, `timestamp`

**reviews**
- `review_id` (PK)
- `resource_id` (FK), `reviewer_id` (FK), `booking_id` (FK)
- `rating` (1-5), `comment`, `is_hidden`, `timestamp`

**admin_logs**
- `log_id` (PK)
- `admin_id` (FK), `action`, `target_table`, `target_id`
- `details`, `timestamp`

See `docs/ERD.png` for complete entity-relationship diagram.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/your-team/campus-resource-hub.git
cd campus-resource-hub
```

2. **Create virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
=======
**AI-Driven Development (AiDD) - 2025 Capstone Project**  
Indiana University - Master of Science in Information Systems (MSIS)

A full-stack web application enabling university departments, student organizations, and individuals to list, share, and reserve campus resources.

## 🎯 Quick Start

```bash
# Clone and setup
git clone https://github.com/rzona-msis/AIDD-Final.git
cd "AIDD-Final"
python -m venv venv
.\venv\Scripts\activate
>>>>>>> 68c125b043200000d3a0998c5741ae4adbdc948b
pip install -r requirements.txt

# Initialize database and run
python run.py init-db
python run.py

# Access at http://localhost:5000
```

<<<<<<< HEAD
4. **Initialize the database**

The database will be automatically initialized on first run with sample data.

5. **Run the application**

```bash
python run.py
```

The application will be available at: **http://localhost:5000**

---

## 👥 Test Accounts

The system is pre-seeded with test accounts:

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@university.edu | admin123 |
| **Staff** | sjohnson@university.edu | staff123 |
| **Student** | asmith@university.edu | student123 |

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_user_dal.py

# Run with coverage
pytest --cov=src tests/
```

### Test Coverage

- ✅ Unit tests for Data Access Layer (user, booking, resource)
- ✅ Integration tests for authentication flow
- ✅ Booking conflict detection tests
- ✅ Security validation tests

---

## 🔒 Security Features

### Implemented Security Measures

✅ **Password Security**
- Bcrypt hashing with salt (12 rounds)
- No plaintext passwords in database or logs

✅ **Input Validation**
- Server-side validation for all inputs
- WTForms with custom validators
- Type checking and length limits

✅ **CSRF Protection**
- CSRF tokens on all forms
- Flask-WTF integration

✅ **SQL Injection Prevention**
- Parameterized queries throughout
- No raw SQL with user input

✅ **XSS Protection**
- Template auto-escaping enabled
- Content Security Policy headers

✅ **Authentication & Authorization**
- Session-based authentication
- Role-based access control
- Protected routes with decorators

✅ **File Upload Security**
- File type validation
- Size limits enforced
- Secure filename handling

---

## 🤖 AI-First Development

This project was developed using AI-first methodologies as part of the AiDD curriculum.

### AI Tools Used

- **Cursor AI**: Primary development assistant
- **GitHub Copilot**: Code completion and suggestions
- **Context Management**: Structured prompts and context packs

### AI Documentation

All AI interactions are documented in:
- `.prompt/dev_notes.md` - Complete log of AI assistance
- `.prompt/golden_prompts.md` - Most effective prompts

### Context Pack Structure

```
docs/context/
├── APA/       # Agility, Processes & Automation artifacts
├── DT/        # Design Thinking (personas, journey maps)
├── PM/        # Product Management (PRD, OKRs)
└── shared/    # Common items (glossary, personas)
```

This structure enables AI tools to:
- Understand project requirements and user needs
- Generate contextually appropriate code
- Make informed architectural decisions
- Produce accurate documentation

---

## 📝 API Endpoints

### Authentication
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Authenticate user
- `GET /auth/logout` - End user session

### Resources
- `GET /resources/` - List and search resources
- `GET /resources/<id>` - View resource details
- `POST /resources/create` - Create new resource
- `PUT /resources/<id>/edit` - Update resource
- `DELETE /resources/<id>/delete` - Delete resource

### Bookings
- `POST /bookings/create` - Request booking
- `GET /bookings/<id>` - View booking details
- `POST /bookings/<id>/approve` - Approve booking
- `POST /bookings/<id>/reject` - Reject booking
- `POST /bookings/<id>/cancel` - Cancel booking

### Messages
- `GET /messages/` - List message threads
- `GET /messages/thread/<thread_id>` - View conversation
- `POST /messages/send` - Send message

### Dashboard
- `GET /dashboard/` - User dashboard
- `GET /dashboard/my-resources` - User's resources
- `GET /dashboard/my-bookings` - User's bookings
- `GET /dashboard/profile` - Profile settings

### Admin
- `GET /admin/` - Admin dashboard
- `GET /admin/users` - User management
- `GET /admin/resources` - Resource management
- `GET /admin/bookings` - Booking oversight
- `GET /admin/reviews` - Review moderation

---

## 🎨 User Interface

The application features a modern, responsive design built with Bootstrap 5:

- **Homepage**: Hero section with search, featured resources, categories
- **Resource Listing**: Grid/list view with filters and sorting
- **Resource Details**: Full information, booking interface, reviews
- **Dashboard**: Personalized view of resources, bookings, and messages
- **Admin Panel**: Comprehensive system management interface

### Accessibility Features

- Semantic HTML5 structure
- ARIA labels and roles
- Keyboard navigation support
- Color contrast compliance
- Responsive design (mobile-friendly)

---

## 📈 Project Management

### Development Timeline (18 Days)

- **Days 1-3**: Planning & Setup
- **Days 4-6**: Database & Auth
- **Days 7-9**: Resource CRUD & Search
- **Days 10-12**: Booking Logic & Messaging
- **Days 13-14**: Frontend Polish
- **Days 15**: Testing & Security
- **Days 16**: Documentation
- **Days 17**: Deployment Prep
- **Day 18**: Presentation

### Team Roles

- **Product Lead / PM**: Requirements, prioritization, demo
- **Backend Engineer**: Database, API, authentication, deployment
- **Frontend Engineer / UX**: Templates, components, accessibility
- **Quality & DevOps / Security**: Testing, CI/CD, security audits

---

## 🚢 Deployment

### Local Development

```bash
python run.py
```

### Production Deployment (Optional)

The application is ready for deployment to:
- Heroku
- AWS Elastic Beanstalk
- Google Cloud Platform
- Microsoft Azure

**Environment Variables for Production:**

```
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgresql://... (if using PostgreSQL)
FLASK_ENV=production
```

---

## 📚 Additional Documentation

- **Product Requirements Document**: `docs/context/PM/prd.md`
- **User Personas**: `docs/context/DT/personas.md`
- **Glossary**: `docs/context/shared/glossary.md`
- **AI Development Notes**: `.prompt/dev_notes.md`
- **Golden Prompts**: `.prompt/golden_prompts.md`

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is developed for educational purposes as part of the MSIS AiDD course.

---

## 👨‍💻 Team Members

- [Your Name] - Product Lead
- [Team Member 2] - Backend Engineer
- [Team Member 3] - Frontend Engineer
- [Team Member 4] - QA & Security

---

## 🙏 Acknowledgments

- Indiana University Kelley School of Business
- AiDD Course Instructors
- Open-source community (Flask, Bootstrap, SQLite)
- AI development tools (Cursor, GitHub Copilot)

---

## 📞 Support

For questions or issues:
- Create an issue in the GitHub repository
- Contact team members via university email
- Consult course instructors

---

**Built with ❤️ using AI-First Development practices**

*Campus Resource Hub - Connecting the University Community*
=======
## ✨ Key Features
- 🔍 Search & filter resources by category, location, availability
- 📅 Calendar-based booking with conflict detection
- 👥 Role-based access (Student, Staff, Admin)
- ⭐ Ratings & reviews system
- 💬 Messaging between users
- ♿ **WCAG 2.1 AA Accessibility** - Full keyboard navigation, screen reader support, ARIA labels

## 📁 Project Structure
```
app/
├── controllers/     # Flask routes (MVC)
├── models/         # Database models
├── views/          # Jinja2 templates
├── data_access/    # CRUD operations (DAL)
└── static/         # CSS, JS, images
docs/              # PRD, wireframes, ER diagram
.prompt/           # AI development log
tests/             # pytest test suite
```

See full documentation in [docs/](docs/) folder.

**Due:** November 15, 2025 | **Status:** 🚧 In Development
>>>>>>> 68c125b043200000d3a0998c5741ae4adbdc948b




User Reflection on AI Integration within Development and Completion of This Task:
AI was used extensively throughout the completion of this project, allowing for rapid iteration and development. Our team selected Sonnet 4.5 as our operating model within Cursor as our IDE. AI-driven software development removed a large portion of the labor-intensive coding and provided a strong base of code requiring minimal debugging. Our team extensively utilized RACEF prompt engineering to ensure efficient AI usage, leveraging prompt engineering to reduce token consumption for limited-access models. The two primary “developers” our prompt engineering was built around included a developer and a debugger, prompting one or the other depending on the use case. The separation of tasks and duties ensured proper context and role management during development, reducing overall token usage.

One key takeaway from this assignment that applies to broader AI-driven development was the bottom-line investment required to create a fully functional software solution for the given problem of campus resource management. Outside of time investment (which could be framed as billable hours of development), leveraging an advanced AI model made development incredibly fast. The total bottom-line cost of development consisted of billable hours of coding and the $20 monthly charge for Cursor’s paid model. Compared to standard development, this is a highly cost-effective way to build software, with the ability to scale across multiple developers and more complex tasks.

Word Count: 243 words