"""
Analytics API Controller

Provides endpoints for:
- Exporting data to Google BigQuery
- Real-time dashboard metrics
- Administrative analytics views
"""

from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from src.services.google_cloud_analytics import cloud_analytics
from src.data_access.analytics_dal import AnalyticsDAL
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__)


def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


@analytics_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """
    Main analytics dashboard view for administrators.
    
    Shows real-time metrics and export status.
    """
    metrics = cloud_analytics.get_dashboard_metrics()
    is_gcp_enabled = cloud_analytics.is_enabled()
    
    return render_template('analytics/dashboard.html',
                         metrics=metrics,
                         is_gcp_enabled=is_gcp_enabled)


@analytics_bp.route('/daily')
@login_required
@admin_required
def daily_analytics():
    """
    Daily booking analytics dashboard.
    
    Admin-only access. Shows comprehensive booking metrics, resource usage, and operational insights.
    """
    
    try:
        # Get all analytics data
        daily_metrics = AnalyticsDAL.get_daily_booking_metrics(days=30)
        timeline_data = AnalyticsDAL.get_booking_timeline(days=30)
        resource_stats = AnalyticsDAL.get_resource_usage_stats()
        peak_hours = AnalyticsDAL.get_peak_hours_data()
        day_distribution = AnalyticsDAL.get_day_of_week_distribution()
        user_activity = AnalyticsDAL.get_user_activity_stats()
        operational = AnalyticsDAL.get_operational_insights()
        lead_time = AnalyticsDAL.get_booking_lead_time_stats()
        
        return render_template('analytics/daily_dashboard.html',
                             daily_metrics=daily_metrics,
                             timeline_data=timeline_data,
                             resource_stats=resource_stats,
                             peak_hours=peak_hours,
                             day_distribution=day_distribution,
                             user_activity=user_activity,
                             operational=operational,
                             lead_time=lead_time,
                             now=datetime.now())
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))


@analytics_bp.route('/api/metrics', methods=['GET'])
@login_required
@admin_required
def get_metrics():
    """
    Get real-time dashboard metrics.
    
    Returns:
        JSON with various analytics metrics
    """
    metrics = cloud_analytics.get_dashboard_metrics()
    
    return jsonify({
        'success': True,
        'metrics': metrics,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@analytics_bp.route('/api/export', methods=['POST'])
@login_required
@admin_required
def export_to_bigquery():
    """
    Export all analytics data to Google BigQuery.
    
    Requires Google Cloud Platform to be configured.
    
    Returns:
        JSON with export results
    """
    if not cloud_analytics.is_enabled():
        return jsonify({
            'success': False,
            'error': 'Google Cloud Platform not configured',
            'message': 'Please set GCP_PROJECT_ID and GOOGLE_APPLICATION_CREDENTIALS'
        }), 400
    
    try:
        results = cloud_analytics.export_all_analytics()
        
        all_successful = all(results.values())
        
        return jsonify({
            'success': all_successful,
            'results': results,
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Data exported to BigQuery successfully' if all_successful else 'Some exports failed'
        }), 200 if all_successful else 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error exporting data to BigQuery'
        }), 500


@analytics_bp.route('/api/export/users', methods=['POST'])
@login_required
@admin_required
def export_users():
    """Export only users data to BigQuery."""
    if not cloud_analytics.is_enabled():
        return jsonify({'success': False, 'error': 'GCP not configured'}), 400
    
    try:
        success = cloud_analytics.export_users_data()
        return jsonify({
            'success': success,
            'message': 'Users data exported' if success else 'Export failed'
        }), 200 if success else 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/api/export/resources', methods=['POST'])
@login_required
@admin_required
def export_resources():
    """Export only resources data to BigQuery."""
    if not cloud_analytics.is_enabled():
        return jsonify({'success': False, 'error': 'GCP not configured'}), 400
    
    try:
        success = cloud_analytics.export_resources_data()
        return jsonify({
            'success': success,
            'message': 'Resources data exported' if success else 'Export failed'
        }), 200 if success else 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/api/export/bookings', methods=['POST'])
@login_required
@admin_required
def export_bookings():
    """Export only bookings data to BigQuery."""
    if not cloud_analytics.is_enabled():
        return jsonify({'success': False, 'error': 'GCP not configured'}), 400
    
    try:
        success = cloud_analytics.export_bookings_data()
        return jsonify({
            'success': success,
            'message': 'Bookings data exported' if success else 'Export failed'
        }), 200 if success else 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analytics_bp.route('/api/status', methods=['GET'])
@login_required
@admin_required
def get_status():
    """
    Get Google Cloud Platform integration status.
    
    Returns:
        JSON with configuration status and details
    """
    import os
    
    return jsonify({
        'success': True,
        'gcp_enabled': cloud_analytics.is_enabled(),
        'project_id': cloud_analytics.project_id,
        'dataset_id': cloud_analytics.dataset_id,
        'credentials_configured': bool(os.getenv('GOOGLE_APPLICATION_CREDENTIALS')),
        'ga_measurement_id': bool(os.getenv('GA_MEASUREMENT_ID'))
    }), 200


@analytics_bp.route('/api/initialize', methods=['POST'])
@login_required
@admin_required
def initialize_bigquery():
    """
    Initialize BigQuery dataset and tables.
    
    Creates dataset and all necessary tables if they don't exist.
    
    Returns:
        JSON with initialization results
    """
    if not cloud_analytics.is_enabled():
        return jsonify({
            'success': False,
            'error': 'Google Cloud Platform not configured'
        }), 400
    
    try:
        # Ensure dataset exists
        dataset_success = cloud_analytics.ensure_dataset_exists()
        
        # Create tables
        tables_success = cloud_analytics.create_analytics_tables()
        
        return jsonify({
            'success': dataset_success and tables_success,
            'dataset_created': dataset_success,
            'tables_created': tables_success,
            'message': 'BigQuery initialized successfully' if (dataset_success and tables_success) else 'Initialization failed'
        }), 200 if (dataset_success and tables_success) else 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error initializing BigQuery'
        }), 500

