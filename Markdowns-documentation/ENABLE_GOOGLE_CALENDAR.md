# Enable Google Calendar Integration for Students

## Current Status
✅ **Fixed!** Students will now only see the Google Calendar option if it's properly configured on the server.

## What Was Changed

### 1. Smart Display Logic
- **If Calendar IS configured**: All users (students, staff, admin) see the calendar integration option
- **If Calendar NOT configured**: 
  - Students don't see anything (no confusing warnings!)
  - Staff/Admin see a warning with setup instructions

### 2. Files Modified
- `src/views/dashboard/profile.html` - Added conditional display
- `src/controllers/dashboard.py` - Pass `calendar_enabled` status to template

## How to Enable Google Calendar Integration

### Quick Setup (5 minutes)

1. **Get Google Calendar API Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable "Google Calendar API"
   - Create OAuth 2.0 credentials
   - Download client secret JSON

2. **Set Environment Variables**
   
   Add to your `.env` file:
   ```bash
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:5000/calendar/callback
   ```

3. **Configure OAuth Consent Screen**
   - Add test users (your student emails)
   - Or publish the app (requires verification for production)

4. **Restart Your Application**
   ```bash
   python src/run.py
   ```

5. **Test It**
   - Login as any user
   - Go to Profile
   - You should now see "Google Calendar Integration" section
   - Click "Connect Google Calendar"
   - Authorize the app
   - Your bookings will now sync automatically!

### For Production Deployment

If deploying to a production server:

1. **Update Redirect URI**
   ```bash
   GOOGLE_REDIRECT_URI=https://your-domain.com/calendar/callback
   ```

2. **Add to Google Cloud Console**
   - Go to your OAuth credentials
   - Add the production URI to "Authorized redirect URIs"

3. **Publish OAuth Consent Screen**
   - Required for users outside your test list
   - May require Google verification for sensitive scopes

## Benefits for Students

Once enabled, students can:
- ✅ **Auto-sync bookings** to their personal Google Calendar
- ✅ **Get reminders** 1 day and 1 hour before their bookings
- ✅ **See all commitments** in one place (classes + bookings)
- ✅ **Never miss a booking** with automatic notifications
- ✅ **Works on mobile** - Google Calendar syncs everywhere

## Testing

### As a Student:
1. Go to Dashboard → Profile
2. Click "Connect Google Calendar"
3. Authorize the app
4. Make a booking
5. Once approved, check your Google Calendar
6. You should see the booking with a 🎓 emoji!

### As Staff/Admin:
- Same process as students
- Plus you see resource bookings on your calendar
- Helps avoid double-booking resources

## Troubleshooting

### "Google Calendar integration is not configured"
**For Students**: You won't see this anymore! The section is hidden if not configured.
**For Admins**: Follow the setup steps above to enable the feature.

### "Redirect URI mismatch" error
Make sure your `GOOGLE_REDIRECT_URI` matches exactly what's in Google Cloud Console:
- Local: `http://localhost:5000/calendar/callback`
- Production: `https://your-domain.com/calendar/callback`

### Calendar events not appearing
- Check that the booking was **approved** (pending bookings don't sync)
- Refresh your Google Calendar
- Check the user connected the right Google account

## Advanced: What Gets Synced

**Automatically synced to Google Calendar:**
- ✅ Booking title with resource name
- ✅ Location (building, room)
- ✅ Start and end times
- ✅ Description with booking details
- ✅ Reminders (1 day + 1 hour before)
- ✅ Color coding (green for resource bookings)

**When events are created:**
- When booking status changes to "approved"
- Automatically during the approval process

**When events are deleted:**
- When booking is cancelled
- When booking is rejected
- When user disconnects calendar (events remain)

## Security & Privacy

- ✅ Users control their own calendar connection
- ✅ Only syncs bookings for that specific user
- ✅ Uses secure OAuth2 authentication
- ✅ Tokens stored encrypted in database
- ✅ Can disconnect anytime without affecting bookings
- ✅ No access to other calendar data

## Full Documentation

For detailed setup instructions, see:
- `Google_API's/GOOGLE_CALENDAR_SETUP.md` - Complete setup guide
- `Google_API's/GOOGLE_CALENDAR_INTEGRATION.md` - Integration details

---

**Ready to enable? Just add the environment variables and restart!** 🎉

