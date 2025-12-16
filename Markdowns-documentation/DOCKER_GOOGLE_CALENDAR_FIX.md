# Fix Google Calendar Integration in Docker

## Problem
The Google Calendar API credentials weren't being passed to the Docker container, so the integration wasn't working.

## Solution

### Step 1: Update .env File (IMPORTANT!)

Open your `.env` file and change the redirect URI from port **5000** to port **8080**:

**Change this:**
```bash
GOOGLE_REDIRECT_URI=http://localhost:5000/calendar/callback
```

**To this:**
```bash
GOOGLE_REDIRECT_URI=http://localhost:8080/calendar/callback
```

**Why?** Docker exposes the app on port 8080, not 5000.

### Step 2: Update Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs":
   - **Add**: `http://localhost:8080/calendar/callback`
   - Keep the old one if you also run without Docker: `http://localhost:5000/calendar/callback`
4. Click **SAVE**

### Step 3: Restart Docker

```bash
# Stop the current container
docker-compose down

# Rebuild and start with new environment variables
docker-compose up --build -d

# Check if it's running
docker-compose ps
```

### Step 4: Test the Connection

1. Open browser: http://localhost:8080
2. Login as student: `asmith@university.edu` / `student123`
3. Go to Dashboard → Profile
4. Scroll to "Google Calendar Integration"
5. Click "Connect Google Calendar"
6. Should redirect to Google authorization page ✅
7. Authorize and you're connected! 🎉

---

## What Was Fixed

✅ Added `GOOGLE_CLIENT_ID` to docker-compose.yml  
✅ Added `GOOGLE_CLIENT_SECRET` to docker-compose.yml  
✅ Added `GOOGLE_REDIRECT_URI` to docker-compose.yml  
✅ Set default redirect URI to port 8080 for Docker

---

## Quick Commands

```bash
# Stop Docker
docker-compose down

# Start Docker with updated config
docker-compose up -d

# View logs
docker-compose logs -f web

# Check container status
docker-compose ps

# Restart if needed
docker-compose restart
```

---

## Verify Environment Variables in Container

Check if the variables are loaded in the container:

```bash
docker-compose exec web python -c "import os; print('GOOGLE_CLIENT_ID:', 'SET' if os.getenv('GOOGLE_CLIENT_ID') else 'NOT SET')"
```

Should show: `GOOGLE_CLIENT_ID: SET`

---

## For Production Deployment

When deploying to production, update:

1. **In .env:**
   ```bash
   GOOGLE_REDIRECT_URI=https://your-domain.com/calendar/callback
   ```

2. **In Google Cloud Console:**
   - Add production URI: `https://your-domain.com/calendar/callback`

---

## Troubleshooting

### "redirect_uri_mismatch" error
- Make sure you updated the redirect URI in BOTH:
  1. `.env` file (to port 8080)
  2. Google Cloud Console (add the 8080 version)

### Environment variables not loading
```bash
# Rebuild the container
docker-compose up --build -d

# Or completely remove and recreate
docker-compose down -v
docker-compose up -d
```

### Still showing "not configured" warning
- Check container logs: `docker-compose logs web`
- Verify .env file has the correct values
- Make sure you ran `docker-compose down` and `docker-compose up` after changes

---

**Now restart Docker with these changes and test!** 🚀

