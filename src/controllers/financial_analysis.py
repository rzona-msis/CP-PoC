"""
Controller for AI Financial Analysis functionality.

This module provides routes for natural language financial queries and analysis.
"""

from flask import Blueprint, render_template, request, jsonify
import traceback

financial_bp = Blueprint('financial', __name__)

# Initialize services with error handling
try:
    from src.services.llm_service import get_llm_service
    llm_service = get_llm_service()
except Exception as e:
    print(f"Warning: LLM service initialization failed: {e}")
    llm_service = None

try:
    from src.data_access.financial_dal import FinancialDAL
    financial_dal = FinancialDAL()
except Exception as e:
    print(f"Warning: Financial DAL initialization failed: {e}")
    financial_dal = None


@financial_bp.route('/financial-analysis')
def analysis_page():
    """Render the financial analysis interface"""
    try:
        # Get some summary stats for the dashboard if DAL is available
        regional_summary = []
        product_performance = []
        
        if financial_dal:
            try:
                regional_summary = financial_dal.get_regional_summary()
                product_performance = financial_dal.get_product_performance(limit=5)
            except Exception as dal_error:
                print(f"Warning: Could not load dashboard data: {dal_error}")
        
        return render_template(
            'financial_analysis.html',
            regional_summary=regional_summary,
            product_performance=product_performance
        )
    except Exception as e:
        print(f"Error loading financial analysis page: {e}")
        traceback.print_exc()
        # Always return a valid page, even with errors
        return render_template('financial_analysis.html', 
                             regional_summary=[], 
                             product_performance=[],
                             error=str(e)), 200


@financial_bp.route('/api/analyze', methods=['POST'])
def analyze_financial_query():
    """
    Process natural language financial query
    
    Request JSON:
        {
            "query": "user's natural language question"
        }
    
    Returns:
        JSON with SQL, results, anomalies, LLM summary
    """
    try:
        # Check if services are available
        if not financial_dal or not llm_service:
            return jsonify({
                'success': False,
                'error': 'Financial services are not available. Please check server configuration.'
            }), 503
        
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing query parameter'
            }), 400
        
        user_query = data['query'].strip()
        
        if not user_query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        print(f"\n=== Processing Query ===")
        print(f"User Query: {user_query}")
        
        # Step 1: Convert natural language to SQL using LLM
        print("Step 1: Converting to SQL...")
        sql_query = llm_service.natural_language_to_sql(user_query)
        print(f"Generated SQL: {sql_query}")
        
        # Step 2: Execute SQL query
        print("Step 2: Executing SQL...")
        results = financial_dal.execute_query(sql_query)
        print(f"Retrieved {len(results)} rows")
        
        # Step 3: Detect anomalies in results
        print("Step 3: Detecting anomalies...")
        anomalies = financial_dal.detect_anomalies(results)
        print(f"Found {len(anomalies)} anomalies")
        
        # Step 4: Generate LLM summary
        print("Step 4: Generating summary...")
        summary = llm_service.summarize_financial_analysis(
            query=user_query,
            results=results,
            anomalies=anomalies,
            sql_query=sql_query
        )
        print("Summary generated")
        
        # Step 5: Log the analysis
        print("Step 5: Logging analysis...")
        log_id = financial_dal.log_analysis(user_query, sql_query, summary, anomalies)
        print(f"Logged with ID: {log_id}")
        
        print("=== Query Complete ===\n")
        
        return jsonify({
            'success': True,
            'query': user_query,
            'sql': sql_query,
            'results': results,
            'result_count': len(results),
            'anomalies': anomalies,
            'summary': summary,
            'log_id': log_id
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error in analyze_financial_query: {error_msg}")
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'traceback': traceback.format_exc()
        }), 500


@financial_bp.route('/api/regional-summary', methods=['GET'])
def get_regional_summary():
    """Get financial summary by region"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        summary = financial_dal.get_regional_summary(start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@financial_bp.route('/api/product-performance', methods=['GET'])
def get_product_performance():
    """Get top performing products"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        performance = financial_dal.get_product_performance(limit)
        
        return jsonify({
            'success': True,
            'data': performance
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@financial_bp.route('/api/time-series', methods=['GET'])
def get_time_series():
    """Get time series data"""
    try:
        metric = request.args.get('metric', 'revenue')
        granularity = request.args.get('granularity', 'month')
        
        data = financial_dal.get_time_series_data(metric, granularity)
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@financial_bp.route('/api/analysis-history', methods=['GET'])
def get_analysis_history():
    """Get recent analysis queries"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        history = financial_dal.get_analysis_history(limit)
        
        return jsonify({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
