"""
Intents module for Rule-Based Chatbot
Defines intent patterns and responses using a clean, maintainable structure
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """Enumeration of intent types"""
    GREETING = "greeting"
    FAREWELL = "farewell"
    GRATITUDE = "gratitude"
    HELP = "help"
    PROJECT_INFO = "project_info"
    AI_INFO = "ai_info"
    PERSONAL = "personal"
    TIME_GREETING = "time_greeting"
    MISC = "misc"


@dataclass
class Intent:
    """
    Represents a chatbot intent with patterns and responses

    Attributes:
        name: Intent identifier
        intent_type: Type of intent (from IntentType enum)
        exact_matches: List of exact phrase matches
        keyword_matches: List of keyword patterns
        responses: List of possible responses (randomly selected)
        description: Human-readable description
    """

    name: str
    intent_type: IntentType
    exact_matches: List[str]
    keyword_matches: List[str]
    responses: List[str]
    description: str

    def __post_init__(self):
        """Normalize patterns to lowercase"""
        self.exact_matches = [m.lower() for m in self.exact_matches]
        self.keyword_matches = [k.lower() for k in self.keyword_matches]


class IntentsRegistry:
    """
    Central registry for all intents
    Provides clean interface for intent management and lookup
    """

    def __init__(self):
        self._intents: Dict[str, Intent] = {}
        self._intent_type_index: Dict[IntentType, List[Intent]] = {}
        self._initialize_intents()

    def _initialize_intents(self) -> None:
        """Initialize all predefined intents"""
        intents_list = [
            Intent(
                name="greeting",
                intent_type=IntentType.GREETING,
                exact_matches=["hello", "hi", "hey"],
                keyword_matches=["greet", "sup", "yo"],
                responses=[
                    "Hi there! Welcome to DecodeLabs. 👋",
                    "Hello! How can I assist you today?",
                    "Hey! Great to see you.",
                    "Welcome! What can I help you with?",
                ],
                description="General greeting responses",
            ),
            Intent(
                name="farewell",
                intent_type=IntentType.FAREWELL,
                exact_matches=["bye", "goodbye", "exit"],
                keyword_matches=["see you", "farewell", "catch you"],
                responses=[
                    "Goodbye! Have a great day. 👋",
                    "See you soon! Keep learning.",
                    "Catch you later! Keep growing.",
                    "Bye! Thanks for chatting.",
                ],
                description="Farewell and exit responses",
            ),
            Intent(
                name="gratitude",
                intent_type=IntentType.GRATITUDE,
                exact_matches=["thanks", "thank you", "thx"],
                keyword_matches=["thank", "grateful", "appreciate"],
                responses=[
                    "You're welcome! Happy to help. 😊",
                    "Happy to help!",
                    "Anytime, glad I could assist.",
                    "Thanks for using me!",
                ],
                description="Gratitude and appreciation responses",
            ),
            Intent(
                name="help",
                intent_type=IntentType.HELP,
                exact_matches=["help", "?", "commands"],
                keyword_matches=["help", "assist", "how", "what can"],
                responses=[
                    "I can help with:\n"
                    "  • Greetings (hello, hi)\n"
                    "  • Questions about AI and DecodeLabs\n"
                    "  • Information about Project 1\n"
                    "  • General chat\n"
                    "  • Motivation and tips\n"
                    "Try asking 'What is AI?' or 'Tell me about the project'",
                ],
                description="Help and command information",
            ),
            Intent(
                name="good_morning",
                intent_type=IntentType.TIME_GREETING,
                exact_matches=["good morning"],
                keyword_matches=["morning", "wake up"],
                responses=[
                    "Good morning! ☀️ Ready to learn some AI?",
                    "Morning! Let's make today productive.",
                    "Good morning! Time to code and create.",
                ],
                description="Morning greeting responses",
            ),
            Intent(
                name="good_night",
                intent_type=IntentType.TIME_GREETING,
                exact_matches=["good night"],
                keyword_matches=["night", "sleep", "bedtime"],
                responses=[
                    "Good night! 🌙 Don't forget to rest well.",
                    "Sleep tight! Tomorrow's a new opportunity.",
                    "Good night! See you after some rest.",
                ],
                description="Night greeting responses",
            ),
            Intent(
                name="personal_status",
                intent_type=IntentType.PERSONAL,
                exact_matches=["how are you"],
                keyword_matches=["how are you", "how you doing"],
                responses=[
                    "I'm just code, but I'm running smoothly! 🤖",
                    "I'm here and ready to help!",
                    "Functioning perfectly, thanks for asking!",
                ],
                description="Personal status inquiries",
            ),
            Intent(
                name="bot_identity",
                intent_type=IntentType.PERSONAL,
                exact_matches=["who are you"],
                keyword_matches=["who are you", "introduce yourself"],
                responses=[
                    "I'm a rule-based chatbot built by DecodeLabs for Project 1. 🤖",
                    "I'm your AI learning companion, here to help you grow!",
                    "I'm a chatbot designed to teach AI fundamentals.",
                ],
                description="Bot identity and introduction",
            ),
            Intent(
                name="ai_definition",
                intent_type=IntentType.AI_INFO,
                exact_matches=["what is ai"],
                keyword_matches=["what is ai", "artificial intelligence", "define ai"],
                responses=[
                    "AI (Artificial Intelligence) is the simulation of human intelligence "
                    "by machines. 🧠\nIt includes machine learning, neural networks, and more!",
                    "AI stands for Artificial Intelligence — machines that simulate "
                    "human thinking and decision-making.",
                ],
                description="AI definition and explanation",
            ),
            Intent(
                name="decodelabs_info",
                intent_type=IntentType.PROJECT_INFO,
                exact_matches=["decode", "decodelabs"],
                keyword_matches=["decodelabs", "decode labs"],
                responses=[
                    "DecodeLabs is your AI training hub! 🚀\n"
                    "We provide projects and education to help you master AI.",
                ],
                description="DecodeLabs information",
            ),
            Intent(
                name="project_info",
                intent_type=IntentType.PROJECT_INFO,
                exact_matches=["project"],
                keyword_matches=["project", "project 1"],
                responses=[
                    "You're working on Project 1: Rule-Based Chatbot! 💬\n"
                    "This project teaches you control flow, NLP basics, and AI fundamentals.",
                ],
                description="Project information",
            ),
            Intent(
                name="weather_info",
                intent_type=IntentType.MISC,
                exact_matches=["weather"],
                keyword_matches=["weather", "rain", "sunny", "temperature"],
                responses=[
                    "I can't check real weather yet, but I hope it's nice outside! ☀️",
                    "Weather data is not available in my current version.",
                ],
                description="Weather-related queries",
            ),
            Intent(
                name="time_info",
                intent_type=IntentType.MISC,
                exact_matches=["time"],
                keyword_matches=["time", "what time", "current time"],
                responses=[
                    "I don't track real time yet, but you can check your system clock. ⏰",
                ],
                description="Time-related queries",
            ),
            Intent(
                name="joke",
                intent_type=IntentType.MISC,
                exact_matches=["joke"],
                keyword_matches=["joke", "funny", "laugh"],
                responses=[
                    "Why did the computer go to therapy? Because it had too many bugs! 🐛",
                    "Why do programmers prefer dark mode? "
                    "Because light attracts bugs! 💡",
                    "How many programmers does it take to change a light bulb? "
                    "None, that's a hardware problem! 🔧",
                ],
                description="Joke responses",
            ),
            Intent(
                name="study_tips",
                intent_type=IntentType.MISC,
                exact_matches=["study"],
                keyword_matches=["study", "learn", "practice"],
                responses=[
                    "Consistency is key! Study a little every day. 📚",
                    "Pro tip: Build projects while learning. It sticks better!",
                    "Practice makes perfect. Code daily! 💻",
                ],
                description="Study and learning tips",
            ),
            Intent(
                name="internship_info",
                intent_type=IntentType.PROJECT_INFO,
                exact_matches=["internship"],
                keyword_matches=["internship", "career", "job"],
                responses=[
                    "DecodeLabs internships help you build real-world AI skills! 🏢\n"
                    "Complete projects and boost your portfolio.",
                ],
                description="Internship information",
            ),
            Intent(
                name="portfolio_tips",
                intent_type=IntentType.PROJECT_INFO,
                exact_matches=["portfolio"],
                keyword_matches=["portfolio", "resume", "projects"],
                responses=[
                    "Your projects here will become part of your AI portfolio! 📁\n"
                    "Show them to employers and build your career.",
                ],
                description="Portfolio building tips",
            ),
        ]

        for intent in intents_list:
            self._register_intent(intent)

    def _register_intent(self, intent: Intent) -> None:
        """Register an intent in the registry"""
        self._intents[intent.name] = intent

        # Index by type
        if intent.intent_type not in self._intent_type_index:
            self._intent_type_index[intent.intent_type] = []
        self._intent_type_index[intent.intent_type].append(intent)

    def get_intent(self, name: str) -> Intent:
        """
        Retrieve intent by name

        Args:
            name: Intent name

        Returns:
            Intent object

        Raises:
            KeyError if intent not found
        """
        return self._intents[name]

    def get_intents_by_type(self, intent_type: IntentType) -> List[Intent]:
        """
        Get all intents of a specific type

        Args:
            intent_type: Type of intent to retrieve

        Returns:
            List of Intent objects
        """
        return self._intent_type_index.get(intent_type, [])

    def list_all_intents(self) -> Dict[str, Intent]:
        """
        Get all registered intents

        Returns:
            Dictionary of all intents
        """
        return self._intents.copy()

    def get_intent_count(self) -> int:
        """
        Get total number of registered intents

        Returns:
            Count of intents
        """
        return len(self._intents)


# Global intents registry instance
intents_registry = IntentsRegistry()