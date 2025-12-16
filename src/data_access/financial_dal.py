"""
Data Access Layer for financial analysis operations.

This module provides database operations for financial queries, analysis logging,
and anomaly detection.
"""

import sqlite3
from typing import List, Dict, Any, Optional
import statistics
from datetime import datetime
from src.models.financial_db import get_db_connection


class FinancialDAL:
    """Data Access Layer for financial analysis"""
    
    def __init__(self):
        """Initialize Financial DAL"""
        pass
    
    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as list of dicts
        
        Args:
            sql_query: SQL query string
            
        Returns:
            List of dictionaries representing rows
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            # Convert sqlite3.Row objects to dicts
            results = [dict(row) for row in rows]
            
            conn.close()
            return results
            
        except sqlite3.Error as e:
            conn.close()
            raise Exception(f"Database query error: {str(e)}")
    
    def detect_anomalies(self, results: List[Dict[str, Any]], threshold_std: float = 2.0) -> List[str]:
        """
        Detect anomalies in query results using statistical methods
        
        Args:
            results: Query results
            threshold_std: Number of standard deviations for outlier detection
            
        Returns:
            List of anomaly descriptions
        """
        anomalies = []
        
        if not results or len(results) < 3:
            return anomalies
        
        # Try to find numeric columns for anomaly detection
        numeric_cols = []
        for key in results[0].keys():
            try:
                # Check if column has numeric values
                values = [row[key] for row in results if row[key] is not None]
                if values and all(isinstance(v, (int, float)) for v in values):
                    numeric_cols.append(key)
            except:
                continue
        
        # Detect outliers in numeric columns
        for col in numeric_cols:
            values = [row[col] for row in results if row[col] is not None]
            
            if len(values) < 3:
                continue
            
            try:
                mean_val = statistics.mean(values)
                stdev_val = statistics.stdev(values)
                
                if stdev_val == 0:
                    continue
                
                # Find outliers
                for i, row in enumerate(results):
                    val = row.get(col)
                    if val is None:
                        continue
                    
                    z_score = abs((val - mean_val) / stdev_val)
                    
                    if z_score > threshold_std:
                        # Identify the row
                        row_identifier = self._get_row_identifier(row)
                        
                        if val < mean_val:
                            anomalies.append(
                                f"Low outlier in '{col}' for {row_identifier}: "
                                f"{val:.2f} (mean: {mean_val:.2f}, z-score: {z_score:.2f})"
                            )
                        else:
                            anomalies.append(
                                f"High outlier in '{col}' for {row_identifier}: "
                                f"{val:.2f} (mean: {mean_val:.2f}, z-score: {z_score:.2f})"
                            )
            except statistics.StatisticsError:
                continue
        
        # Detect margin compression (revenue/cost ratio anomalies)
        if 'revenue' in results[0] and 'cost' in results[0]:
            margins = []
            for row in results:
                if row.get('revenue') and row.get('cost') and row['cost'] > 0:
                    margin_pct = ((row['revenue'] - row['cost']) / row['revenue']) * 100
                    margins.append((margin_pct, row))
            
            if margins:
                margin_values = [m[0] for m in margins]
                if len(margin_values) >= 3:
                    try:
                        mean_margin = statistics.mean(margin_values)
                        
                        # Flag low margins
                        for margin_pct, row in margins:
                            if margin_pct < 10:  # Less than 10% margin
                                row_id = self._get_row_identifier(row)
                                anomalies.append(
                                    f"⚠️ Very low margin for {row_id}: {margin_pct:.1f}% "
                                    f"(significantly below average of {mean_margin:.1f}%)"
                                )
                    except statistics.StatisticsError:
                        pass
        
        return anomalies
    
    def _get_row_identifier(self, row: Dict[str, Any]) -> str:
        """
        Get a human-readable identifier for a row
        
        Args:
            row: Dictionary representing a database row
            
        Returns:
            String identifier
        """
        # Try common identifier fields
        id_fields = ['region_name', 'product_name', 'customer_name', 'transaction_date', 'category']
        
        for field in id_fields:
            if field in row and row[field]:
                return f"{field.replace('_', ' ').title()}: {row[field]}"
        
        # Fallback to first non-null field
        for key, value in row.items():
            if value is not None and not key.endswith('_id'):
                return f"{key}: {value}"
        
        return "Row"
    
    def log_analysis(
        self, 
        user_query: str, 
        sql_query: Optional[str], 
        llm_response: str, 
        anomalies: List[str]
    ) -> int:
        """
        Log an analysis query for audit and history
        
        Args:
            user_query: User's original question
            sql_query: Generated SQL query
            llm_response: LLM summary response
            anomalies: List of detected anomalies
            
        Returns:
            Log ID of the inserted record
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        anomalies_json = '\n'.join(anomalies) if anomalies else None
        
        cursor.execute("""
            INSERT INTO analysis_logs (user_query, sql_query, llm_response, anomalies_detected)
            VALUES (?, ?, ?, ?)
        """, (user_query, sql_query, llm_response, anomalies_json))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent analysis queries
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of analysis log dictionaries
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT log_id, user_query, sql_query, llm_response, anomalies_detected, timestamp
            FROM analysis_logs
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
    
    def get_regional_summary(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get financial summary by region
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of regional summaries
        """
        query = """
            SELECT 
                r.region_name,
                r.region_code,
                COUNT(ft.transaction_id) as transaction_count,
                SUM(ft.revenue) as total_revenue,
                SUM(ft.cost) as total_cost,
                SUM(ft.margin) as total_margin,
                AVG((ft.margin / ft.revenue) * 100) as avg_margin_pct,
                SUM(ft.quantity) as total_quantity
            FROM financial_transactions ft
            JOIN regions r ON ft.region_id = r.region_id
        """
        
        params = []
        if start_date or end_date:
            query += " WHERE "
            conditions = []
            if start_date:
                conditions.append("ft.transaction_date >= ?")
                params.append(start_date)
            if end_date:
                conditions.append("ft.transaction_date <= ?")
                params.append(end_date)
            query += " AND ".join(conditions)
        
        query += " GROUP BY r.region_id, r.region_name, r.region_code ORDER BY total_revenue DESC"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
    
    def get_product_performance(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top performing products by revenue
        
        Args:
            limit: Number of top products to return
            
        Returns:
            List of product performance dictionaries
        """
        query = """
            SELECT 
                p.product_name,
                p.category,
                COUNT(ft.transaction_id) as transaction_count,
                SUM(ft.revenue) as total_revenue,
                SUM(ft.margin) as total_margin,
                AVG((ft.margin / ft.revenue) * 100) as avg_margin_pct
            FROM financial_transactions ft
            JOIN products p ON ft.product_id = p.product_id
            GROUP BY p.product_id, p.product_name, p.category
            ORDER BY total_revenue DESC
            LIMIT ?
        """
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (limit,))
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
    
    def get_time_series_data(self, metric: str = 'revenue', granularity: str = 'month') -> List[Dict[str, Any]]:
        """
        Get time series data for a specific metric
        
        Args:
            metric: Metric to retrieve ('revenue', 'margin', 'cost')
            granularity: Time granularity ('day', 'month', 'quarter')
            
        Returns:
            List of time series data points
        """
        if granularity == 'month':
            date_format = '%Y-%m'
        elif granularity == 'quarter':
            date_format = '%Y-Q'
        else:
            date_format = '%Y-%m-%d'
        
        query = f"""
            SELECT 
                strftime('{date_format}', transaction_date) as time_period,
                SUM(revenue) as total_revenue,
                SUM(cost) as total_cost,
                SUM(margin) as total_margin,
                COUNT(*) as transaction_count
            FROM financial_transactions
            GROUP BY time_period
            ORDER BY time_period
        """
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
