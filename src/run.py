"""
Application entry point for Campus Resource Hub.

Run this script to start the Flask development server.
"""

import os
from src.app import create_app
from src.models.database import DATABASE_PATH, init_database, seed_sample_data

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DATABASE_PATH):
        print("=" * 60)
        print("Database not found. Initializing new database...")
        print("=" * 60)
        init_database()
        seed_sample_data()
        print("\n" + "=" * 60)
        print("Database initialized successfully!")
        print("=" * 60)
        print("\nTest Accounts Created:")
        print("-" * 60)
        print("Admin:   admin@university.edu / admin123")
        print("Staff:   sjohnson@university.edu / staff123")
        print("Student: asmith@university.edu / student123")
        print("=" * 60)
        print()
    
    # Create and run Flask app
    app = create_app()
    
    print("\n" + "=" * 60)
    print("Campus Resource Hub is starting...")
    print("=" * 60)
    print("Access the application at: http://localhost:5000")
    print("Press CTRL+C to stop the server")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
