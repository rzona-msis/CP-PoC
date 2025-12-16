# Campus Resource Hub - Setup & Run Guide

## Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git

## Quick Start

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

This installs:
- Flask 3.0.0 (web framework)
- Flask-Login 0.6.3 (authentication)
- Flask-WTF 1.2.1 (forms & CSRF)
- Flask-SQLAlchemy 3.1.1 (ORM)
- bcrypt 4.1.1 (password hashing)
- pytest 7.4.3 (testing)
- And all dependencies

### 2. Initialize Database
```powershell
python run.py init-db
```

This will:
- Create `instance/campus_resource_hub.db` SQLite database
- Create all tables (users, resources, bookings, messages, reviews)
- Create default admin user:
  - Email: admin@campus.edu
  - Password: admin123
  - **Change this password immediately after first login!**

### 3. Run Development Server
```powershell
python run.py
```

Or alternatively:
```powershell
flask run
```

Access the application at: **http://localhost:5000**

### 4. Login with Admin Account
- Navigate to http://localhost:5000/auth/login
- Email: admin@campus.edu
- Password: admin123
- Immediately change password in admin settings

## Project Structure

```
Campus Resource Hub/
├── app/
│   ├── __init__.py           # Flask application factory
│   ├── controllers/          # Route blueprints
│   │   ├── auth.py          # Login, register, logout
│   │   ├── main.py          # Homepage, search
│   │   ├── resources.py     # Resource CRUD
│   │   ├── bookings.py      # Booking management
│   │   ├── messages.py      # User messaging
│   │   ├── reviews.py       # Resource reviews
│   │   └── admin.py         # Admin dashboard
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── resource.py
│   │   ├── booking.py
│   │   ├── message.py
│   │   └── review.py
│   ├── data_access/         # Data Access Layer
│   │   ├── user_dal.py
│   │   ├── resource_dal.py
│   │   ├── booking_dal.py
│   │   ├── message_dal.py
│   │   └── review_dal.py
│   ├── views/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── auth/
│   │   ├── resources/
│   │   └── bookings/
│   └── static/
│       └── css/
│           └── style.css    # Custom CSS with WCAG compliance
├── tests/                   # Test suite (to be implemented)
├── docs/
│   ├── PRD.md              # Product Requirements
│   └── ACCESSIBILITY.md     # WCAG compliance details
├── .prompt/
│   ├── dev_notes.md        # AI development log
│   └── golden_prompts.md   # Effective prompts reference
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── README.md               # Project overview
```

## Database Commands

### Reset Database (WARNING: Deletes all data!)
```powershell
python run.py reset-db
```

This will:
- Drop all tables
- Recreate tables
- Re-create default admin user

### Manual Database Access
```powershell
# Using Python
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     # Run database queries here
...     from app.models import User
...     users = User.query.all()
```

## Creating Test Data

### Option 1: Manual via Web Interface
1. Start the server
2. Register new users with different roles
3. Login as staff to create resources
4. Login as students to book resources
5. Leave reviews and send messages

### Option 2: Python Script (Create this file)
```python
# scripts/seed_data.py
from app import create_app, db
from app.data_access import UserDAL, ResourceDAL

app = create_app()
with app.app_context():
    # Create test users
    student = UserDAL.create_user(
        name="Test Student",
        email="student@campus.edu",
        password="password123",
        role="student"
    )
    
    staff = UserDAL.create_user(
        name="Test Staff",
        email="staff@campus.edu",
        password="password123",
        role="staff"
    )
    
    # Create test resources
    resource = ResourceDAL.create_resource(
        owner_id=staff.user_id,
        title="Computer Lab 1",
        description="Modern computer lab with 30 workstations",
        category="lab",
        location="Science Building Room 101",
        capacity=30
    )
    
    ResourceDAL.publish_resource(resource.resource_id)
    
    print("Test data created successfully!")
```

Run with: `python scripts/seed_data.py`

## User Roles & Permissions

### Student (Default)
- ✅ Browse and search resources
- ✅ Book resources
- ✅ Send messages to resource owners
- ✅ Leave reviews
- ❌ Cannot create resources
- ❌ Cannot access admin panel

### Staff
- ✅ All student permissions
- ✅ Create and manage resources
- ✅ Approve/reject booking requests for their resources
- ❌ Cannot access admin panel

### Admin
- ✅ All staff permissions
- ✅ Access admin dashboard
- ✅ Manage all users (promote, demote, delete)
- ✅ Moderate all resources
- ✅ View system statistics

## Development Workflow

### 1. Make Changes to Code
Edit files in `app/` directory

### 2. Test Changes
```powershell
# Run the development server (auto-reloads on changes)
python run.py
```

### 3. Run Tests (when implemented)
```powershell
pytest
pytest --cov=app  # With coverage
```

### 4. Commit to Git
```powershell
git add .
git commit -m "Description of changes"
git push origin master
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
**Solution:** Install dependencies: `pip install -r requirements.txt`

### "Database not found" or "no such table"
**Solution:** Initialize database: `python run.py init-db`

### Port 5000 already in use
**Solution:** Specify different port:
```powershell
$env:FLASK_RUN_PORT=5001
python run.py
```

### CSS not loading
**Solution:** Hard refresh browser (Ctrl+Shift+R) or clear cache

### Import errors in Python files
**Solution:** These are expected until dependencies are installed. Run `pip install -r requirements.txt`

### CSRF token errors
**Solution:** Ensure you're using POST forms with `{{ csrf_token() }}` in templates

## Accessibility Testing

### Keyboard Navigation Test
1. Start application
2. Use only Tab, Shift+Tab, Enter, Escape keys
3. Verify all functionality is accessible
4. Check skip navigation link appears on Tab

### Screen Reader Test
1. Install NVDA (free, Windows) or use VoiceOver (macOS)
2. Enable screen reader
3. Navigate through pages
4. Verify all content is announced correctly

### Color Contrast Test
1. Use WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
2. Test text colors against backgrounds
3. Verify 4.5:1 minimum for normal text
4. Verify 3:1 minimum for large text and UI components

### Automated Accessibility Test (when implemented)
```powershell
pytest tests/test_accessibility.py
```

## Next Steps

### Immediate
- [ ] Install dependencies
- [ ] Initialize database
- [ ] Run application and test basic functionality
- [ ] Create test users and resources

### Short Term
- [ ] Implement remaining templates (create resource, booking form, admin panel)
- [ ] Write comprehensive test suite
- [ ] Add demo data seed script
- [ ] Test with screen readers

### Medium Term
- [ ] Deploy to production server
- [ ] Set up CI/CD pipeline
- [ ] Performance optimization
- [ ] User acceptance testing

### Future Enhancements
- [ ] Email notifications
- [ ] Calendar integration
- [ ] Mobile app
- [ ] Advanced search and filters

## Support & Documentation

- **PRD**: See `docs/PRD.md` for product requirements
- **Accessibility**: See `docs/ACCESSIBILITY.md` for WCAG compliance details
- **Development Log**: See `.prompt/dev_notes.md` for AI-driven development notes
- **Effective Prompts**: See `.prompt/golden_prompts.md` for reusable prompt patterns

## License

Copyright 2025 - AiDD 2025 Capstone Project

---

**Last Updated:** November 9, 2025  
**Version:** 1.0  
**Status:** Core application complete, testing phase next
