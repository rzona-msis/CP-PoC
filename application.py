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

# Initialize financial database before importing app
try:
    from src.models.financial_db import DATABASE_PATH, init_financial_database, seed_financial_data
    
    print(f"Database path: {DATABASE_PATH}", flush=True)
    print(f"Database exists: {os.path.exists(DATABASE_PATH)}", flush=True)
    
    if not os.path.exists(DATABASE_PATH):
        # Ensure database directory exists
        db_dir = os.path.dirname(DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            print(f"Creating database directory: {db_dir}", flush=True)
            os.makedirs(db_dir, exist_ok=True)
        
        print("=" * 60, flush=True)
        print("Financial database not found. Initializing...", flush=True)
        print("=" * 60, flush=True)
        init_financial_database()
        seed_financial_data()
        print("\n" + "=" * 60, flush=True)
        print("Financial database initialized successfully!", flush=True)
        print("=" * 60, flush=True)
    else:
        print("Financial database already exists. Skipping initialization.", flush=True)
except Exception as e:
    print(f"ERROR initializing financial database: {e}", flush=True)
    import traceback
    traceback.print_exc()
    # Continue anyway - database might exist

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

