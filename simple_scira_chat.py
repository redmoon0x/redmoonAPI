#!/usr/bin/env python3
"""
Simple Scira.ai Chat Client

A clean, simplified command-line client for chatting with Scira.ai's AI models.
"""

import json
import uuid
import time
import argparse
import requests
from typing import Dict, List, Any, Optional, Iterator, Union

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


class SciraChat:
    """Simple chat client for Scira.ai."""

    # Available models
    MODELS = {
        "default": "scira-default",
        "grok": "scira-grok-3-mini",
        "claude": "scira-claude",
        "vision": "scira-vision"
    }

    def __init__(self, model: str = "default"):
        """Initialize the chat client.

        Args:
            model: Model to use (default, grok, claude, vision)
        """
        self.api_url = "https://scira.ai/api/search"
        self.base_url = "https://scira.ai"
        self.session = requests.Session()
        self.conversation_history = []
        self.user_id = f"user-{self._generate_random_id()}"

        # Set up headers - simplified for better compatibility with hosted environments
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://scira.ai",
            "referer": "https://scira.ai/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # Set the model
        self.set_model(model)

        # Get initial cookies
        self._refresh_cookies()

    def _generate_random_id(self, length: int = 10) -> str:
        """Generate a random ID string."""
        return str(uuid.uuid4()).replace("-", "")[:length]

    def _refresh_cookies(self) -> bool:
        """Refresh the cookies by visiting the main website."""
        try:
            # Visit the main page to get cookies
            response = self.session.get(
                self.base_url,
                headers={
                    "User-Agent": self.headers["user-agent"],
                    "Accept": "text/html,application/xhtml+xml,application/xml"
                },
                timeout=10  # Add timeout to prevent hanging
            )

            # Check if we got a successful response
            if response.status_code == 200:
                # Print cookies for debugging
                cookies_dict = dict(self.session.cookies)
                print(f"Cookies refreshed successfully. Got {len(cookies_dict)} cookies.")
                return True
            else:
                print(f"Failed to refresh cookies. Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error refreshing cookies: {str(e)}")
            return False

    def set_model(self, model: str):
        """Set the model to use for chat.

        Args:
            model: Model name (default, grok, claude, vision) or full model name
        """
        # If the model is a full model name, use it directly
        if model in self.MODELS.values():
            self.model = model
            return

        # Otherwise, look up the model in the available models
        if model.lower() in self.MODELS:
            self.model = self.MODELS[model.lower()]
        else:
            # Default to scira-default if model not recognized
            print(f"Model '{model}' not recognized. Using default model.")
            self.model = self.MODELS["default"]

    def get_model(self) -> str:
        """Get the current model name."""
        # Get the friendly name for the current model
        for name, model_id in self.MODELS.items():
            if model_id == self.model:
                return name
        return "unknown"

    def chat(self, message: str) -> Optional[str]:
        """Send a chat message and get a response.

        Args:
            message: The message to send

        Returns:
            The response text or None if the request failed
        """
        # Generate a unique message ID for this request
        message_id = self._generate_random_id(12)

        # Add the user message to history
        user_message = {
            "role": "user",
            "content": message,
            "parts": [{"type": "text", "text": message}]
        }
        self.conversation_history.append(user_message)

        # Prepare the payload
        payload = {
            "id": message_id,
            "group": "chat",
            "messages": self.conversation_history,
            "model": self.model,
            "timezone": "UTC",
            "user_id": self.user_id
        }

        print(f"Sending request to {self.api_url} with model {self.model}")

        # Try to send the request
        try:
            # Make the request with stream=True to handle chunked responses
            response = self.session.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=30  # Add timeout to prevent hanging
            )

            print(f"Received response with status code: {response.status_code}")

            if response.status_code != 200:
                if response.status_code in (401, 403):
                    print("Authentication error. Refreshing cookies and retrying...")
                    # Try to refresh cookies and retry
                    if self._refresh_cookies():
                        print("Cookies refreshed. Retrying request...")
                        response = self.session.post(
                            self.api_url,
                            headers=self.headers,
                            json=payload,
                            stream=True,
                            timeout=30
                        )
                        print(f"Retry response status code: {response.status_code}")
                        if response.status_code != 200:
                            print(f"Retry failed with status code: {response.status_code}")
                            return None
                    else:
                        print("Failed to refresh cookies. Cannot proceed.")
                        return None
                else:
                    print(f"Request failed with status code: {response.status_code}")
                    try:
                        error_content = response.text
                        print(f"Error response: {error_content[:200]}...")
                    except Exception as e:
                        print(f"Could not read error response: {str(e)}")
                    return None

            # Process the streaming response
            print("Processing streaming response...")
            full_response = self._process_response(response)

            # Add the assistant response to history
            if full_response:
                print(f"Received full response of length: {len(full_response)}")
                assistant_message = {
                    "role": "assistant",
                    "content": full_response,
                    "parts": [{"type": "text", "text": full_response}]
                }
                self.conversation_history.append(assistant_message)
            else:
                print("No response content received from the API")

            return full_response

        except requests.exceptions.Timeout:
            print("Request timed out. The server took too long to respond.")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error during chat request: {str(e)}")
            return None

    def _process_response(self, response: requests.Response) -> Optional[str]:
        """Process a streaming response and return the full text.

        Args:
            response: The streaming response

        Returns:
            The full response text or None if processing failed
        """
        buffer = ""
        full_response = ""
        chunk_count = 0
        line_count = 0

        try:
            print("Starting to process response chunks...")
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=False):
                chunk_count += 1
                if not chunk:
                    continue

                # Convert bytes to string
                try:
                    chunk_str = chunk.decode('utf-8')
                    buffer += chunk_str

                    # Process each line in the buffer
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line_count += 1

                        if not line.strip():
                            continue

                        # Parse the line
                        if ':' in line:
                            prefix, content = line.split(':', 1)

                            # Log the prefix for debugging
                            if chunk_count <= 3 or line_count <= 5:
                                print(f"Received line with prefix '{prefix}' (length: {len(content)})")

                            # Handle actual message content (0:"Hello...")
                            if prefix == '0':
                                # Remove quotes if present
                                if content.startswith('"') and content.endswith('"'):
                                    try:
                                        content = json.loads(content)
                                    except json.JSONDecodeError as e:
                                        print(f"JSON decode error: {str(e)} for content: {content[:50]}...")
                                        pass

                                full_response += content
                                # In web context, don't print to console
                                # print(content, end="", flush=True)
                            elif prefix in ('1', '2', '3', '4', '5', '6', '7', '8', '9'):
                                # These are other message types that might contain useful information
                                try:
                                    if content.strip():
                                        parsed = json.loads(content) if content.strip()[0] in '{[' else content
                                        print(f"Additional data (prefix {prefix}): {str(parsed)[:100]}...")
                                except Exception:
                                    pass

                except UnicodeDecodeError as e:
                    print(f"Unicode decode error: {str(e)}")
                    continue

            print(f"Finished processing response. Received {chunk_count} chunks, {line_count} lines.")
            print(f"Final response length: {len(full_response)} characters")

            # If we got no response but had chunks, this might indicate a parsing issue
            if not full_response and chunk_count > 0:
                print("Warning: Received chunks but couldn't extract a response. Possible format change.")
                # Try to extract anything that looks like a response from the buffer
                if buffer:
                    print(f"Remaining buffer (first 100 chars): {buffer[:100]}...")
                    # Try to find any content in quotes that might be the response
                    import re
                    quoted_content = re.findall(r'"([^"]*)"', buffer)
                    if quoted_content:
                        print(f"Found {len(quoted_content)} quoted strings in buffer")
                        # Use the longest quoted string as a fallback response
                        longest = max(quoted_content, key=len)
                        if len(longest) > 10:  # Only use if it's reasonably long
                            print(f"Using longest quoted string as fallback response: {longest[:50]}...")
                            full_response = longest

            return full_response

        except Exception as e:
            print(f"Error processing response: {str(e)}")
            return None

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []


def print_colored(text: str, color=None, style=None):
    """Print text with color if supported."""
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
║  Simple command-line client for chatting  ║
║  with Scira.ai's AI models                ║
╚═══════════════════════════════════════════╝
"""
    print_colored(header, Fore.CYAN, Style.BRIGHT)

    # Print available models
    models_info = """
Available models: default, grok, claude, vision
Type 'model <name>' to switch models (e.g., 'model grok')
Type 'clear' to clear history, 'exit' to quit
"""
    print_colored(models_info, Fore.YELLOW)


def main():
    """Main function to run the Scira.ai Chat Client."""
    parser = argparse.ArgumentParser(description="Simple Scira.ai Chat Client")
    parser.add_argument("--model", "-m", default="default",
                      choices=["default", "grok", "claude", "vision"],
                      help="Model to use (default, grok, claude, vision)")
    args = parser.parse_args()

    # Create chat client
    client = SciraChat(model=args.model)

    # Print header
    print_header()
    print_colored(f"Currently using model: {client.get_model()}", Fore.GREEN)

    # Main chat loop
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
            client.clear_history()
            print_colored("Conversation history cleared.", Fore.YELLOW)
            continue
        elif message.lower().startswith('model '):
            model_name = message[6:].strip().lower()
            if model_name in ["default", "grok", "claude", "vision"]:
                client.set_model(model_name)
                print_colored(f"Switched to model: {client.get_model()}", Fore.GREEN)
            else:
                print_colored(f"Unknown model: {model_name}. Available models: default, grok, claude, vision", Fore.RED)
            continue
        # Also handle just the model name
        elif message.lower() in ["default", "grok", "claude", "vision"]:
            client.set_model(message.lower())
            print_colored(f"Switched to model: {client.get_model()}", Fore.GREEN)
            continue

        # Send the message to the API
        print_colored("Scira:", Fore.CYAN, Style.BRIGHT)
        response = client.chat(message)

        if not response:
            print_colored("Failed to get a response. Please try again.", Fore.RED)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
