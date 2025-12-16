# Quick Google Calendar Setup for Students

## Current Status
✅ Credentials are configured in `.env`  
⚠️ Need to verify Google Cloud Console settings

---

## Step-by-Step Setup (5 minutes)

### Step 1: Access Google Cloud Console

1. Go to: https://console.cloud.google.com/
2. Select your project (or create a new one if you haven't)

### Step 2: Enable Google Calendar API

1. Go to: **APIs & Services** → **Library**
2. Search for: **"Google Calendar API"**
3. Click on it → Click **"ENABLE"** (if not already enabled)

### Step 3: Configure OAuth Consent Screen

1. Go to: **APIs & Services** → **OAuth consent screen**
2. If not configured yet:
   - Select **External** user type
   - Click **Create**

3. Fill in required fields:
   - **App name**: Campus Resource Hub
   - **User support email**: Your email
   - **Developer contact information**: Your email
   - Click **Save and Continue**

4. **Scopes** page:
   - Click **Add or Remove Scopes**
   - Search: "calendar"
   - Select: `https://www.googleapis.com/auth/calendar.events`
   - Click **Update** → **Save and Continue**

5. **Test Users** (IMPORTANT!):
   - Click **+ Add Users**
   - Add these emails:
     ```
     asmith@university.edu
     mgarcia@university.edu
     admin@university.edu
     sjohnson@university.edu
     dlee@university.edu
     ```
   - Or add any email addresses that need to test the feature
   - Click **Save and Continue**

6. Click **Back to Dashboard**

### Step 4: Verify OAuth Credentials

1. Go to: **APIs & Services** → **Credentials**

2. Look for your OAuth 2.0 Client ID
   - If you don't have one, click **+ Create Credentials** → **OAuth client ID**
   - Application type: **Web application**
   - Name: Campus Resource Hub

3. **Add Authorized Redirect URIs** (CRITICAL!):
   - Under "Authorized redirect URIs", click **+ ADD URI**
   - Add exactly: `http://localhost:5000/calendar/callback`
   - Click **Save**

4. Copy your credentials:
   - **Client ID**: Should match what's in your `.env` file
   - **Client secret**: Should match what's in your `.env` file

### Step 5: Verify Your .env File

Your `.env` file should have (already configured ✅):
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:5000/calendar/callback
```

### Step 6: Restart Flask

```bash
# Stop Flask (Ctrl+C in the terminal running it)
# Then restart:
python src/run.py
```

---

## Testing the Integration

### Test as Student:

1. **Login** as: `asmith@university.edu` / `student123`

2. **Go to Profile** (Dashboard → Profile)

3. **Scroll down** to "Google Calendar Integration" section

4. **Click "Connect Google Calendar"** button

5. **What should happen:**
   - Redirected to Google login/authorization page
   - Choose your Google account
   - See permissions request: "Campus Resource Hub wants to access your Google Calendar"
   - Click **Continue** or **Allow**
   - Redirected back to your profile
   - See green "Calendar Connected" message ✅

6. **Make a test booking:**
   - Browse resources
   - Book a resource
   - Once approved, check your Google Calendar
   - You should see the booking with 🎓 emoji!

---

## Troubleshooting

### Error: "redirect_uri_mismatch"
**Problem**: Redirect URI in Google Cloud Console doesn't match exactly

**Fix**:
1. Go to Google Cloud Console → Credentials
2. Edit your OAuth client
3. Make sure redirect URI is EXACTLY: `http://localhost:5000/calendar/callback`
4. No trailing slash, no extra characters
5. Save changes

### Error: "Access blocked: This app's request is invalid"
**Problem**: OAuth consent screen not configured properly

**Fix**:
1. Complete Step 3 above (OAuth consent screen)
2. Make sure you added scopes
3. Save all changes

### Error: "Access blocked: Campus Resource Hub has not completed the Google verification process"
**Problem**: User not added as test user

**Fix**:
1. Go to OAuth consent screen → Test users
2. Add the email address you're trying to login with
3. Save changes
4. Try again

### Warning: "Google Calendar integration is not configured"
**Problem**: This shouldn't appear anymore with your current config!

**Fix**:
1. Hard refresh browser: Ctrl+Shift+R
2. Or clear the flash message (click X)
3. This is a leftover message from before

---

## What Students Get

Once connected, students will:

✅ **Auto-sync approved bookings** to their Google Calendar  
✅ **Get email reminders** 24 hours before booking  
✅ **Get popup reminders** 1 hour before booking  
✅ **See booking details** in calendar event description  
✅ **Updates sync automatically** if booking is modified  
✅ **Events removed automatically** if booking is cancelled  

### Calendar Event Details:
- **Title**: 🎓 [Resource Name]
- **Location**: Building, room number
- **Description**: Booking details, ID, notes
- **Color**: Green (for easy identification)
- **Reminders**: 1 day before (email) + 1 hour before (popup)

---

## For Production Deployment

When you deploy to a production server:

1. **Update redirect URI** in `.env`:
   ```bash
   GOOGLE_REDIRECT_URI=https://your-domain.com/calendar/callback
   ```

2. **Add production URI** to Google Cloud Console:
   - Go to Credentials → Edit OAuth client
   - Add: `https://your-domain.com/calendar/callback`
   - Keep localhost URI for development
   - Save

3. **Publish OAuth consent screen** (for unlimited users):
   - Go to OAuth consent screen
   - Click "Publish App"
   - May require verification by Google (takes a few days)

4. **Or keep as "Testing"** and manually add each user as test user
   - Limited to 100 test users
   - Good for campus deployment with known users

---

## Security Notes

✅ **User Control**: Each user connects their own Google account  
✅ **Limited Scope**: Only calendar events access (not full Google account)  
✅ **Secure Storage**: Tokens encrypted in database  
✅ **Revokable**: Users can disconnect anytime  
✅ **Privacy**: Only syncs that user's bookings, nothing else  

Users can also revoke access from: https://myaccount.google.com/permissions

---

## Quick Checklist

Before students can use it:

- [ ] Google Calendar API enabled
- [ ] OAuth consent screen configured
- [ ] Scopes added (calendar.events)
- [ ] Test users added (or app published)
- [ ] OAuth credentials created
- [ ] Redirect URI added: `http://localhost:5000/calendar/callback`
- [ ] Client ID and Secret in `.env` (✅ Already done!)
- [ ] Flask restarted

---

## Need Help?

If you encounter issues:
1. Check the console/terminal where Flask is running for error messages
2. Check browser console (F12) for JavaScript errors
3. Verify all redirect URIs match exactly
4. Make sure user is added as test user in Google Cloud Console

**Ready to test? Follow the steps above and try connecting as a student!** 🚀

