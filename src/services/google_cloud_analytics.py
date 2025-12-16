"""
Google Cloud Platform Analytics Integration

This module provides integration with Google BigQuery for:
- Exporting application analytics data
- Building dashboards in Google Cloud Platform
- Syncing data for Looker Studio visualizations
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
import pandas as pd

try:
    from google.cloud import bigquery
    from google.cloud import storage
    from google.oauth2 import service_account
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False

from src.models.database import get_db_connection

load_dotenv()


class GoogleCloudAnalytics:
    """Service for managing Google Cloud Platform analytics integration."""
    
    def __init__(self):
        """Initialize Google Cloud Platform connection."""
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.dataset_id = os.getenv("GCP_DATASET_ID", "campus_resource_hub")
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.is_configured = bool(self.project_id and self.credentials_path and BIGQUERY_AVAILABLE)
        
        self.client = None
        self.storage_client = None
        
        if self.is_configured:
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=["https://www.googleapis.com/auth/bigquery",
                           "https://www.googleapis.com/auth/cloud-platform"]
                )
                self.client = bigquery.Client(
                    credentials=credentials,
                    project=self.project_id
                )
                self.storage_client = storage.Client(
                    credentials=credentials,
                    project=self.project_id
                )
            except Exception as e:
                print(f"Error initializing Google Cloud clients: {e}")
                self.is_configured = False
    
    def is_enabled(self) -> bool:
        """Check if Google Cloud Platform integration is enabled."""
        return self.is_configured
    
    def ensure_dataset_exists(self) -> bool:
        """
        Ensure the BigQuery dataset exists, create if it doesn't.
        
        Returns:
            True if dataset exists or was created successfully
        """
        if not self.is_configured:
            return False
        
        try:
            dataset_id = f"{self.project_id}.{self.dataset_id}"
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = "US"
            dataset.description = "Campus Resource Hub Analytics Data"
            
            # Try to get dataset, create if doesn't exist
            try:
                self.client.get_dataset(dataset_id)
                return True
            except Exception:
                self.client.create_dataset(dataset, exists_ok=True)
                print(f"Created dataset {dataset_id}")
                return True
                
        except Exception as e:
            print(f"Error ensuring dataset exists: {e}")
            return False
    
    def create_analytics_tables(self) -> bool:
        """
        Create BigQuery tables for analytics data export.
        
        Returns:
            True if tables created successfully
        """
        if not self.ensure_dataset_exists():
            return False
        
        tables = {
            'users_analytics': """
                CREATE TABLE IF NOT EXISTS `{project}.{dataset}.users_analytics` (
                    user_id INT64,
                    role STRING,
                    department STRING,
                    created_at TIMESTAMP,
                    has_google_calendar BOOL,
                    exported_at TIMESTAMP
                )
            """,
            'resources_analytics': """
                CREATE TABLE IF NOT EXISTS `{project}.{dataset}.resources_analytics` (
                    resource_id INT64,
                    owner_id INT64,
                    title STRING,
                    category STRING,
                    location STRING,
                    capacity INT64,
                    status STRING,
                    requires_approval BOOL,
                    average_rating FLOAT64,
                    total_reviews INT64,
                    total_bookings INT64,
                    created_at TIMESTAMP,
                    exported_at TIMESTAMP
                )
            """,
            'bookings_analytics': """
                CREATE TABLE IF NOT EXISTS `{project}.{dataset}.bookings_analytics` (
                    booking_id INT64,
                    resource_id INT64,
                    requester_id INT64,
                    start_datetime TIMESTAMP,
                    end_datetime TIMESTAMP,
                    status STRING,
                    duration_hours FLOAT64,
                    has_calendar_event BOOL,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    exported_at TIMESTAMP
                )
            """,
            'resource_utilization': """
                CREATE TABLE IF NOT EXISTS `{project}.{dataset}.resource_utilization` (
                    resource_id INT64,
                    date DATE,
                    total_bookings INT64,
                    approved_bookings INT64,
                    total_hours_booked FLOAT64,
                    utilization_rate FLOAT64,
                    exported_at TIMESTAMP
                )
            """,
            'user_engagement': """
                CREATE TABLE IF NOT EXISTS `{project}.{dataset}.user_engagement` (
                    user_id INT64,
                    date DATE,
                    bookings_created INT64,
                    bookings_approved INT64,
                    bookings_completed INT64,
                    resources_owned INT64,
                    messages_sent INT64,
                    reviews_written INT64,
                    exported_at TIMESTAMP
                )
            """
        }
        
        try:
            for table_name, query in tables.items():
                formatted_query = query.format(
                    project=self.project_id,
                    dataset=self.dataset_id
                )
                self.client.query(formatted_query).result()
                print(f"Created/verified table: {table_name}")
            
            return True
            
        except Exception as e:
            print(f"Error creating analytics tables: {e}")
            return False
    
    def export_users_data(self) -> bool:
        """
        Export users data to BigQuery.
        
        Returns:
            True if export successful
        """
        if not self.is_configured:
            return False
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    user_id,
                    role,
                    department,
                    created_at,
                    CASE WHEN google_calendar_token IS NOT NULL THEN 1 ELSE 0 END as has_google_calendar
                FROM users
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return True  # No data to export
            
            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=['user_id', 'role', 'department', 'created_at', 'has_google_calendar'])
            df['exported_at'] = datetime.utcnow()
            
            # Upload to BigQuery
            table_id = f"{self.project_id}.{self.dataset_id}.users_analytics"
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            )
            
            job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()
            
            print(f"Exported {len(df)} users to BigQuery")
            return True
            
        except Exception as e:
            print(f"Error exporting users data: {e}")
            return False
    
    def export_resources_data(self) -> bool:
        """
        Export resources data with aggregated metrics to BigQuery.
        
        Returns:
            True if export successful
        """
        if not self.is_configured:
            return False
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    r.resource_id,
                    r.owner_id,
                    r.title,
                    r.category,
                    r.location,
                    r.capacity,
                    r.status,
                    r.requires_approval,
                    COALESCE(AVG(rv.rating), 0) as average_rating,
                    COUNT(DISTINCT rv.review_id) as total_reviews,
                    COUNT(DISTINCT b.booking_id) as total_bookings,
                    r.created_at
                FROM resources r
                LEFT JOIN reviews rv ON r.resource_id = rv.resource_id
                LEFT JOIN bookings b ON r.resource_id = b.resource_id
                GROUP BY r.resource_id, r.owner_id, r.title, r.category, r.location, 
                         r.capacity, r.status, r.requires_approval, r.created_at
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return True
            
            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=[
                'resource_id', 'owner_id', 'title', 'category', 'location',
                'capacity', 'status', 'requires_approval', 'average_rating',
                'total_reviews', 'total_bookings', 'created_at'
            ])
            df['exported_at'] = datetime.utcnow()
            
            # Upload to BigQuery
            table_id = f"{self.project_id}.{self.dataset_id}.resources_analytics"
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            )
            
            job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()
            
            print(f"Exported {len(df)} resources to BigQuery")
            return True
            
        except Exception as e:
            print(f"Error exporting resources data: {e}")
            return False
    
    def export_bookings_data(self) -> bool:
        """
        Export bookings data to BigQuery.
        
        Returns:
            True if export successful
        """
        if not self.is_configured:
            return False
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    booking_id,
                    resource_id,
                    requester_id,
                    start_datetime,
                    end_datetime,
                    status,
                    (julianday(end_datetime) - julianday(start_datetime)) * 24 as duration_hours,
                    CASE WHEN calendar_event_id IS NOT NULL THEN 1 ELSE 0 END as has_calendar_event,
                    created_at,
                    updated_at
                FROM bookings
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return True
            
            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=[
                'booking_id', 'resource_id', 'requester_id', 'start_datetime',
                'end_datetime', 'status', 'duration_hours', 'has_calendar_event',
                'created_at', 'updated_at'
            ])
            df['exported_at'] = datetime.utcnow()
            
            # Upload to BigQuery
            table_id = f"{self.project_id}.{self.dataset_id}.bookings_analytics"
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            )
            
            job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()
            
            print(f"Exported {len(df)} bookings to BigQuery")
            return True
            
        except Exception as e:
            print(f"Error exporting bookings data: {e}")
            return False
    
    def calculate_resource_utilization(self, days_back: int = 30) -> bool:
        """
        Calculate and export resource utilization metrics.
        
        Args:
            days_back: Number of days to look back for calculation
            
        Returns:
            True if calculation and export successful
        """
        if not self.is_configured:
            return False
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT 
                    resource_id,
                    DATE(start_datetime) as date,
                    COUNT(*) as total_bookings,
                    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_bookings,
                    SUM((julianday(end_datetime) - julianday(start_datetime)) * 24) as total_hours_booked
                FROM bookings
                WHERE DATE(start_datetime) >= ?
                GROUP BY resource_id, DATE(start_datetime)
            """, (start_date,))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return True
            
            # Convert to DataFrame and calculate utilization rate
            df = pd.DataFrame(rows, columns=[
                'resource_id', 'date', 'total_bookings', 'approved_bookings', 'total_hours_booked'
            ])
            
            # Assuming 10 hours per day as available time
            df['utilization_rate'] = (df['total_hours_booked'] / 10.0 * 100).round(2)
            df['exported_at'] = datetime.utcnow()
            
            # Upload to BigQuery
            table_id = f"{self.project_id}.{self.dataset_id}.resource_utilization"
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            )
            
            job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()
            
            print(f"Exported resource utilization data for {days_back} days")
            return True
            
        except Exception as e:
            print(f"Error calculating resource utilization: {e}")
            return False
    
    def export_all_analytics(self) -> Dict[str, bool]:
        """
        Export all analytics data to BigQuery.
        
        Returns:
            Dictionary with export results for each table
        """
        if not self.is_configured:
            return {
                'configured': False,
                'message': 'Google Cloud Platform not configured'
            }
        
        # Ensure tables exist
        self.create_analytics_tables()
        
        results = {
            'users': self.export_users_data(),
            'resources': self.export_resources_data(),
            'bookings': self.export_bookings_data(),
            'utilization': self.calculate_resource_utilization()
        }
        
        return results
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Get real-time metrics for dashboards from local database.
        
        Returns:
            Dictionary with various metrics
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        metrics = {}
        
        # Total counts
        cursor.execute("SELECT COUNT(*) FROM users")
        metrics['total_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM resources WHERE status = 'published'")
        metrics['total_resources'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bookings")
        metrics['total_bookings'] = cursor.fetchone()[0]
        
        # Bookings by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM bookings
            GROUP BY status
        """)
        metrics['bookings_by_status'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Resources by category
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM resources
            WHERE status = 'published'
            GROUP BY category
        """)
        metrics['resources_by_category'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Top resources (most booked)
        cursor.execute("""
            SELECT r.title, COUNT(b.booking_id) as bookings_count
            FROM resources r
            LEFT JOIN bookings b ON r.resource_id = b.resource_id
            GROUP BY r.resource_id, r.title
            ORDER BY bookings_count DESC
            LIMIT 10
        """)
        metrics['top_resources'] = [
            {'title': row[0], 'bookings': row[1]}
            for row in cursor.fetchall()
        ]
        
        # Recent activity (last 30 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM bookings
            WHERE DATE(created_at) >= DATE('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        metrics['bookings_trend'] = [
            {'date': row[0], 'count': row[1]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return metrics


# Global service instance
cloud_analytics = GoogleCloudAnalytics()

