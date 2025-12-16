# TMHNA Financial AI Assistant

**AI-Powered Financial Analysis and Master Data Matching MVP**

## 🎯 Overview

This MVP demonstrates how AI can help Toyota Material Handling North America (TMHNA) unify insights and accelerate decision-making across fragmented financial and sales systems resulting from acquisitions.

### Key Features

1. **AI Financial Analysis Assistant**
   - Natural language queries to SQL conversion
   - Automated anomaly detection
   - Variance analysis by region/product
   - Executive-level AI summaries

2. **AI Master Data Matching Tool**
   - Rule-based fuzzy duplicate detection
   - LLM-powered confidence scoring
   - Golden record recommendations
   - Approval workflow for data quality

## 🏗️ Architecture

```
Web Browser (Bootstrap UI)
         ↓
Flask Application (Python)
         ↓
   ┌─────┴─────┐
   │           │
LLM API    SQLite DB
(OpenAI/   (Financial &
Anthropic)  Master Data)
```

## 📊 Technology Stack

- **Frontend**: HTML, Jinja2, Bootstrap 5, Chart.js
- **Backend**: Python 3.9+, Flask
- **Database**: SQLite
- **AI**: OpenAI GPT-4 or Anthropic Claude
- **Deployment**: Compatible with AWS Elastic Beanstalk, Docker

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- OpenAI API key OR Anthropic API key

### Installation

1. **Navigate to project directory**
   ```powershell
   cd "c:\Users\reidz\OneDrive - Indiana University\MSIS\Core Project\PoC\Campus_Resource_Hub"
   ```

2. **Create virtual environment**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```powershell
   # Copy template
   cp .env.template .env
   
   # Edit .env and add your LLM API key
   # For OpenAI:
   #   OPENAI_API_KEY=sk-your-key-here
   # For Anthropic:
   #   ANTHROPIC_API_KEY=your-key-here
   #   LLM_PROVIDER=anthropic
   ```

5. **Initialize database** (automatically runs on first startup, or run manually)
   ```powershell
   python -c "from src.models.financial_db import init_financial_database, seed_financial_data; init_financial_database(); seed_financial_data()"
   ```

6. **Run the application**
   ```powershell
   python application.py
   ```

7. **Access the application**
   - Open browser to: `http://localhost:5000`
   - Navigate to:
     - `/financial-analysis` - AI Financial Analysis
     - `/master-data-matching` - Master Data Matching

## 💡 Example Usage

### Financial Analysis Queries

Try these natural language queries:

- "Explain margin erosion for Q2 by region"
- "Show me total revenue by region for all of 2024"
- "Which products had the highest margin in July 2024?"
- "Compare online vs retail sales performance"
- "Show me products with margins below 20%"

### Master Data Matching

1. Select entity type (Customer, Vendor, or Product)
2. Adjust similarity threshold (0.5-1.0)
3. Enable/disable AI scoring
4. Click "Find Duplicates"
5. Review suggested matches and golden records
6. Approve or reject each match

## 📁 Project Structure

```
Campus_Resource_Hub/
├── application.py              # Entry point for production
├── src/
│   ├── app.py                 # Flask app factory
│   ├── models/
│   │   └── financial_db.py    # Database schema & seeding
│   ├── controllers/
│   │   ├── financial_analysis.py      # Financial routes
│   │   └── master_data_matching.py    # Master data routes
│   ├── services/
│   │   └── llm_service.py     # LLM API wrapper
│   ├── data_access/
│   │   ├── financial_dal.py   # Financial data access
│   │   └── master_data_dal.py # Master data access
│   ├── views/                  # HTML templates
│   │   ├── tmhna_home.html
│   │   ├── financial_analysis.html
│   │   └── master_data_matching.html
│   └── static/                 # CSS, JS, images
├── requirements.txt
├── .env.template
└── README.md
```

## 🗄️ Database Schema

### Financial Analysis Tables

- **regions**: Geographic regions (NA, EU, APAC, LATAM)
- **products**: Product master data with SKUs
- **customers**: Customer records from multiple systems
- **vendors**: Vendor information
- **financial_transactions**: 6 months of transaction data (Q2-Q3 2024)
- **analysis_logs**: History of AI queries and results

### Master Data Tables

- **match_results**: Duplicate detection results with confidence scores
- **golden_records**: Unified master data records

### Demo Data Characteristics

- **180+ days** of financial transactions
- **Intentional anomalies**: Q2 2024 margin compression in Asia Pacific
- **Duplicate records**: Customer, vendor, and product duplicates across SAP/Oracle/Legacy systems
- **Multi-system data**: Simulates data from acquisitions

## 🔧 Configuration

### LLM Provider Options

**OpenAI** (recommended):
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4
```

**Anthropic Claude**:
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here
LLM_MODEL=claude-3-sonnet-20240229
```

### Running Without LLM API (Demo Mode)

The application includes mock LLM responses for testing without an API key. Simply leave the API key fields empty in `.env` and the system will use fallback responses.

## 🧪 Testing

Run the test suite:
```powershell
pytest
```

Test specific modules:
```powershell
pytest src/services/test_llm_service.py
```

## 📈 Next Steps & Enhancements

### Short-Term (2-4 weeks)
- [ ] Enhanced anomaly detection with time-series forecasting
- [ ] Bulk merge operations for duplicates
- [ ] Interactive dashboards with Plotly Dash
- [ ] Export to PowerPoint/PDF

### Mid-Term (1-3 months)
- [ ] Connect to actual TMHNA systems via APIs
- [ ] Role-based access control (RBAC)
- [ ] Audit logging for compliance
- [ ] Query history and favorites

### Long-Term (3-6 months)
- [ ] Migrate to PostgreSQL for production
- [ ] Deploy to AWS/Azure with auto-scaling
- [ ] Predictive modeling for forecasting
- [ ] Integration with Tableau/Power BI

## 🐛 Troubleshooting

### Database Issues
```powershell
# Delete and recreate database
rm src/tmhna_financial.db
python -c "from src.models.financial_db import init_financial_database, seed_financial_data; init_financial_database(); seed_financial_data()"
```

### LLM API Errors
- Verify API key is correct in `.env`
- Check API rate limits and quotas
- Ensure LLM_PROVIDER matches your API key type

### Port Already in Use
```powershell
# Change port in application.py or use environment variable
$env:FLASK_RUN_PORT="5001"
python application.py
```

## 📝 API Documentation

### Financial Analysis Endpoints

**POST /api/analyze**
```json
{
  "query": "Explain margin erosion for Q2 by region"
}
```

**GET /api/regional-summary**
```
?start_date=2024-04-01&end_date=2024-06-30
```

### Master Data Endpoints

**POST /api/find-duplicates**
```json
{
  "entity_type": "customer",
  "threshold": 0.7,
  "use_llm": true
}
```

**POST /api/update-match-status**
```json
{
  "match_id": 123,
  "status": "approved",
  "reviewed_by": "admin"
}
```

## 🤝 Contributing

This is an MVP proof-of-concept. For production deployment, consider:

1. Security hardening (HTTPS, authentication, input validation)
2. Database optimization (indexes, query optimization)
3. Error handling and logging
4. Monitoring and alerting
5. Backup and disaster recovery

## 📄 License

Internal TMHNA proof-of-concept. Not for external distribution.

## 👥 Support

For questions or issues:
- Review ARCHITECTURE.md for technical details
- Check troubleshooting section above
- Contact the development team

---

**Built for TMHNA** | Powered by AI | Flask + Bootstrap + SQLite
