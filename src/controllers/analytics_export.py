"""
FREE Analytics Export (CSV/JSON) - No BigQuery Required

Export analytics data to CSV or JSON files for use with:
- Google Sheets (free)
- Excel (free)
- Looker Studio with Sheets connector (free)
"""

from flask import Blueprint, jsonify, send_file, request
from flask_login import login_required, current_user
from functools import wraps
import csv
import json
import io
from datetime import datetime
from src.services.google_cloud_analytics import cloud_analytics

export_bp = Blueprint('export', __name__)


def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


@export_bp.route('/csv/all', methods=['GET'])
@login_required
@admin_required
def export_all_csv():
    """
    Export all analytics data as CSV files in a ZIP.
    100% FREE - No cloud services needed!
    """
    metrics = cloud_analytics.get_dashboard_metrics()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write summary
    writer.writerow(['Campus Resource Hub Analytics Export'])
    writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    # Key metrics
    writer.writerow(['Key Metrics'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Users', metrics['total_users']])
    writer.writerow(['Total Resources', metrics['total_resources']])
    writer.writerow(['Total Bookings', metrics['total_bookings']])
    writer.writerow([])
    
    # Bookings by status
    writer.writerow(['Bookings by Status'])
    writer.writerow(['Status', 'Count'])
    for status, count in metrics['bookings_by_status'].items():
        writer.writerow([status, count])
    writer.writerow([])
    
    # Resources by category
    writer.writerow(['Resources by Category'])
    writer.writerow(['Category', 'Count'])
    for category, count in metrics['resources_by_category'].items():
        writer.writerow([category, count])
    writer.writerow([])
    
    # Top resources
    writer.writerow(['Top 10 Resources'])
    writer.writerow(['Rank', 'Resource', 'Bookings'])
    for idx, resource in enumerate(metrics['top_resources'], 1):
        writer.writerow([idx, resource['title'], resource['bookings']])
    writer.writerow([])
    
    # Booking trend
    writer.writerow(['Booking Trend (Last 30 Days)'])
    writer.writerow(['Date', 'Bookings'])
    for trend in metrics['bookings_trend']:
        writer.writerow([trend['date'], trend['count']])
    
    # Prepare file for download
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'campus_hub_analytics_{datetime.now().strftime("%Y%m%d")}.csv'
    )


@export_bp.route('/json/metrics', methods=['GET'])
@login_required
@admin_required
def export_json():
    """
    Export current metrics as JSON.
    100% FREE - Perfect for Google Sheets import!
    """
    metrics = cloud_analytics.get_dashboard_metrics()
    metrics['exported_at'] = datetime.now().isoformat()
    metrics['export_type'] = 'free_json_export'
    
    return jsonify(metrics), 200


@export_bp.route('/sheets-ready', methods=['GET'])
@login_required
@admin_required
def export_sheets_ready():
    """
    Export data in a format ready for Google Sheets import.
    Returns JSON that can be copied to Sheets or used with Apps Script.
    """
    metrics = cloud_analytics.get_dashboard_metrics()
    
    # Format for easy Sheets import
    sheets_data = {
        'summary': {
            'headers': ['Metric', 'Value'],
            'rows': [
                ['Total Users', metrics['total_users']],
                ['Total Resources', metrics['total_resources']],
                ['Total Bookings', metrics['total_bookings']],
                ['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            ]
        },
        'bookings_by_status': {
            'headers': ['Status', 'Count'],
            'rows': [[k, v] for k, v in metrics['bookings_by_status'].items()]
        },
        'resources_by_category': {
            'headers': ['Category', 'Count'],
            'rows': [[k, v] for k, v in metrics['resources_by_category'].items()]
        },
        'top_resources': {
            'headers': ['Rank', 'Resource', 'Bookings'],
            'rows': [[i+1, r['title'], r['bookings']] for i, r in enumerate(metrics['top_resources'])]
        },
        'booking_trend': {
            'headers': ['Date', 'Bookings'],
            'rows': [[t['date'], t['count']] for t in metrics['bookings_trend']]
        }
    }
    
    return jsonify(sheets_data), 200

