"""
Email Notification Service
Handles all email communications for the Campus Resource Hub
"""

import os
from flask import render_template_string
from flask_mail import Mail, Message
from datetime import datetime

mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with app configuration"""
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@campusresourcehub.com')
    
    mail.init_app(app)
    return mail


class EmailService:
    """Service for sending various email notifications"""
    
    @staticmethod
    def send_booking_confirmation(user_email, user_name, resource_title, booking_details):
        """Send booking confirmation email"""
        try:
            msg = Message(
                subject=f"Booking Confirmation - {resource_title}",
                recipients=[user_email]
            )
            
            msg.html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #990000 0%, #7C0000 100%); 
                                padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                        <h1 style="color: #EFEAE4; margin: 0; font-size: 28px;">
                            🎉 Booking Confirmed!
                        </h1>
                    </div>
                    
                    <div style="background: #fff; padding: 30px; border: 2px solid #EFEAE4; 
                                border-top: none; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px;">Hi <strong>{user_name}</strong>,</p>
                        
                        <p>Great news! Your booking has been confirmed.</p>
                        
                        <div style="background: #F7F2ED; padding: 20px; border-radius: 8px; 
                                    border-left: 4px solid #990000; margin: 20px 0;">
                            <h3 style="color: #990000; margin-top: 0;">📋 Booking Details</h3>
                            <p style="margin: 5px 0;"><strong>Resource:</strong> {resource_title}</p>
                            <p style="margin: 5px 0;"><strong>Start:</strong> {booking_details['start_time']}</p>
                            <p style="margin: 5px 0;"><strong>End:</strong> {booking_details['end_time']}</p>
                            <p style="margin: 5px 0;"><strong>Status:</strong> 
                                <span style="background: #2D6A4F; color: white; padding: 2px 8px; 
                                      border-radius: 12px; font-size: 12px;">
                                    {booking_details['status'].upper()}
                                </span>
                            </p>
                        </div>
                        
                        <p>You can view and manage your bookings in your dashboard.</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{booking_details.get('dashboard_url', '#')}" 
                               style="background: #990000; color: #EFEAE4; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 25px; font-weight: bold;
                                      display: inline-block;">
                                View Dashboard
                            </a>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #EFEAE4; margin: 20px 0;">
                        
                        <p style="font-size: 12px; color: #666;">
                            If you need to cancel or modify this booking, please visit your dashboard.
                        </p>
                    </div>
                    
                    <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                        <p>Campus Resource Hub | Indiana University</p>
                        <p>This is an automated message, please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending booking confirmation email: {e}")
            return False
    
    @staticmethod
    def send_booking_approval(user_email, user_name, resource_title, booking_details):
        """Send booking approval notification"""
        try:
            msg = Message(
                subject=f"Booking Approved - {resource_title}",
                recipients=[user_email]
            )
            
            msg.html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #2D6A4F 0%, #52B788 100%); 
                                padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">
                            ✅ Booking Approved!
                        </h1>
                    </div>
                    
                    <div style="background: #fff; padding: 30px; border: 2px solid #EFEAE4; 
                                border-top: none; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px;">Hi <strong>{user_name}</strong>,</p>
                        
                        <p>Excellent news! Your booking request has been approved.</p>
                        
                        <div style="background: #d4edda; padding: 20px; border-radius: 8px; 
                                    border-left: 4px solid #2D6A4F; margin: 20px 0;">
                            <h3 style="color: #2D6A4F; margin-top: 0;">📋 Booking Details</h3>
                            <p style="margin: 5px 0;"><strong>Resource:</strong> {resource_title}</p>
                            <p style="margin: 5px 0;"><strong>Start:</strong> {booking_details['start_time']}</p>
                            <p style="margin: 5px 0;"><strong>End:</strong> {booking_details['end_time']}</p>
                            {f"<p style='margin: 5px 0;'><strong>Location:</strong> {booking_details.get('location', 'TBD')}</p>" if booking_details.get('location') else ""}
                        </div>
                        
                        <p>Your booking is now confirmed! Please arrive on time and follow any guidelines for the resource.</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{booking_details.get('dashboard_url', '#')}" 
                               style="background: #2D6A4F; color: white; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 25px; font-weight: bold;
                                      display: inline-block;">
                                View My Bookings
                            </a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                        <p>Campus Resource Hub | Indiana University</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending approval email: {e}")
            return False
    
    @staticmethod
    def send_booking_rejection(user_email, user_name, resource_title, booking_details, reason=None):
        """Send booking rejection notification"""
        try:
            msg = Message(
                subject=f"Booking Update - {resource_title}",
                recipients=[user_email]
            )
            
            reason_text = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
            
            msg.html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #990000 0%, #E63946 100%); 
                                padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">
                            ℹ️ Booking Update
                        </h1>
                    </div>
                    
                    <div style="background: #fff; padding: 30px; border: 2px solid #EFEAE4; 
                                border-top: none; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px;">Hi <strong>{user_name}</strong>,</p>
                        
                        <p>We regret to inform you that your booking request was not approved at this time.</p>
                        
                        <div style="background: #f8d7da; padding: 20px; border-radius: 8px; 
                                    border-left: 4px solid #990000; margin: 20px 0;">
                            <h3 style="color: #990000; margin-top: 0;">📋 Booking Details</h3>
                            <p style="margin: 5px 0;"><strong>Resource:</strong> {resource_title}</p>
                            <p style="margin: 5px 0;"><strong>Requested Time:</strong> {booking_details['start_time']}</p>
                            {reason_text}
                        </div>
                        
                        <p>Please feel free to:</p>
                        <ul>
                            <li>Try booking a different time slot</li>
                            <li>Contact the resource owner for more information</li>
                            <li>Browse alternative resources</li>
                        </ul>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{booking_details.get('resource_url', '#')}" 
                               style="background: #990000; color: white; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 25px; font-weight: bold;
                                      display: inline-block;">
                                View Resource
                            </a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                        <p>Campus Resource Hub | Indiana University</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending rejection email: {e}")
            return False
    
    @staticmethod
    def send_booking_cancellation(user_email, user_name, resource_title, booking_details):
        """Send booking cancellation notification"""
        try:
            msg = Message(
                subject=f"Booking Cancelled - {resource_title}",
                recipients=[user_email]
            )
            
            msg.html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #666666 0%, #333333 100%); 
                                padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">
                            🚫 Booking Cancelled
                        </h1>
                    </div>
                    
                    <div style="background: #fff; padding: 30px; border: 2px solid #EFEAE4; 
                                border-top: none; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px;">Hi <strong>{user_name}</strong>,</p>
                        
                        <p>This is to confirm that the following booking has been cancelled:</p>
                        
                        <div style="background: #F7F2ED; padding: 20px; border-radius: 8px; 
                                    border-left: 4px solid #666; margin: 20px 0;">
                            <h3 style="color: #666; margin-top: 0;">📋 Cancelled Booking</h3>
                            <p style="margin: 5px 0;"><strong>Resource:</strong> {resource_title}</p>
                            <p style="margin: 5px 0;"><strong>Was Scheduled For:</strong> {booking_details['start_time']}</p>
                        </div>
                        
                        <p>If you didn't cancel this booking, please contact support immediately.</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{booking_details.get('browse_url', '#')}" 
                               style="background: #990000; color: white; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 25px; font-weight: bold;
                                      display: inline-block;">
                                Browse Resources
                            </a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                        <p>Campus Resource Hub | Indiana University</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending cancellation email: {e}")
            return False
    
    @staticmethod
    def send_waitlist_notification(user_email, user_name, resource_title, booking_details):
        """Send waitlist spot available notification"""
        try:
            msg = Message(
                subject=f"🎉 Spot Available - {resource_title}",
                recipients=[user_email]
            )
            
            msg.html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #C17817 0%, #F4A261 100%); 
                                padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">
                            🎉 A Spot Opened Up!
                        </h1>
                    </div>
                    
                    <div style="background: #fff; padding: 30px; border: 2px solid #EFEAE4; 
                                border-top: none; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px;">Hi <strong>{user_name}</strong>,</p>
                        
                        <p>Great news! A booking spot is now available for <strong>{resource_title}</strong>.</p>
                        
                        <div style="background: #fff3cd; padding: 20px; border-radius: 8px; 
                                    border-left: 4px solid #C17817; margin: 20px 0;">
                            <h3 style="color: #C17817; margin-top: 0;">⚡ Available Slot</h3>
                            <p style="margin: 5px 0;"><strong>Resource:</strong> {resource_title}</p>
                            <p style="margin: 5px 0;"><strong>Time:</strong> {booking_details['start_time']}</p>
                            <p style="color: #856404; font-weight: bold; margin-top: 15px;">
                                ⏰ Act fast! This spot is first-come, first-served.
                            </p>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{booking_details.get('booking_url', '#')}" 
                               style="background: #C17817; color: white; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 25px; font-weight: bold;
                                      display: inline-block;">
                                Book Now
                            </a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                        <p>Campus Resource Hub | Indiana University</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending waitlist notification: {e}")
            return False
    
    @staticmethod
    def send_review_reminder(user_email, user_name, resource_title, booking_details):
        """Send review reminder after completed booking"""
        try:
            msg = Message(
                subject=f"Rate Your Experience - {resource_title}",
                recipients=[user_email]
            )
            
            msg.html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #990000 0%, #7C0000 100%); 
                                padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                        <h1 style="color: #EFEAE4; margin: 0; font-size: 28px;">
                            ⭐ How Was Your Experience?
                        </h1>
                    </div>
                    
                    <div style="background: #fff; padding: 30px; border: 2px solid #EFEAE4; 
                                border-top: none; border-radius: 0 0 10px 10px;">
                        <p style="font-size: 16px;">Hi <strong>{user_name}</strong>,</p>
                        
                        <p>We hope you had a great experience with <strong>{resource_title}</strong>!</p>
                        
                        <p>Your feedback helps other students and improves our platform. Would you take a moment to rate your experience?</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{booking_details.get('review_url', '#')}" 
                               style="background: #990000; color: white; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 25px; font-weight: bold;
                                      display: inline-block;">
                                Leave a Review
                            </a>
                        </div>
                        
                        <p style="text-align: center; color: #666; font-size: 14px;">
                            ⭐⭐⭐⭐⭐<br>
                            It only takes a minute!
                        </p>
                    </div>
                    
                    <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
                        <p>Campus Resource Hub | Indiana University</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending review reminder: {e}")
            return False
