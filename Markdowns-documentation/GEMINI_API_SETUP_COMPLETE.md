# Complete Gemini API Setup Guide

## Current Issue
The API key is showing as "expired" which usually means:
1. Gemini API is not enabled for your project
2. API key restrictions are blocking it
3. API key was created incorrectly

## Step-by-Step Fix

### Step 1: Enable Gemini API (CRITICAL!)

1. **Go to API Library**
   - https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com

2. **Enable the API**
   - Click **"ENABLE"** button
   - Wait 1-2 minutes for activation
   - You should see "API enabled" message

### Step 2: Create API Key Properly

1. **Go to Credentials**
   - https://console.cloud.google.com/apis/credentials

2. **Create New API Key**
   - Click **"+ CREATE CREDENTIALS"**
   - Select **"API key"**
   - Copy the key immediately (you won't see it again!)

3. **Configure API Key Restrictions** (Important!)
   - Click on the newly created API key
   - Under **"API restrictions"**:
     - Select **"Restrict key"**
     - Under "Select APIs", search for **"Generative Language API"**
     - Check the box next to it
     - Click **"SAVE"**

### Step 3: Verify API Key Works

Test in Google AI Studio:
- Go to: https://makersuite.google.com/app/apikey
- Use your API key to test
- If it works there, it should work in your app

### Step 4: Update .env File

```bash
GEMINI_API_KEY=your-new-api-key-here
```

### Step 5: Rebuild Docker

```bash
docker-compose down
docker-compose up --build -d
```

## Common Mistakes

### ❌ Mistake 1: API Not Enabled
- **Symptom**: "API key expired" or "API key invalid"
- **Fix**: Enable Generative Language API in API Library

### ❌ Mistake 2: Wrong API Restrictions
- **Symptom**: Key works in AI Studio but not in app
- **Fix**: Make sure "Generative Language API" is in restrictions

### ❌ Mistake 3: Using Old/Expired Key
- **Symptom**: "API key expired"
- **Fix**: Create a completely new API key

### ❌ Mistake 4: Wrong Project
- **Symptom**: Key doesn't work
- **Fix**: Make sure you're using the same Google Cloud project

## Verification Checklist

Before using the API key:

- [ ] Generative Language API is **ENABLED** in API Library
- [ ] API key is **CREATED** in Credentials
- [ ] API key has **"Generative Language API"** in restrictions
- [ ] API key is **COPIED** correctly (no extra spaces)
- [ ] `.env` file is **UPDATED** with new key
- [ ] Docker is **REBUILT** with new key

## Test API Key

After setup, test it:

```bash
docker-compose exec web python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content('Hello')
print('✅ Works! Response:', response.text)
"
```

## If Still Not Working

1. **Check API Status**
   - https://console.cloud.google.com/apis/dashboard
   - Look for "Generative Language API" - should show as enabled

2. **Check Billing** (if needed)
   - Free tier should work without billing
   - But some features require billing account

3. **Try Different Project**
   - Create a new Google Cloud project
   - Enable Gemini API
   - Create new API key
   - Try again

4. **Check API Key Format**
   - Should start with: `AIzaSy`
   - Should be about 39 characters long
   - No spaces or extra characters

## Quick Test in Browser

Test your API key directly:
- Go to: https://makersuite.google.com/app/apikey
- Enter your API key
- Try generating content
- If it works there, it should work in your app

---

**Most likely issue: Gemini API is not enabled. Make sure to enable it in the API Library!**

