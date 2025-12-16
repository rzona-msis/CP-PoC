"""
Database initialization and schema definition for TMHNA Financial AI Assistant.

This module defines the database schema for financial analysis and master data matching.
"""

import sqlite3
from datetime import datetime, timedelta
import random
import os
import json

# Determine database path - support both environment variable and default
# Handle hosted environments that may set DATABASE_PATH to /app/data/campus_hub.db
DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(__file__), '..', 'tmhna_financial.db'))

# Ensure database directory exists
DATABASE_DIR = os.path.dirname(DATABASE_PATH)
if DATABASE_DIR and not os.path.exists(DATABASE_DIR):
    print(f"Creating database directory: {DATABASE_DIR}")
    os.makedirs(DATABASE_DIR, exist_ok=True)


def get_db_connection():
    """
    Create and return a database connection with row factory.
    Creates the database file if it doesn't exist.
    
    Returns:
        sqlite3.Connection: Database connection object
        
    Raises:
        Exception: If database cannot be accessed
    """
    try:
        # Ensure database directory exists
        db_dir = os.path.dirname(DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            print(f"Creating database directory: {db_dir}")
            os.makedirs(db_dir, exist_ok=True)
        
        # Connect to database (will create file if it doesn't exist)
        conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Exception as e:
        print(f"ERROR: Could not connect to database: {e}")
        raise Exception(f"Database connection failed: {str(e)}")


def init_financial_database():
    """Initialize financial analysis database schema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Initializing financial database schema...")
    
    # Drop existing tables in reverse dependency order
    cursor.execute("DROP TABLE IF EXISTS analysis_logs")
    cursor.execute("DROP TABLE IF EXISTS golden_records")
    cursor.execute("DROP TABLE IF EXISTS match_results")
    cursor.execute("DROP TABLE IF EXISTS financial_transactions")
    cursor.execute("DROP TABLE IF EXISTS vendors")
    cursor.execute("DROP TABLE IF EXISTS customers")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS regions")
    
    # Create regions table
    cursor.execute("""
        CREATE TABLE regions (
            region_id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_name TEXT NOT NULL,
            region_code TEXT NOT NULL,
            country TEXT NOT NULL
        )
    """)
    print("✓ Created regions table")
    
    # Create products table
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            sku TEXT NOT NULL,
            category TEXT NOT NULL,
            unit_cost REAL NOT NULL,
            source_system TEXT DEFAULT 'legacy',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created products table")
    
    # Create customers table
    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            address TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,
            email TEXT,
            phone TEXT,
            source_system TEXT DEFAULT 'legacy',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created customers table")
    
    # Create vendors table
    cursor.execute("""
        CREATE TABLE vendors (
            vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_name TEXT NOT NULL,
            address TEXT,
            city TEXT,
            state TEXT,
            contact_email TEXT,
            phone TEXT,
            source_system TEXT DEFAULT 'legacy',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created vendors table")
    
    # Create financial_transactions table
    cursor.execute("""
        CREATE TABLE financial_transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date DATE NOT NULL,
            region_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            revenue REAL NOT NULL,
            cost REAL NOT NULL,
            margin REAL NOT NULL,
            quantity INTEGER NOT NULL,
            sales_channel TEXT CHECK(sales_channel IN ('online', 'retail', 'partner')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (region_id) REFERENCES regions(region_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    print("✓ Created financial_transactions table")
    
    # Create analysis_logs table
    cursor.execute("""
        CREATE TABLE analysis_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_query TEXT NOT NULL,
            sql_query TEXT,
            llm_response TEXT,
            anomalies_detected TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created analysis_logs table")
    
    # Create match_results table
    cursor.execute("""
        CREATE TABLE match_results (
            match_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT CHECK(entity_type IN ('customer', 'vendor', 'product')),
            entity_a_id INTEGER NOT NULL,
            entity_b_id INTEGER NOT NULL,
            confidence_score REAL NOT NULL,
            match_reason TEXT,
            golden_record_suggestion TEXT,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
            reviewed_by TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created match_results table")
    
    # Create golden_records table
    cursor.execute("""
        CREATE TABLE golden_records (
            golden_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            unified_data TEXT NOT NULL,
            source_ids TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created golden_records table")
    
    # Create indexes for performance
    cursor.execute("CREATE INDEX idx_transactions_date ON financial_transactions(transaction_date)")
    cursor.execute("CREATE INDEX idx_transactions_region ON financial_transactions(region_id)")
    cursor.execute("CREATE INDEX idx_match_results_type ON match_results(entity_type, status)")
    print("✓ Created indexes")
    
    conn.commit()
    conn.close()
    print("\n✅ Financial database schema created successfully!")


def seed_financial_data():
    """Seed dummy financial transaction data with intentional patterns and anomalies"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\nSeeding financial data...")
    
    # Insert regions
    regions = [
        ('North America', 'NA', 'USA'),
        ('Europe', 'EU', 'Germany'),
        ('Asia Pacific', 'APAC', 'Japan'),
        ('Latin America', 'LATAM', 'Brazil')
    ]
    cursor.executemany("INSERT INTO regions (region_name, region_code, country) VALUES (?, ?, ?)", regions)
    print(f"✓ Inserted {len(regions)} regions")
    
    # Insert products (with intentional duplicates from different systems)
    products = [
        ('Raymond 7400 Reach Truck', 'RAY-7400', 'Forklifts', 45000.00, 'SAP'),
        ('Raymond Reach Truck 7400', 'RAY7400', 'Forklifts', 45200.00, 'Oracle'),  # Duplicate with slight cost difference
        ('TMHNA Sit-Down Counterbalance', 'TMHNA-8FBE', 'Forklifts', 35000.00, 'SAP'),
        ('TMHNA 8FBE Counterbalance Forklift', 'TMHNA8FBE', 'Forklifts', 34950.00, 'Legacy'),  # Duplicate
        ('Raymond 5500 Orderpicker', 'RAY-5500', 'Forklifts', 52000.00, 'SAP'),
        ('Forklift Battery - 48V 1000Ah', 'BAT-48V1000', 'Parts', 8500.00, 'Oracle'),
        ('Annual Maintenance Contract', 'AMC-2024', 'Services', 2400.00, 'SAP'),
        ('Preventive Maintenance Plan', 'PMP-2024', 'Services', 2350.00, 'Legacy'),
        ('Raymond 9000 Turret Truck', 'RAY-9000', 'Forklifts', 62000.00, 'Oracle'),
        ('Raymond Turret Truck 9000', 'RAY9000', 'Forklifts', 61800.00, 'SAP'),  # Duplicate
    ]
    cursor.executemany(
        "INSERT INTO products (product_name, sku, category, unit_cost, source_system) VALUES (?, ?, ?, ?, ?)", 
        products
    )
    print(f"✓ Inserted {len(products)} products (including duplicates)")
    
    # Insert customers with intentional duplicates
    customers = [
        ('Amazon Fulfillment Center', '123 Logistics Blvd', 'New York', 'NY', '10001', 'procurement@amazon.com', '555-1234', 'SAP'),
        ('Amazon Fulfillment Ctr', '123 Logistics Boulevard', 'New York', 'NY', '10001', 'purchasing@amazon.com', '555-1234', 'Oracle'),  # Duplicate
        ('Walmart Distribution Center', '456 Distribution Dr', 'Bentonville', 'AR', '72712', 'fleet@walmart.com', '555-5678', 'SAP'),
        ('Walmart Dist Center', '456 Distribution Drive', 'Bentonville', 'AR', '72712', 'fleet@walmart.com', '555-5678', 'Legacy'),  # Duplicate
        ('Home Depot Warehouse', '789 Supply Chain Way', 'Atlanta', 'GA', '30339', 'equipment@homedepot.com', '555-9012', 'SAP'),
        ('FedEx Logistics Hub', '100 Express Center', 'Memphis', 'TN', '38125', 'sales@fedex.com', '555-2345', 'Oracle'),
        ('FedEx Logistics Ctr', '100 Express Ctr', 'Memphis', 'TN', '38125', 'sales@fedex.com', '555-2345', 'Legacy'),  # Duplicate
        ('Target Supply Chain', '200 Retail Parkway', 'Minneapolis', 'MN', '55403', 'procurement@target.com', '555-3456', 'SAP'),
        ('Sysco Food Distribution', '300 Foodservice Blvd', 'Houston', 'TX', '77077', 'equipment@sysco.com', '555-4567', 'Oracle'),
        ('Costco Warehouse Operations', '400 Wholesale Way', 'Issaquah', 'WA', '98027', 'fleet@costco.com', '555-5679', 'SAP'),
    ]
    cursor.executemany(
        "INSERT INTO customers (customer_name, address, city, state, postal_code, email, phone, source_system) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        customers
    )
    print(f"✓ Inserted {len(customers)} customers (including duplicates)")
    
    # Insert vendors with duplicates
    vendors = [
        ('Hawker Battery Systems', '100 Power Way', 'Warrensburg', 'MO', 'sales@hawkerbattery.com', '555-1111', 'SAP'),
        ('Hawker Battery Sys', '100 Power Way', 'Warrensburg', 'MO', 'sales@hawkerbattery.com', '555-1111', 'Oracle'),  # Duplicate
        ('Parker Hydraulic Components', '200 Industrial Blvd', 'Cleveland', 'OH', 'orders@parker.com', '555-2222', 'SAP'),
        ('Parker Hydraulics Co', '200 Industrial Boulevard', 'Cleveland', 'OH', 'orders@parker.com', '555-2222', 'Legacy'),  # Duplicate
        ('Crown Equipment Manufacturing', '300 Factory Dr', 'New Bremen', 'OH', 'parts@crownequip.com', '555-3333', 'SAP'),
        ('Cascade Corporation - Forks', '400 Lifting Solutions Way', 'Portland', 'OR', 'sales@cascorp.com', '555-4444', 'Oracle'),
        ('Continental Tire & Rubber Co', '500 Tire Manufacturing Pkwy', 'Charlotte', 'NC', 'contact@continental-tires.com', '555-5555', 'SAP'),
    ]
    cursor.executemany(
        "INSERT INTO vendors (vendor_name, address, city, state, contact_email, phone, source_system) VALUES (?, ?, ?, ?, ?, ?, ?)",
        vendors
    )
    print(f"✓ Inserted {len(vendors)} vendors (including duplicates)")
    
    # Generate financial transactions (6 months of data with Q2 anomaly)
    channels = ['online', 'retail', 'partner']
    start_date = datetime(2024, 4, 1)  # Q2 start (April 1)
    transaction_count = 0
    
    print("✓ Generating financial transactions...")
    
    for day_offset in range(180):  # 6 months of data (Apr-Sep 2024)
        current_date = start_date + timedelta(days=day_offset)
        num_transactions = random.randint(8, 20)  # 8-20 transactions per day
        
        for _ in range(num_transactions):
            region_id = random.randint(1, 4)
            product_id = random.randint(1, 10)
            customer_id = random.randint(1, 10)
            quantity = random.randint(1, 50)
            
            # Get product cost
            cursor.execute("SELECT unit_cost FROM products WHERE product_id = ?", (product_id,))
            unit_cost = cursor.fetchone()['unit_cost']
            
            # Calculate base revenue with variance
            base_revenue = unit_cost * quantity * random.uniform(1.5, 2.8)
            
            # INTRODUCE ANOMALY: Q2 margin erosion in Asia Pacific region
            if region_id == 3 and current_date.month in [4, 5, 6]:  # APAC in Q2
                # Significant margin compression (revenue closer to cost)
                revenue = unit_cost * quantity * random.uniform(1.1, 1.3)  # Much lower margin
            # INTRODUCE ANOMALY: Spike in July for Europe
            elif region_id == 2 and current_date.month == 7:
                # Unusually high revenue spike
                revenue = base_revenue * random.uniform(1.5, 2.0)
            else:
                revenue = base_revenue
            
            cost = unit_cost * quantity
            margin = revenue - cost
            channel = random.choice(channels)
            
            cursor.execute("""
                INSERT INTO financial_transactions 
                (transaction_date, region_id, product_id, customer_id, revenue, cost, margin, quantity, sales_channel)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (current_date.strftime('%Y-%m-%d'), region_id, product_id, customer_id, 
                  round(revenue, 2), round(cost, 2), round(margin, 2), quantity, channel))
            
            transaction_count += 1
    
    conn.commit()
    conn.close()
    print(f"✓ Inserted {transaction_count} financial transactions")
    print("\n✅ Financial data seeded successfully!")
    print("\nKey data characteristics:")
    print("  • Q2 2024 (Apr-Jun): Margin erosion in Asia Pacific region")
    print("  • July 2024: Revenue spike in Europe region")
    print("  • Intentional master data duplicates across SAP/Oracle/Legacy systems")
    print("  • 6 months of transaction history (Apr-Sep 2024)")


if __name__ == "__main__":
    """Run database initialization and seeding"""
    print("=" * 60)
    print("TMHNA Financial Database Setup")
    print("=" * 60)
    init_financial_database()
    seed_financial_data()
    print("\n" + "=" * 60)
    print("Setup complete! Database ready for use.")
    print(f"Location: {DATABASE_PATH}")
    print("=" * 60)
