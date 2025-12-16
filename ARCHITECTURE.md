# TMHNA Financial AI Assistant - Architecture & Build Plan

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Browser (Client)                      │
│          Bootstrap UI + Jinja Templates + JS                 │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/HTTPS
┌────────────────▼────────────────────────────────────────────┐
│                    Flask Application                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Route Controllers                                    │   │
│  │  - /financial-analysis (Natural Language Queries)    │   │
│  │  - /master-data-matching (Duplicate Detection)       │   │
│  │  - /api/analyze (AJAX endpoint)                      │   │
│  │  - /api/match (AJAX endpoint)                        │   │
│  └──────────┬───────────────────────────┬────────────────┘   │
│             │                           │                    │
│  ┌──────────▼──────────┐    ┌───────────▼─────────────┐     │
│  │  Business Logic     │    │   LLM API Wrapper       │     │
│  │  - Query Parser     │    │   - OpenAI/Anthropic    │     │
│  │  - Anomaly Detector │    │   - Prompt Templates    │     │
│  │  - Duplicate Scorer │    │   - Response Parser     │     │
│  └──────────┬──────────┘    └─────────────────────────┘     │
│             │                                                │
│  ┌──────────▼──────────────────────────────────────────┐    │
│  │  Data Access Layer (DAL)                            │    │
│  │  - Financial Data DAL                               │    │
│  │  - Master Data DAL                                  │    │
│  └──────────┬──────────────────────────────────────────┘    │
└─────────────┼──────────────────────────────────────────────┘
              │
┌─────────────▼──────────────────────────────────────────────┐
│                    SQLite Database                          │
│  - financial_transactions                                   │
│  - regions, products, customers, vendors                    │
│  - analysis_logs, match_results                             │
└─────────────────────────────────────────────────────────────┘
              │
┌─────────────▼──────────────────────────────────────────────┐
│                   External LLM API                          │
│           (OpenAI / Anthropic / Azure)                      │
└─────────────────────────────────────────────────────────────┘
```

## Data Model

### Financial Analysis Tables

**financial_transactions**
- transaction_id (PK, INTEGER)
- transaction_date (DATE)
- region_id (FK, INTEGER)
- product_id (FK, INTEGER)
- customer_id (FK, INTEGER)
- revenue (DECIMAL)
- cost (DECIMAL)
- margin (DECIMAL, computed)
- quantity (INTEGER)
- sales_channel (TEXT: 'online', 'retail', 'partner')
- created_at (DATETIME)

**regions**
- region_id (PK, INTEGER)
- region_name (TEXT)
- region_code (TEXT)
- country (TEXT)

**products**
- product_id (PK, INTEGER)
- product_name (TEXT)
- sku (TEXT)
- category (TEXT)
- unit_cost (DECIMAL)

**analysis_logs**
- log_id (PK, INTEGER)
- user_query (TEXT)
- sql_query (TEXT)
- llm_response (TEXT)
- anomalies_detected (TEXT, JSON)
- timestamp (DATETIME)

### Master Data Matching Tables

**customers**
- customer_id (PK, INTEGER)
- customer_name (TEXT)
- address (TEXT)
- city (TEXT)
- state (TEXT)
- postal_code (TEXT)
- email (TEXT)
- phone (TEXT)
- source_system (TEXT)
- created_at (DATETIME)

**vendors**
- vendor_id (PK, INTEGER)
- vendor_name (TEXT)
- address (TEXT)
- city (TEXT)
- state (TEXT)
- contact_email (TEXT)
- source_system (TEXT)
- created_at (DATETIME)

**match_results**
- match_id (PK, INTEGER)
- entity_type (TEXT: 'customer', 'vendor', 'product')
- entity_a_id (INTEGER)
- entity_b_id (INTEGER)
- confidence_score (DECIMAL)
- match_reason (TEXT)
- golden_record_suggestion (TEXT, JSON)
- status (TEXT: 'pending', 'approved', 'rejected')
- reviewed_by (TEXT)
- timestamp (DATETIME)

**golden_records**
- golden_id (PK, INTEGER)
- entity_type (TEXT)
- unified_data (TEXT, JSON)
- source_ids (TEXT, JSON array)
- created_at (DATETIME)

## Step-by-Step Build Plan

### Phase 1: Foundation (Steps 1-4)

**Step 1: Clean Up Existing Project Structure**
- Remove Campus Resource Hub specific controllers (resources, bookings, messages, waitlist)
- Keep authentication and admin if needed, or simplify
- Clean up templates folder
- Update README and documentation

**Step 2: Create New Database Schema**
- Write `src/models/financial_db.py` with schema definition
- Create init_financial_database() function
- Write seed_financial_data() for dummy transactions
- Write seed_master_data() for products/customers/vendors with intentional duplicates

**Step 3: Set Up LLM API Wrapper**
- Create `src/services/llm_service.py`
- Implement OpenAI/Anthropic client initialization
- Create prompt templates for financial analysis and duplicate detection
- Add error handling and retry logic
- Support environment variable configuration

**Step 4: Create Data Access Layer**
- Write `src/data_access/financial_dal.py` for query execution
- Write `src/data_access/master_data_dal.py` for duplicate search
- Implement SQL query builders for flexible filtering
- Add methods for logging and result storage

### Phase 2: Core Features (Steps 5-8)

**Step 5: Build Financial Analysis Controller**
- Create `src/controllers/financial_analysis.py`
- Implement route for analysis page (GET /financial-analysis)
- Implement API endpoint for queries (POST /api/analyze)
- Parse natural language → SQL using LLM
- Execute SQL, detect anomalies, format response
- Log all queries and responses

**Step 6: Build Master Data Matching Controller**
- Create `src/controllers/master_data_matching.py`
- Implement route for matching page (GET /master-data-matching)
- Implement API endpoint (POST /api/match)
- Write rule-based duplicate detection (fuzzy matching)
- Call LLM for confidence scoring and golden record suggestions
- Store results in match_results table

**Step 7: Create Frontend Templates**
- Create `src/views/financial_analysis.html`
  - Input form for natural language queries
  - Results panel with SQL, data table, charts
  - Anomaly alerts panel
- Create `src/views/master_data_matching.html`
  - Entity type selector (product/customer/vendor)
  - Duplicate pairs display with confidence scores
  - Golden record recommendations
  - Approve/reject actions
- Create `src/views/index.html` - landing page with nav

**Step 8: Add Visualization and Formatting**
- Integrate Chart.js or similar for financial visualizations
- Add Bootstrap cards, tables, badges for clean UI
- Implement AJAX for async API calls
- Add loading spinners and error messages

### Phase 3: Polish & Testing (Steps 9-12)

**Step 9: Update Configuration**
- Create `.env.template` with LLM API keys
- Update `requirements.txt` with new dependencies
- Configure Flask app in `src/app.py`
- Register new blueprints

**Step 10: Add Business Logic**
- Implement anomaly detection algorithm (z-score, IQR)
- Implement Levenshtein distance for fuzzy matching
- Create confidence scoring rubric
- Add variance analysis helpers

**Step 11: Testing & Validation**
- Test financial queries with sample prompts
- Test duplicate detection accuracy
- Verify SQL injection protection
- Test LLM API error handling
- Validate seed data quality

**Step 12: Documentation & Deployment Prep**
- Write QUICKSTART.md with setup instructions
- Document API endpoints
- Add example queries and outputs
- Create architecture diagrams
- Document next-step enhancements

## Sample Code Scaffolding

### Flask Routes (src/controllers/financial_analysis.py)

```python
from flask import Blueprint, render_template, request, jsonify
from src.services.llm_service import LLMService
from src.data_access.financial_dal import FinancialDAL
import json

financial_bp = Blueprint('financial', __name__)
llm_service = LLMService()
financial_dal = FinancialDAL()

@financial_bp.route('/financial-analysis')
def analysis_page():
    """Render the financial analysis interface"""
    return render_template('financial_analysis.html')

@financial_bp.route('/api/analyze', methods=['POST'])
def analyze_financial_query():
    """
    Process natural language financial query
    Returns: JSON with SQL, results, anomalies, LLM summary
    """
    try:
        user_query = request.json.get('query')
        
        # Step 1: Convert natural language to SQL using LLM
        sql_query = llm_service.natural_language_to_sql(user_query)
        
        # Step 2: Execute SQL query
        results = financial_dal.execute_query(sql_query)
        
        # Step 3: Detect anomalies in results
        anomalies = financial_dal.detect_anomalies(results)
        
        # Step 4: Generate LLM summary
        summary = llm_service.summarize_financial_analysis(
            query=user_query,
            results=results,
            anomalies=anomalies
        )
        
        # Step 5: Log the analysis
        financial_dal.log_analysis(user_query, sql_query, summary, anomalies)
        
        return jsonify({
            'success': True,
            'query': user_query,
            'sql': sql_query,
            'results': results,
            'anomalies': anomalies,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

### HTML/Jinja Templates (src/views/financial_analysis.html)

```html
{% extends "base.html" %}
{% block title %}AI Financial Analysis{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">🤖 AI Financial Analysis Assistant</h1>
    
    <div class="row">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">
                    <h5>Ask a Question About Your Financial Data</h5>
                </div>
                <div class="card-body">
                    <form id="analysisForm">
                        <div class="form-group">
                            <label for="queryInput">Natural Language Query</label>
                            <textarea 
                                class="form-control" 
                                id="queryInput" 
                                rows="3" 
                                placeholder="Example: Explain margin erosion for Q2 by region"
                                required
                            ></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary mt-2">
                            <i class="fas fa-search"></i> Analyze
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Loading Spinner -->
    <div id="loadingSpinner" class="text-center mt-4" style="display: none;">
        <div class="spinner-border text-primary" role="status">
            <span class="sr-only">Analyzing...</span>
        </div>
        <p class="mt-2">AI is analyzing your query...</p>
    </div>
    
    <!-- Results Panel -->
    <div id="resultsPanel" class="mt-4" style="display: none;">
        <!-- LLM Summary -->
        <div class="card mb-3">
            <div class="card-header bg-info text-white">
                <h5>💡 AI Analysis Summary</h5>
            </div>
            <div class="card-body">
                <p id="summaryText"></p>
            </div>
        </div>
        
        <!-- Anomalies -->
        <div id="anomaliesCard" class="card mb-3" style="display: none;">
            <div class="card-header bg-warning">
                <h5>⚠️ Anomalies Detected</h5>
            </div>
            <div class="card-body">
                <ul id="anomaliesList"></ul>
            </div>
        </div>
        
        <!-- SQL Query -->
        <div class="card mb-3">
            <div class="card-header">
                <h5>🔍 Generated SQL Query</h5>
            </div>
            <div class="card-body">
                <pre><code id="sqlQuery"></code></pre>
            </div>
        </div>
        
        <!-- Data Results -->
        <div class="card mb-3">
            <div class="card-header">
                <h5>📊 Query Results</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table id="resultsTable" class="table table-striped table-hover">
                        <thead id="resultsTableHead"></thead>
                        <tbody id="resultsTableBody"></tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Visualization -->
        <div class="card">
            <div class="card-header">
                <h5>📈 Visualization</h5>
            </div>
            <div class="card-body">
                <canvas id="resultsChart"></canvas>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
<script>
document.getElementById('analysisForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const query = document.getElementById('queryInput').value;
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsPanel = document.getElementById('resultsPanel');
    
    // Show loading, hide results
    loadingSpinner.style.display = 'block';
    resultsPanel.style.display = 'none';
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: query})
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Display summary
            document.getElementById('summaryText').textContent = data.summary;
            
            // Display SQL
            document.getElementById('sqlQuery').textContent = data.sql;
            
            // Display anomalies
            if (data.anomalies && data.anomalies.length > 0) {
                const anomaliesList = document.getElementById('anomaliesList');
                anomaliesList.innerHTML = '';
                data.anomalies.forEach(a => {
                    const li = document.createElement('li');
                    li.textContent = a;
                    anomaliesList.appendChild(li);
                });
                document.getElementById('anomaliesCard').style.display = 'block';
            } else {
                document.getElementById('anomaliesCard').style.display = 'none';
            }
            
            // Display results table
            displayResultsTable(data.results);
            
            // Display chart
            displayChart(data.results);
            
            resultsPanel.style.display = 'block';
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Request failed: ' + error.message);
    } finally {
        loadingSpinner.style.display = 'none';
    }
});

function displayResultsTable(results) {
    // Implementation for rendering table...
}

function displayChart(results) {
    // Implementation for Chart.js rendering...
}
</script>
{% endblock %}
```

### SQL Schema + Seed Data (src/models/financial_db.py)

```python
import sqlite3
from datetime import datetime, timedelta
import random
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'tmhna_financial.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_financial_database():
    """Initialize financial analysis database schema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS analysis_logs")
    cursor.execute("DROP TABLE IF EXISTS financial_transactions")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS customers")
    cursor.execute("DROP TABLE IF EXISTS vendors")
    cursor.execute("DROP TABLE IF EXISTS regions")
    cursor.execute("DROP TABLE IF EXISTS match_results")
    cursor.execute("DROP TABLE IF EXISTS golden_records")
    
    # Create regions table
    cursor.execute("""
        CREATE TABLE regions (
            region_id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_name TEXT NOT NULL,
            region_code TEXT NOT NULL,
            country TEXT NOT NULL
        )
    """)
    
    # Create products table
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            sku TEXT NOT NULL,
            category TEXT NOT NULL,
            unit_cost REAL NOT NULL,
            source_system TEXT DEFAULT 'legacy'
        )
    """)
    
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
            margin REAL GENERATED ALWAYS AS (revenue - cost) STORED,
            quantity INTEGER NOT NULL,
            sales_channel TEXT CHECK(sales_channel IN ('online', 'retail', 'partner')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (region_id) REFERENCES regions(region_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    
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
    
    conn.commit()
    conn.close()
    print("Financial database schema created successfully!")

def seed_financial_data():
    """Seed dummy financial transaction data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert regions
    regions = [
        ('North America', 'NA', 'USA'),
        ('Europe', 'EU', 'Germany'),
        ('Asia Pacific', 'APAC', 'Japan'),
        ('Latin America', 'LATAM', 'Brazil')
    ]
    cursor.executemany("INSERT INTO regions (region_name, region_code, country) VALUES (?, ?, ?)", regions)
    
    # Insert products
    products = [
        ('Widget Pro 3000', 'WP-3000', 'Electronics', 45.00, 'SAP'),
        ('Widget Pro 3000', 'WP3000', 'Electronics', 45.00, 'Oracle'),  # Duplicate
        ('Service Plan Premium', 'SPP-001', 'Services', 120.00, 'SAP'),
        ('Premium Service Plan', 'SPP001', 'Services', 120.00, 'Legacy'),  # Duplicate
        ('Industrial Pump X200', 'IPX-200', 'Industrial', 2500.00, 'SAP'),
        ('Hydraulic Valve Set', 'HVS-050', 'Industrial', 340.00, 'Oracle')
    ]
    cursor.executemany(
        "INSERT INTO products (product_name, sku, category, unit_cost, source_system) VALUES (?, ?, ?, ?, ?)", 
        products
    )
    
    # Insert customers with intentional duplicates
    customers = [
        ('Acme Corporation', '123 Main St', 'New York', 'NY', '10001', 'contact@acme.com', '555-1234', 'SAP'),
        ('ACME Corp', '123 Main Street', 'New York', 'NY', '10001', 'info@acme.com', '555-1234', 'Oracle'),  # Duplicate
        ('TechStart Industries', '456 Tech Blvd', 'San Francisco', 'CA', '94102', 'hello@techstart.io', '555-5678', 'SAP'),
        ('TechStart Ind.', '456 Tech Boulevard', 'San Francisco', 'CA', '94102', 'hello@techstart.io', '555-5678', 'Legacy'),  # Duplicate
        ('Global Dynamics Ltd', '789 Enterprise Way', 'Chicago', 'IL', '60601', 'contact@globaldynamics.com', '555-9012', 'SAP')
    ]
    cursor.executemany(
        "INSERT INTO customers (customer_name, address, city, state, postal_code, email, phone, source_system) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        customers
    )
    
    # Insert vendors with duplicates
    vendors = [
        ('Superior Parts Supply', '100 Warehouse Dr', 'Dallas', 'TX', 'sales@superiorparts.com', '555-1111', 'SAP'),
        ('Superior Parts Sply', '100 Warehouse Drive', 'Dallas', 'TX', 'sales@superiorparts.com', '555-1111', 'Oracle'),  # Duplicate
        ('Mountain Manufacturing Co', '200 Factory Ln', 'Denver', 'CO', 'orders@mountainmfg.com', '555-2222', 'SAP'),
        ('Eastern Logistics Group', '300 Shipping Blvd', 'Boston', 'MA', 'logistics@easternlg.com', '555-3333', 'Legacy')
    ]
    cursor.executemany(
        "INSERT INTO vendors (vendor_name, address, city, state, contact_email, phone, source_system) VALUES (?, ?, ?, ?, ?, ?, ?)",
        vendors
    )
    
    # Generate financial transactions (2 quarters of data)
    channels = ['online', 'retail', 'partner']
    start_date = datetime(2024, 4, 1)  # Q2 start
    
    for day_offset in range(180):  # 6 months of data
        current_date = start_date + timedelta(days=day_offset)
        num_transactions = random.randint(5, 15)
        
        for _ in range(num_transactions):
            region_id = random.randint(1, 4)
            product_id = random.randint(1, 6)
            customer_id = random.randint(1, 5)
            quantity = random.randint(1, 50)
            
            # Get product cost
            cursor.execute("SELECT unit_cost FROM products WHERE product_id = ?", (product_id,))
            unit_cost = cursor.fetchone()['unit_cost']
            
            # Calculate revenue with some variance
            base_revenue = unit_cost * quantity * random.uniform(1.3, 2.5)
            
            # Introduce anomaly: Q2 margin erosion in APAC region
            if region_id == 3 and current_date.month in [4, 5, 6]:
                # Lower revenue in Q2 for APAC (margin erosion)
                revenue = base_revenue * random.uniform(0.7, 0.9)
            else:
                revenue = base_revenue
            
            cost = unit_cost * quantity
            channel = random.choice(channels)
            
            cursor.execute("""
                INSERT INTO financial_transactions 
                (transaction_date, region_id, product_id, customer_id, revenue, cost, quantity, sales_channel)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (current_date.strftime('%Y-%m-%d'), region_id, product_id, customer_id, revenue, cost, quantity, channel))
    
    conn.commit()
    conn.close()
    print(f"Seeded financial data with {180 * 10} transactions (approx)")
```

### LLM API Wrapper (src/services/llm_service.py)

```python
import os
import json
from typing import Dict, List, Any
import openai  # or anthropic

class LLMService:
    """Wrapper service for LLM API calls"""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('ANTHROPIC_API_KEY')
        self.model = os.environ.get('LLM_MODEL', 'gpt-4')
        self.provider = os.environ.get('LLM_PROVIDER', 'openai')
        
        if self.provider == 'openai':
            openai.api_key = self.api_key
    
    def natural_language_to_sql(self, user_query: str) -> str:
        """
        Convert natural language query to SQL
        
        Args:
            user_query: User's natural language question
            
        Returns:
            SQL query string
        """
        schema_context = """
        Available tables:
        - financial_transactions (transaction_id, transaction_date, region_id, product_id, customer_id, revenue, cost, margin, quantity, sales_channel)
        - regions (region_id, region_name, region_code, country)
        - products (product_id, product_name, sku, category, unit_cost)
        - customers (customer_id, customer_name, city, state)
        
        Margin is calculated as: revenue - cost
        """
        
        prompt = f"""You are a SQL expert for a financial analysis system.
        
{schema_context}

User question: {user_query}

Generate a valid SQLite query to answer this question. Return ONLY the SQL query, no explanations.
Use JOINs where necessary. Format dates as YYYY-MM-DD. Use strftime for date functions.
"""
        
        if self.provider == 'openai':
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a SQL query generator. Return only SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            sql_query = response.choices[0].message.content.strip()
        else:
            # Implement Anthropic or other provider
            pass
        
        # Clean up the SQL (remove markdown code blocks if present)
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        return sql_query
    
    def summarize_financial_analysis(self, query: str, results: List[Dict], anomalies: List[str]) -> str:
        """
        Generate natural language summary of financial analysis
        
        Args:
            query: Original user query
            results: Query results
            anomalies: List of detected anomalies
            
        Returns:
            Natural language summary
        """
        results_json = json.dumps(results[:10], indent=2)  # Limit to first 10 rows
        anomalies_text = "\n".join(anomalies) if anomalies else "None detected"
        
        prompt = f"""You are a financial analyst AI assistant for TMHNA.

User asked: "{query}"

Query returned {len(results)} results. Sample data:
{results_json}

Anomalies detected:
{anomalies_text}

Provide a concise, executive-level summary (2-3 paragraphs) explaining:
1. What the data shows
2. Key insights and trends
3. Any anomalies or concerns
4. Recommended actions

Be specific with numbers and percentages where relevant.
"""
        
        if self.provider == 'openai':
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial analyst providing executive summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            summary = response.choices[0].message.content.strip()
        else:
            # Implement other providers
            pass
        
        return summary
    
    def score_duplicate_match(self, entity_a: Dict, entity_b: Dict, entity_type: str) -> Dict[str, Any]:
        """
        Use LLM to score duplicate match confidence and suggest golden record
        
        Args:
            entity_a: First entity dict
            entity_b: Second entity dict
            entity_type: 'customer', 'vendor', or 'product'
            
        Returns:
            Dict with confidence_score, reasoning, and golden_record
        """
        prompt = f"""You are a master data quality expert analyzing potential duplicate {entity_type} records.

Entity A: {json.dumps(entity_a, indent=2)}
Entity B: {json.dumps(entity_b, indent=2)}

Analyze these records and return a JSON object with:
1. "confidence_score": 0-100 (likelihood they are the same entity)
2. "match_reason": Brief explanation of matching/non-matching fields
3. "golden_record": Suggested unified record with best values from both

Return ONLY valid JSON, no other text.
"""
        
        if self.provider == 'openai':
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data quality expert. Return only JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            result_text = response.choices[0].message.content.strip()
            # Parse JSON response
            result = json.loads(result_text)
        else:
            # Implement other providers
            pass
        
        return result
```

## Instructions to Run Locally

### Prerequisites
- Python 3.9+
- pip
- Git

### Setup Steps

1. **Clone or Navigate to Project**
```powershell
cd "c:\Users\reidz\OneDrive - Indiana University\MSIS\Core Project\PoC\Campus_Resource_Hub"
```

2. **Create Virtual Environment**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. **Install Dependencies**
```powershell
pip install -r requirements.txt
```

4. **Configure Environment Variables**
```powershell
# Copy template
cp .env.template .env

# Edit .env and add your LLM API key:
# OPENAI_API_KEY=your-key-here
# or
# ANTHROPIC_API_KEY=your-key-here
```

5. **Initialize Database**
```powershell
python -c "from src.models.financial_db import init_financial_database, seed_financial_data; init_financial_database(); seed_financial_data()"
```

6. **Run Flask Application**
```powershell
python application.py
```

7. **Access Application**
- Open browser to `http://localhost:5000`
- Navigate to:
  - `/financial-analysis` for AI Financial Assistant
  - `/master-data-matching` for Duplicate Detection

### Example Queries

**Financial Analysis:**
- "Show me margin trends by region for Q2 2024"
- "Explain margin erosion for Q2 by region"
- "Which products had the highest revenue in July?"
- "Compare online vs retail sales performance"

**Master Data Matching:**
- Select entity type: "Products"
- Click "Find Duplicates"
- Review confidence scores and suggested golden records
- Approve or reject matches

## Next-Step Enhancements After MVP

### Short-Term (2-4 weeks)
1. **Enhanced Anomaly Detection**
   - Time-series forecasting with Prophet/ARIMA
   - Multi-dimensional outlier detection
   - Automated alert notifications

2. **Advanced Duplicate Resolution**
   - Bulk merge operations
   - Fuzzy matching with adjustable thresholds
   - Human-in-the-loop workflow for approvals

3. **Visualization Improvements**
   - Interactive dashboards (Plotly Dash)
   - Drill-down capabilities
   - Export to PowerPoint/PDF

### Mid-Term (1-3 months)
4. **Real Data Integration**
   - Connect to actual TMHNA systems via APIs
   - ETL pipelines for ongoing data sync
   - Incremental duplicate detection

5. **User Management & Security**
   - Role-based access control (RBAC)
   - Audit logging for all actions
   - Single sign-on (SSO) integration

6. **Query Intelligence**
   - Query history and favorites
   - Suggested follow-up questions
   - Natural language to BI dashboard conversion

### Long-Term (3-6 months)
7. **Production Deployment**
   - Migrate SQLite → PostgreSQL/MySQL
   - Deploy to AWS/Azure with auto-scaling
   - CI/CD pipeline with automated testing

8. **Advanced Analytics**
   - Predictive modeling for revenue forecasting
   - What-if scenario analysis
   - Root cause analysis for anomalies

9. **Enterprise Features**
   - Multi-tenancy for different business units
   - Scheduled reports and alerts
   - Integration with Tableau/Power BI
   - RESTful API for third-party integrations

10. **AI Model Fine-Tuning**
    - Train custom models on TMHNA financial data
    - Improve duplicate detection with labeled training data
    - Domain-specific financial terminology understanding
