# Quick Start Guide - Campus Resource Hub

Get up and running in 5 minutes! 🚀

---

## Prerequisites

- Python 3.10+ installed
- pip package manager
- Git (to clone repository)

---

## Installation Steps

### 1. Clone and Navigate
```bash
git clone https://github.com/your-team/campus-resource-hub.git
cd campus-resource-hub
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python run.py
```

The app will:
- ✅ Automatically create the database
- ✅ Seed sample data
- ✅ Start the development server

---

## Access the Application

Open your browser and navigate to:
**http://localhost:5000**

---

## Test Accounts

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@university.edu | admin123 |
| **Staff** | sjohnson@university.edu | staff123 |
| **Student** | asmith@university.edu | student123 |

---

## What to Try

### As a Student:
1. **Login** with student account
2. **Browse Resources** - Search for study rooms
3. **Book a Resource** - Select a resource and request booking
4. **View Dashboard** - Check your bookings
5. **Leave a Review** - After a completed booking

### As Staff:
1. **Login** with staff account
2. **Create a Resource** - Add a new resource listing
3. **Manage Bookings** - Approve/reject booking requests
4. **View Dashboard** - See your resources and pending approvals

### As Admin:
1. **Login** with admin account
2. **Access Admin Panel** - Click "Admin" in navigation
3. **View Statistics** - System-wide analytics
4. **Manage Users** - View and moderate users
5. **Moderate Content** - Review and hide inappropriate reviews

---

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_user_dal.py

# Run with coverage report
pytest --cov=src tests/
```

---

## Common Issues

### Issue: Port 5000 already in use
**Solution**: Change the port in `run.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use 5001 instead
```

### Issue: Module not found errors
**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
pip install -r requirements.txt
```

### Issue: Database locked
**Solution**: Stop the Flask server and delete `campus_hub.db`, then restart:
```bash
rm campus_hub.db  # On Windows: del campus_hub.db
python run.py
```

---

## Project Structure Overview

```
campus-resource-hub/
├── src/
│   ├── controllers/      # Flask routes (auth, resources, bookings, etc.)
│   ├── data_access/      # Database operations (DAL pattern)
│   ├── models/           # Data models (database, user)
│   ├── views/            # HTML templates (Jinja2)
│   ├── static/           # CSS, JS, images
│   ├── forms.py          # WTForms validation
│   └── app.py            # Flask app factory
├── tests/                # Unit and integration tests
├── docs/                 # Documentation and context
├── .prompt/              # AI development logs
├── requirements.txt      # Python dependencies
├── run.py                # Application entry point
└── README.md             # Full documentation
```

---

## Next Steps

1. **Read the README** - Full project documentation
2. **Explore the Code** - Check out MVC architecture
3. **Review Tests** - See test-driven development examples
4. **Check Documentation** - `.prompt/dev_notes.md` for AI usage
5. **Customize** - Modify for your specific needs

---

## Key Features to Explore

✅ User authentication with role-based access  
✅ Resource creation and management  
✅ Booking system with conflict detection  
✅ Real-time messaging between users  
✅ Review and rating system  
✅ Admin dashboard with analytics  
✅ Responsive Bootstrap 5 UI  
✅ Security features (CSRF, XSS protection, password hashing)  

---

## Need Help?

- **Full Documentation**: See [README.md](README.md)
- **AI Features**: See [docs/AI_FEATURE_GUIDE.md](docs/AI_FEATURE_GUIDE.md)
- **Product Requirements**: See [docs/context/PM/prd.md](docs/context/PM/prd.md)
- **User Personas**: See [docs/context/DT/personas.md](docs/context/DT/personas.md)

---

## Stopping the Server

Press `CTRL+C` in the terminal where the server is running.

---

**Happy Coding! 🎓**

*Campus Resource Hub - Built with AI-First Development practices*

