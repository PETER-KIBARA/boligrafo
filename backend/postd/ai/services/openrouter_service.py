import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class OpenRouterService:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "liquid/lfm-2.5-1.2b-instruct:free"
        
        self.site_url = "https://boligrafo.app" # Optional: Site URL for OpenRouter rankings
        self.app_name = "Boligrafo" # Optional: App Name for OpenRouter rankings

        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not correctly configured in settings. OpenRouter AI will not be available.")
            self.enabled = False
        else:
            self.enabled = True

    def generate_population_insights(self, population_data):
        if not self.enabled:
            return []

        prompt = f"""
        Analyze the following population-level clinical data for hypertension management and provide 3-5 high-level insights.
        
        Population Data:
        - Total Patients: {population_data.get('total_patients')}
        - Population Averages: Systolic {population_data.get('avg_systolic')}, Diastolic {population_data.get('avg_diastolic')}, Heart Rate {population_data.get('avg_heartrate')}
        - Uncontrolled BP Count (>140/90): {population_data.get('uncontrolled_count')}
        - Recent Trends: {json.dumps(population_data.get('trends', []), indent=2)}

        Please provide your insights in a structured JSON format with:
        1. "insights": A list of strings (clinical observations).
        2. "actions": A list of objects with:
           - "title": Action title
           - "description": Action description
           - "urgency": "low", "medium", or "high"

        Only return the JSON object.
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.app_name,
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a clinical AI analyst for a healthcare dashboard. Return insights in JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return self._get_fallback_population_insights(population_data)

            result = response.json()
            content = result['choices'][0]['message']['content']
            return self._parse_population_response(content, population_data)
            
        except Exception as e:
            logger.error(f"Error generating population insights: {e}")
            return self._get_fallback_population_insights(population_data)

    def _parse_population_response(self, text, data):
        try:
            clean_text = text.strip()
            if clean_text.startswith("```json"): clean_text = clean_text[7:]
            if clean_text.endswith("```"): clean_text = clean_text[:-3]
            res = json.loads(clean_text.strip())
            return res
        except:
            return self._get_fallback_population_insights(data)

    def _get_fallback_population_insights(self, data):
        # Basic rule-based fallback
        insights = []
        actions = []
        avg_sys = data.get('avg_systolic', 0)
        uncontrolled = data.get('uncontrolled_count', 0)
        
        if avg_sys and avg_sys > 135:
            insights.append(f"Average population BP ({avg_sys}) is above target levels.")
            actions.append({"title": "Review High-Risk Patients", "description": "Prioritize follow-ups for patients above 140/90.", "urgency": "high"})
        
        if uncontrolled > (data.get('total_patients', 0) / 2):
            insights.append("Over 50% of patients have uncontrolled blood pressure.")
            
        if not insights:
            insights.append("Clinical data is within normal variations for the current population.")
            actions.append({"title": "Routine Monitoring", "description": "Maintain current monitoring schedules.", "urgency": "low"})
            
        return {"insights": insights, "actions": actions}

    def generate_suggestions(self, patient_data):
        if not self.enabled:
            return []

        prompt = self._build_prompt(patient_data)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.app_name,
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a clinical AI assistant specialized in hypertension management. Always return suggestions in JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                # Raise an exception so the view can handle the specific status code
                error_msg = f"OpenRouter API Error: {response.status_code}"
                if response.status_code == 401:
                    error_msg = "OpenRouter Unauthorized: Invalid API Key or User not found."
                elif response.status_code == 402:
                    error_msg = "Insufficient Balance in OpenRouter account."
                raise Exception(error_msg)

            result = response.json()
            content = result['choices'][0]['message']['content']
            return self._parse_response(content)
            
        except Exception as e:
            logger.error(f"Error generating suggestions from OpenRouter: {e}")
            raise  # Re-raise to be caught by the view

    def _build_prompt(self, data):
        """
        Builds a clinical prompt based on patient data.
        """
        prompt = f"""
        Analyze the following patient data and provide actionable health insights and suggestions for hypertension management.

        Patient ID: {data.get('patient_id')}
        As of: {data.get('as_of')}

        Vital Readings (Last 30 days):
        {json.dumps(data.get('vitals', []), indent=2)}

        Active Prescriptions:
        {json.dumps(data.get('prescriptions', []), indent=2)}

        Recent Treatments:
        {json.dumps(data.get('treatments', []), indent=2)}

        Appointments:
        {json.dumps(data.get('appointments', []), indent=2)}

        Please provide your suggestions in a structured JSON format with a key "ai_suggestions" containing a list of objects.
        
        CRITICAL ANALYSIS RULE:
        - If a patient has been on the SAME medication for > 60 days (check 'started_at' and 'active' status) AND their recent BP readings (last 3-5 entries) are consistently above 140/90, you MUST include a suggestion for the clinician to "Consider Titrating or Changing Medication".
        - Mention that the current regimen has not achieved target BP goals despite 8+ weeks of therapy.

        Each object should have:
        - "rule_id": A unique identifier (e.g., "AI_OR_001", "MED_STAGNATION_001")
        - "message": A clear, concise clinical suggestion or observation.
        - "evidence": A brief explanation of the data points that led to this suggestion.
        - "severity": "low", "medium", or "high". 
        - "confidence": A float between 0.0 and 1.0.
        - "rationale": A brief clinical reasoning for this suggestion.

        Only return the JSON object.
        """
        return prompt

    def _parse_response(self, response_text):
        """
        Parses the JSON response from OpenRouter.
        """
        try:
            # Clean up the response text if it contains markdown code blocks
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            data = json.loads(clean_text)
            # Support both a direct list or a wrapped object
            if isinstance(data, dict) and "ai_suggestions" in data:
                return data["ai_suggestions"]
            elif isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenRouter response as JSON: {e}. Raw response: {response_text}")
            return []
