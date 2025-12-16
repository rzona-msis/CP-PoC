"""
LLM API wrapper service for TMHNA Financial AI Assistant.

This module provides a unified interface for calling LLM APIs (OpenAI, Anthropic, etc.)
for financial analysis and master data matching tasks.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional

# Try importing available LLM libraries
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LLMService:
    """Wrapper service for LLM API calls"""
    
    def __init__(self):
        """Initialize LLM service with API credentials from environment"""
        self.provider = os.environ.get('LLM_PROVIDER', 'openai').lower()
        self.model = os.environ.get('LLM_MODEL', 'gpt-4')
        self.api_key = None
        self.client = None
        
        # Initialize based on provider
        if self.provider == 'openai':
            self.api_key = os.environ.get('OPENAI_API_KEY')
            if self.api_key and OPENAI_AVAILABLE:
                openai.api_key = self.api_key
                self.client = openai
            else:
                print("Warning: OpenAI API key not found or library not installed")
        
        elif self.provider == 'anthropic':
            self.api_key = os.environ.get('ANTHROPIC_API_KEY')
            if self.api_key and ANTHROPIC_AVAILABLE:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            else:
                print("Warning: Anthropic API key not found or library not installed")
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 2
    
    def _call_openai(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Call OpenAI API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise Exception(f"OpenAI API error after {self.max_retries} attempts: {str(e)}")
    
    def _call_anthropic(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Call Anthropic API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                # Convert messages format for Anthropic
                system_msg = next((m['content'] for m in messages if m['role'] == 'system'), '')
                user_messages = [m for m in messages if m['role'] != 'system']
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_msg,
                    messages=user_messages
                )
                return response.content[0].text
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise Exception(f"Anthropic API error after {self.max_retries} attempts: {str(e)}")
    
    def _call_llm(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generic LLM call that routes to the configured provider"""
        if not self.client or not self.api_key:
            # Fallback for demo/testing without API
            return self._generate_mock_response(messages)
        
        if self.provider == 'openai':
            return self._call_openai(messages, temperature, max_tokens)
        elif self.provider == 'anthropic':
            return self._call_anthropic(messages, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _generate_mock_response(self, messages: List[Dict]) -> str:
        """Generate mock response for testing without API key"""
        user_message = next((m['content'] for m in messages if m['role'] == 'user'), '')
        
        if 'SQL' in user_message or 'query' in user_message.lower():
            return """SELECT 
    r.region_name,
    SUM(ft.revenue) as total_revenue,
    SUM(ft.cost) as total_cost,
    SUM(ft.margin) as total_margin,
    AVG((ft.margin / ft.revenue) * 100) as margin_percentage
FROM financial_transactions ft
JOIN regions r ON ft.region_id = r.region_id
WHERE strftime('%Y-%m', ft.transaction_date) BETWEEN '2024-04' AND '2024-06'
GROUP BY r.region_name
ORDER BY margin_percentage ASC"""
        
        elif 'confidence' in user_message.lower() or 'duplicate' in user_message.lower():
            return json.dumps({
                "confidence_score": 85,
                "match_reason": "Strong similarity in name, address, and contact information with minor formatting differences",
                "golden_record": {
                    "name": "Acme Corporation",
                    "address": "123 Main Street",
                    "city": "New York",
                    "state": "NY",
                    "postal_code": "10001",
                    "email": "contact@acme.com",
                    "phone": "555-1234"
                }
            })
        
        else:
            return "Mock LLM response: The financial analysis shows interesting trends across regions with notable variations in margin performance during Q2 2024."
    
    def natural_language_to_sql(self, user_query: str) -> str:
        """
        Convert natural language query to SQL
        
        Args:
            user_query: User's natural language question
            
        Returns:
            SQL query string
        """
        schema_context = """
Available tables and columns:

financial_transactions:
  - transaction_id, transaction_date, region_id, product_id, customer_id
  - revenue, cost, margin, quantity, sales_channel

regions:
  - region_id, region_name, region_code, country

products:
  - product_id, product_name, sku, category, unit_cost, source_system

customers:
  - customer_id, customer_name, address, city, state, postal_code, email, phone, source_system

vendors:
  - vendor_id, vendor_name, address, city, state, contact_email, phone, source_system

Notes:
- Margin = revenue - cost
- Date format: YYYY-MM-DD
- Use strftime('%Y-%m', date) for year-month grouping
- Q2 2024 = months 04, 05, 06
- Join tables using appropriate foreign keys
"""
        
        prompt = f"""You are a SQL expert for a financial analysis database using SQLite.

{schema_context}

User question: "{user_query}"

Generate a valid SQLite query to answer this question.
- Return ONLY the SQL query, no explanations or markdown
- Use appropriate JOINs
- Include column aliases for clarity
- Use aggregate functions (SUM, AVG, COUNT) where appropriate
- Order results meaningfully

SQL Query:"""
        
        messages = [
            {"role": "system", "content": "You are a SQL query generator. Return only valid SQL queries without any formatting or explanation."},
            {"role": "user", "content": prompt}
        ]
        
        sql_query = self._call_llm(messages, temperature=0.1, max_tokens=500)
        
        # Clean up the SQL (remove markdown code blocks if present)
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        # Remove any leading/trailing quotes
        if sql_query.startswith('"') and sql_query.endswith('"'):
            sql_query = sql_query[1:-1]
        if sql_query.startswith("'") and sql_query.endswith("'"):
            sql_query = sql_query[1:-1]
        
        return sql_query
    
    def summarize_financial_analysis(
        self, 
        query: str, 
        results: List[Dict], 
        anomalies: List[str],
        sql_query: Optional[str] = None
    ) -> str:
        """
        Generate natural language summary of financial analysis
        
        Args:
            query: Original user query
            results: Query results (list of dicts)
            anomalies: List of detected anomalies
            sql_query: The SQL query that was executed (optional)
            
        Returns:
            Natural language summary
        """
        # Limit results sample for LLM context
        results_sample = results[:20] if len(results) > 20 else results
        results_json = json.dumps(results_sample, indent=2, default=str)
        
        anomalies_text = "\n".join(f"- {a}" for a in anomalies) if anomalies else "None detected"
        
        result_count_text = f"{len(results)} rows" if len(results) > 1 else "1 row"
        sample_text = f" (showing first 20)" if len(results) > 20 else ""
        
        prompt = f"""You are an expert financial analyst AI assistant for TMHNA (Toyota Material Handling North America).

User asked: "{query}"

The query returned {result_count_text}{sample_text}:
{results_json}

Anomalies detected:
{anomalies_text}

Provide a concise, executive-level analysis summary (2-4 paragraphs) that:
1. Directly answers the user's question with specific numbers and insights
2. Highlights key trends, patterns, or notable findings
3. Explains any anomalies or concerns detected
4. Provides actionable recommendations based on the data

Be specific with numbers, percentages, and comparisons. Use clear business language.
Focus on insights that would matter to TMHNA executives making strategic decisions."""
        
        messages = [
            {"role": "system", "content": "You are a senior financial analyst providing executive briefings. Be concise, data-driven, and actionable."},
            {"role": "user", "content": prompt}
        ]
        
        summary = self._call_llm(messages, temperature=0.7, max_tokens=1000)
        return summary
    
    def score_duplicate_match(
        self, 
        entity_a: Dict, 
        entity_b: Dict, 
        entity_type: str
    ) -> Dict[str, Any]:
        """
        Use LLM to score duplicate match confidence and suggest golden record
        
        Args:
            entity_a: First entity dict
            entity_b: Second entity dict
            entity_type: 'customer', 'vendor', or 'product'
            
        Returns:
            Dict with confidence_score, match_reason, and golden_record
        """
        entity_a_json = json.dumps(entity_a, indent=2, default=str)
        entity_b_json = json.dumps(entity_b, indent=2, default=str)
        
        prompt = f"""You are a master data quality expert analyzing potential duplicate {entity_type} records from different systems (SAP, Oracle, Legacy).

Entity A:
{entity_a_json}

Entity B:
{entity_b_json}

Analyze these records and provide a JSON response with:

1. "confidence_score": A number from 0-100 indicating likelihood they represent the same {entity_type}
   - 90-100: Definite match (minor formatting differences only)
   - 70-89: Probable match (some field variations but clearly same entity)
   - 50-69: Possible match (significant differences but could be same entity)
   - 0-49: Unlikely match (different entities)

2. "match_reason": Brief explanation (1-2 sentences) of why you assigned this score, citing specific matching or non-matching fields

3. "golden_record": A suggested unified record combining the best values from both entities. Choose the most complete, accurate, and standardized values.

Return ONLY a valid JSON object, no other text or markdown:
{{
  "confidence_score": 85,
  "match_reason": "Strong match based on...",
  "golden_record": {{...}}
}}"""
        
        messages = [
            {"role": "system", "content": "You are a data quality expert. Return only valid JSON objects."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result_text = self._call_llm(messages, temperature=0.3, max_tokens=800)
            
            # Clean up response
            result_text = result_text.strip()
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            # Parse JSON response
            result = json.loads(result_text)
            
            # Validate required fields
            if 'confidence_score' not in result:
                result['confidence_score'] = 50
            if 'match_reason' not in result:
                result['match_reason'] = "Unable to determine match reason"
            if 'golden_record' not in result:
                result['golden_record'] = entity_a
            
            return result
            
        except json.JSONDecodeError as e:
            # Fallback if JSON parsing fails
            print(f"Warning: Failed to parse LLM JSON response: {e}")
            return {
                "confidence_score": 50,
                "match_reason": "Error parsing LLM response",
                "golden_record": entity_a
            }
    
    def explain_variance(self, data: List[Dict], dimension: str) -> str:
        """
        Generate explanation for variance in financial metrics
        
        Args:
            data: Financial data with variance
            dimension: Dimension being analyzed (region, product, time, etc.)
            
        Returns:
            Natural language explanation
        """
        data_json = json.dumps(data[:10], indent=2, default=str)
        
        prompt = f"""Analyze this financial variance data by {dimension}:

{data_json}

Provide a brief explanation (2-3 sentences) of:
1. What's driving the variance
2. Which {dimension}(s) are outliers
3. Potential business implications"""
        
        messages = [
            {"role": "system", "content": "You are a financial variance analyst. Be concise and insightful."},
            {"role": "user", "content": prompt}
        ]
        
        explanation = self._call_llm(messages, temperature=0.7, max_tokens=300)
        return explanation


# Singleton instance
_llm_service_instance = None

def get_llm_service() -> LLMService:
    """Get or create singleton LLM service instance"""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance
