"""
AI Resource Concierge Service

Provides natural language interface for resource discovery and booking assistance.
Uses Google Gemini API for conversational AI capabilities.
"""

import os
import json
from datetime import datetime, timedelta
from src.data_access.resource_dal import ResourceDAL
from src.data_access.booking_dal import BookingDAL

# Import Google Gemini (will be installed separately)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class ResourceConcierge:
    """
    AI-powered assistant for campus resource discovery and booking.
    Uses Google Gemini API for natural language processing.
    """
    
    def __init__(self):
        """Initialize the AI concierge with Gemini API credentials."""
        self.api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        # Use latest stable model - gemini-pro works with newer SDK (0.8+)
        self.model_name = os.environ.get('GEMINI_MODEL', 'gemini-pro')
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                
                # List available models and use the first one that supports generateContent
                try:
                    available_models = genai.list_models()
                    model_initialized = False
                    
                    # Try to find a model that supports generateContent
                    # Prefer stable models over experimental ones (avoid -exp, -preview)
                    stable_models = []
                    other_models = []
                    
                    for model in available_models:
                        if 'generateContent' in model.supported_generation_methods:
                            model_name = model.name
                            # Skip experimental models (they have no free tier quota)
                            if '-exp' in model_name or 'experimental' in model_name.lower():
                                continue
                            # Prefer stable models (no -preview)
                            if '-preview' not in model_name:
                                stable_models.append(model)
                            else:
                                other_models.append(model)
                    
                    # Try stable models first
                    for model in stable_models:
                        try:
                            self.model = genai.GenerativeModel(model.name)
                            print(f"✓ Using Google Gemini AI ({model.name})")
                            self.model_name = model.name
                            model_initialized = True
                            break
                        except Exception as e:
                            continue
                    
                    # If no stable model works, try preview models
                    if not model_initialized:
                        for model in other_models[:3]:  # Limit to first 3 preview models
                            try:
                                self.model = genai.GenerativeModel(model.name)
                                print(f"✓ Using Google Gemini AI ({model.name})")
                                self.model_name = model.name
                                model_initialized = True
                                break
                            except Exception as e:
                                continue
                    
                    if not model_initialized:
                        # Fallback: try stable model names that actually exist
                        models_to_try = [
                            'models/gemini-2.5-flash',  # Fast, stable
                            'models/gemini-2.5-pro',    # More capable
                            'models/gemini-flash-latest', # Latest flash
                            'models/gemini-pro-latest',  # Latest pro
                        ]
                        for model_name in models_to_try:
                            try:
                                self.model = genai.GenerativeModel(model_name)
                                print(f"✓ Using Google Gemini AI ({model_name})")
                                self.model_name = model_name
                                model_initialized = True
                                break
                            except Exception as e:
                                print(f"  Trying {model_name}... failed")
                                continue
                    
                    if not model_initialized:
                        print("❌ Failed to initialize any Gemini model")
                        self.model = None
                        self.enabled = False
                        return
                        
                except Exception as e:
                    print(f"Error listing models: {e}")
                    # Fallback to known working models
                    models_to_try = [
                        'models/gemini-2.5-flash',
                        'models/gemini-2.5-pro',
                        'models/gemini-flash-latest',
                    ]
                    model_initialized = False
                    for model_name in models_to_try:
                        try:
                            self.model = genai.GenerativeModel(model_name)
                            print(f"✓ Using Google Gemini AI ({model_name} - fallback)")
                            self.model_name = model_name
                            model_initialized = True
                            break
                        except:
                            continue
                    
                    if not model_initialized:
                        print(f"❌ Failed to initialize Gemini: {e}")
                        self.model = None
                        self.enabled = False
                        return
                self.enabled = True
            except Exception as e:
                print(f"Failed to configure Gemini: {e}")
                import traceback
                traceback.print_exc()
                self.model = None
                self.enabled = False
        else:
            self.model = None
            self.enabled = False
    
    def is_enabled(self):
        """Check if AI features are available."""
        return self.enabled
    
    def chat(self, user_message, user_id=None, conversation_history=None):
        """
        Process user message and generate AI response using Gemini.
        
        Args:
            user_message (str): User's input message
            user_id (int, optional): Current user ID for personalization
            conversation_history (list, optional): Previous messages in conversation
            
        Returns:
            dict: {
                'response': str,
                'resources': list,
                'suggestions': list,
                'error': str (if any)
            }
        """
        if not self.enabled:
            return {
                'response': "AI features are not available. Please set GEMINI_API_KEY environment variable.",
                'resources': [],
                'suggestions': [],
                'error': 'API key not configured'
            }
        
        try:
            # Get context about available resources
            context = self._get_resource_context()
            
            # Build system prompt with resource context
            system_prompt = self._build_system_prompt(context)
            
            # Build full prompt with conversation history
            full_prompt = system_prompt + "\n\n"
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages
                    role = "User" if msg['role'] == 'user' else "Assistant"
                    full_prompt += f"{role}: {msg['content']}\n\n"
            
            # Add current user message
            full_prompt += f"User: {user_message}\n\nAssistant:"
            
            # Call Gemini API
            response = self.model.generate_content(full_prompt)
            ai_response = response.text
            
            # Extract resource recommendations from response
            resources = self._extract_resource_references(ai_response, user_message)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(user_message, resources)
            
            return {
                'response': ai_response,
                'resources': resources,
                'suggestions': suggestions,
                'error': None
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"Gemini API error: {error_msg}")
            import traceback
            traceback.print_exc()
            
            # Provide more helpful error message
            if "404" in error_msg or "not found" in error_msg.lower():
                error_response = "The AI model is temporarily unavailable. Please try again in a moment."
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                error_response = "AI service quota exceeded. Please try again later."
            elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
                error_response = "AI service authentication error. Please contact support."
            else:
                error_response = "I apologize, but I'm having trouble processing your request right now. Please try again."
            
            return {
                'response': error_response,
                'resources': [],
                'suggestions': [],
                'error': error_msg
            }
    
    def _build_system_prompt(self, context):
        """Build system prompt with resource context for Gemini."""
        return f"""You are a helpful campus resource assistant for a university resource booking system.

Your role is to help students and staff find and book campus resources like study rooms, equipment, lab spaces, and event venues.

AVAILABLE RESOURCES:
{context['resources_summary']}

GUIDELINES:
1. Be friendly, concise, and helpful
2. Only recommend resources that actually exist (from the list above)
3. Ask clarifying questions if the request is vague
4. Mention important details like location, capacity, and booking requirements
5. If you recommend a resource, include its ID in your response like [Resource #ID]
6. Be honest if you don't have information about something
7. Keep responses concise (2-3 paragraphs maximum)

CURRENT DATE: {datetime.now().strftime('%Y-%m-%d')}

Remember: You can only recommend resources from the available list. Never invent resources that don't exist.

---

CONVERSATION:
"""
    
    def _get_resource_context(self):
        """Get current resource availability context."""
        try:
            # Get all published resources
            resources = ResourceDAL.search_resources(status='published')
            
            # Build summary of available resources
            resources_by_category = {}
            for resource in resources[:30]:  # Limit to prevent token overflow
                category = resource['category'] or 'Other'
                if category not in resources_by_category:
                    resources_by_category[category] = []
                
                resources_by_category[category].append({
                    'id': resource['resource_id'],
                    'title': resource['title'],
                    'location': resource['location'],
                    'capacity': resource['capacity'],
                    'rating': round(resource['avg_rating'] or 0, 1)
                })
            
            # Format as text summary
            summary_lines = []
            for category, items in resources_by_category.items():
                summary_lines.append(f"\n{category}:")
                for item in items:
                    summary_lines.append(
                        f"  - [#{item['id']}] {item['title']} - "
                        f"{item['location']} - "
                        f"Capacity: {item['capacity'] or 'N/A'} - "
                        f"Rating: {item['rating']}⭐"
                    )
            
            resources_summary = '\n'.join(summary_lines) if summary_lines else "No resources currently available."
            
            return {
                'resources_summary': resources_summary,
                'total_resources': len(resources)
            }
            
        except Exception as e:
            print(f"Error getting resource context: {e}")
            return {
                'resources_summary': "Unable to load resource information.",
                'total_resources': 0
            }
    
    def _extract_resource_references(self, ai_response, user_message):
        """
        Extract resource IDs mentioned in AI response and fetch details.
        
        Returns list of resource dictionaries.
        """
        import re
        
        # Find resource IDs in format [#123] or [Resource #123]
        pattern = r'\[(?:Resource\s*)?#(\d+)\]'
        matches = re.findall(pattern, ai_response)
        
        resources = []
        for resource_id in matches:
            try:
                resource = ResourceDAL.get_resource_by_id(int(resource_id))
                if resource:
                    # Handle sqlite3.Row which doesn't have .get() method
                    try:
                        rating = resource['avg_rating'] if 'avg_rating' in resource.keys() else 0
                    except:
                        rating = 0
                    
                    resources.append({
                        'resource_id': resource['resource_id'],
                        'title': resource['title'],
                        'description': resource['description'],
                        'category': resource['category'],
                        'location': resource['location'],
                        'capacity': resource['capacity'],
                        'rating': rating
                    })
            except Exception as e:
                print(f"Error fetching resource {resource_id}: {e}")
                continue
        
        return resources
    
    def _generate_suggestions(self, user_message, recommended_resources):
        """Generate helpful suggestions based on user query."""
        suggestions = []
        
        # Keywords to suggest specific actions
        if any(word in user_message.lower() for word in ['book', 'reserve', 'schedule']):
            suggestions.append({
                'text': 'Ready to book? Click on a resource to see availability',
                'action': 'book'
            })
        
        if 'study' in user_message.lower() or 'quiet' in user_message.lower():
            suggestions.append({
                'text': 'Looking for study spaces? Try filtering by "Study Room"',
                'action': 'filter_category',
                'category': 'Study Room'
            })
        
        if any(word in user_message.lower() for word in ['equipment', 'camera', 'projector']):
            suggestions.append({
                'text': 'Need equipment? Check out our Equipment category',
                'action': 'filter_category',
                'category': 'Equipment'
            })
        
        if recommended_resources:
            suggestions.append({
                'text': f'View {len(recommended_resources)} recommended resource(s)',
                'action': 'show_resources'
            })
        
        return suggestions[:3]  # Limit to 3 suggestions


class FallbackConcierge:
    """
    Simple rule-based fallback when Gemini API is not available.
    Provides keyword-based resource recommendations.
    """
    
    def chat(self, user_message, user_id=None, conversation_history=None):
        """Process message using keyword matching."""
        user_message_lower = user_message.lower()
        
        # Extract keywords
        keywords = []
        category = None
        
        if any(word in user_message_lower for word in ['study', 'quiet', 'library']):
            keywords.append('study')
            category = 'Study Room'
        
        if any(word in user_message_lower for word in ['meeting', 'conference', 'group']):
            keywords.append('meeting')
            category = 'Meeting Room'
        
        if any(word in user_message_lower for word in ['equipment', 'camera', 'projector', 'video']):
            keywords.append('equipment')
            category = 'Equipment'
        
        if any(word in user_message_lower for word in ['lab', 'laboratory', 'science']):
            keywords.append('lab')
            category = 'Lab Space'
        
        # Search for resources
        resources = []
        try:
            if category:
                results = ResourceDAL.search_resources(category=category, status='published')
                resources = results[:5]  # Top 5
            else:
                # General search with keywords
                keyword = ' '.join(keywords) if keywords else None
                results = ResourceDAL.search_resources(keyword=keyword, status='published')
                resources = results[:5]
        except Exception as e:
            print(f"Error searching resources: {e}")
        
        # Build response
        if resources:
            response = f"I found {len(resources)} resources that might help:\n\n"
            resource_list = []
            for r in resources:
                rating = f" - Rating: {r.get('avg_rating', 0):.1f}⭐" if r.get('avg_rating') else ""
                resource_list.append({
                    'resource_id': r['resource_id'],
                    'title': r['title'],
                    'description': r['description'],
                    'category': r['category'],
                    'location': r['location'],
                    'capacity': r['capacity']
                })
                response += f"• {r['title']} ({r['location']}){rating}\n"
            
            response += "\nClick on any resource to view details and book!"
            
            return {
                'response': response,
                'resources': resource_list,
                'suggestions': [{'text': 'View resource details', 'action': 'show_resources'}],
                'error': None
            }
        else:
            return {
                'response': "I couldn't find specific resources matching your request. Try browsing all resources or search by category!",
                'resources': [],
                'suggestions': [
                    {'text': 'Browse all resources', 'action': 'browse'},
                    {'text': 'Search by category', 'action': 'categories'}
                ],
                'error': None
            }
    
    def is_enabled(self):
        """Fallback is always enabled."""
        return True


# Factory function to get appropriate concierge
def get_concierge():
    """
    Get AI concierge instance (Gemini or fallback).
    
    Returns:
        ResourceConcierge or FallbackConcierge
    """
    concierge = ResourceConcierge()
    if concierge.is_enabled():
        # Message already printed in __init__
        return concierge
    else:
        print("⚠ Using keyword-based fallback (Gemini not available)")
        return FallbackConcierge()
