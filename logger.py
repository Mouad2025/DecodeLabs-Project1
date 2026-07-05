"""
Logging module for Rule-Based Chatbot
Provides structured logging with file rotation and formatting
"""

import logging
import logging.handlers
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from config import config


class CustomFormatter(logging.Formatter):
    """
    Custom formatter with color support for console output
    """

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",   # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",   # Red
        "CRITICAL": "\033[41m",  # Red background
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class ChatInteractionLogger:
    """
    Specialized logger for chat interactions
    Stores user-bot exchanges in JSON format for analysis
    """

    def __init__(self, log_file: str = config.CHAT_LOG_FILE):
        self.log_file = log_file
        self._ensure_log_dir()

    def _ensure_log_dir(self) -> None:
        """Ensure log directory exists"""
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)

    def log_interaction(
        self,
        user_input: str,
        bot_response: str,
        intent: Optional[str] = None,
        confidence: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a user-bot interaction to JSON file

        Args:
            user_input: The user's input text
            bot_response: The bot's response
            intent: Detected intent (if any)
            confidence: Confidence score (0.0-1.0)
            metadata: Additional metadata
        """
        if not config.ENABLE_LOGGING:
            return

        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "bot_response": bot_response,
            "intent": intent,
            "confidence": round(confidence, 3),
            "metadata": metadata or {},
        }

        try:
            interactions = []
            # Read existing logs
            if Path(self.log_file).exists():
                with open(self.log_file, "r", encoding="utf-8") as f:
                    interactions = json.load(f)

            # Append new interaction
            interactions.append(interaction)

            # Write back
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(interactions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to log interaction: {e}")

    def get_interactions(
        self, limit: Optional[int] = None
    ) -> list:
        """
        Retrieve logged interactions

        Args:
            limit: Maximum number of interactions to retrieve

        Returns:
            List of interaction dictionaries
        """
        try:
            if not Path(self.log_file).exists():
                return []

            with open(self.log_file, "r", encoding="utf-8") as f:
                interactions = json.load(f)
                return interactions[-limit:] if limit else interactions
        except Exception as e:
            logger.error(f"Failed to read interactions: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """
        Generate statistics from logged interactions

        Returns:
            Dictionary with statistics
        """
        interactions = self.get_interactions()

        if not interactions:
            return {
                "total_interactions": 0,
                "average_confidence": 0.0,
                "most_common_intent": None,
            }

        intents = [i.get("intent") for i in interactions if i.get("intent")]
        confidences = [i.get("confidence", 0) for i in interactions]

        return {
            "total_interactions": len(interactions),
            "average_confidence": round(sum(confidences) / len(confidences), 3),
            "most_common_intent": max(set(intents), key=intents.count) if intents else None,
        }


def setup_logger(name: str) -> logging.Logger:
    """
    Setup and configure logger with file and console handlers

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(getattr(logging, config.LOG_LEVEL))

    # Ensure log directory exists
    Path(config.LOG_DIR).mkdir(parents=True, exist_ok=True)

    # Remove existing handlers
    logger_instance.handlers.clear()

    # Console Handler with color
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        CustomFormatter(fmt=config.LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger_instance.addHandler(console_handler)

    # File Handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(
        logging.Formatter(fmt=config.LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger_instance.addHandler(file_handler)

    return logger_instance


# Global logger instance
logger = setup_logger(__name__)
chat_logger = ChatInteractionLogger()