# Email Notification System Setup

## Overview

The Campus Resource Hub includes a comprehensive email notification system that sends automated emails for:

✅ **Booking Confirmations** - When a user creates a booking  
✅ **Booking Approvals** - When a booking is approved by staff/admin  
✅ **Booking Rejections** - When a booking request is denied  
✅ **Booking Cancellations** - When a user cancels their booking  
✅ **Waitlist Notifications** - When a spot opens up (coming soon)  
✅ **Review Reminders** - After completed bookings

---

## Email Configuration

### Option 1: Gmail SMTP (Recommended for Development)

1. **Create an App Password** (if using Gmail):
   - Go to [Google Account Settings](https://myaccount.google.com/)
   - Navigate to **Security** → **2-Step Verification** → **App passwords**
   - Generate an app password for "Mail"

2. **Add to `.env` file**:

```env
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password-here
MAIL_DEFAULT_SENDER=noreply@campushub.edu
MAIL_SUPPRESS_SEND=False  # Set to True to disable emails in development
```

### Option 2: SendGrid (Recommended for Production)

```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_DEFAULT_SENDER=noreply@campushub.edu
MAIL_SUPPRESS_SEND=False
```

### Option 3: AWS SES

```env
MAIL_SERVER=email-smtp.us-east-1.amazonaws.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-aws-access-key
MAIL_PASSWORD=your-aws-secret-key
MAIL_DEFAULT_SENDER=noreply@campushub.edu
MAIL_SUPPRESS_SEND=False
```

---

## Development Mode

During development, you can **disable email sending** to avoid spam:

```env
MAIL_SUPPRESS_SEND=True
```

When `MAIL_SUPPRESS_SEND=True`, emails won't actually be sent, but you'll see confirmation messages in the logs.

---

## Email Templates

All emails follow the **Indiana University brand theme** (Crimson & Cream) and include:

- Professional HTML layouts
- Responsive design for mobile devices
- Clear call-to-action buttons
- Booking details summaries
- Direct links to relevant pages

### Example Email: Booking Confirmation

```html
Subject: Booking Confirmation - Study Room 14

📧 Beautiful HTML email with:
- IU Crimson gradient header
- Booking details (date, time, location)
- Status badge
- "View Dashboard" button
- Responsive design
```

---

## Testing Emails

### Method 1: Use a Test Email Service

**[Mailtrap.io](https://mailtrap.io/)** - Free testing inbox

```env
MAIL_SERVER=smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=your-mailtrap-username
MAIL_PASSWORD=your-mailtrap-password
MAIL_DEFAULT_SENDER=test@campushub.edu
MAIL_SUPPRESS_SEND=False
```

### Method 2: Use Your Own Email

Set your email as the recipient and test:

1. Create a booking
2. Approve/reject a booking
3. Cancel a booking
4. Check your inbox!

---

## Email Service Methods

Located in `src/services/email_service.py`:

### `EmailService.send_booking_confirmation(user_email, user_name, resource_title, booking_details)`
Sent when a user creates a new booking.

### `EmailService.send_booking_approval(user_email, user_name, resource_title, booking_details)`
Sent when a staff member approves a pending booking.

### `EmailService.send_booking_rejection(user_email, user_name, resource_title, booking_details, reason=None)`
Sent when a booking request is denied.

### `EmailService.send_booking_cancellation(user_email, user_name, resource_title, booking_details)`
Sent when a user cancels their booking.

### `EmailService.send_waitlist_notification(user_email, user_name, resource_title, booking_details)`
Sent when a waitlist spot opens up.

### `EmailService.send_review_reminder(user_email, user_name, resource_title, booking_details)`
Sent after a booking is completed to request a review.

---

## Troubleshooting

### Emails Not Sending?

**1. Check `.env` file exists and is loaded:**
```python
import os
print(os.environ.get('MAIL_USERNAME'))  # Should print your email
```

**2. Check MAIL_SUPPRESS_SEND:**
```env
MAIL_SUPPRESS_SEND=False  # Must be False to send emails
```

**3. Check Gmail App Password:**
- Don't use your regular Gmail password
- Use an App Password from Google Account Security settings

**4. Check firewall/network:**
```bash
# Test SMTP connection
telnet smtp.gmail.com 587
```

**5. Check Flask-Mail is installed:**
```bash
pip install Flask-Mail
```

### Gmail "Less Secure Apps" Error

If you get "Username and Password not accepted":
- Enable 2-Step Verification
- Generate an App Password
- Use the App Password in `.env`, not your regular password

### Emails Going to Spam?

To improve deliverability:
1. Use a verified domain email
2. Set up SPF/DKIM records
3. Use a professional email service (SendGrid, AWS SES)
4. Add unsubscribe links
5. Maintain a good sender reputation

---

## Production Considerations

### For Production Deployment:

1. **Use a professional email service** (SendGrid, AWS SES, Mailgun)
2. **Set up a custom domain** (noreply@your-university.edu)
3. **Configure SPF/DKIM/DMARC** records
4. **Monitor bounce rates** and delivery metrics
5. **Implement rate limiting** to prevent abuse
6. **Add email preferences** (let users opt-out)
7. **Log email events** for debugging

### Recommended: SendGrid Free Tier

- 100 emails/day free
- Easy setup
- Great deliverability
- Detailed analytics

Sign up at [sendgrid.com](https://sendgrid.com/)

---

## Future Enhancements

- [ ] Email templates with personalization
- [ ] Batch email sending for notifications
- [ ] Email preference center
- [ ] Email analytics and tracking
- [ ] Multi-language email support
- [ ] SMS notifications (Twilio integration)
- [ ] In-app notifications

---

## Support

For issues or questions:
- Check the Flask-Mail documentation: https://pythonhosted.org/Flask-Mail/
- Review logs in the terminal for error messages
- Test with Mailtrap.io first before using real email

---

**✅ Email notifications are now fully integrated into the Campus Resource Hub!**
