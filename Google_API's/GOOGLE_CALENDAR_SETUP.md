# Google Calendar Integration Setup Guide

This guide will help you set up Google Calendar integration for your Campus Resource Hub application.

## Overview

The Google Calendar integration allows users to:
- Connect their Google Calendar account to the application
- Automatically sync approved bookings to their Google Calendar
- Receive reminders for upcoming reservations
- View all their commitments in one place

## Prerequisites

- Google Account with access to Google Cloud Console
- Campus Resource Hub application running
- Administrator access to configure environment variables

---

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Create Project** or select an existing project
3. Enter a project name (e.g., "Campus Resource Hub")
4. Click **Create**

---

## Step 2: Enable Google Calendar API

1. In the Google Cloud Console, ensure your project is selected
2. Navigate to **APIs & Services** → **Library**
3. Search for "Google Calendar API"
4. Click on **Google Calendar API**
5. Click **Enable**

---

## Step 3: Configure OAuth Consent Screen

1. Navigate to **APIs & Services** → **OAuth consent screen**
2. Choose **External** user type (or **Internal** if using Google Workspace)
3. Click **Create**

### Fill in App Information:
- **App name**: Campus Resource Hub
- **User support email**: Your support email
- **Developer contact email**: Your development team email
- **App logo** (optional): Upload your app logo
- Click **Save and Continue**

### Add Scopes:
4. Click **Add or Remove Scopes**
5. Search for "Google Calendar API"
6. Select the following scope:
   - `.../auth/calendar.events` (Create, read, update, and delete events)
7. Click **Update** → **Save and Continue**

### Test Users (for development):
8. Add test users' email addresses who will test the integration
9. Click **Save and Continue**

---

## Step 4: Create OAuth 2.0 Credentials

1. Navigate to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Select application type: **Web application**
4. Enter a name: "Campus Resource Hub Web Client"

### Configure Authorized Redirect URIs:
5. Add the following redirect URIs:
   - **Development**: `http://localhost:5000/calendar/callback`
   - **Production**: `https://yourdomain.com/calendar/callback`
   
   Replace `yourdomain.com` with your actual domain.

6. Click **Create**
7. **IMPORTANT**: Copy your **Client ID** and **Client Secret** - you'll need these!

---

## Step 5: Configure Environment Variables

1. Open or create the `.env` file in your project root:

```bash
# Google Calendar API Configuration
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:5000/calendar/callback
```

2. Replace the values:
   - `GOOGLE_CLIENT_ID`: Paste your Client ID from Step 4
   - `GOOGLE_CLIENT_SECRET`: Paste your Client Secret from Step 4
   - `GOOGLE_REDIRECT_URI`: Update with your production URL when deploying

**Security Note**: Never commit your `.env` file to version control! It should be in your `.gitignore`.

---

## Step 6: Install Dependencies

If you haven't already, install the required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- `google-auth`
- `google-auth-oauthlib`
- `google-auth-httplib2`
- `google-api-python-client`

---

## Step 7: Reset Database (if needed)

Since we added new fields to the database schema, you need to recreate the database:

**⚠️ WARNING: This will delete all existing data!**

```bash
# Delete the existing database
rm src/campus_hub.db

# Run the application - it will create a new database with the updated schema
python run.py
```

For production, you should use proper database migrations instead.

---

## Step 8: Test the Integration

1. Start your application:
```bash
python run.py
```

2. Log in to the application with a test account
3. Go to **Dashboard** → **Profile**
4. Scroll down to **Google Calendar Integration**
5. Click **Connect Google Calendar**
6. You'll be redirected to Google's OAuth consent screen
7. Select your Google account
8. Review the permissions (Calendar Events access)
9. Click **Allow**
10. You should be redirected back to your profile with a success message

---

## Step 9: Verify Calendar Sync

1. Create a booking request for a resource
2. Have the resource owner approve the booking
3. Check your Google Calendar - you should see the booking event!

The event will include:
- 🎓 Resource name in the title
- Location details
- Full booking description
- Reminders (1 day before and 1 hour before)

---

## Production Deployment

### Update Redirect URI

1. Update your `.env` file with production URL:
```bash
GOOGLE_REDIRECT_URI=https://yourdomain.com/calendar/callback
```

2. In Google Cloud Console → **Credentials**, edit your OAuth client:
   - Add your production redirect URI
   - Keep the development URI for testing

### Publish OAuth Consent Screen

For production use with any Google user:

1. Go to **OAuth consent screen**
2. Click **Publish App**
3. Submit for Google verification (required for public apps)
4. Wait for approval (can take several days)

Until verification:
- Only test users can connect their calendars
- Users will see an "unverified app" warning

---

## Troubleshooting

### "Error 400: redirect_uri_mismatch"
- Check that your redirect URI in `.env` exactly matches the one in Google Cloud Console
- Ensure there are no trailing slashes or typos
- URI must be registered in Google Cloud Console before use

### "Access blocked: This app's request is invalid"
- OAuth consent screen not configured
- Required scopes not added
- App not published or user not added as test user

### "Invalid grant: account not found"
- User hasn't granted calendar permissions
- Token expired - user needs to reconnect

### Calendar Events Not Creating
- Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
- Verify user has connected their calendar (check profile page)
- Check application logs for error messages
- Ensure booking is approved (events only created on approval)

### "The user did not consent to the scopes required"
- User clicked "Deny" during OAuth flow
- Ask user to try connecting again and click "Allow"

---

## Security Best Practices

1. **Keep credentials secret**: Never commit `.env` or expose credentials
2. **Use HTTPS in production**: Required for OAuth callbacks
3. **Rotate secrets regularly**: Update Client Secret periodically
4. **Monitor API usage**: Check Google Cloud Console for usage quotas
5. **Handle token refresh**: Tokens auto-refresh - don't store expired tokens
6. **Limit scopes**: Only request calendar.events (minimum required)

---

## API Quotas

Google Calendar API free tier limits:
- **Queries per day**: 1,000,000
- **Queries per user per second**: 5

For most campus applications, these limits are sufficient. Monitor usage in Google Cloud Console.

---

## Support

### Google Calendar API Documentation
- [Google Calendar API Reference](https://developers.google.com/calendar/api/v3/reference)
- [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)

### Application Support
For issues with the Campus Resource Hub application:
- Check application logs
- Review the code in `src/services/google_calendar_service.py`
- Check database schema in `src/models/database.py`

---

## Testing Checklist

- [ ] Google Cloud Project created
- [ ] Calendar API enabled
- [ ] OAuth consent screen configured
- [ ] OAuth credentials created
- [ ] Environment variables set
- [ ] Dependencies installed
- [ ] Database recreated with new schema
- [ ] User can connect Google Calendar
- [ ] Booking creates calendar event when approved
- [ ] Event appears in Google Calendar
- [ ] User can disconnect calendar
- [ ] Reminders work correctly

---

## Feature Details

### What Gets Synced
- ✅ Approved bookings automatically create calendar events
- ✅ Resource name, location, and details included
- ✅ Automatic reminders (1 day and 1 hour before)
- ✅ Color-coded events (green for resource bookings)

### What Doesn't Get Synced
- ❌ Pending bookings (only approved bookings)
- ❌ Rejected or cancelled bookings
- ❌ Draft resources
- ❌ Messages or other activities

### Privacy
- Users' calendar tokens are stored securely in the database
- Each user controls their own calendar connection
- Application can only create/update/delete events it created
- No access to users' other calendar events
- Users can disconnect at any time

---

## Next Steps

Once Google Calendar integration is working:

1. **Customize event details**: Edit `src/services/google_calendar_service.py`
2. **Add event updates**: Sync changes when bookings are modified
3. **Handle cancellations**: Delete calendar events when bookings are cancelled
4. **Bulk sync**: Add option to sync existing approved bookings

---

*Last updated: November 2025*
*Campus Resource Hub - AiDD Final Project*

