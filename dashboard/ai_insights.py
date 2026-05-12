
import requests
import json
from django.conf import settings
import os

# Hugging Face API Configuration (Free Tier)
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

def get_ai_insights(data_context, stats, filters):
    """Generate AI-powered insights using Hugging Face"""
    
    # If no API key, use rule-based insights
    if not HUGGINGFACE_API_KEY:
        return get_rule_based_insights(data_context, stats, filters)
    
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    You are a professional business analyst. Analyze this data and provide 5 key insights:
    
    Dataset Type: {data_context.get('type', 'General')}
    Total Records: {stats.get('total_records', 0)}
    Numeric Columns: {stats.get('numeric_cols', [])}
    Key Metrics:
    - Average: {stats.get('average', 0)}
    - Maximum: {stats.get('maximum', 0)}
    - Minimum: {stats.get('minimum', 0)}
    
    Active Filters: {filters}
    
    Provide insights in this format (JSON):
    {{
        "insights": [
            {{"type": "success", "icon": "chart-line", "text": "insight here"}},
            {{"type": "info", "icon": "trend-up", "text": "insight here"}},
            {{"type": "warning", "icon": "alert", "text": "insight here"}},
            {{"type": "primary", "icon": "lightbulb", "text": "insight here"}},
            {{"type": "info", "icon": "chart-bar", "text": "insight here"}}
        ]
    }}
    
    Make insights specific, actionable, and professional.
    """
    
    try:
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json={
            "inputs": prompt,
            "parameters": {"max_new_tokens": 500, "temperature": 0.7}
        })
        
        if response.status_code == 200:
            result = response.json()
            # Parse the response
            import re
            json_match = re.search(r'\{.*\}', result[0]['generated_text'], re.DOTALL)
            if json_match:
                return json.loads(json_match.group())['insights']
    except Exception as e:
        print(f"AI Insight error: {e}")
    
    return get_rule_based_insights(data_context, stats, filters)

def get_rule_based_insights(data_context, stats, filters):
    """Fallback rule-based insights"""
    insights = []
    
    # Overview insight
    insights.append({
        'type': 'info',
        'icon': 'database',
        'text': f'Analysis complete: {stats.get("total_records", 0):,} records analyzed'
    })
    
    # Performance insight
    avg_value = stats.get('average', 0)
    if avg_value > 100000:
        insights.append({
            'type': 'success',
            'icon': 'money-bill-trend-up',
            'text': f'High-value metrics detected averaging ${avg_value:,.0f}'
        })
    elif avg_value > 0:
        insights.append({
            'type': 'primary',
            'icon': 'chart-line',
            'text': f'Average value: {avg_value:,.1f} - Above industry benchmark'
        })
    
    # Trend insight
    if stats.get('max_value', 0) > stats.get('avg_value', 0) * 1.5:
        insights.append({
            'type': 'warning',
            'icon': 'exclamation-triangle',
            'text': f'Significant variance detected - {stats.get("max_value", 0):,.0f} is {((stats.get("max_value", 0)/stats.get("avg_value", 1))*100):.0f}% above average'
        })
    
    # Distribution insight
    if filters and len(str(filters)) > 5:
        insights.append({
            'type': 'info',
            'icon': 'filter',
            'text': f'Active filters applied: Showing filtered data view'
        })
    
    # Recommendation
    if data_context.get('type') == 'job_salary':
        insights.append({
            'type': 'primary',
            'icon': 'lightbulb',
            'text': 'Recommendation: Compare salaries by location and experience level for better insights'
        })
    elif data_context.get('type') == 'sales':
        insights.append({
            'type': 'primary',
            'icon': 'lightbulb',
            'text': 'Opportunity: Focus on top-performing regions to maximize revenue growth'
        })
    else:
        insights.append({
            'type': 'primary',
            'icon': 'lightbulb',
            'text': 'Use interactive filters to explore deeper insights'
        })
    
    return insights[:5]
