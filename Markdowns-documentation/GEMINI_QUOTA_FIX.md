# Fix Gemini AI "Quota Exceeded" Error

## Current Issue
✅ **Good News**: Gemini API is connecting successfully!  
❌ **Problem**: API quota has been exceeded

## Quick Fixes

### Option 1: Check Google Cloud Console Quota

1. **Go to Google Cloud Console**
   - https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas

2. **Check Your Quotas**
   - Look for "Requests per minute" or "Requests per day"
   - Free tier: Usually 60 requests/minute, 1,500 requests/day

3. **Increase Quota (if needed)**
   - Click "Edit Quotas"
   - Request higher limits
   - May require billing account

### Option 2: Verify API Key

1. **Check API Key Status**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Find your API key
   - Check if it's enabled and has correct restrictions

2. **Regenerate API Key (if needed)**
   - Create a new API key
   - Update `.env` file:
     ```bash
     GEMINI_API_KEY=your-new-api-key-here
     ```
   - Rebuild Docker: `docker-compose down && docker-compose up --build -d`

### Option 3: Enable Billing (for Higher Quotas)

1. **Add Billing Account**
   - Go to: https://console.cloud.google.com/billing
   - Add a billing account
   - Link it to your project

2. **Request Quota Increase**
   - Go to quotas page
   - Request higher limits
   - Usually approved within 24 hours

### Option 4: Use Fallback Mode Temporarily

The app will automatically use keyword-based fallback if Gemini fails. This works but is less intelligent.

---

## Check Current Quota Usage

1. **Go to API Dashboard**
   - https://console.cloud.google.com/apis/dashboard
   - Select your project
   - Click on "Generative Language API"
   - View "Quotas" tab

2. **Check Usage**
   - See current usage vs. limits
   - Identify if you're hitting rate limits or daily limits

---

## Common Quota Limits (Free Tier)

- **Requests per minute**: 60
- **Requests per day**: 1,500
- **Tokens per minute**: 32,000
- **Tokens per day**: 1,000,000

---

## Solutions

### Immediate: Wait for Quota Reset
- Daily quotas reset at midnight Pacific Time
- Rate limits reset every minute
- Try again in a few minutes

### Short-term: Use Fallback Mode
- The app automatically falls back to keyword matching
- Less intelligent but still functional
- No API calls needed

### Long-term: Enable Billing
- Get much higher quotas
- Pay only for what you use
- First $300/month free with Google Cloud credits

---

## Verify API Key is Working

Test your API key directly:

```bash
# In Docker container
docker-compose exec web python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
models = genai.list_models()
print('Available models:', [m.name for m in models])
"
```

---

## Update API Key in Docker

If you got a new API key:

1. **Update .env file:**
   ```bash
   GEMINI_API_KEY=your-new-key-here
   ```

2. **Rebuild Docker:**
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

3. **Verify it's loaded:**
   ```bash
   docker-compose exec web env | grep GEMINI
   ```

---

## Alternative: Use Different API Key

If you have multiple Google accounts or projects:

1. Create a new API key in a different project
2. Update `.env` with the new key
3. Rebuild Docker

---

## Monitor Quota Usage

Set up alerts in Google Cloud Console:

1. Go to: https://console.cloud.google.com/monitoring/alerting
2. Create alert for API quota usage
3. Get notified before hitting limits

---

## Summary

**The error means:**
- ✅ Gemini API is working
- ✅ Authentication is successful
- ❌ Quota limit reached

**Next steps:**
1. Check quota usage in Google Cloud Console
2. Wait for reset OR enable billing for higher limits
3. Or use fallback mode (automatic)

**The app will still work** with keyword-based fallback, just less intelligently!

