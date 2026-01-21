import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class DeepSeekService:
    def __init__(self):
        self.api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        self.base_url = "https://api.deepseek.com/v1" # Or the specific DeepSeek endpoint
        self.model = "deepseek-chat" # Default DeepSeek model

        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY not correctly configured in settings. DeepSeek AI will not be available.")
            self.enabled = False
        else:
            self.enabled = True

    def generate_suggestions(self, patient_data):
        if not self.enabled:
            return []

        prompt = self._build_prompt(patient_data)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a clinical AI assistant specialized in hypertension management. Always return suggestions in the requested JSON format."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
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
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                # Raise an exception so the view can handle the specific status code
                error_msg = f"DeepSeek API Error: {response.status_code}"
                if response.status_code == 402:
                    error_msg = "Insufficient Balance in DeepSeek account."
                raise Exception(error_msg)

            result = response.json()
            content = result['choices'][0]['message']['content']
            return self._parse_response(content)
            
        except Exception as e:
            logger.error(f"Error generating suggestions from DeepSeek: {e}")
            raise  # Re-raise to be caught by the view

    def _build_prompt(self, data):
        """
        Builds a clinical prompt for DeepSeek based on patient data.
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
        Each object should have:
        - "rule_id": A unique identifier (e.g., "AI_D_001")
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
        Parses the JSON response from DeepSeek.
        """
        try:
            data = json.loads(response_text)
            # Support both a direct list or a wrapped object
            if isinstance(data, dict) and "ai_suggestions" in data:
                return data["ai_suggestions"]
            elif isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse DeepSeek response as JSON: {e}. Raw response: {response_text}")
            return []
