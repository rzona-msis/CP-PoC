# Google Calendar Integration - Quick Reference

## ✅ Implementation Complete!

Your Campus Resource Hub now supports Google Calendar integration! Users can connect their Google Calendar to automatically sync approved bookings.

---

## 📋 What Was Added

### 1. Database Changes
- Added Google Calendar token fields to `users` table
- Added `calendar_event_id` field to `bookings` table

### 2. Backend Services
- **`src/services/google_calendar_service.py`** - Core calendar API integration
- **`src/controllers/google_calendar.py`** - OAuth2 authentication flow
- **Updated `src/data_access/user_dal.py`** - Calendar token management
- **Updated `src/data_access/booking_dal.py`** - Calendar event ID storage
- **Updated `src/controllers/bookings.py`** - Auto-create events on approval

### 3. Frontend UI
- **Updated `src/views/dashboard/profile.html`** - Calendar connection UI
- Connect/disconnect buttons
- Visual status indicators

### 4. Dependencies
Added to `requirements.txt`:
- `google-auth==2.25.2`
- `google-auth-oauthlib==1.2.0`
- `google-auth-httplib2==0.2.0`
- `google-api-python-client==2.111.0`

### 5. Blueprint Registration
- Registered `google_calendar_bp` in `src/app.py`
- Routes: `/calendar/connect`, `/calendar/callback`, `/calendar/disconnect`

---

## 🚀 How to Use

### For Administrators

1. **Set up Google Cloud Project**
   - Follow detailed steps in `GOOGLE_CALENDAR_SETUP.md`
   - Create OAuth credentials
   - Enable Calendar API

2. **Configure Environment Variables**
   ```bash
   # Add to .env file
   GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_client_secret
   GOOGLE_REDIRECT_URI=http://localhost:5000/calendar/callback
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Reset Database** (⚠️ Deletes existing data!)
   ```bash
   rm src/campus_hub.db
   python run.py
   ```

### For End Users

1. **Connect Calendar**
   - Go to Dashboard → Profile
   - Find "Google Calendar Integration" card
   - Click "Connect Google Calendar"
   - Authorize the application

2. **Automatic Sync**
   - Create booking requests as usual
   - When booking is approved, it's automatically added to your Google Calendar
   - Includes reminders (1 day and 1 hour before)

3. **Disconnect**
   - Go to Dashboard → Profile
   - Click "Disconnect Calendar"
   - Existing calendar events remain (not deleted)

---

## 🎨 Features

### What Gets Synced
- ✅ **Approved bookings only** - Events created when booking approved
- ✅ **Full details** - Resource name, location, category, capacity
- ✅ **Automatic reminders** - Email (1 day) and popup (1 hour)
- ✅ **Color-coded** - Green events for resource bookings
- ✅ **IU timezone** - America/Indiana/Indianapolis

### Event Details Format
```
🎓 Conference Room A

Campus Resource Booking
━━━━━━━━━━━━━━━━━━━━━
Resource: Conference Room A
Category: Meeting Room
Location: Business Building, Floor 3
Capacity: 12 people

Booking ID: #123
Status: Approved

━━━━━━━━━━━━━━━━━━━━━
Managed by Campus Resource Hub
```

---

## 🔐 Security & Privacy

### User Data Protection
- Calendar tokens stored securely in database
- Tokens encrypted with Flask secret key
- Each user manages their own connection
- No access to users' other calendar events

### OAuth Flow
- Standard OAuth 2.0 with PKCE
- State parameter for CSRF protection
- Automatic token refresh
- Scope limited to `calendar.events` only

### Best Practices
- Never commit `.env` file
- Use HTTPS in production
- Rotate client secret regularly
- Monitor API usage quotas

---

## 🔧 Technical Architecture

### OAuth 2.0 Flow
```
User clicks "Connect Calendar"
    ↓
App generates state token & redirects to Google
    ↓
User authorizes (Google OAuth consent screen)
    ↓
Google redirects to /calendar/callback with code
    ↓
App exchanges code for access & refresh tokens
    ↓
Tokens stored in database (user record)
    ↓
Calendar connected! ✅
```

### Booking Approval Flow
```
Resource owner approves booking
    ↓
Booking status updated to "approved"
    ↓
Check if requester has calendar connected
    ↓
If yes: Get user's credentials from database
    ↓
Create calendar event via Google Calendar API
    ↓
Store event ID in booking record
    ↓
User sees event in their Google Calendar! 🎉
```

---

## 🐛 Troubleshooting

### Common Issues

**Calendar not connecting:**
- Check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
- Verify redirect URI matches Google Cloud Console
- Ensure OAuth consent screen is configured

**Events not appearing:**
- Verify booking is approved (only approved bookings sync)
- Check user has connected calendar (profile page)
- Review application logs for errors

**"redirect_uri_mismatch" error:**
- Redirect URI in `.env` must match Google Cloud Console exactly
- No trailing slashes
- Check protocol (http vs https)

**"Access blocked" error:**
- Add user as test user in OAuth consent screen
- Or publish the app (requires Google verification)

---

## 📊 Files Modified/Created

### New Files
- `src/services/google_calendar_service.py` - Calendar service
- `src/controllers/google_calendar.py` - OAuth controller
- `GOOGLE_CALENDAR_SETUP.md` - Setup documentation
- `GOOGLE_CALENDAR_INTEGRATION.md` - This file

### Modified Files
- `src/models/database.py` - Added calendar fields
- `src/data_access/user_dal.py` - Token management
- `src/data_access/booking_dal.py` - Event ID storage
- `src/controllers/bookings.py` - Auto-create events
- `src/controllers/dashboard.py` - Calendar status
- `src/views/dashboard/profile.html` - Connection UI
- `src/app.py` - Blueprint registration
- `requirements.txt` - Google API dependencies

---

## 📈 Next Steps & Enhancements

### Future Improvements
1. **Event Updates** - Sync changes when bookings are modified
2. **Event Deletion** - Remove events when bookings cancelled
3. **Bulk Sync** - Sync existing approved bookings
4. **Calendar Selection** - Let users choose which calendar
5. **Event Customization** - User preferences for event details
6. **Recurring Bookings** - Support repeating events

### Additional Features
- Email notifications when calendar event created
- Calendar preview before connecting
- Multiple calendar support
- iCal/ICS export option
- Calendar sharing for team bookings

---

## 🎓 Indiana University Theme

The Google Calendar integration follows the IU theme:
- **Event Color**: Green (IU academic events)
- **Emoji**: 🎓 (graduation cap) in event titles
- **Timezone**: America/Indiana/Indianapolis
- **Professional formatting** in event descriptions

---

## 📚 Documentation

- **Setup Guide**: `GOOGLE_CALENDAR_SETUP.md` - Complete setup instructions
- **This File**: Quick reference and architecture overview
- **API Reference**: `src/services/google_calendar_service.py` - Code documentation
- **Google Docs**: [Google Calendar API](https://developers.google.com/calendar)

---

## ✨ Testing

### Test Scenario
1. **Setup**: Configure Google Calendar API credentials
2. **Connect**: User connects their Google Calendar
3. **Book**: User creates a booking request
4. **Approve**: Resource owner approves the booking
5. **Verify**: Check Google Calendar for event
6. **Reminders**: Verify reminders work
7. **Disconnect**: User disconnects calendar

### Success Criteria
- ✅ Calendar connection works without errors
- ✅ Approved bookings appear in Google Calendar
- ✅ Event details are correct and complete
- ✅ Reminders are set properly
- ✅ Disconnect removes tokens (events remain)
- ✅ UI shows correct connection status

---

## 🎉 Congratulations!

Your Campus Resource Hub now has professional Google Calendar integration! Users will love the convenience of automatic calendar syncing for their bookings.

---

*Implemented: November 2025*
*Campus Resource Hub - AI-First Development*

