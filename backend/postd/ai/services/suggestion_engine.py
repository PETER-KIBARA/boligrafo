from .openrouter_service import OpenRouterService
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class SuggestionEngine:
    """
    Suggestion engine that exclusively uses OpenRouter AI.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.ai_service = OpenRouterService()

    def evaluate(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluates the patient profile using OpenRouter AI.
        """
        try:
            if not self.ai_service.enabled:
                logger.warning("OpenRouterService is not enabled.")
                return []

            logger.info("Attempting suggestions with OpenRouterService...")
            return self.ai_service.generate_suggestions(profile)
        
        except Exception as e:
            logger.error(f"OpenRouterService failed: {str(e)}")
            raise