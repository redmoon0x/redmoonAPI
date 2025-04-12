#!/usr/bin/env python3
"""
Scira.ai Chat Interface

This module provides an interactive chat interface for the Scira.ai API,
allowing for conversation with search history.
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
from api import SciraAPI
from utils import extract_search_results, extract_search_queries, format_search_results


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
    ║  chatting with Scira.ai's AI search       ║
    ╚═══════════════════════════════════════════╝
    """
    print_colored(header, Fore.CYAN, Style.BRIGHT)


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
    return os.path.join(home_dir, ".scira_history.json")


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


def chat_mode(api: SciraAPI, history_path: str):
    """Run the client in chat mode with conversation history.
    
    Args:
        api: SciraAPI instance
        history_path: Path to conversation history file
    """
    print_header()
    print_colored("\nWelcome to Scira.ai Chat!", Fore.GREEN)
    print_colored("Type your questions and get AI-powered search results.", Fore.GREEN)
    print_colored("Type 'exit' to quit, 'clear' to clear history, or 'help' for more commands.", Fore.GREEN)
    
    # Load conversation history
    conversation_history = load_conversation_history(history_path)
    
    # Display conversation history if any
    if conversation_history:
        print_colored(f"\nLoaded conversation with {len(conversation_history)} messages.", Fore.BLUE)
    
    while True:
        print("\n" + "="*50)
        print_colored("Enter your question (or type 'exit' to quit):", Fore.CYAN)
        query = input("> ").strip()
        
        if not query:
            continue
        
        # Handle special commands
        if query.lower() in ('exit', 'quit', 'q'):
            break
        elif query.lower() == 'clear':
            conversation_history = []
            save_conversation_history(history_path, conversation_history)
            print_colored("Conversation history cleared.", Fore.YELLOW)
            continue
        elif query.lower() == 'help':
            print_colored("\nAvailable commands:", Fore.CYAN)
            print_colored("  exit, quit, q - Exit the chat", Fore.CYAN)
            print_colored("  clear - Clear conversation history", Fore.CYAN)
            print_colored("  help - Show this help message", Fore.CYAN)
            print_colored("  save <filename> - Save conversation to a file", Fore.CYAN)
            continue
        elif query.lower().startswith('save '):
            filename = query[5:].strip()
            if not filename:
                filename = "scira_conversation.json"
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(conversation_history, f, indent=2, ensure_ascii=False)
                print_colored(f"Conversation saved to {filename}", Fore.GREEN)
            except Exception as e:
                print_colored(f"Error saving conversation: {str(e)}", Fore.RED)
            continue
        
        print_colored(f"\nSearching for: {query}", Fore.CYAN)
        
        # Add user message to history
        user_message = {
            "role": "user",
            "content": query,
            "parts": [{"type": "text", "text": query}]
        }
        conversation_history.append(user_message)
        
        # Perform the search with history
        start_time = time.time()
        results_stream = api.search_with_history(query, conversation_history)
        if not results_stream:
            print_colored("Search failed. Please try again.", Fore.RED)
            # Remove the failed message from history
            conversation_history.pop()
            continue
        
        # Process and display the results
        stream_data = []
        search_results = []
        queries = []
        assistant_response = ""
        
        try:
            for result in results_stream:
                stream_data.append(result)
                
                # Extract and display search queries as they come in
                if result.get("type") == "json":
                    data = result.get("data", {})
                    
                    # Handle tool calls with web_search
                    if "toolName" in data and data["toolName"] == "web_search" and "args" in data:
                        if "queries" in data["args"]:
                            new_queries = data["args"]["queries"]
                            for q in new_queries:
                                if q not in queries:
                                    queries.append(q)
                                    print_colored(f"Searching for: {q}", Fore.YELLOW)
                    
                    # Handle query completion data
                    if isinstance(data, list) and data and "type" in data[0]:
                        if data[0]["type"] == "query_completion" and "data" in data[0]:
                            completion_data = data[0]["data"]
                            query_text = completion_data.get("query", "")
                            results_count = completion_data.get("resultsCount", 0)
                            if query_text and results_count and query_text not in queries:
                                queries.append(query_text)
                                print_colored(f"Found {results_count} results for: {query_text}", Fore.GREEN)
        except KeyboardInterrupt:
            print_colored("\nSearch interrupted.", Fore.RED)
        
        # Extract search results
        search_results = extract_search_results(stream_data)
        
        # Calculate and display search time
        elapsed_time = time.time() - start_time
        print_colored(f"\nSearch completed in {elapsed_time:.2f} seconds", Fore.CYAN)
        
        # Display the search results
        if search_results:
            print_colored(f"\nFound {len(search_results)} results across {len(queries)} queries:", Fore.CYAN)
            print(format_search_results(search_results, include_content=False))
            
            # Add assistant response to history
            assistant_message = {
                "role": "assistant",
                "content": f"I found {len(search_results)} results for your query.",
                "parts": [{"type": "text", "text": f"I found {len(search_results)} results for your query."}]
            }
            conversation_history.append(assistant_message)
        else:
            print_colored("\nNo search results found.", Fore.YELLOW)
            
            # Add assistant response to history
            assistant_message = {
                "role": "assistant",
                "content": "I couldn't find any results for your query.",
                "parts": [{"type": "text", "text": "I couldn't find any results for your query."}]
            }
            conversation_history.append(assistant_message)
        
        # Save updated conversation history
        save_conversation_history(history_path, conversation_history)


def main():
    """Main function to run the Scira.ai Chat."""
    parser = argparse.ArgumentParser(description="Scira.ai Chat Interface")
    parser.add_argument("--cookies", "-c", help="Path to cookies file")
    parser.add_argument("--history", "-H", help="Path to conversation history file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
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
    api = SciraAPI(auth=auth, debug=args.debug)
    
    # Run chat mode
    try:
        chat_mode(api, history_path)
    except KeyboardInterrupt:
        print_colored("\nExiting...", Fore.RED)
    
    return 0


if __name__ == "__main__":
    exit(main())
