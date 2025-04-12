#!/usr/bin/env python3
"""
Scira.ai API Client

This module provides a client for interacting with the Scira.ai API,
which allows users to perform searches and get AI-powered results.
"""

import json
import uuid
import time
import argparse
import requests
from typing import Dict, List, Optional, Iterator, Any, Union


class SciraClient:
    """Client for interacting with the Scira.ai API."""

    def __init__(self, cookies: Optional[Dict[str, str]] = None, debug: bool = False):
        """Initialize the Scira.ai API client.

        Args:
            cookies: Optional dictionary of cookies for authentication
            debug: Whether to print debug information
        """
        self.api_url = "https://scira.ai/api/search"
        self.base_url = "https://scira.ai"
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.6",
            "content-type": "application/json",
            "origin": "https://scira.ai",
            "referer": "https://scira.ai/",
            "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }
        self.cookies = cookies or {}
        self.session = requests.Session()
        self.debug = debug
        self.max_retries = 3
        self.user_id = f"user-{self._generate_random_id()}"

    def _generate_random_id(self, length: int = 10) -> str:
        """Generate a random ID string.
        
        Args:
            length: Length of the random ID
            
        Returns:
            A random string ID
        """
        return str(uuid.uuid4()).replace("-", "")[:length]

    def refresh_cookies(self) -> bool:
        """Refresh the cookies by visiting the main website.
        
        Returns:
            True if cookies were successfully refreshed, False otherwise
        """
        if self.debug:
            print("\nAttempting to refresh cookies...")

        try:
            # Visit the main page to get cookies
            response = self.session.get(
                self.base_url,
                headers={
                    "User-Agent": self.headers["user-agent"],
                    "Accept": "text/html,application/xhtml+xml,application/xml"
                }
            )

            if response.status_code == 200:
                # Update the cookies dictionary with the new cookies
                self.cookies = dict(self.session.cookies)
                if self.debug:
                    print("Cookies refreshed successfully!")
                    print("New cookies:")
                    print(json.dumps(self.cookies, indent=2))
                return True
            else:
                if self.debug:
                    print(f"Failed to refresh cookies. Status code: {response.status_code}")
                return False
        except Exception as e:
            if self.debug:
                print(f"Error refreshing cookies: {str(e)}")
            return False

    def search(self, query: str) -> Optional[Iterator[Dict[str, Any]]]:
        """Perform a search using the Scira.ai API.
        
        Args:
            query: The search query
            
        Returns:
            An iterator of search results, or None if the request failed
        """
        # Generate a unique message ID for this request
        message_id = self._generate_random_id(12)
        
        # Prepare the payload
        payload = {
            "id": message_id,
            "group": "web",
            "messages": [
                {
                    "role": "user", 
                    "content": query,
                    "parts": [
                        {
                            "type": "text", 
                            "text": query
                        }
                    ]
                }
            ],
            "model": "scira-default",
            "timezone": "UTC",
            "user_id": self.user_id
        }

        if self.debug:
            print("\nSending request with payload:")
            print(json.dumps(payload, indent=2))
            print("\nUsing headers:")
            print(json.dumps(self.headers, indent=2))
            print("\nUsing cookies:")
            print(json.dumps(self.cookies, indent=2))

        # Set cookies in the session
        for key, value in self.cookies.items():
            self.session.cookies.set(key, value)

        # Try sending the request with retries and cookie refresh
        retries = 0
        while retries <= self.max_retries:
            # Make the request with stream=True to handle chunked responses
            response = self.session.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                stream=True
            )

            if response.status_code == 200:
                break
            elif response.status_code in (401, 403):
                print(f"Error: {response.status_code} - Authentication error. Refreshing cookies...")
                if self.refresh_cookies():
                    # Update session cookies after refresh
                    for key, value in self.cookies.items():
                        self.session.cookies.set(key, value)
                    retries += 1
                    continue
                else:
                    print("Failed to refresh cookies. Please add cookies manually.")
                    return None
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                return None

            retries += 1

        if response.status_code != 200:
            print(f"Error: Failed after {self.max_retries} retries")
            return None

        # Process the streaming response
        return self._process_stream(response)

    def _process_stream(self, response: requests.Response) -> Iterator[Dict[str, Any]]:
        """Process a streaming response from the Scira.ai API.
        
        Args:
            response: The streaming response from the API
            
        Yields:
            Parsed chunks of the response
        """
        buffer = ""
        
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if not chunk:
                continue
                
            # Convert bytes to string if needed
            if isinstance(chunk, bytes):
                chunk = chunk.decode('utf-8')
                
            buffer += chunk
            
            # Process each line in the buffer
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                
                if not line.strip():
                    continue
                    
                # Parse the line
                try:
                    # Lines typically start with a prefix like "f:", "9:", "8:", "a:", etc.
                    if ':' in line:
                        prefix, content = line.split(':', 1)
                        
                        try:
                            data = json.loads(content)
                            if self.debug:
                                print(f"Received data with prefix {prefix}:")
                                print(json.dumps(data, indent=2))
                            yield {"prefix": prefix, "data": data}
                        except json.JSONDecodeError:
                            if self.debug:
                                print(f"Non-JSON content with prefix {prefix}: {content}")
                            yield {"prefix": prefix, "text": content}
                    else:
                        if self.debug:
                            print(f"Unknown format: {line}")
                        yield {"text": line}
                except Exception as e:
                    if self.debug:
                        print(f"Error processing line: {str(e)}")
                    yield {"error": str(e), "line": line}

    def save_cookies(self, file_path: str) -> bool:
        """Save cookies to a file.
        
        Args:
            file_path: Path to save the cookies
            
        Returns:
            True if cookies were successfully saved, False otherwise
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self.cookies, f, indent=2)
            print(f"Cookies saved to {file_path}")
            return True
        except Exception as e:
            print(f"Error saving cookies: {str(e)}")
            return False

    def load_cookies(self, file_path: str) -> bool:
        """Load cookies from a file.
        
        Args:
            file_path: Path to load the cookies from
            
        Returns:
            True if cookies were successfully loaded, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                self.cookies = json.load(f)
            print(f"Cookies loaded from {file_path}")
            return True
        except Exception as e:
            print(f"Error loading cookies: {str(e)}")
            return False


def format_search_results(results: List[Dict[str, Any]]) -> str:
    """Format search results for display.
    
    Args:
        results: List of search result items
        
    Returns:
        Formatted string of search results
    """
    formatted = []
    
    for item in results:
        if "url" in item and "title" in item:
            formatted.append(f"Title: {item['title']}")
            formatted.append(f"URL: {item['url']}")
            if "content" in item:
                content = item.get("content", "").strip()
                if content:
                    # Truncate content if it's too long
                    if len(content) > 200:
                        content = content[:197] + "..."
                    formatted.append(f"Content: {content}")
            formatted.append("")  # Empty line between results
    
    return "\n".join(formatted)


def main():
    """Main function to run the Scira.ai client from the command line."""
    parser = argparse.ArgumentParser(description="Scira.ai API Client")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--cookies", "-c", help="Path to cookies file")
    parser.add_argument("--save-cookies", "-s", help="Save cookies to file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    client = SciraClient(debug=args.debug)
    
    # Load cookies if provided
    if args.cookies:
        client.load_cookies(args.cookies)
    else:
        # Try to refresh cookies automatically
        client.refresh_cookies()
    
    # Get query from command line or prompt
    query = args.query
    if not query:
        query = input("Enter your search query: ")
    
    print(f"\nSearching for: {query}")
    print("Waiting for results...\n")
    
    # Perform the search
    results_stream = client.search(query)
    if not results_stream:
        print("Search failed. Please try again.")
        return
    
    # Process and display the results
    search_results = []
    tool_calls = []
    
    try:
        for result in results_stream:
            if "data" in result:
                data = result["data"]
                
                # Handle message ID
                if "messageId" in data:
                    print(f"Message ID: {data['messageId']}")
                
                # Handle tool calls
                if "toolCallId" in data and "toolName" in data:
                    tool_calls.append(data)
                    if data["toolName"] == "web_search" and "args" in data:
                        print(f"Performing web search with queries: {', '.join(data['args'].get('queries', []))}")
                
                # Handle search results
                if "result" in data and "searches" in data["result"]:
                    for search in data["result"]["searches"]:
                        if "results" in search:
                            search_results.extend(search["results"])
                            print(f"Found {len(search['results'])} results for query: {search.get('query', 'unknown')}")
    except KeyboardInterrupt:
        print("\nSearch interrupted.")
    
    # Display the search results
    if search_results:
        print("\n=== SEARCH RESULTS ===\n")
        print(format_search_results(search_results))
    else:
        print("\nNo search results found.")
    
    # Save cookies if requested
    if args.save_cookies:
        client.save_cookies(args.save_cookies)


if __name__ == "__main__":
    main()
