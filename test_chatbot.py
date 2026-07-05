"""
Comprehensive unit tests for Rule-Based Chatbot
Tests engine, intents, logging, and integration
"""

import unittest
import json
import os
import tempfile
from pathlib import Path

from config import Config, TestingConfig, Environment
from engine import ChatbotEngine, MatchResult
from intents import IntentsRegistry, IntentType, Intent
from logger import ChatInteractionLogger, setup_logger


class TestIntentsRegistry(unittest.TestCase):
    """Test intent registration and retrieval"""

    def setUp(self):
        self.registry = IntentsRegistry()

    def test_registry_initialization(self):
        """Test that registry initializes with intents"""
        self.assertGreater(self.registry.get_intent_count(), 0)

    def test_get_intent_by_name(self):
        """Test retrieving intent by name"""
        intent = self.registry.get_intent("greeting")
        self.assertIsNotNone(intent)
        self.assertEqual(intent.name, "greeting")

    def test_get_intents_by_type(self):
        """Test retrieving intents by type"""
        greetings = self.registry.get_intents_by_type(IntentType.GREETING)
        self.assertGreater(len(greetings), 0)
        self.assertTrue(all(i.intent_type == IntentType.GREETING for i in greetings))

    def test_list_all_intents(self):
        """Test listing all intents"""
        intents = self.registry.list_all_intents()
        self.assertEqual(len(intents), self.registry.get_intent_count())

    def test_exact_matches_normalized(self):
        """Test that exact matches are normalized to lowercase"""
        intent = self.registry.get_intent("greeting")
        self.assertTrue(all(m.islower() for m in intent.exact_matches))


class TestChatbotEngine(unittest.TestCase):
    """Test core chatbot engine"""

    def setUp(self):
        self.engine = ChatbotEngine()

    def test_engine_initialization(self):
        """Test engine initializes correctly"""
        info = self.engine.get_engine_info()
        self.assertGreater(info["total_intents"], 0)
        self.assertTrue(info["confidence_threshold"] > 0)

    def test_exact_match_greeting(self):
        """Test exact match for greeting"""
        result = self.engine.process_input("hello")
        self.assertEqual(result.match_type, "exact")
        self.assertEqual(result.confidence, 1.0)
        self.assertIsNotNone(result.intent)
        self.assertEqual(result.intent.name, "greeting")

    def test_case_insensitivity(self):
        """Test case-insensitive matching"""
        result1 = self.engine.process_input("hello")
        result2 = self.engine.process_input("HELLO")
        result3 = self.engine.process_input("HeLLo")

        self.assertEqual(result1.intent.name, result2.intent.name)
        self.assertEqual(result1.intent.name, result3.intent.name)

    def test_exact_match_farewell(self):
        """Test exact match for farewell"""
        result = self.engine.process_input("bye")
        self.assertEqual(result.match_type, "exact")
        self.assertEqual(result.intent.name, "farewell")

    def test_keyword_match(self):
        """Test keyword matching"""
        result = self.engine.process_input("how are you doing")
        self.assertEqual(result.match_type, "keyword")
        self.assertGreater(result.confidence, 0.5)

    def test_empty_input(self):
        """Test handling of empty input"""
        result = self.engine.process_input("")
        self.assertEqual(result.match_type, "empty_input")
        self.assertEqual(result.confidence, 0.0)

    def test_whitespace_handling(self):
        """Test handling of whitespace"""
        result1 = self.engine.process_input("hello")
        result2 = self.engine.process_input("  hello  ")
        self.assertEqual(result1.intent.name, result2.intent.name)

    def test_fallback_response(self):
        """Test fallback for unknown input"""
        result = self.engine.process_input("xyzabc123")
        self.assertEqual(result.match_type, "fallback")
        self.assertEqual(result.confidence, 0.0)
        self.assertIsNotNone(result.response)

    def test_fallback_suggestions(self):
        """Test that fallback provides helpful suggestions"""
        result = self.engine.process_input("xyzabc123")
        self.assertIn(result.response.lower(), [r.lower() for r in [
            "I'm not sure what you mean",
            "try asking",
            "that's a complex question"
        ]])


class TestChatInteractionLogger(unittest.TestCase):
    """Test conversation logging functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test_chat.json")
        self.logger = ChatInteractionLogger(self.log_file)

    def tearDown(self):
        # Cleanup
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        os.rmdir(self.temp_dir)

    def test_log_interaction(self):
        """Test logging an interaction"""
        self.logger.log_interaction(
            user_input="hello",
            bot_response="Hi there!",
            intent="greeting",
            confidence=1.0,
        )
        interactions = self.logger.get_interactions()
        self.assertEqual(len(interactions), 1)
        self.assertEqual(interactions[0]["user_input"], "hello")

    def test_multiple_interactions(self):
        """Test logging multiple interactions"""
        for i in range(5):
            self.logger.log_interaction(
                user_input=f"input_{i}",
                bot_response=f"response_{i}",
                intent="test",
                confidence=0.9,
            )
        interactions = self.logger.get_interactions()
        self.assertEqual(len(interactions), 5)

    def test_get_statistics(self):
        """Test statistics generation"""
        self.logger.log_interaction(
            user_input="hello",
            bot_response="Hi!",
            intent="greeting",
            confidence=1.0,
        )
        self.logger.log_interaction(
            user_input="thank you",
            bot_response="Welcome!",
            intent="gratitude",
            confidence=0.95,
        )
        stats = self.logger.get_statistics()
        self.assertEqual(stats["total_interactions"], 2)
        self.assertGreater(stats["average_confidence"], 0.9)


class TestMatchResult(unittest.TestCase):
    """Test MatchResult data structure"""

    def test_match_result_creation(self):
        """Test creating MatchResult"""
        result = MatchResult(
            intent=None,
            response="Test response",
            confidence=0.8,
            match_type="test",
        )
        self.assertEqual(result.response, "Test response")
        self.assertEqual(result.confidence, 0.8)
        self.assertEqual(result.match_type, "test")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""

    def setUp(self):
        self.engine = ChatbotEngine()
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test_integration.json")
        self.logger = ChatInteractionLogger(self.log_file)

    def tearDown(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        os.rmdir(self.temp_dir)

    def test_full_conversation_flow(self):
        """Test a complete conversation flow"""
        inputs = [
            "hello",
            "what is ai",
            "thanks",
            "bye",
        ]

        responses = []
        for user_input in inputs:
            result = self.engine.process_input(user_input)
            responses.append(result)
            self.assertIsNotNone(result.response)
            self.assertGreater(len(result.response), 0)

        self.assertEqual(len(responses), 4)

    def test_conversation_logging_flow(self):
        """Test logging during conversation"""
        result1 = self.engine.process_input("hello")
        self.logger.log_interaction(
            user_input="hello",
            bot_response=result1.response,
            intent=result1.intent.name if result1.intent else None,
            confidence=result1.confidence,
        )

        result2 = self.engine.process_input("thanks")
        self.logger.log_interaction(
            user_input="thanks",
            bot_response=result2.response,
            intent=result2.intent.name if result2.intent else None,
            confidence=result2.confidence,
        )

        interactions = self.logger.get_interactions()
        self.assertEqual(len(interactions), 2)
        stats = self.logger.get_statistics()
        self.assertEqual(stats["total_interactions"], 2)


class TestConfiguration(unittest.TestCase):
    """Test configuration system"""

    def test_config_defaults(self):
        """Test default configuration values"""
        config = Config()
        self.assertIsNotNone(config.APP_NAME)
        self.assertIsNotNone(config.APP_VERSION)
        self.assertGreater(config.CONFIDENCE_THRESHOLD, 0)

    def test_testing_config(self):
        """Test testing configuration"""
        config = TestingConfig()
        self.assertFalse(config.ENABLE_LOGGING)
        self.assertFalse(config.ENABLE_ANALYTICS)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)