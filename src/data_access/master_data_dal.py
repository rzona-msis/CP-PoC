"""
Data Access Layer for master data matching operations.

This module provides database operations for duplicate detection, fuzzy matching,
and golden record management.
"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple
import difflib
import json
from src.models.financial_db import get_db_connection


class MasterDataDAL:
    """Data Access Layer for master data matching"""
    
    def __init__(self):
        """Initialize Master Data DAL"""
        pass
    
    def get_entities_by_type(self, entity_type: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all entities of a given type
        
        Args:
            entity_type: 'customer', 'vendor', or 'product'
            limit: Optional limit on number of results
            
        Returns:
            List of entity dictionaries
        """
        table_map = {
            'customer': 'customers',
            'vendor': 'vendors',
            'product': 'products'
        }
        
        table_name = table_map.get(entity_type)
        if not table_name:
            raise ValueError(f"Invalid entity type: {entity_type}")
        
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            
            conn.close()
            return results
        except Exception as e:
            # Database connection failed - return empty results
            print(f"WARNING: Database connection failed in get_entities_by_type: {e}")
            return []
    
    def find_potential_duplicates(
        self, 
        entity_type: str, 
        threshold: float = 0.7,
        search_field: str = 'all'
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any], float]]:
        """
        Find potential duplicate entities using fuzzy matching
        
        Args:
            entity_type: 'customer', 'vendor', or 'product'
            threshold: Similarity threshold (0-1)
            search_field: Specific field to search ('all' for all fields, or field name)
            
        Returns:
            List of tuples: (entity_a, entity_b, similarity_score)
        """
        entities = self.get_entities_by_type(entity_type)
        duplicates = []
        
        # Primary field to match on
        name_field_map = {
            'customer': 'customer_name',
            'vendor': 'vendor_name',
            'product': 'product_name'
        }
        name_field = name_field_map[entity_type]
        
        # Filter out entities with null or empty primary name field
        valid_entities = []
        for entity in entities:
            name_value = entity.get(name_field)
            if name_value and str(name_value).strip() and str(name_value).lower() != 'none':
                valid_entities.append(entity)
        
        print(f"Found {len(valid_entities)} valid entities out of {len(entities)} total")
        print(f"Searching on field(s): {search_field}")
        
        # Compare each entity with every other entity
        for i in range(len(valid_entities)):
            for j in range(i + 1, len(valid_entities)):
                entity_a = valid_entities[i]
                entity_b = valid_entities[j]
                
                # Calculate similarity
                similarity = self._calculate_similarity(entity_a, entity_b, entity_type, search_field)
                
                if similarity >= threshold:
                    duplicates.append((entity_a, entity_b, similarity))
        
        # Sort by similarity (highest first)
        duplicates.sort(key=lambda x: x[2], reverse=True)
        
        return duplicates
    
    def _calculate_similarity(
        self, 
        entity_a: Dict[str, Any], 
        entity_b: Dict[str, Any], 
        entity_type: str,
        search_field: str = 'all'
    ) -> float:
        """
        Calculate similarity score between two entities
        
        Args:
            entity_a: First entity
            entity_b: Second entity
            entity_type: Type of entity
            search_field: Specific field to search or 'all' for all fields
            
        Returns:
            Similarity score (0-1)
        """
        # Define weights for different fields
        if entity_type == 'customer':
            all_fields = {
                'customer_name': 0.40,
                'email': 0.25,
                'phone': 0.15,
                'address': 0.10,
                'city': 0.05,
                'state': 0.05
            }
        elif entity_type == 'vendor':
            all_fields = {
                'vendor_name': 0.40,
                'contact_email': 0.25,
                'phone': 0.15,
                'address': 0.10,
                'city': 0.05,
                'state': 0.05
            }
        elif entity_type == 'product':
            all_fields = {
                'product_name': 0.50,
                'sku': 0.30,
                'category': 0.20
            }
        else:
            all_fields = {}
        
        # Filter fields based on search_field parameter
        if search_field != 'all':
            # Map generic field names to entity-specific names
            field_mapping = {
                'customer': {
                    'name': 'customer_name',
                    'email': 'email',
                    'phone': 'phone',
                    'address': 'address'
                },
                'vendor': {
                    'name': 'vendor_name',
                    'contact_email': 'contact_email',
                    'phone': 'phone',
                    'address': 'address'
                },
                'product': {
                    'name': 'product_name',
                    'sku': 'sku',
                    'category': 'category'
                }
            }
            
            # Get actual field name for this entity type
            mapped_field = field_mapping.get(entity_type, {}).get(search_field, search_field)
            
            # Use only the specified field with full weight
            if mapped_field in all_fields:
                fields = {mapped_field: 1.0}
            else:
                fields = all_fields  # Fallback to all fields if mapping fails
        else:
            fields = all_fields
        
        total_score = 0.0
        total_weight = 0.0
        
        for field, weight in fields.items():
            val_a = entity_a.get(field)
            val_b = entity_b.get(field)
            
            # Skip if either value is None or empty
            if val_a is None or val_b is None:
                continue
            
            # Convert to strings and normalize
            str_a = str(val_a).lower().strip()
            str_b = str(val_b).lower().strip()
            
            # Skip empty strings
            if not str_a or not str_b or str_a == 'none' or str_b == 'none':
                continue
            
            # Calculate string similarity
            field_similarity = self._string_similarity(str_a, str_b)
            
            total_score += field_similarity * weight
            total_weight += weight
        
        # Normalize by actual weight used
        if total_weight > 0:
            return total_score / total_weight
        else:
            return 0.0
    
    def _string_similarity(self, str_a: str, str_b: str) -> float:
        """
        Calculate similarity between two strings using multiple methods
        
        Args:
            str_a: First string
            str_b: Second string
            
        Returns:
            Similarity score (0-1)
        """
        if str_a == str_b:
            return 1.0
        
        # Use difflib for sequence matching
        seq_ratio = difflib.SequenceMatcher(None, str_a, str_b).ratio()
        
        # Check for substring matches
        if str_a in str_b or str_b in str_a:
            substring_bonus = 0.2
        else:
            substring_bonus = 0.0
        
        # Combine scores
        final_score = min(seq_ratio + substring_bonus, 1.0)
        
        return final_score
    
    def save_match_result(
        self,
        entity_type: str,
        entity_a_id: int,
        entity_b_id: int,
        confidence_score: float,
        match_reason: str,
        golden_record: Dict[str, Any],
        status: str = 'pending'
    ) -> int:
        """
        Save a match result to the database
        
        Args:
            entity_type: Type of entity
            entity_a_id: ID of first entity
            entity_b_id: ID of second entity
            confidence_score: Confidence score (0-100)
            match_reason: Explanation of the match
            golden_record: Suggested unified record
            status: Match status
            
        Returns:
            Match ID of the inserted record
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        golden_record_json = json.dumps(golden_record, default=str)
        
        cursor.execute("""
            INSERT INTO match_results 
            (entity_type, entity_a_id, entity_b_id, confidence_score, match_reason, golden_record_suggestion, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (entity_type, entity_a_id, entity_b_id, confidence_score, match_reason, golden_record_json, status))
        
        match_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return match_id
    
    def get_match_results(
        self, 
        entity_type: Optional[str] = None, 
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve match results with optional filters
        
        Args:
            entity_type: Filter by entity type
            status: Filter by status
            limit: Maximum number of results
            
        Returns:
            List of match result dictionaries
        """
        query = "SELECT * FROM match_results WHERE 1=1"
        params = []
        
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY confidence_score DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        conn.close()
        return results
    
    def update_match_status(
        self, 
        match_id: int, 
        status: str, 
        reviewed_by: Optional[str] = None
    ) -> bool:
        """
        Update the status of a match result
        
        Args:
            match_id: ID of the match result
            status: New status ('approved', 'rejected')
            reviewed_by: Username of reviewer
            
        Returns:
            True if successful
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE match_results 
            SET status = ?, reviewed_by = ?
            WHERE match_id = ?
        """, (status, reviewed_by, match_id))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def create_golden_record(
        self,
        entity_type: str,
        unified_data: Dict[str, Any],
        source_ids: List[int]
    ) -> int:
        """
        Create a golden record from merged duplicates
        
        Args:
            entity_type: Type of entity
            unified_data: Unified data dictionary
            source_ids: List of source entity IDs that were merged
            
        Returns:
            Golden record ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        unified_data_json = json.dumps(unified_data, default=str)
        source_ids_json = json.dumps(source_ids)
        
        cursor.execute("""
            INSERT INTO golden_records (entity_type, unified_data, source_ids)
            VALUES (?, ?, ?)
        """, (entity_type, unified_data_json, source_ids_json))
        
        golden_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return golden_id
    
    def get_golden_records(self, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve golden records
        
        Args:
            entity_type: Optional filter by entity type
            
        Returns:
            List of golden record dictionaries
        """
        query = "SELECT * FROM golden_records"
        params = []
        
        if entity_type:
            query += " WHERE entity_type = ?"
            params.append(entity_type)
        
        query += " ORDER BY created_at DESC"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        # Parse JSON fields
        for result in results:
            if result.get('unified_data'):
                result['unified_data'] = json.loads(result['unified_data'])
            if result.get('source_ids'):
                result['source_ids'] = json.loads(result['source_ids'])
        
        conn.close()
        return results
    
    def get_entity_details(self, entity_type: str, entity_id: int) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific entity
        
        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            
        Returns:
            Entity dictionary or None
        """
        table_map = {
            'customer': ('customers', 'customer_id'),
            'vendor': ('vendors', 'vendor_id'),
            'product': ('products', 'product_id')
        }
        
        table_info = table_map.get(entity_type)
        if not table_info:
            return None
        
        table_name, id_field = table_info
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE {id_field} = ?", (entity_id,))
        
        row = cursor.fetchone()
        result = dict(row) if row else None
        
        conn.close()
        return result
    
    def get_duplicate_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about duplicates in the system
        
        Returns:
            Dictionary with duplicate statistics
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Count matches by type and status
        cursor.execute("""
            SELECT entity_type, status, COUNT(*) as count
            FROM match_results
            GROUP BY entity_type, status
        """)
        
        matches = cursor.fetchall()
        stats['matches_by_type_status'] = [dict(row) for row in matches]
        
        # Count golden records by type
        cursor.execute("""
            SELECT entity_type, COUNT(*) as count
            FROM golden_records
            GROUP BY entity_type
        """)
        
        golden_records = cursor.fetchall()
        stats['golden_records_by_type'] = [dict(row) for row in golden_records]
        
        # Count total entities by type
        for entity_type in ['customers', 'vendors', 'products']:
            cursor.execute(f"SELECT COUNT(*) as count FROM {entity_type}")
            count = cursor.fetchone()['count']
            stats[f'total_{entity_type}'] = count
        
        conn.close()
        return stats
