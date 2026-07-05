"""
Core chatbot engine module
Implements the NLU (Natural Language Understanding) and response generation logic
"""

import random
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass

from config import config
from logger import logger, chat_logger
from intents import intents_registry, Intent


@dataclass
class MatchResult:
    """
    Represents the result of intent matching

    Attributes:
        intent: Matched intent object
        response: Generated response
        confidence: Confidence score (0.0-1.0)
        match_type: Type of match ('exact', 'keyword', 'fallback')
    """

    intent: Optional[Intent]
    response: str
    confidence: float
    match_type: str


class ChatbotEngine:
    """
    Core chatbot engine implementing intent matching and response generation
    Follows a clean, testable architecture with clear separation of concerns
    """

    def __init__(self):
        self.intents_registry = intents_registry
        self._response_cache: Dict[str, str] = {}
        logger.info(f"ChatbotEngine initialized with {self.intents_registry.get_intent_count()} intents")

    def process_input(self, user_input: str) -> MatchResult:
        """
        Process user input and generate appropriate response

        Args:
            user_input: Raw user input text

        Returns:
            MatchResult containing intent, response, confidence, and match type
        """
        # Validate input
        if not user_input or not user_input.strip():
            logger.warning("Received empty user input")
            return MatchResult(
                intent=None,
                response=config.EMPTY_INPUT_MESSAGE,
                confidence=0.0,
                match_type="empty_input",
            )

        # Sanitize input
        sanitized_input = user_input.lower().strip()
        logger.debug(f"Processing input: {sanitized_input}")

        # Try exact match first (highest confidence)
        result = self._try_exact_match(sanitized_input)
        if result.confidence > config.CONFIDENCE_THRESHOLD:
            return result

        # Try keyword match (medium confidence)
        result = self._try_keyword_match(sanitized_input)
        if result.confidence > config.CONFIDENCE_THRESHOLD:
            return result

        # Fallback with intelligent suggestions
        result = self._generate_fallback(sanitized_input)
        return result

    def _try_exact_match(self, user_input: str) -> MatchResult:
        """
        Try to match user input exactly against intent patterns

        Args:
            user_input: Sanitized user input

        Returns:
            MatchResult with exact match attempt
        """
        for intent in self.intents_registry.list_all_intents().values():
            if user_input in intent.exact_matches:
                response = random.choice(intent.responses)
                logger.debug(f"Exact match found: {intent.name}")
                return MatchResult(
                    intent=intent,
                    response=response,
                    confidence=1.0,
                    match_type="exact",
                )

        return MatchResult(
            intent=None,
            response="",
            confidence=0.0,
            match_type="no_match",
        )

    def _try_keyword_match(self, user_input: str) -> MatchResult:
        """
        Try to match user input using keyword patterns

        Args:
            user_input: Sanitized user input

        Returns:
            MatchResult with keyword match attempt
        """
        best_match = None
        best_confidence = 0.0

        for intent in self.intents_registry.list_all_intents().values():
            for keyword in intent.keyword_matches:
                if keyword in user_input:
                    # Calculate confidence based on keyword length
                    # Longer keywords = more specific = higher confidence
                    confidence = min(0.5 + (len(keyword) / 100), 0.95)

                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = intent
                        break

        if best_match and best_confidence >= config.CONFIDENCE_THRESHOLD:
            response = random.choice(best_match.responses)
            logger.debug(f"Keyword match found: {best_match.name} (confidence: {best_confidence:.2f})")
            return MatchResult(
                intent=best_match,
                response=response,
                confidence=best_confidence,
                match_type="keyword",
            )

        return MatchResult(
            intent=None,
            response="",
            confidence=0.0,
            match_type="no_match",
        )

    def _generate_fallback(self, user_input: str) -> MatchResult:
        """
        Generate intelligent fallback response when no match is found

        Args:
            user_input: Sanitized user input

        Returns:
            MatchResult with fallback response
        """
        logger.debug(f"No intent matched. Generating fallback response.")
        fallback_response = self._create_intelligent_fallback(user_input)

        return MatchResult(
            intent=None,
            response=fallback_response,
            confidence=0.0,
            match_type="fallback",
        )

    def _create_intelligent_fallback(self, user_input: str) -> str:
        """
        Create context-aware fallback response

        Args:
            user_input: Sanitized user input

        Returns:
            Intelligent fallback message
        """
        words = user_input.split()

        if len(words) == 1:
            return (
                f"I'm not sure what you mean by '{user_input}'. "
                "Type 'help' to see what I can do. 🤔"
            )
        elif len(words) <= 3:
            return (
                "Interesting question! I don't have an answer for that yet. "
                "Try asking about AI, DecodeLabs, or the project. 💡"
            )
        else:
            return (
                "That's a complex question! I'm still learning. "
                "Try simpler questions or type 'help'. 📚"
            )

    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get information about the engine

        Returns:
            Dictionary with engine information
        """
        return {
            "total_intents": self.intents_registry.get_intent_count(),
            "confidence_threshold": config.CONFIDENCE_THRESHOLD,
            "cache_enabled": config.CACHE_ENABLED,
            "logging_enabled": config.ENABLE_LOGGING,
        }