from .openrouter_service import OpenRouterService
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class SuggestionEngine:
    """
    Suggestion engine that relies entirely on OpenRouter AI.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.ai_service = OpenRouterService()

    def evaluate(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        # This engine relies entirely on OpenRouter AI for suggestions.
        return self.ai_service.generate_suggestions(profile)