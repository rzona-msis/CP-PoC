# Complete Google APIs Setup for Docker

This guide configures **all three Google integrations** for Docker deployment:
1. ✅ **Google Calendar** - Auto-sync bookings
2. ✅ **Gemini AI** - AI chatbot assistant
3. ✅ **Google Analytics** - Usage tracking & analytics

---

## Quick Fix - Update Your .env File

### Step 1: Edit .env File

Open your `.env` file and **update this line**:

**CHANGE FROM:**
```bash
GOOGLE_REDIRECT_URI=http://localhost:5000/calendar/callback
```

**CHANGE TO:**
```bash
GOOGLE_REDIRECT_URI=http://localhost:8080/calendar/callback
```

**Why?** Docker uses port 8080, not 5000.

### Step 2: Verify All Google API Settings

Your `.env` should have these sections (use `env.docker.template` as reference):

```bash
# Google Calendar (already configured ✅)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8080/calendar/callback

# Gemini AI (add if using AI chatbot)
GEMINI_API_KEY=your-gemini-api-key-here

# Google Analytics (add if using analytics)
GA_MEASUREMENT_ID=G-XXXXXXXXXX

# Google Cloud Platform (add if using BigQuery analytics)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-credentials.json
```

---

## Google Cloud Console Setup

### 1. Google Calendar API ✅

**Already configured**, but verify:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs", **add both**:
   ```
   http://localhost:5000/calendar/callback  (for local dev without Docker)
   http://localhost:8080/calendar/callback  (for Docker) ← ADD THIS!
   ```
4. Click **SAVE**

**Test Users:**
- Go to: https://console.cloud.google.com/apis/credentials/consent
- Add test users: `asmith@university.edu`, etc.

---

### 2. Gemini AI Setup

**Get API Key:**
1. Go to: https://makersuite.google.com/app/apikey
2. Click **"Create API Key"**
3. Select your Google Cloud project (or create new)
4. Click **"Create API key in existing project"**
5. **Copy the API key**

**Add to .env:**
```bash
GEMINI_API_KEY=your-actual-api-key-here
```

**Enable in Google Cloud:**
1. Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
2. Click **"ENABLE"**

**What it does:**
- Powers the AI Assistant chatbot at `/ai`
- Answers questions about resources
- Helps users find what they need

---

### 3. Google Analytics Setup

**Get Measurement ID:**
1. Go to: https://analytics.google.com/
2. Admin (bottom left) → Create Property
3. Property Name: "Campus Resource Hub"
4. Set timezone, currency
5. After creation, go to **Data Streams**
6. Click your web stream
7. Copy the **"Measurement ID"** (starts with G-)

**Add to .env:**
```bash
GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

**What it does:**
- Tracks page views, user behavior
- Dashboard at `/analytics/dashboard`
- Exports data for analysis

---

### 4. Google Cloud Platform (Advanced Analytics)

**Only needed if using BigQuery integration**

**Create Service Account:**
1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click **"CREATE SERVICE ACCOUNT"**
3. Name: "campus-hub-analytics"
4. Grant role: **"BigQuery Admin"**
5. Click **"DONE"**
6. Click on the service account
7. Keys tab → **"ADD KEY"** → **"Create new key"**
8. Choose **JSON**
9. Download the JSON file

**Add to Docker:**

1. Save the JSON file as `gcp-credentials.json` in your project root

2. Update `docker-compose.yml` volumes:
```yaml
volumes:
  - ./src/campus_hub.db:/app/src/campus_hub.db
  - ./logs:/app/logs
  - ./gcp-credentials.json:/app/credentials/gcp-credentials.json:ro  # ← ADD THIS
```

3. Update `.env`:
```bash
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-credentials.json
```

**Enable APIs:**
- BigQuery API: https://console.cloud.google.com/apis/library/bigquery.googleapis.com
- Cloud Storage API: https://console.cloud.google.com/apis/library/storage-json.googleapis.com

---

## Restart Docker with All APIs

### Stop Current Container
```bash
docker-compose down
```

### Rebuild and Start
```bash
docker-compose up --build -d
```

### Check Logs
```bash
docker-compose logs -f web
```

### Verify Environment Variables
```bash
# Check all Google APIs are loaded
docker-compose exec web python -c "
import os
print('Google Calendar:', 'SET' if os.getenv('GOOGLE_CLIENT_ID') else 'NOT SET')
print('Gemini AI:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET')
print('Analytics:', 'SET' if os.getenv('GA_MEASUREMENT_ID') else 'NOT SET')
print('GCP:', 'SET' if os.getenv('GOOGLE_CLOUD_PROJECT') else 'NOT SET')
"
```

Should show all as "SET" if configured.

---

## Testing Each Feature

### Test 1: Google Calendar ✅

1. Open: http://localhost:8080
2. Login: `asmith@university.edu` / `student123`
3. Dashboard → Profile
4. Scroll to "Google Calendar Integration"
5. Click **"Connect Google Calendar"**
6. Should redirect to Google authorization
7. Authorize → Success!

### Test 2: Gemini AI Chatbot ✅

1. Click **"AI Assistant"** in top menu
2. Or go to: http://localhost:8080/ai
3. Ask: "What study rooms are available?"
4. Should get AI-powered response
5. Try: "Show me equipment I can borrow"

### Test 3: Google Analytics ✅

1. Browse around the site (creates events)
2. Login as admin: `admin@university.edu` / `admin123`
3. Go to: http://localhost:8080/analytics/dashboard
4. Should see analytics dashboard
5. Events may take 24-48 hours to appear in GA

### Test 4: GCP BigQuery (Advanced) ✅

1. Login as admin
2. Analytics → Export
3. Click "Export to BigQuery"
4. Check BigQuery console for data

---

## Summary Checklist

**Environment Variables (.env file):**
- [ ] `GOOGLE_CLIENT_ID` - Set ✅
- [ ] `GOOGLE_CLIENT_SECRET` - Set ✅
- [ ] `GOOGLE_REDIRECT_URI` - Changed to port **8080** ✅
- [ ] `GEMINI_API_KEY` - Set (if using AI)
- [ ] `GA_MEASUREMENT_ID` - Set (if using analytics)
- [ ] `GOOGLE_CLOUD_PROJECT` - Set (if using GCP)
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` - Set (if using GCP)

**Google Cloud Console:**
- [ ] Calendar API enabled
- [ ] OAuth redirect URI updated (port 8080)
- [ ] Test users added
- [ ] Gemini API key generated
- [ ] GA property created
- [ ] Service account created (if using GCP)
- [ ] BigQuery/Storage APIs enabled (if using GCP)

**Docker:**
- [ ] `docker-compose.yml` updated with environment variables ✅
- [ ] GCP credentials mounted (if using)
- [ ] Container rebuilt: `docker-compose up --build -d`
- [ ] Logs checked: `docker-compose logs -f web`

---

## Quick Commands Reference

```bash
# Stop Docker
docker-compose down

# Start Docker (rebuilds if needed)
docker-compose up --build -d

# View logs
docker-compose logs -f web

# Check running containers
docker-compose ps

# Access container shell
docker-compose exec web bash

# Test environment variables
docker-compose exec web env | grep GOOGLE

# Restart container
docker-compose restart web

# Complete reset (removes volumes)
docker-compose down -v
docker-compose up --build -d
```

---

## Troubleshooting

### Google Calendar: "redirect_uri_mismatch"
**Fix:** 
1. Update `.env`: `GOOGLE_REDIRECT_URI=http://localhost:8080/calendar/callback`
2. Add URI in Google Cloud Console
3. Rebuild Docker: `docker-compose up --build -d`

### Gemini AI: "AI Assistant not available"
**Fix:**
1. Verify `GEMINI_API_KEY` in `.env`
2. Enable Gemini API in Google Cloud Console
3. Restart Docker

### Analytics: "Not configured"
**Fix:**
1. Add `GA_MEASUREMENT_ID` to `.env`
2. Verify measurement ID format: `G-XXXXXXXXXX`
3. Restart Docker

### GCP: "Application Default Credentials not found"
**Fix:**
1. Ensure JSON file is mounted in docker-compose.yml
2. Verify file path in container: `docker-compose exec web ls /app/credentials/`
3. Check `GOOGLE_APPLICATION_CREDENTIALS` points to correct path

---

## Production Deployment

When deploying to production:

**Update .env:**
```bash
GOOGLE_REDIRECT_URI=https://your-domain.com/calendar/callback
FLASK_ENV=production
SECRET_KEY=generate-new-secure-key
```

**Update Google Cloud Console:**
- Add production redirect URI
- Update GA settings for production domain
- Review OAuth consent screen settings
- May need app verification for public access

**Security:**
- Never commit `.env` to Git
- Use Docker secrets in production
- Rotate API keys regularly
- Monitor API usage/quotas

---

## Cost & Limits

**Free Tier:**
- Google Calendar API: Free
- Gemini AI: 60 requests/minute free
- Google Analytics: Free (standard)
- BigQuery: 1 TB queries/month free

**Monitoring:**
- Check quotas: https://console.cloud.google.com/apis/dashboard
- Set up billing alerts
- Monitor API usage

---

**All three APIs are now configured for Docker!** 🎉

Restart Docker and test each feature. See `env.docker.template` for complete reference.

