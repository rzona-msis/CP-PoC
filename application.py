"""
Application entry point for AWS Elastic Beanstalk and production deployment.

Elastic Beanstalk expects a file named 'application.py' with an 'application' object.
This file creates the Flask app and exposes it as 'application' for WSGI servers.
"""

import os
import sys

print("=" * 60, flush=True)
print("Starting application initialization...", flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"Current working directory: {os.getcwd()}", flush=True)
print("=" * 60, flush=True)

# Initialize financial database before importing app - ALWAYS check and create if missing
try:
    from src.models.financial_db import DATABASE_PATH, init_financial_database, seed_financial_data
    
    print(f"Database path: {DATABASE_PATH}", flush=True)
    print(f"Database exists: {os.path.exists(DATABASE_PATH)}", flush=True)
    
    # Always ensure database directory exists
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        print(f"Creating database directory: {db_dir}", flush=True)
        os.makedirs(db_dir, exist_ok=True)
    
    # Check if database exists and is valid
    db_needs_init = False
    if not os.path.exists(DATABASE_PATH):
        print("Database file does not exist.", flush=True)
        db_needs_init = True
    elif os.path.getsize(DATABASE_PATH) == 0:
        print("Database file is empty.", flush=True)
        db_needs_init = True
    
    if db_needs_init:
        print("=" * 60, flush=True)
        print("Initializing financial database...", flush=True)
        print("=" * 60, flush=True)
        try:
            init_financial_database()
            seed_financial_data()
            print("\n" + "=" * 60, flush=True)
            print("Financial database initialized successfully!", flush=True)
            print("=" * 60, flush=True)
        except Exception as init_error:
            print(f"WARNING: Could not initialize database: {init_error}", flush=True)
            import traceback
            traceback.print_exc()
            print("Application will continue with limited functionality.", flush=True)
    else:
        print("Financial database already exists and is valid.", flush=True)
except Exception as e:
    print(f"WARNING: Database initialization skipped: {e}", flush=True)
    import traceback
    traceback.print_exc()
    print("Application will continue with limited functionality.", flush=True)

# Create the Flask application
try:
    from src.app import create_app
    app = create_app()
    print("Flask app created successfully!", flush=True)
except Exception as e:
    print(f"ERROR creating Flask app: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Expose as 'application' for Elastic Beanstalk / WSGI servers
application = app

# For local testing
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)

