"""
Controller for AI Master Data Matching functionality.

This module provides routes for duplicate detection and master data quality management.
"""

from flask import Blueprint, render_template, request, jsonify
import traceback

master_data_bp = Blueprint('master_data', __name__)

# Initialize services with error handling
try:
    from src.services.llm_service import get_llm_service
    llm_service = get_llm_service()
except Exception as e:
    print(f"Warning: LLM service initialization failed: {e}")
    llm_service = None

try:
    from src.data_access.master_data_dal import MasterDataDAL
    master_data_dal = MasterDataDAL()
except Exception as e:
    print(f"Warning: Master Data DAL initialization failed: {e}")
    master_data_dal = None


@master_data_bp.route('/master-data-matching')
def matching_page():
    """Render the master data matching interface"""
    try:
        # Get statistics if DAL is available
        stats = {}
        recent_matches = []
        
        if master_data_dal:
            try:
                stats = master_data_dal.get_duplicate_statistics()
                recent_matches = master_data_dal.get_match_results(limit=10)
            except Exception as dal_error:
                print(f"Warning: Could not load master data stats: {dal_error}")
        
        return render_template(
            'master_data_matching.html',
            stats=stats,
            recent_matches=recent_matches
        )
    except Exception as e:
        print(f"Error loading master data matching page: {e}")
        traceback.print_exc()
        # Always return a valid page
        return render_template('master_data_matching.html', 
                             stats={}, 
                             recent_matches=[],
                             error=str(e)), 200


@master_data_bp.route('/api/find-duplicates', methods=['POST'])
def find_duplicates():
    """
    Find potential duplicate entities
    
    Request JSON:
        {
            "entity_type": "customer|vendor|product",
            "threshold": 0.7 (optional, default 0.7),
            "use_llm": true (optional, default false),
            "search_field": "all|name|email|phone|address|sku|category" (optional, default "all")
        }
    
    Returns:
        JSON with list of duplicate pairs and match details
    """
    try:
        # Check if services are available
        if not master_data_dal:
            return jsonify({
                'success': False,
                'error': 'Master data services are not available. Please check server configuration.'
            }), 503
        
        data = request.get_json()
        
        if not data or 'entity_type' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing entity_type parameter'
            }), 400
        
        entity_type = data['entity_type']
        threshold = data.get('threshold', 0.7)
        use_llm = data.get('use_llm', False)
        search_field = data.get('search_field', 'all')
        
        if entity_type not in ['customer', 'vendor', 'product']:
            return jsonify({
                'success': False,
                'error': 'Invalid entity_type. Must be customer, vendor, or product'
            }), 400
        
        print(f"\n=== Finding Duplicates ===")
        print(f"Entity Type: {entity_type}")
        print(f"Threshold: {threshold}")
        print(f"Use LLM: {use_llm}")
        print(f"Search Field: {search_field}")
        
        # Find potential duplicates using rule-based matching
        print("Step 1: Rule-based duplicate detection...")
        try:
            duplicates = master_data_dal.find_potential_duplicates(entity_type, threshold, search_field)
            print(f"Found {len(duplicates)} potential duplicate pairs")
        except Exception as dal_error:
            print(f"ERROR in find_potential_duplicates: {dal_error}")
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Database error: {str(dal_error)}'
            }), 500
        
        # Handle case where no duplicates found
        if not duplicates or len(duplicates) == 0:
            print("No duplicates found, returning empty result")
            return jsonify({
                'success': True,
                'entity_type': entity_type,
                'duplicate_count': 0,
                'duplicates': []
            })
        
        # Process each duplicate pair
        results = []
        
        for i, (entity_a, entity_b, similarity) in enumerate(duplicates):
            print(f"\nProcessing pair {i+1}/{len(duplicates)}...")
            
            # Ensure entities are valid dictionaries
            if not entity_a or not entity_b:
                print(f"  Skipping invalid entity pair")
                continue
            
            # Get entity IDs
            id_field_map = {
                'customer': 'customer_id',
                'vendor': 'vendor_id',
                'product': 'product_id'
            }
            id_field = id_field_map[entity_type]
            entity_a_id = entity_a.get(id_field)
            entity_b_id = entity_b.get(id_field)
            
            if not entity_a_id or not entity_b_id:
                print(f"  Skipping pair with missing IDs")
                continue
            
            # If use_llm is enabled, get LLM scoring
            if use_llm:
                print(f"  Getting LLM confidence score...")
                llm_result = llm_service.score_duplicate_match(entity_a, entity_b, entity_type)
                
                confidence_score = llm_result['confidence_score']
                match_reason = llm_result['match_reason']
                golden_record = llm_result['golden_record']
            else:
                # Use rule-based score
                confidence_score = similarity * 100  # Convert to 0-100 scale
                match_reason = f"Rule-based similarity: {similarity:.2f}"
                
                # Simple golden record (prefer entity A)
                golden_record = entity_a.copy()
            
            # Save match result to database
            match_id = master_data_dal.save_match_result(
                entity_type=entity_type,
                entity_a_id=entity_a_id,
                entity_b_id=entity_b_id,
                confidence_score=confidence_score,
                match_reason=match_reason,
                golden_record=golden_record,
                status='pending'
            )
            
            # Ensure entities are serializable (convert any None values to empty strings)
            entity_a_clean = {k: (v if v is not None else '') for k, v in entity_a.items()}
            entity_b_clean = {k: (v if v is not None else '') for k, v in entity_b.items()}
            golden_record_clean = {k: (v if v is not None else '') for k, v in golden_record.items()}
            
            results.append({
                'match_id': match_id,
                'entity_a': entity_a_clean,
                'entity_b': entity_b_clean,
                'confidence_score': confidence_score,
                'match_reason': match_reason,
                'golden_record': golden_record_clean,
                'rule_based_similarity': similarity
            })
        
        print(f"\n=== Duplicate Detection Complete ===")
        print(f"Total pairs found: {len(results)}\n")
        
        return jsonify({
            'success': True,
            'entity_type': entity_type,
            'duplicate_count': len(results),
            'duplicates': results
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error in find_duplicates: {error_msg}")
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'traceback': traceback.format_exc()
        }), 500


@master_data_bp.route('/api/match-results', methods=['GET'])
def get_match_results():
    """Get saved match results with optional filters"""
    try:
        entity_type = request.args.get('entity_type')
        status = request.args.get('status')
        limit = request.args.get('limit', 100, type=int)
        
        results = master_data_dal.get_match_results(entity_type, status, limit)
        
        # Enrich with entity details
        for result in results:
            entity_type = result['entity_type']
            entity_a_id = result['entity_a_id']
            entity_b_id = result['entity_b_id']
            
            result['entity_a'] = master_data_dal.get_entity_details(entity_type, entity_a_id)
            result['entity_b'] = master_data_dal.get_entity_details(entity_type, entity_b_id)
            
            # Parse golden record JSON if it's a string
            if isinstance(result.get('golden_record_suggestion'), str):
                import json
                try:
                    result['golden_record_suggestion'] = json.loads(result['golden_record_suggestion'])
                except:
                    pass
        
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@master_data_bp.route('/api/update-match-status', methods=['POST'])
def update_match_status():
    """
    Update the status of a match result
    
    Request JSON:
        {
            "match_id": 123,
            "status": "approved|rejected",
            "reviewed_by": "username" (optional)
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'match_id' not in data or 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing match_id or status parameter'
            }), 400
        
        match_id = data['match_id']
        status = data['status']
        reviewed_by = data.get('reviewed_by', 'System')
        
        if status not in ['approved', 'rejected']:
            return jsonify({
                'success': False,
                'error': 'Invalid status. Must be approved or rejected'
            }), 400
        
        success = master_data_dal.update_match_status(match_id, status, reviewed_by)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Match {match_id} status updated to {status}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Match not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@master_data_bp.route('/api/create-golden-record', methods=['POST'])
def create_golden_record():
    """
    Create a golden record from approved duplicates
    
    Request JSON:
        {
            "match_id": 123
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'match_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing match_id parameter'
            }), 400
        
        match_id = data['match_id']
        
        # Get the match result
        matches = master_data_dal.get_match_results()
        match = next((m for m in matches if m['match_id'] == match_id), None)
        
        if not match:
            return jsonify({
                'success': False,
                'error': 'Match not found'
            }), 404
        
        if match['status'] != 'approved':
            return jsonify({
                'success': False,
                'error': 'Only approved matches can be converted to golden records'
            }), 400
        
        # Parse golden record if it's a string
        import json
        golden_data = match['golden_record_suggestion']
        if isinstance(golden_data, str):
            golden_data = json.loads(golden_data)
        
        # Create golden record
        golden_id = master_data_dal.create_golden_record(
            entity_type=match['entity_type'],
            unified_data=golden_data,
            source_ids=[match['entity_a_id'], match['entity_b_id']]
        )
        
        return jsonify({
            'success': True,
            'golden_id': golden_id,
            'message': f'Golden record created with ID {golden_id}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@master_data_bp.route('/api/golden-records', methods=['GET'])
def get_golden_records():
    """Get golden records"""
    try:
        entity_type = request.args.get('entity_type')
        
        records = master_data_dal.get_golden_records(entity_type)
        
        return jsonify({
            'success': True,
            'count': len(records),
            'records': records
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@master_data_bp.route('/api/entities', methods=['GET'])
def get_entities():
    """Get all entities of a specific type"""
    try:
        entity_type = request.args.get('entity_type')
        limit = request.args.get('limit', type=int)
        
        if not entity_type:
            return jsonify({
                'success': False,
                'error': 'Missing entity_type parameter'
            }), 400
        
        entities = master_data_dal.get_entities_by_type(entity_type, limit)
        
        return jsonify({
            'success': True,
            'entity_type': entity_type,
            'count': len(entities),
            'entities': entities
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@master_data_bp.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get duplicate statistics"""
    try:
        stats = master_data_dal.get_duplicate_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
