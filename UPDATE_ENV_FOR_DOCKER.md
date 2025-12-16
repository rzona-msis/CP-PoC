# Update .env File for Docker - All Google Services

## What Needs to Change

Your `.env` file has **ONE LINE** that needs updating for Docker:

**Change the Google Calendar redirect URI from port 5000 → 8080**

---

## Updated .env File (Copy This)

Open your `.env` file and replace its contents with this:

```bash
# Campus Resource Hub - Environment Variables (Docker Configuration)
#
# ================================================================

# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production

# Google Analytics 4 (ACTIVE! - 100% FREE)
GA_MEASUREMENT_ID=G-673T555LVN

# Google Gemini AI Chatbot (ACTIVE! - FREE)
GEMINI_API_KEY=AIzaSyAW4Fwx9MCQld-ICIZBgVAqu5SvMj2ryVY
GEMINI_MODEL=gemini-2.5-flash

# Google Calendar Integration (FULLY CONFIGURED! - FREE)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8080/calendar/callback

# ================================================================
# BigQuery Export (OPTIONAL - Skip to avoid costs!)
# Leave these commented out to use FREE CSV export instead
# ================================================================
# GCP_PROJECT_ID=
# GCP_DATASET_ID=campus_resource_hub
# GOOGLE_APPLICATION_CREDENTIALS=

# ================================================================
# ALL SET! Your configuration includes:
# ✅ Google Analytics tracking (FREE) - Ready for Docker
# ✅ AI Chatbot with Gemini (FREE) - Ready for Docker
# ✅ Google Calendar auto-sync (FREE) - Ready for Docker
# ✅ Analytics dashboard (FREE)
# ✅ CSV data export (FREE)
#
# Total cost: $0.00 per month! 🎉
# Docker port: 8080
# ================================================================
```

**What changed:**
- Line 19: `GOOGLE_REDIRECT_URI=http://localhost:5000/calendar/callback` 
- **Changed to:** `GOOGLE_REDIRECT_URI=http://localhost:8080/calendar/callback`

---

## Quick Change Option

If you prefer to just change the one line:

**Find this line:**
```bash
GOOGLE_REDIRECT_URI=http://localhost:5000/calendar/callback
```

**Change it to:**
```bash
GOOGLE_REDIRECT_URI=http://localhost:8080/calendar/callback
```

---

## Update Google Cloud Console

Since you're changing the redirect URI, you need to add the new one to Google Cloud:

1. Go to: https://console.cloud.google.com/apis/credentials/oauthclient/366276102829-q1rogvpgqh280bqlbqsteqr0fku1mrgn.apps.googleusercontent.com

2. Under "Authorized redirect URIs", click **+ ADD URI**

3. Add: `http://localhost:8080/calendar/callback`

4. Keep the old one too if you want to support both Docker and non-Docker:
   - `http://localhost:5000/calendar/callback` (non-Docker)
   - `http://localhost:8080/calendar/callback` (Docker) ✅ NEW

5. Click **SAVE**

---

## Restart Docker with All Services

```bash
# Stop Docker
docker-compose down

# Start with updated configuration
docker-compose up -d

# View logs to confirm everything loaded
docker-compose logs -f web
```

---

## Verify All Three Services Are Working

### 1. ✅ Google Analytics (Automatic)
- Already working! Tracks page views automatically
- No user action needed
- View in: https://analytics.google.com/

### 2. ✅ Gemini AI Chatbot

**Test it:**
1. Open: http://localhost:8080
2. Login: `asmith@university.edu` / `student123`
3. Click **"AI Assistant"** in top menu
4. Ask: "What resources are available?"
5. Should get AI response! 🤖

**If not working:**
```bash
# Check if API key is loaded
docker-compose exec web python -c "import os; print('GEMINI_API_KEY:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"
```

### 3. ✅ Google Calendar Integration

**Test it:**
1. Open: http://localhost:8080
2. Login: `asmith@university.edu` / `student123`
3. Go to: Dashboard → Profile
4. Scroll to "Google Calendar Integration"
5. Click **"Connect Google Calendar"**
6. Authorize with Google
7. Success! 📅

**If not working:**
```bash
# Check if credentials are loaded
docker-compose exec web python -c "import os; print('GOOGLE_CLIENT_ID:', 'SET' if os.getenv('GOOGLE_CLIENT_ID') else 'NOT SET'); print('GOOGLE_CLIENT_SECRET:', 'SET' if os.getenv('GOOGLE_CLIENT_SECRET') else 'NOT SET'); print('REDIRECT_URI:', os.getenv('GOOGLE_REDIRECT_URI'))"
```

---

## docker-compose.yml Status

✅ **Already updated!** Your docker-compose.yml now includes all three:

```yaml
environment:
  # Already had these:
  - GEMINI_API_KEY=${GEMINI_API_KEY}
  - GA_MEASUREMENT_ID=${GA_MEASUREMENT_ID}
  
  # Just added these:
  - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
  - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
  - GOOGLE_REDIRECT_URI=${GOOGLE_REDIRECT_URI:-http://localhost:8080/calendar/callback}
```

---

## Summary Checklist

- [ ] Update `.env` file (change port 5000 → 8080)
- [ ] Add new redirect URI to Google Cloud Console
- [ ] Run `docker-compose down`
- [ ] Run `docker-compose up -d`
- [ ] Test Gemini AI chatbot
- [ ] Test Google Calendar connection
- [ ] Check Analytics is tracking (it auto-works)

---

## After Updates - What Users Get

### Students Can:
- ✅ **Chat with AI** about resources, bookings, campus info
- ✅ **Connect Google Calendar** to auto-sync approved bookings
- ✅ Get automatic reminders for bookings

### Staff/Admin Can:
- ✅ Everything students can do, plus:
- ✅ **View analytics dashboard** with usage metrics
- ✅ **Export data** to CSV for reports
- ✅ See Google Analytics in real-time

### Automatically Tracked:
- ✅ Page views (Google Analytics)
- ✅ User activity
- ✅ Resource popularity
- ✅ Booking patterns

---

## Quick Test Commands

```bash
# Test all environment variables are loaded
docker-compose exec web python -c "
import os
print('=== Environment Variables Status ===')
print('GEMINI_API_KEY:', 'âœ… SET' if os.getenv('GEMINI_API_KEY') else 'âŒ NOT SET')
print('GA_MEASUREMENT_ID:', 'âœ… SET' if os.getenv('GA_MEASUREMENT_ID') else 'âŒ NOT SET')
print('GOOGLE_CLIENT_ID:', 'âœ… SET' if os.getenv('GOOGLE_CLIENT_ID') else 'âŒ NOT SET')
print('GOOGLE_CLIENT_SECRET:', 'âœ… SET' if os.getenv('GOOGLE_CLIENT_SECRET') else 'âŒ NOT SET')
print('GOOGLE_REDIRECT_URI:', os.getenv('GOOGLE_REDIRECT_URI'))
"

# View application logs
docker-compose logs --tail=50 web

# Restart if needed
docker-compose restart web
```

---

## Troubleshooting

### Gemini AI not responding
- Check API key is valid: https://aistudio.google.com/app/apikey
- Verify quota limits haven't been exceeded (free tier: 60 requests/min)
- Check logs: `docker-compose logs web | grep -i gemini`

### Google Calendar won't connect
- Verify redirect URI matches in both .env and Google Cloud Console
- Check test users are added in OAuth consent screen
- Make sure you're using port 8080 (not 5000)

### Analytics not tracking
- Should work automatically, no setup needed!
- Check browser isn't blocking analytics
- View real-time reports in Google Analytics (takes 24-48 hours for full reports)

---

**Ready to update? Change that one line in .env and restart Docker!** 🚀

