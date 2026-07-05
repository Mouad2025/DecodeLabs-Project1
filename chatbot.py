"""
Main Rule-Based Chatbot Application
Production-ready chatbot with professional architecture and design patterns
"""

import sys
from typing import Optional
from pathlib import Path

from config import config, Environment
from logger import logger, chat_logger
from engine import ChatbotEngine, MatchResult


class Chatbot:
    """
    Main chatbot application class
    Orchestrates user interaction, input/output, and logging
    """

    def __init__(self, enable_greeting: bool = True):
        """
        Initialize the chatbot

        Args:
            enable_greeting: Whether to show startup greeting
        """
        self.engine = ChatbotEngine()
        self.running = False
        self.exchange_count = 0
        self.enable_greeting = enable_greeting

        logger.info("="*60)
        logger.info(f"Chatbot initialized: {config.APP_NAME} v{config.APP_VERSION}")
        logger.info(f"Organization: {config.ORGANIZATION}")
        logger.info(f"Environment: {config.ENVIRONMENT.value}")
        logger.info("="*60)

    def _print_header(self) -> None:
        """
        Print application header with styling
        """
        header = f"""
╔{'='*58}╗
║ {config.APP_NAME.center(56)} ║
║ {('v' + config.APP_VERSION).center(56)} ║
║ {config.ORGANIZATION.center(56)} ║
╚{'='*58}╝
        """
        print(header)

    def _print_instructions(self) -> None:
        """
        Print usage instructions
        """
        instructions = """
💬 CHATBOT COMMANDS:
   • Type any message to chat
   • Type 'help' for available commands
   • Type 'stats' to see conversation statistics
   • Type 'exit' or 'bye' to quit

🤖 Get started: Hello! How are you? What is AI? Tell me about DecodeLabs

"""
        print(instructions)

    def _print_separator(self) -> None:
        """
        Print visual separator
        """
        print("─" * 60)

    def process_command(self, user_input: str) -> bool:
        """
        Process special commands

        Args:
            user_input: User input text

        Returns:
            True if should continue, False to exit
        """
        command = user_input.lower().strip()

        if command in ["exit", "bye", "quit"]:
            self._handle_exit()
            return False

        if command == "stats":
            self._show_statistics()
            return True

        if command == "help":
            self._print_instructions()
            return True

        if command == "clear":
            self._clear_screen()
            return True

        return None  # Not a command, process as regular input

    def _handle_exit(self) -> None:
        """
        Handle chatbot exit gracefully
        """
        print("\n" + "─" * 60)
        exit_messages = [
            "Goodbye! Keep learning and growing! 🚀",
            "See you later! Thanks for chatting. 👋",
            "Bye! Don't forget to practice. 💻",
            "Thanks for using me! Until next time! 😊",
        ]
        import random
        print(f"Bot: {random.choice(exit_messages)}")
        print(f"\n📊 Session Summary:")
        print(f"   • Total exchanges: {self.exchange_count}")
        stats = chat_logger.get_statistics()
        print(f"   • Average confidence: {stats['average_confidence']:.1%}")
        if stats["most_common_intent"]:
            print(f"   • Most common intent: {stats['most_common_intent']}")
        print("\n" + "─" * 60)
        logger.info(f"Chatbot session ended. Total exchanges: {self.exchange_count}")

    def _show_statistics(self) -> None:
        """
        Display conversation statistics
        """
        stats = chat_logger.get_statistics()
        print("\n" + "─" * 60)
        print("📊 CONVERSATION STATISTICS")
        print("─" * 60)
        print(f"Total exchanges: {stats['total_interactions']}")
        print(f"Average confidence: {stats['average_confidence']:.1%}")
        if stats["most_common_intent"]:
            print(f"Most common intent: {stats['most_common_intent']}")
        print("─" * 60 + "\n")

    def _clear_screen(self) -> None:
        """
        Clear terminal screen
        """
        import os
        os.system("cls" if os.name == "nt" else "clear")
        self._print_header()
        self._print_instructions()

    def _display_response(self, user_input: str, result: MatchResult) -> None:
        """
        Display bot response with formatting

        Args:
            user_input: User's input
            result: MatchResult from engine
        """
        # Print user input
        print(f"\n👤 You: {user_input}")

        # Print bot response
        print(f"🤖 Bot: {result.response}")

        # Debug info in development mode
        if config.ENVIRONMENT == Environment.DEVELOPMENT:
            print(
                f"   [Intent: {result.intent.name if result.intent else 'None'} | "
                f"Confidence: {result.confidence:.2%} | "
                f"Type: {result.match_type}]"
            )

    def run(self) -> None:
        """
        Main chatbot loop
        """
        self.running = True
        self._print_header()
        self._print_instructions()

        try:
            while self.running:
                try:
                    # Get user input
                    user_input = input("👤 You: ").strip()

                    if not user_input:
                        continue

                    # Check for special commands
                    command_result = self.process_command(user_input)
                    if command_result is False:
                        self.running = False
                        break
                    if command_result is True:
                        continue

                    # Process regular input
                    result = self.engine.process_input(user_input)
                    self._display_response(user_input, result)

                    # Log interaction
                    if config.ENABLE_LOGGING:
                        chat_logger.log_interaction(
                            user_input=user_input,
                            bot_response=result.response,
                            intent=result.intent.name if result.intent else None,
                            confidence=result.confidence,
                            metadata={"match_type": result.match_type},
                        )

                    self.exchange_count += 1
                    self._print_separator()

                except KeyboardInterrupt:
                    print("\n\n⚠️  Session interrupted by user.")
                    self._handle_exit()
                    self.running = False
                except Exception as e:
                    logger.error(f"Error processing input: {e}", exc_info=True)
                    print(f"❌ An error occurred: {str(e)}")

        except EOFError:
            # Handle EOF (Ctrl+D on Unix, Ctrl+Z on Windows)
            print("\n")
            self._handle_exit()
        finally:
            self.running = False
            logger.info("Chatbot session terminated")


def main() -> int:
    """
    Application entry point

    Returns:
        Exit code
    """
    try:
        chatbot = Chatbot(enable_greeting=True)
        chatbot.run()
        return 0
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())