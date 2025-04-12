#!/usr/bin/env python3
"""
Chat API module for Scira.ai

This module handles the chat API interactions with Scira.ai.
"""

import json
import time
from typing import Dict, List, Any, Iterator, Optional, Union

import requests

from auth import SciraAuth
from utils import process_stream, generate_random_id


class SciraChatAPI:
    """Chat API handler for Scira.ai."""

    # Available models
    AVAILABLE_MODELS = {
        "default": "scira-default",
        "grok": "scira-grok-3-mini",
        "claude": "scira-claude",
        "vision": "scira-vision"
    }

    def __init__(self, auth: SciraAuth, model: str = "default", debug: bool = False):
        """Initialize the Chat API handler.

        Args:
            auth: SciraAuth instance for authentication
            model: Model to use (default, grok, claude, vision)
            debug: Whether to print debug information
        """
        self.auth = auth
        self.api_url = "https://scira.ai/api/search"  # Same endpoint as search
        self.debug = debug
        self.max_retries = 3
        self.user_id = f"user-{generate_random_id()}"
        self.conversation_history = []

        # Set the model
        self.set_model(model)

    def chat(self, message: str, history: Optional[List[Dict[str, Any]]] = None) -> Optional[Iterator[Dict[str, Any]]]:
        """Send a chat message to Scira.ai.

        Args:
            message: The chat message
            history: Previous conversation history (optional)

        Returns:
            An iterator of response chunks, or None if the request failed
        """
        # Generate a unique message ID for this request
        message_id = generate_random_id(12)

        # Prepare messages with history
        messages = []

        # Add history if provided
        if history:
            messages.extend(history)
        elif self.conversation_history:
            messages.extend(self.conversation_history)

        # Add the current message
        user_message = {
            "role": "user",
            "content": message,
            "parts": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }
        messages.append(user_message)

        # Prepare the payload
        payload = {
            "id": message_id,
            "group": "chat",  # Use "chat" group for conversational mode
            "messages": messages,
            "model": self.model,
            "timezone": "UTC",  # Can be customized
            "user_id": self.user_id
        }

        if self.debug:
            print("\nSending chat request with payload:")
            print(json.dumps(payload, indent=2))

        # Get a prepared session with authentication
        session = self.auth.prepare_session()

        # Try sending the request with retries and cookie refresh
        retries = 0
        while retries <= self.max_retries:
            try:
                # Make the request with stream=True to handle chunked responses
                response = session.post(
                    self.api_url,
                    json=payload,
                    stream=True
                )

                if response.status_code == 200:
                    break
                elif response.status_code in (401, 403):
                    print(f"Error: {response.status_code} - Authentication error. Refreshing cookies...")
                    if self.auth.refresh_cookies(force=True):
                        # Get a new session with updated cookies
                        session = self.auth.prepare_session()
                        retries += 1
                        continue
                    else:
                        print("Failed to refresh cookies. Please check your authentication.")
                        return None
                else:
                    print(f"Error: {response.status_code}")
                    if self.debug:
                        print(response.text)
                    return None
            except requests.RequestException as e:
                print(f"Request error: {str(e)}")
                # Wait before retrying
                time.sleep(1)
                retries += 1
                continue

            retries += 1

        if response.status_code != 200:
            print(f"Error: Failed after {self.max_retries} retries")
            return None

        # Store the user message in conversation history
        self.conversation_history.append(user_message)

        # Process the streaming response
        return self._process_chat_stream(response)

    def _process_chat_stream(self, response: requests.Response) -> Iterator[Dict[str, Any]]:
        """Process a streaming chat response from the Scira.ai API.

        Args:
            response: The streaming response from the API

        Yields:
            Parsed chunks of the response
        """
        buffer = ""
        assistant_message = {"role": "assistant", "content": "", "parts": []}

        for chunk in response.iter_content(chunk_size=1024, decode_unicode=False):
            if not chunk:
                continue

            # Convert bytes to string
            try:
                chunk_str = chunk.decode('utf-8')
                buffer += chunk_str

                # Process each line in the buffer
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)

                    if not line.strip():
                        continue

                    # Parse the line
                    try:
                        # Lines typically start with a prefix like "f:", "0:", "e:", etc.
                        if ':' in line:
                            prefix, content = line.split(':', 1)

                            # Handle message ID (f:{"messageId":"msg-..."})
                            if prefix == 'f' and content.startswith('{'):
                                try:
                                    data = json.loads(content)
                                    if self.debug:
                                        print(f"Received message ID: {data.get('messageId', 'unknown')}")
                                    yield {"type": "message_id", "data": data}
                                except json.JSONDecodeError:
                                    if self.debug:
                                        print(f"Failed to parse message ID: {content}")

                            # Handle actual message content (0:"Hello...")
                            elif prefix == '0':
                                # Remove quotes if present
                                if content.startswith('"') and content.endswith('"'):
                                    content = json.loads(content)

                                if self.debug:
                                    print(f"Received message content: {content}")

                                # Update the assistant message
                                assistant_message["content"] += content
                                assistant_message["parts"].append({"type": "text", "text": content})

                                yield {"type": "content", "text": content}

                            # Handle finish reason (e:{"finishReason":"stop",...})
                            elif prefix == 'e' or prefix == 'd':
                                try:
                                    data = json.loads(content)
                                    if self.debug:
                                        print(f"Received finish reason: {data.get('finishReason', 'unknown')}")
                                    yield {"type": "finish", "data": data}
                                except json.JSONDecodeError:
                                    if self.debug:
                                        print(f"Failed to parse finish reason: {content}")

                            # Handle other prefixes
                            else:
                                if self.debug:
                                    print(f"Unknown prefix {prefix}: {content}")
                                yield {"type": "unknown", "prefix": prefix, "content": content}
                        else:
                            if self.debug:
                                print(f"Line without prefix: {line}")
                            yield {"type": "text", "text": line}
                    except Exception as e:
                        if self.debug:
                            print(f"Error processing line: {str(e)}")
                        yield {"type": "error", "error": str(e), "line": line}
            except UnicodeDecodeError as e:
                if self.debug:
                    print(f"Unicode decode error: {str(e)}")
                continue

        # Add the complete assistant message to conversation history
        if assistant_message["content"]:
            self.conversation_history.append(assistant_message)

    def set_model(self, model: str):
        """Set the model to use for chat.

        Args:
            model: Model name (default, grok, claude, vision) or full model name

        Raises:
            ValueError: If the model is not recognized
        """
        # If the model is a full model name, use it directly
        if model in self.AVAILABLE_MODELS.values():
            self.model = model
            return

        # Otherwise, look up the model in the available models
        if model.lower() in self.AVAILABLE_MODELS:
            self.model = self.AVAILABLE_MODELS[model.lower()]
        else:
            # Default to scira-default if model not recognized
            print(f"Warning: Model '{model}' not recognized. Using default model.")
            self.model = self.AVAILABLE_MODELS["default"]

        if self.debug:
            print(f"Using model: {self.model}")

    def get_model(self) -> str:
        """Get the current model name.

        Returns:
            Current model name
        """
        return self.model

    def get_available_models(self) -> Dict[str, str]:
        """Get the available models.

        Returns:
            Dictionary of available models
        """
        return self.AVAILABLE_MODELS.copy()

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history.

        Returns:
            List of conversation messages
        """
        return self.conversation_history.copy()

    def set_history(self, history: List[Dict[str, Any]]):
        """Set the conversation history.

        Args:
            history: List of conversation messages
        """
        self.conversation_history = history.copy()
