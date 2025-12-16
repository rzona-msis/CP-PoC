# Google Cloud Platform Analytics Setup Guide

Complete guide for setting up Google Analytics 4 and BigQuery integration for your Campus Resource Hub.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Part 1: Google Analytics 4 Setup](#part-1-google-analytics-4-setup)
3. [Part 2: Google Cloud Platform & BigQuery Setup](#part-2-google-cloud-platform--bigquery-setup)
4. [Part 3: Configure Application](#part-3-configure-application)
5. [Part 4: Export Data to BigQuery](#part-4-export-data-to-bigquery)
6. [Part 5: Build Looker Studio Dashboards](#part-5-build-looker-studio-dashboards)
7. [Troubleshooting](#troubleshooting)

---

## Overview

This integration provides:
- **Google Analytics 4**: Real-time website traffic and user behavior tracking
- **BigQuery**: Data warehouse for analytics data export
- **Looker Studio**: Visual dashboards for data insights
- **Automated exports**: Scheduled data sync from your database to BigQuery

---

## Part 1: Google Analytics 4 Setup

### Step 1: Create Google Analytics Account

1. Go to [Google Analytics](https://analytics.google.com/)
2. Click **Start measuring** or **Admin** (bottom left)
3. Click **Create Account**
   - Account name: "Campus Resource Hub"
   - Click **Next**

### Step 2: Create Property

4. Property name: "Campus Resource Hub - Production"
5. Select timezone: America/Indiana/Indianapolis
6. Select currency: USD
7. Click **Next**

### Step 3: Configure Property Details

8. Industry category: Education
9. Business size: Small (adjust as needed)
10. Usage: Examine user behavior
11. Click **Create**
12. Accept Terms of Service

### Step 4: Set Up Data Stream

13. Select platform: **Web**
14. Website URL: `http://localhost:5000` (development) or your production URL
15. Stream name: "Campus Hub Web App"
16. Click **Create stream**

### Step 5: Get Measurement ID

17. You'll see your **Measurement ID** (format: G-XXXXXXXXXX)
18. **Copy this ID** - you'll need it for `.env` file
19. Keep this page open for Enhanced Measurement settings

### Step 6: Configure Enhanced Measurement (Optional but Recommended)

20. Scroll down to **Enhanced measurement**
21. Enable these tracking options:
    - ✅ Page views (automatic)
    - ✅ Scrolls
    - ✅ Outbound clicks
    - ✅ Site search
    - ✅ Form interactions
    - ✅ File downloads

---

## Part 2: Google Cloud Platform & BigQuery Setup

### Step 1: Create/Select GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click project dropdown (top left)
3. Click **New Project**
   - Project name: "campus-resource-hub"
   - Organization: (select if applicable)
   - Click **Create**
4. **Copy the Project ID** (e.g., "campus-resource-hub-12345")

### Step 2: Enable Required APIs

5. In the search bar, type "BigQuery API"
6. Click **BigQuery API** → Click **Enable**
7. Search for "Cloud Storage API"
8. Click **Cloud Storage API** → Click **Enable**

### Step 3: Create Service Account

9. Navigate to **IAM & Admin** → **Service Accounts**
10. Click **Create Service Account**
    - Name: "campus-hub-analytics"
    - Description: "Service account for analytics data export"
    - Click **Create and Continue**

### Step 4: Grant Permissions

11. Add these roles:
    - **BigQuery Admin** (full access to BigQuery)
    - **Storage Admin** (optional, for file uploads)
12. Click **Continue** → Click **Done**

### Step 5: Create Service Account Key

13. Click on the service account you just created
14. Go to **Keys** tab
15. Click **Add Key** → **Create new key**
16. Select **JSON** format
17. Click **Create**
18. **JSON file downloads automatically** - save it securely!
19. **Important**: Keep this file safe and NEVER commit it to git!

### Step 6: Create BigQuery Dataset (Optional - can be done via app)

20. Go to **BigQuery** in the left menu
21. Click your project name
22. Click **Create Dataset**
    - Dataset ID: "campus_resource_hub"
    - Location: US (multi-region)
    - Click **Create dataset**

---

## Part 3: Configure Application

### Step 1: Set Up Environment Variables

1. Open or create `.env` file in project root:

```bash
# Google Analytics 4
GA_MEASUREMENT_ID=G-XXXXXXXXXX

# Google Cloud Platform - BigQuery
GCP_PROJECT_ID=campus-resource-hub-12345
GCP_DATASET_ID=campus_resource_hub
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

2. Replace values:
   - `GA_MEASUREMENT_ID`: From Part 1, Step 17
   - `GCP_PROJECT_ID`: From Part 2, Step 4
   - `GOOGLE_APPLICATION_CREDENTIALS`: Full path to JSON key file

**Example paths:**
- Windows: `C:\Users\yourname\keys\campus-hub-analytics.json`
- macOS/Linux: `/home/yourname/keys/campus-hub-analytics.json`
- Relative: `./keys/campus-hub-analytics.json`

### Step 2: Secure Your Keys

3. Ensure `.gitignore` includes:
```
.env
*.json
keys/
```

4. **Never commit credentials!**

### Step 3: Install Dependencies

5. Install required packages:
```bash
pip install -r requirements.txt
```

This installs:
- `google-cloud-bigquery`
- `google-cloud-storage`
- `pandas`

---

## Part 4: Export Data to BigQuery

### Option A: Via Admin Dashboard (Recommended)

1. Start your application:
```bash
python run.py
```

2. Log in as admin (admin@university.edu / admin123)

3. Go to **Analytics Dashboard**:
   - Navigate to `/analytics/dashboard`
   - Or add link to admin menu

4. Click **Initialize BigQuery Tables**
   - Creates dataset (if doesn't exist)
   - Creates all necessary tables

5. Click **Export All Data to BigQuery**
   - Exports users, resources, bookings
   - Calculates utilization metrics
   - Shows success/failure for each table

### Option B: Via API (for automation)

**Initialize BigQuery:**
```bash
curl -X POST http://localhost:5000/analytics/api/initialize \
  -H "Cookie: session=your_session_cookie"
```

**Export All Data:**
```bash
curl -X POST http://localhost:5000/analytics/api/export \
  -H "Cookie: session=your_session_cookie"
```

**Individual Exports:**
```bash
# Users only
POST /analytics/api/export/users

# Resources only
POST /analytics/api/export/resources

# Bookings only
POST /analytics/api/export/bookings
```

### Verify Data in BigQuery

1. Go to BigQuery Console
2. Expand your project → dataset
3. You should see tables:
   - `users_analytics`
   - `resources_analytics`
   - `bookings_analytics`
   - `resource_utilization`
   - `user_engagement`

4. Query a table:
```sql
SELECT * FROM `your-project-id.campus_resource_hub.resources_analytics`
LIMIT 10;
```

---

## Part 5: Build Looker Studio Dashboards

### Step 1: Access Looker Studio

1. Go to [Looker Studio](https://lookerstudio.google.com/)
2. Sign in with your Google account
3. Click **Create** → **Data Source**

### Step 2: Connect BigQuery

4. Search for "BigQuery"
5. Click **BigQuery** connector
6. Authorize Looker Studio to access BigQuery
7. Select:
   - **My Projects**
   - Your project: "campus-resource-hub"
   - Dataset: "campus_resource_hub"
   - Table: "resources_analytics"
8. Click **Connect**

### Step 3: Configure Data Source

9. Review fields and data types
10. Click **Create Report** (top right)
11. Click **Add to Report**

### Step 4: Build Your First Dashboard

**Add Charts:**

1. **Total Resources Card**
   - Add → Scorecard
   - Metric: Record Count
   - Label: "Total Resources"

2. **Resources by Category**
   - Add → Pie Chart
   - Dimension: category
   - Metric: Record Count

3. **Average Rating**
   - Add → Scorecard
   - Metric: AVG(average_rating)
   - Label: "Average Resource Rating"

4. **Resources by Status**
   - Add → Bar Chart
   - Dimension: status
   - Metric: Record Count

### Step 5: Add More Data Sources

Repeat Steps 2-3 for other tables:
- `bookings_analytics` - booking trends
- `resource_utilization` - usage metrics
- `user_engagement` - user activity

### Step 6: Create Advanced Visualizations

**Booking Trend Line Chart:**
1. Data source: `bookings_analytics`
2. Chart: Time Series
3. Dimension: created_at (Date)
4. Metric: Record Count
5. Filter: Last 30 days

**Resource Utilization Heatmap:**
1. Data source: `resource_utilization`
2. Chart: Heatmap
3. Rows: resource_id
4. Columns: date
5. Metric: utilization_rate

**Top Resources Table:**
1. Data source: `resources_analytics`
2. Chart: Table
3. Columns: title, total_bookings, average_rating
4. Sort by: total_bookings (descending)
5. Rows: 10

### Sample Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│          Campus Resource Hub Analytics               │
├─────────────────────────────────────────────────────┤
│  Total Resources  │  Total Bookings │  Avg Rating   │
│       156         │      1,234      │     4.5       │
├─────────────────────────────────────────────────────┤
│  Resources by Category    │  Booking Trend          │
│  [Pie Chart]             │  [Line Chart]           │
├─────────────────────────────────────────────────────┤
│  Resource Utilization Rate                          │
│  [Heatmap]                                          │
├─────────────────────────────────────────────────────┤
│  Top 10 Most Booked Resources                       │
│  [Table]                                            │
└─────────────────────────────────────────────────────┘
```

### Step 7: Share Dashboard

1. Click **Share** (top right)
2. Set permissions:
   - **Viewer**: Can only view
   - **Editor**: Can modify dashboard
3. Share link or invite by email
4. Click **Done**

---

## Automated Scheduled Exports

### Option A: Using Cron (Linux/macOS)

Create a script `export_analytics.sh`:
```bash
#!/bin/bash
curl -X POST http://yourdomain.com/analytics/api/export \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

Add to crontab:
```bash
# Export daily at 2 AM
0 2 * * * /path/to/export_analytics.sh
```

### Option B: Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 2:00 AM
4. Action: Start a program
   - Program: `python`
   - Arguments: `path\to\export_script.py`

### Option C: Using Cloud Functions (Advanced)

Create a Google Cloud Function that:
1. Triggers on schedule (Cloud Scheduler)
2. Calls your export API endpoint
3. Sends notification on completion

---

## Troubleshooting

### Google Analytics Not Tracking

**Issue**: No data in Google Analytics dashboard

**Solutions**:
1. Check `GA_MEASUREMENT_ID` in `.env`
2. Clear browser cache
3. Verify script loads:
   - Open browser DevTools → Network tab
   - Look for `gtag/js?id=G-XXXXXXXXXX`
4. Check if ad blockers are interfering
5. Wait 24-48 hours for data to appear

### BigQuery Connection Failed

**Issue**: "GCP not configured" error

**Solutions**:
1. Verify environment variables are set:
```python
import os
print(os.getenv('GCP_PROJECT_ID'))
print(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
```

2. Check JSON key file exists at specified path
3. Verify service account has BigQuery Admin role
4. Ensure APIs are enabled in GCP Console

### Export Fails with Permission Error

**Issue**: "Permission denied" when exporting

**Solutions**:
1. Verify service account roles:
   - Go to IAM & Admin → IAM
   - Find your service account
   - Ensure "BigQuery Admin" role is assigned

2. Check dataset permissions:
   - Open BigQuery → Select dataset
   - Click "Sharing" → "Permissions"
   - Add service account with "BigQuery Data Editor" role

### Looker Studio Can't Connect

**Issue**: "Unable to connect to BigQuery"

**Solutions**:
1. Authorize Looker Studio:
   - Disconnect and reconnect data source
   - Grant all requested permissions

2. Verify table exists in BigQuery
3. Check if you have viewer access to the dataset
4. Try refreshing data source credentials

### Data Not Updating in Dashboard

**Issue**: Dashboard shows old data

**Solutions**:
1. Click "Refresh" in Looker Studio
2. Check when last export ran
3. Verify export completed successfully
4. Refresh data source:
   - Resource → Manage added data sources
   - Click your BigQuery source → Refresh fields

---

## Best Practices

### Security
- ✅ Never commit service account JSON keys
- ✅ Use IAM roles with least privilege
- ✅ Rotate service account keys regularly
- ✅ Enable VPC Service Controls for production
- ✅ Use Secret Manager for credentials

### Performance
- ✅ Export data during low-traffic hours
- ✅ Use incremental exports for large datasets
- ✅ Partition BigQuery tables by date
- ✅ Monitor BigQuery costs and quotas

### Data Quality
- ✅ Validate data before export
- ✅ Log export success/failures
- ✅ Set up alerts for failed exports
- ✅ Regularly verify data accuracy

---

## Cost Estimation

### Google Analytics 4
- **Free tier**: Unlimited events
- **Cost**: $0 for standard implementation

### BigQuery
- **Storage**: $0.02 per GB/month
- **Queries**: $5 per TB processed
- **Streaming inserts**: $0.01 per 200MB

**Estimated monthly cost for Campus Hub:**
- Storage (1 GB): $0.02
- Queries (10 GB processed): $0.05
- **Total**: ~$0.10/month (nearly free!)

### Looker Studio
- **Cost**: Free (included with Google account)

---

## Sample SQL Queries for BigQuery

### Most Popular Resources
```sql
SELECT 
  title,
  total_bookings,
  average_rating
FROM `your-project.campus_resource_hub.resources_analytics`
ORDER BY total_bookings DESC
LIMIT 10;
```

### Daily Booking Trend
```sql
SELECT 
  DATE(created_at) as booking_date,
  COUNT(*) as total_bookings,
  status
FROM `your-project.campus_resource_hub.bookings_analytics`
WHERE created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY booking_date, status
ORDER BY booking_date;
```

### Resource Utilization by Category
```sql
SELECT 
  r.category,
  AVG(u.utilization_rate) as avg_utilization,
  SUM(u.total_bookings) as total_bookings
FROM `your-project.campus_resource_hub.resources_analytics` r
JOIN `your-project.campus_resource_hub.resource_utilization` u
  ON r.resource_id = u.resource_id
GROUP BY r.category
ORDER BY avg_utilization DESC;
```

### User Engagement Metrics
```sql
SELECT 
  date,
  SUM(bookings_created) as new_bookings,
  SUM(bookings_completed) as completed_bookings,
  SUM(reviews_written) as new_reviews
FROM `your-project.campus_resource_hub.user_engagement`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY date
ORDER BY date;
```

---

## Next Steps

Once everything is set up:

1. ✅ Monitor Google Analytics for user behavior
2. ✅ Schedule regular BigQuery exports (daily or weekly)
3. ✅ Build comprehensive Looker Studio dashboards
4. ✅ Set up alerts for key metrics
5. ✅ Share dashboards with stakeholders
6. ✅ Regularly review and optimize queries

---

## Support & Resources

### Official Documentation
- [Google Analytics 4](https://support.google.com/analytics/answer/10089681)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Looker Studio Help](https://support.google.com/looker-studio)

### Campus Resource Hub
- Check application logs for export errors
- Review API documentation at `/analytics/api/status`
- Contact IT administrator for GCP access issues

---

*Last Updated: November 2025*
*Campus Resource Hub - AI-First Development Project*

