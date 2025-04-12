#!/usr/bin/env python3
"""
Scira.ai Chat Client

This module provides a command-line client for chatting with Scira.ai.
"""

import os
import json
import time
import argparse
from typing import Dict, List, Any, Optional

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLOR_SUPPORT = True
except ImportError:
    # Create dummy colorama classes if not available
    class DummyFore:
        def __getattr__(self, name):
            return ""
    class DummyStyle:
        def __getattr__(self, name):
            return ""
    Fore = DummyFore()
    Style = DummyStyle()
    COLOR_SUPPORT = False

from auth import SciraAuth
from chat_api import SciraChatAPI


def print_colored(text: str, color=None, style=None):
    """Print text with color if supported.

    Args:
        text: Text to print
        color: Color from colorama.Fore
        style: Style from colorama.Style
    """
    if COLOR_SUPPORT and color:
        prefix = color
        if style:
            prefix = style + color
        print(f"{prefix}{text}{Style.RESET_ALL}")
    else:
        print(text)


def print_header():
    """Print the application header."""
    header = """
    ╔═══════════════════════════════════════════╗
    ║             SCIRA.AI CHAT                 ║
    ║                                           ║
    ║  An unofficial command-line client for    ║
    ║  chatting with Scira.ai's AI assistant    ║
    ╚═══════════════════════════════════════════╝
    """
    print_colored(header, Fore.CYAN, Style.BRIGHT)

    # Print available models
    models_info = """
    Available models:
    - default: Standard Scira AI model
    - grok:    Scira Grok-3-mini model
    - claude:  Scira Claude model
    - vision:  Scira Vision model (supports images)
    """
    print_colored(models_info, Fore.YELLOW)


def get_cookies_path() -> str:
    """Get the default path for cookies file.

    Returns:
        Path to the cookies file
    """
    # Use user's home directory for cookies
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, ".scira_cookies.json")


def get_history_path() -> str:
    """Get the default path for conversation history file.

    Returns:
        Path to the history file
    """
    # Use user's home directory for history
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, ".scira_chat_history.json")


def load_conversation_history(file_path: str) -> List[Dict[str, Any]]:
    """Load conversation history from file.

    Args:
        file_path: Path to the history file

    Returns:
        List of conversation messages
    """
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print_colored(f"Error loading conversation history: {str(e)}", Fore.RED)
        return []


def save_conversation_history(file_path: str, history: List[Dict[str, Any]]) -> bool:
    """Save conversation history to file.

    Args:
        file_path: Path to the history file
        history: List of conversation messages

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print_colored(f"Error saving conversation history: {str(e)}", Fore.RED)
        return False


def chat_mode(api: SciraChatAPI, history_path: str):
    """Run the client in chat mode with conversation history.

    Args:
        api: SciraChatAPI instance
        history_path: Path to conversation history file
    """
    print_header()
    print_colored("\nWelcome to Scira.ai Chat!", Fore.GREEN)
    print_colored("Chat with Scira.ai's AI assistant in a natural conversation.", Fore.GREEN)
    print_colored(f"Currently using model: {api.get_model()}", Fore.GREEN)
    print_colored("Type 'model <name>' to switch models (default, grok, claude, vision).", Fore.GREEN)
    print_colored("Type 'exit' to quit, 'clear' to clear history, or 'help' for more commands.", Fore.GREEN)

    # Load conversation history
    conversation_history = load_conversation_history(history_path)
    if conversation_history:
        api.set_history(conversation_history)
        print_colored(f"\nLoaded conversation with {len(conversation_history)} messages.", Fore.BLUE)

        # Display the last few messages for context
        if len(conversation_history) > 0:
            print_colored("\nRecent conversation:", Fore.BLUE)
            start_idx = max(0, len(conversation_history) - 4)  # Show last 2 exchanges (4 messages)
            for msg in conversation_history[start_idx:]:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if role == "user":
                    print_colored(f"You: {content}", Fore.GREEN)
                elif role == "assistant":
                    print_colored(f"Scira: {content}", Fore.CYAN)

    while True:
        print("\n" + "="*50)
        print_colored("You:", Fore.GREEN, Style.BRIGHT)
        message = input("> ").strip()

        if not message:
            continue

        # Handle special commands
        if message.lower() in ('exit', 'quit', 'q'):
            break
        elif message.lower() == 'clear':
            api.clear_history()
            save_conversation_history(history_path, [])
            print_colored("Conversation history cleared.", Fore.YELLOW)
            continue
        elif message.lower() == 'help':
            print_colored("\nAvailable commands:", Fore.CYAN)
            print_colored("  exit, quit, q - Exit the chat", Fore.CYAN)
            print_colored("  clear - Clear conversation history", Fore.CYAN)
            print_colored("  help - Show this help message", Fore.CYAN)
            print_colored("  save <filename> - Save conversation to a file", Fore.CYAN)
            print_colored("  model <name> - Switch to a different model (default, grok, claude, vision)", Fore.CYAN)
            print_colored(f"  Current model: {api.get_model()}", Fore.CYAN)
            continue
        elif message.lower().startswith('model '):
            model_name = message[6:].strip().lower()
            if model_name in ["default", "grok", "claude", "vision"]:
                api.set_model(model_name)
                print_colored(f"Switched to model: {api.get_model()}", Fore.GREEN)
            else:
                print_colored(f"Unknown model: {model_name}. Available models: default, grok, claude, vision", Fore.RED)
            continue
        elif message.lower().startswith('save '):
            filename = message[5:].strip()
            if not filename:
                filename = "scira_conversation.json"

            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(api.get_history(), f, indent=2, ensure_ascii=False)
                print_colored(f"Conversation saved to {filename}", Fore.GREEN)
            except Exception as e:
                print_colored(f"Error saving conversation: {str(e)}", Fore.RED)
            continue

        # Send the message to the API
        print_colored("Scira is typing...", Fore.YELLOW)

        # Get the response
        response_stream = api.chat(message)
        if not response_stream:
            print_colored("Failed to get a response. Please try again.", Fore.RED)
            continue

        # Process and display the response
        print_colored("Scira:", Fore.CYAN, Style.BRIGHT)
        full_response = ""

        try:
            for chunk in response_stream:
                if chunk.get("type") == "content":
                    text = chunk.get("text", "")
                    full_response += text
                    print(text, end="", flush=True)
            print()  # Add a newline at the end
        except KeyboardInterrupt:
            print_colored("\nResponse interrupted.", Fore.RED)

        # Save the updated conversation history
        save_conversation_history(history_path, api.get_history())


def main():
    """Main function to run the Scira.ai Chat Client."""
    parser = argparse.ArgumentParser(description="Scira.ai Chat Client")
    parser.add_argument("--cookies", "-c", help="Path to cookies file")
    parser.add_argument("--history", "-H", help="Path to conversation history file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    parser.add_argument("--message", "-m", help="Send a single message and exit")
    parser.add_argument("--model", "-M", default="default",
                      choices=["default", "grok", "claude", "vision"],
                      help="Model to use (default, grok, claude, vision)")
    args = parser.parse_args()

    # Determine paths
    cookies_path = args.cookies or get_cookies_path()
    history_path = args.history or get_history_path()

    # Create authentication handler
    auth = SciraAuth(cookies_path=cookies_path, debug=args.debug)

    # Ensure we have cookies
    if not auth.refresh_cookies():
        print_colored("Failed to obtain authentication cookies. Some features may not work.", Fore.RED)

    # Create API handler
    api = SciraChatAPI(auth=auth, model=args.model, debug=args.debug)
    print_colored(f"Using model: {api.get_model()}", Fore.BLUE)

    # Load conversation history
    conversation_history = load_conversation_history(history_path)
    if conversation_history:
        api.set_history(conversation_history)

    if args.message:
        # Single message mode
        print_colored(f"You: {args.message}", Fore.GREEN)
        print_colored("Scira is typing...", Fore.YELLOW)

        # Get the response
        response_stream = api.chat(args.message)
        if not response_stream:
            print_colored("Failed to get a response.", Fore.RED)
            return 1

        # Process and display the response
        print_colored("Scira:", Fore.CYAN)
        full_response = ""

        try:
            for chunk in response_stream:
                if chunk.get("type") == "content":
                    text = chunk.get("text", "")
                    full_response += text
                    print(text, end="", flush=True)
            print()  # Add a newline at the end
        except KeyboardInterrupt:
            print_colored("\nResponse interrupted.", Fore.RED)

        # Save the updated conversation history
        save_conversation_history(history_path, api.get_history())
    else:
        # Interactive chat mode
        try:
            chat_mode(api, history_path)
        except KeyboardInterrupt:
            print_colored("\nExiting...", Fore.RED)

    return 0


if __name__ == "__main__":
    exit(main())
