import google.generativeai as genai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        api_key = getattr(settings, 'GOOGLE_API_KEY', None)
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        else:
            self.model = None
            logger.warning("GOOGLE_API_KEY not found in settings. Gemini AI will not be available.")

    def generate_suggestions(self, patient_data):
        if not self.model:
            return []

        prompt = self._build_prompt(patient_data)
        try:
            response = self.model.generate_content(prompt)
            return self._parse_response(response.text)
        except Exception as e:
            logger.error(f"Error generating suggestions from Gemini: {e}")
            return []

    def _build_prompt(self, data):
        """
        Builds a clinical prompt for Gemini based on patient data.
        """
        prompt = f"""
        As a clinical AI assistant, analyze the following patient data and provide actionable health insights and suggestions.
        The patient is being monitored for hypertension.

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

        Please provide your suggestions in a structured JSON format as a list of objects. 
        Each object should have:
        - "rule_id": A unique identifier (e.g., "AI_G_001")
        - "message": A clear, concise clinical suggestion or observation.
        - "evidence": A brief explanation of the data points that led to this suggestion.
        - "severity": "low", "medium", or "high".
        - "confidence": A float between 0.0 and 1.0 representing your confidence in this suggestion.
        - "rationale": A brief clinical reasoning for this suggestion.

        Only return the JSON list, nothing else.
        """
        return prompt

    def _parse_response(self, response_text):
        """
        Parses the JSON response from Gemini.
        """
        try:
            # Clean up the response text if it contains markdown code blocks
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}. Raw response: {response_text}")
            return []
