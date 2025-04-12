#!/usr/bin/env python3
"""
Scira.ai Command Line Interface

This module provides an interactive command-line interface for the Scira.ai API client.
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

from scira_client import SciraClient


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
    ║             SCIRA.AI SEARCH               ║
    ║                                           ║
    ║  An unofficial command-line client for    ║
    ║  searching with Scira.ai's AI search      ║
    ╚═══════════════════════════════════════════╝
    """
    print_colored(header, Fore.CYAN, Style.BRIGHT)


def print_result(result: Dict[str, Any], index: int):
    """Print a single search result.
    
    Args:
        result: Search result dictionary
        index: Result index number
    """
    print_colored(f"\n[{index}] {result.get('title', 'No Title')}", Fore.GREEN, Style.BRIGHT)
    print_colored(f"URL: {result.get('url', 'No URL')}", Fore.BLUE)
    
    content = result.get('content', '').strip()
    if content:
        # Truncate content if it's too long
        if len(content) > 300:
            content = content[:297] + "..."
        print(f"Content: {content}")


def print_search_results(results: List[Dict[str, Any]]):
    """Print formatted search results.
    
    Args:
        results: List of search result dictionaries
    """
    if not results:
        print_colored("\nNo search results found.", Fore.YELLOW)
        return
    
    print_colored(f"\n=== SEARCH RESULTS ({len(results)}) ===", Fore.CYAN, Style.BRIGHT)
    
    for i, result in enumerate(results, 1):
        print_result(result, i)


def save_results_to_file(results: List[Dict[str, Any]], filename: str) -> bool:
    """Save search results to a file.
    
    Args:
        results: List of search result dictionaries
        filename: File to save results to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print_colored(f"\nResults saved to {filename}", Fore.GREEN)
        return True
    except Exception as e:
        print_colored(f"\nError saving results: {str(e)}", Fore.RED)
        return False


def get_cookies_path() -> str:
    """Get the default path for cookies file.
    
    Returns:
        Path to the cookies file
    """
    # Use user's home directory for cookies
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, ".scira_cookies.json")


def interactive_mode(client: SciraClient, cookies_path: str):
    """Run the client in interactive mode.
    
    Args:
        client: SciraClient instance
        cookies_path: Path to cookies file
    """
    print_header()
    
    # Try to load cookies or refresh them
    if os.path.exists(cookies_path):
        client.load_cookies(cookies_path)
    else:
        print_colored("No saved cookies found. Attempting to get new cookies...", Fore.YELLOW)
        if client.refresh_cookies():
            print_colored("Successfully obtained new cookies.", Fore.GREEN)
            client.save_cookies(cookies_path)
        else:
            print_colored("Could not automatically obtain cookies. Some features may not work.", Fore.RED)
    
    while True:
        print("\n" + "="*50)
        print_colored("Enter your search query (or type 'exit' to quit):", Fore.CYAN)
        query = input("> ").strip()
        
        if query.lower() in ('exit', 'quit', 'q'):
            break
        
        if not query:
            continue
        
        print_colored(f"\nSearching for: {query}", Fore.CYAN)
        print_colored("Waiting for results...", Fore.YELLOW)
        
        # Perform the search
        start_time = time.time()
        results_stream = client.search(query)
        if not results_stream:
            print_colored("Search failed. Please try again.", Fore.RED)
            continue
        
        # Process and display the results
        search_results = []
        tool_calls = []
        queries = []
        
        try:
            for result in results_stream:
                if "data" in result:
                    data = result["data"]
                    
                    # Handle message ID
                    if "messageId" in data:
                        print_colored(f"Message ID: {data['messageId']}", Fore.BLUE)
                    
                    # Handle tool calls
                    if "toolCallId" in data and "toolName" in data:
                        tool_calls.append(data)
                        if data["toolName"] == "web_search" and "args" in data:
                            new_queries = data['args'].get('queries', [])
                            queries.extend(new_queries)
                            print_colored(f"Searching for: {', '.join(new_queries)}", Fore.YELLOW)
                    
                    # Handle query completion
                    if isinstance(data, list) and data and "type" in data[0]:
                        if data[0]["type"] == "query_completion" and "data" in data[0]:
                            completion_data = data[0]["data"]
                            query_text = completion_data.get("query", "")
                            results_count = completion_data.get("resultsCount", 0)
                            if query_text and results_count:
                                print_colored(f"Found {results_count} results for: {query_text}", Fore.GREEN)
                    
                    # Handle search results
                    if "result" in data and "searches" in data["result"]:
                        for search in data["result"]["searches"]:
                            if "results" in search:
                                search_results.extend(search["results"])
        except KeyboardInterrupt:
            print_colored("\nSearch interrupted.", Fore.RED)
        
        # Calculate and display search time
        elapsed_time = time.time() - start_time
        print_colored(f"\nSearch completed in {elapsed_time:.2f} seconds", Fore.CYAN)
        
        # Display the search results
        print_search_results(search_results)
        
        # Ask if user wants to save results
        if search_results:
            print_colored("\nWould you like to save these results to a file? (y/n)", Fore.CYAN)
            save_choice = input("> ").strip().lower()
            if save_choice in ('y', 'yes'):
                print_colored("Enter filename (default: search_results.json):", Fore.CYAN)
                filename = input("> ").strip()
                if not filename:
                    filename = "search_results.json"
                save_results_to_file(search_results, filename)
        
        # Save cookies after each search
        client.save_cookies(cookies_path)


def main():
    """Main function to run the Scira.ai CLI."""
    parser = argparse.ArgumentParser(description="Scira.ai Command Line Interface")
    parser.add_argument("--query", "-q", help="Search query (non-interactive mode)")
    parser.add_argument("--cookies", "-c", help="Path to cookies file")
    parser.add_argument("--output", "-o", help="Save results to this file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    # Determine cookies path
    cookies_path = args.cookies or get_cookies_path()
    
    # Create client
    client = SciraClient(debug=args.debug)
    
    if args.query:
        # Non-interactive mode
        if os.path.exists(cookies_path):
            client.load_cookies(cookies_path)
        else:
            client.refresh_cookies()
            client.save_cookies(cookies_path)
        
        print_colored(f"Searching for: {args.query}", Fore.CYAN)
        results_stream = client.search(args.query)
        
        if not results_stream:
            print_colored("Search failed.", Fore.RED)
            return 1
        
        search_results = []
        
        try:
            for result in results_stream:
                if "data" in result:
                    data = result["data"]
                    
                    # Handle search results
                    if "result" in data and "searches" in data["result"]:
                        for search in data["result"]["searches"]:
                            if "results" in search:
                                search_results.extend(search["results"])
        except KeyboardInterrupt:
            print_colored("\nSearch interrupted.", Fore.RED)
        
        print_search_results(search_results)
        
        if args.output and search_results:
            save_results_to_file(search_results, args.output)
        
        # Save updated cookies
        client.save_cookies(cookies_path)
    else:
        # Interactive mode
        try:
            interactive_mode(client, cookies_path)
        except KeyboardInterrupt:
            print_colored("\nExiting...", Fore.RED)
    
    return 0


if __name__ == "__main__":
    exit(main())
