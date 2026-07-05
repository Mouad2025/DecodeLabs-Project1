"""
Configuration module for Rule-Based Chatbot
Handles all application settings and constants
"""

import os
from typing import Dict
from enum import Enum


class Environment(Enum):
    """Application environment modes"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Config:
    """
    Base configuration class with sensible defaults
    Override these in environment-specific subclasses
    """

    # Application
    APP_NAME = "Rule-Based Chatbot"
    APP_VERSION = "2.0.0"
    ORGANIZATION = "DecodeLabs"
    ENVIRONMENT = Environment(os.getenv("CHATBOT_ENV", "development"))

    # Logging
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    LOG_FILE = os.path.join(LOG_DIR, "chatbot.log")
    CHAT_LOG_FILE = os.path.join(LOG_DIR, "chat_interactions.json")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT = 5

    # Chatbot Behavior
    CONFIDENCE_THRESHOLD = 0.6
    MAX_FALLBACK_SUGGESTIONS = 3
    ENABLE_LOGGING = True
    ENABLE_ANALYTICS = True

    # Response Settings
    DEFAULT_FALLBACK = "I do not understand. Try 'help' for options."
    EMPTY_INPUT_MESSAGE = "Please say something! I'm here to help."

    # Performance
    MAX_RESPONSE_TIME = 1.0  # seconds
    CACHE_ENABLED = True

    @classmethod
    def get_config(cls) -> "Config":
        """Factory method to get environment-specific config"""
        env = cls.ENVIRONMENT
        if env == Environment.PRODUCTION:
            return ProductionConfig()
        elif env == Environment.TESTING:
            return TestingConfig()
        return DevelopmentConfig()


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    ENABLE_ANALYTICS = True


class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    ENABLE_LOGGING = False
    ENABLE_ANALYTICS = False
    LOG_FILE = "test.log"
    CHAT_LOG_FILE = "test_chat.json"


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    CONFIDENCE_THRESHOLD = 0.7


# Global configuration instance
config = Config.get_config()