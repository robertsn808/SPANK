import json
import os
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

class AILeadGenerator:
    """AI-powered lead analysis and generation for handyman business"""
    
    def analyze_contact_message(self, message):
        """Analyze a contact message for urgency, service type, and lead quality"""
        try:
            prompt = f"""
            Analyze this customer message for a handyman business and provide insights:
            
            Customer: {message.name}
            Email: {message.email}
            Phone: {message.phone}
            Subject: {message.subject}
            Message: {message.message}
            
            Please analyze and return JSON with:
            1. urgency_score (1-10): How urgent is this request?
            2. service_category: What type of handyman service is needed?
            3. lead_quality_score (1-10): How likely is this to convert to a paying customer?
            4. estimated_budget: Rough budget estimate based on the request
            5. recommended_response_time: How quickly should we respond?
            6. key_details: Important details extracted from the message
            7. follow_up_suggestions: Specific actions to take
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert handyman business analyst. Analyze customer inquiries to help prioritize leads and improve response strategies."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content:
                return json.loads(content)
            else:
                return {"error": "Empty AI response"}
            
        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}
    
    def generate_service_recommendations(self, service_request):
        """Generate additional service recommendations based on the initial request"""
        try:
            prompt = f"""
            Based on this handyman service request, suggest additional services the customer might need:
            
            Service: {service_request.service}
            Location: {service_request.location}
            Description: {service_request.description}
            Budget Range: {service_request.budget_range}
            
            Return JSON with:
            1. additional_services: List of related services they might need
            2. upsell_opportunities: Higher-value services to suggest
            3. seasonal_recommendations: Services relevant to current season
            4. maintenance_suggestions: Ongoing maintenance they might need
            5. estimated_project_duration: How long this might take
            6. material_considerations: Important materials or permits needed
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a handyman business expert who helps identify service opportunities and provide accurate project estimates."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content:
                return json.loads(content)
            else:
                return {"error": "Empty AI response"}
            
        except Exception as e:
            return {"error": f"Service recommendation failed: {str(e)}"}
    
    def score_lead_quality(self, lead):
        """Score a lead's conversion potential using AI"""
        try:
            prompt = f"""
            Score this potential handyman customer lead:
            
            Name: {lead.name}
            Email: {lead.email}
            Phone: {lead.phone}
            Source: {lead.source}
            Interest Level: {lead.interest_level}
            Notes: {lead.notes}
            
            Return JSON with:
            1. conversion_score (1-10): Likelihood to become a paying customer
            2. value_potential (low/medium/high): Potential customer lifetime value
            3. contact_priority (immediate/within_24h/within_week): When to contact
            4. recommended_approach: Best way to approach this lead
            5. risk_factors: Any red flags or concerns
            6. strengths: Positive indicators about this lead
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a lead qualification expert for service businesses. Help prioritize leads based on conversion potential."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {"error": f"Lead scoring failed: {str(e)}"}
    
    def generate_follow_up_content(self, lead, interaction_history=None):
        """Generate personalized follow-up messages"""
        try:
            history = interaction_history or "No previous interactions"
            
            prompt = f"""
            Create a personalized follow-up message for this handyman business lead:
            
            Lead: {lead.name}
            Source: {lead.source}
            Interest Level: {lead.interest_level}
            Notes: {lead.notes}
            Previous Interactions: {history}
            
            Generate 3 different follow-up approaches:
            1. email_follow_up: Professional email message
            2. text_message: Casual SMS follow-up
            3. phone_script: Key points for phone conversation
            
            Each should be personalized, value-focused, and appropriate for a handyman business.
            Return as JSON.
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a customer communication expert for service businesses. Create engaging, personalized follow-up content."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {"error": f"Follow-up generation failed: {str(e)}"}

# Initialize the AI service
ai_service = AILeadGenerator()