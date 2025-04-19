#!/usr/bin/env python3
"""
Phi4 Chat Client

This module provides a client for interacting with the Phi4 chat API.
"""

import json
import random
import string
import re
import time
import requests
import sseclient
from typing import Dict, Tuple, Optional, List

class Phi4ChatClient:
    """Client for interacting with the Phi4 chat API."""

    def __init__(self, debug: bool = False):
        """Initialize the Phi4 chat client.

        Args:
            debug: Whether to print debug information
        """
        self.api_url = "https://www.phi4.chat/wp-admin/admin-ajax.php"
        self.base_url = "https://www.phi4.chat"
        self.debug = debug
        self.max_retries = 3
        self.session = requests.Session()
        self.wpnonce = None
        self.cookies = {}
        self.chat_history = []
        self.chat_id = None

        # Generate a random client ID
        self.client_id = self._generate_random_id()

        # Set headers
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.8",
            "content-type": "application/x-www-form-urlencoded",
            "origin": self.base_url,
            "referer": self.base_url,
            "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }

        # Initialize session
        self.refresh_cookies()

    def _generate_random_id(self, length: int = 10) -> str:
        """Generate a random ID.

        Args:
            length: Length of the ID

        Returns:
            A random ID
        """
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def refresh_cookies(self) -> bool:
        """Refresh cookies and wpnonce.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Visit the main page to get cookies and wpnonce
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

                # Extract wpnonce from the page content
                self._extract_wpnonce(response.text)

                if self.debug:
                    print(f"Cookies refreshed: {self.cookies}")
                    print(f"WP Nonce: {self.wpnonce}")

                return True
            else:
                if self.debug:
                    print(f"Failed to refresh cookies. Status code: {response.status_code}")
                return False

        except Exception as e:
            if self.debug:
                print(f"Error refreshing cookies: {str(e)}")
            return False

    def _extract_wpnonce(self, html_content: str) -> None:
        """Extract wpnonce from HTML content.

        Args:
            html_content: HTML content to extract wpnonce from
        """
        try:
            # Try to find wpnonce in the HTML content
            nonce_match = re.search(r'_wpnonce\s*:\s*[\'"]([^\'"]+)[\'"]', html_content)
            if nonce_match:
                self.wpnonce = nonce_match.group(1)
                if self.debug:
                    print(f"Extracted wpnonce: {self.wpnonce}")
                return

            # Try another pattern
            nonce_match = re.search(r'name="_wpnonce"\s+value="([^"]+)"', html_content)
            if nonce_match:
                self.wpnonce = nonce_match.group(1)
                if self.debug:
                    print(f"Extracted wpnonce: {self.wpnonce}")
                return

            # If we get here, we couldn't find the nonce
            # Use a fallback nonce from the example
            self.wpnonce = "973cd1e141"
            if self.debug:
                print(f"Using fallback wpnonce: {self.wpnonce}")

        except Exception as e:
            if self.debug:
                print(f"Error extracting wpnonce: {str(e)}")
            # Use fallback nonce
            self.wpnonce = "973cd1e141"

    def send_message(self, message: str) -> str:
        """Send a message to the Phi4 chat API.

        Args:
            message: Message to send

        Returns:
            Response from the API
        """
        # Ensure we have cookies and wpnonce
        if not self.cookies or not self.wpnonce:
            self.refresh_cookies()

        # Prepare the chat history
        if not self.chat_id:
            # Generate a new chat ID if we don't have one
            self.chat_id = random.randint(10000, 99999)

        # Build the form data
        form_data = {
            "_wpnonce": self.wpnonce,
            "post_id": "21",  # This seems to be a fixed value from the example
            "url": self.base_url,
            "action": "wpaicg_chat_shortcode_message",
            "message": message,
            "bot_id": "0",
            "chatbot_identity": "shortcode",
            "wpaicg_chat_client_id": self.client_id,
            "wpaicg_chat_history": json.dumps(self.chat_history),
            "chat_id": str(self.chat_id)
        }

        if self.debug:
            print(f"Sending message: {message}")
            print(f"Form data: {form_data}")

        # Set cookies in the session
        for key, value in self.cookies.items():
            self.session.cookies.set(key, value)

        # Try sending the request with retries
        retries = 0
        while retries <= self.max_retries:
            try:
                # Make the request
                response = self.session.post(
                    self.api_url,
                    headers=self.headers,
                    data=form_data,
                    stream=True
                )

                if response.status_code == 200:
                    # Add the user message to chat history
                    self.chat_history.append({
                        "text": f"Human: {message}"
                    })

                    # Process the response
                    ai_response = self._process_response(response)

                    # Add the AI response to chat history
                    self.chat_history.append({
                        "id": str(len(self.chat_history)),
                        "text": f"AI: {ai_response}"
                    })

                    return ai_response
                else:
                    if self.debug:
                        print(f"Request failed with status code: {response.status_code}")

                    # If authentication error, refresh cookies and retry
                    if response.status_code in (401, 403):
                        if self.debug:
                            print("Authentication error. Refreshing cookies and retrying...")
                        self.refresh_cookies()
                        retries += 1
                    else:
                        # For other errors, just retry
                        retries += 1

                    if retries > self.max_retries:
                        return f"Error: Failed to get a response after {self.max_retries} retries."

                    # Wait before retrying
                    time.sleep(1)
            except Exception as e:
                if self.debug:
                    print(f"Error sending message: {str(e)}")
                retries += 1

                if retries > self.max_retries:
                    return f"Error: {str(e)}"

                # Wait before retrying
                time.sleep(1)

        return "Error: Failed to get a response."

    def _process_response(self, response: requests.Response) -> str:
        """Process the response from the API.

        Args:
            response: Response from the API

        Returns:
            Processed response text
        """
        try:
            # The response is a Server-Sent Events (SSE) stream
            client = sseclient.SSEClient(response)
            full_response = ""

            for event in client.events():
                if self.debug:
                    print(f"Event data: {event.data}")

                # Skip empty events or [DONE] markers
                if not event.data or event.data == "[DONE]":
                    continue

                try:
                    # Try to parse the JSON data
                    data = json.loads(event.data)

                    # Extract the content from the choices
                    if "choices" in data and len(data["choices"]) > 0:
                        choice = data["choices"][0]
                        if "delta" in choice and "content" in choice["delta"]:
                            content = choice["delta"]["content"]
                            # Print the content in real-time
                            print(content, end="", flush=True)
                            full_response += content

                    # Check if this is the final message with usage stats
                    if "usage" in data:
                        # This is the final message
                        break

                except json.JSONDecodeError:
                    # If it's not valid JSON and not [DONE], it might be plain text
                    if event.data != "[DONE]":
                        # Check if it's the final [DONE] message
                        if not event.data.startswith("{") and "[DONE]" in event.data:
                            break
                        print(event.data, end="", flush=True)
                        full_response += event.data

            print()  # Add a newline after the response
            return full_response
        except Exception as e:
            if self.debug:
                print(f"Error processing response: {str(e)}")
            return f"Error processing response: {str(e)}"
        finally:
            response.close()

    def clear_history(self) -> None:
        """Clear the chat history."""
        self.chat_history = []
        self.chat_id = None
        if self.debug:
            print("Chat history cleared.")


def main():
    """Main function to run the Phi4 Chat Client."""
    import argparse
    from colorama import Fore, Style, init

    # Initialize colorama
    init(autoreset=True)

    parser = argparse.ArgumentParser(description="Phi4 Chat Client")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    # Create chat client
    client = Phi4ChatClient(debug=args.debug)

    # Print header
    print(f"{Fore.CYAN}==============================")
    print(f"{Fore.CYAN}       PHI4 CHAT CLIENT       ")
    print(f"{Fore.CYAN}==============================")
    print(f"{Fore.YELLOW}Type 'exit' to quit, 'clear' to clear history")

    # Main chat loop
    while True:
        print("\n" + "="*50)
        print(f"{Fore.GREEN}{Style.BRIGHT}You:")
        message = input("> ").strip()

        if not message:
            continue

        if message.lower() in ('exit', 'quit', 'q'):
            break

        if message.lower() == 'clear':
            client.clear_history()
            print(f"{Fore.YELLOW}Chat history cleared. Starting new conversation.")
            continue

        # Print a spinner or "thinking" message
        print(f"{Fore.YELLOW}Phi4 is thinking...")

        # Get the response
        print(f"{Fore.CYAN}{Style.BRIGHT}Phi4:", end=" ")
        response = client.send_message(message)

        if not response:
            print(f"{Fore.RED}Failed to get a response. Please try again.")


if __name__ == "__main__":
    main()
