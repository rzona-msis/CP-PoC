"""
AI Chatbot Controller

Handles chatbot API endpoints for the Resource Concierge.
"""

from flask import Blueprint, request, jsonify, render_template, session
from flask_login import login_required, current_user
from src.services.ai_concierge import get_concierge

ai_chatbot_bp = Blueprint('ai_chatbot', __name__)


@ai_chatbot_bp.route('/chat', methods=['GET'])
def chat_interface():
    """
    Render the chatbot interface page.
    """
    return render_template('ai/chat.html')


@ai_chatbot_bp.route('/api/chat', methods=['POST'])
def chat_api():
    """
    API endpoint for chatbot interactions.
    
    Accepts JSON: {
        "message": "user message",
        "conversation_history": [...]  # optional
    }
    
    Returns JSON: {
        "response": "AI response",
        "resources": [...],
        "suggestions": [...],
        "model": "gpt-3.5-turbo" or "fallback"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get conversation history from request or session
        conversation_history = data.get('conversation_history', [])
        
        # Get user ID if authenticated
        user_id = current_user.user_id if current_user.is_authenticated else None
        
        # Get AI concierge instance
        concierge = get_concierge()
        
        # Process message
        result = concierge.chat(
            user_message=user_message,
            user_id=user_id,
            conversation_history=conversation_history
        )
        
        # Add metadata
        result['model'] = 'google-gemini' if concierge.__class__.__name__ == 'ResourceConcierge' else 'keyword-fallback'
        result['timestamp'] = __import__('datetime').datetime.now().isoformat()
        
        # Store in session for context (last 10 messages)
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        session['chat_history'].append({
            'role': 'user',
            'content': user_message
        })
        session['chat_history'].append({
            'role': 'assistant',
            'content': result['response']
        })
        
        # Keep only last 10 messages
        session['chat_history'] = session['chat_history'][-10:]
        session.modified = True
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': 'An error occurred processing your request',
            'details': str(e)
        }), 500


@ai_chatbot_bp.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get conversation history from session."""
    history = session.get('chat_history', [])
    return jsonify({'history': history}), 200


@ai_chatbot_bp.route('/api/chat/clear', methods=['POST'])
def clear_chat_history():
    """Clear conversation history."""
    session['chat_history'] = []
    session.modified = True
    return jsonify({'message': 'Chat history cleared'}), 200


@ai_chatbot_bp.route('/api/chat/status', methods=['GET'])
def chat_status():
    """
    Check if AI features are available.
    
    Returns:
        JSON with status information
    """
    concierge = get_concierge()
    
    return jsonify({
        'enabled': concierge.is_enabled(),
        'model': 'Google Gemini' if concierge.__class__.__name__ == 'ResourceConcierge' else 'Keyword Matching',
        'features': {
            'natural_language': concierge.__class__.__name__ == 'ResourceConcierge',
            'context_aware': concierge.__class__.__name__ == 'ResourceConcierge',
            'conversation_memory': True
        }
    }), 200

