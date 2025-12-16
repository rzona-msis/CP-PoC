# Gemini API Key Troubleshooting

## Current Issues Found

1. ❌ **API Key Expired**: The API key is showing as expired
2. ⚠️ **Using Experimental Model**: Code is trying to use `gemini-2.5-pro-exp` which has stricter quotas

## Quick Fixes

### Step 1: Verify API Key in Google Cloud Console

1. **Go to Google Cloud Console**
   - https://console.cloud.google.com/apis/credentials

2. **Check Your API Key**
   - Find the key: `AIzaSyApHWoW7H9tDWWMQZDtr4EZxfcluvkan24`
   - Check if it's:
     - ✅ Enabled
     - ✅ Not expired
     - ✅ Has correct API restrictions

3. **If Expired or Invalid:**
   - Click "Create Credentials" → "API Key"
   - Copy the new key
   - Update `.env` file

### Step 2: Enable Gemini API

1. **Go to API Library**
   - https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com

2. **Enable the API**
   - Click "ENABLE" if not already enabled
   - Wait a few minutes for it to activate

### Step 3: Check API Restrictions

1. **Edit Your API Key**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click on your API key
   - Under "API restrictions":
     - Select "Restrict key"
     - Make sure "Generative Language API" is checked
   - Click "SAVE"

### Step 4: Create New API Key (If Needed)

If the current key is expired:

1. **Create New Key**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click "Create Credentials" → "API Key"
   - Copy the new key immediately (you won't see it again!)

2. **Update .env**
   ```bash
   GEMINI_API_KEY=your-new-key-here
   ```

3. **Rebuild Docker**
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

## Fix Model Selection Issue

The code is trying to use `gemini-2.5-pro-exp` which is experimental. Let's force it to use a stable model.

### Update Model Selection

The code should use:
- `gemini-pro` (stable, free tier)
- `gemini-1.5-flash` (faster, free tier)
- NOT `gemini-2.5-pro-exp` (experimental, stricter quotas)

## Check Quota Status

1. **View Usage**
   - https://ai.dev/usage?tab=rate-limit
   - Check your current usage vs limits

2. **Free Tier Limits**
   - 60 requests/minute
   - 1,500 requests/day
   - 32,000 tokens/minute
   - 1,000,000 tokens/day

## Test API Key Directly

Test if your API key works:

```bash
# In Docker container
docker-compose exec web python -c "
import google.generativeai as genai
import os
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content('Hello')
    print('✅ API Key works!')
    print('Response:', response.text[:100])
except Exception as e:
    print('❌ Error:', str(e)[:200])
"
```

## Common Issues

### "API key expired"
- **Fix**: Create a new API key in Google Cloud Console
- **Update**: `.env` file with new key
- **Rebuild**: Docker container

### "API key invalid"
- **Fix**: Check API key is enabled
- **Fix**: Verify Gemini API is enabled for your project
- **Fix**: Check API restrictions allow Generative Language API

### "Quota exceeded"
- **Wait**: Rate limits reset every minute
- **Wait**: Daily limits reset at midnight Pacific
- **Upgrade**: Enable billing for higher quotas

### "Model not found"
- **Fix**: Use stable models (`gemini-pro`, `gemini-1.5-flash`)
- **Avoid**: Experimental models (`gemini-2.5-pro-exp`)

## Next Steps

1. ✅ Check API key status in Google Cloud Console
2. ✅ Verify Gemini API is enabled
3. ✅ Create new API key if expired
4. ✅ Update `.env` with new key
5. ✅ Rebuild Docker
6. ✅ Test again

---

**The API key appears to be expired. Please create a new one in Google Cloud Console and update the `.env` file!**

