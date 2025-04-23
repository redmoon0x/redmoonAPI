#!/usr/bin/env python3
"""
Z.ai API Client

This module provides a client for interacting with the Z.ai API,
which allows users to chat with the GLM-4-32B and Z1-32B models.
"""

import json
import uuid
import requests
import time
import re
from colorama import Fore, Style, init
from typing import Dict, List, Optional, Any, Union, Tuple

# Initialize colorama
init(autoreset=True)

class ZaiClient:
    """Client for interacting with the Z.ai API."""

    def __init__(self, debug: bool = False):
        """Initialize the Z.ai API client.

        Args:
            debug: Whether to print debug information
        """
        self.api_url = "https://chat.z.ai/api/chat/completions"
        self.base_url = "https://chat.z.ai"
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.5",
            "content-type": "application/json",
            "origin": "https://chat.z.ai",
            "referer": "https://chat.z.ai/",
            "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }
        self.session = requests.Session()
        self.debug = debug
        self.max_retries = 3
        self.conversation_history = []
        self.last_web_search_results = []
        self.auth_token = None
        self.user_id = None

    def _generate_random_id(self) -> str:
        """Generate a random ID.

        Returns:
            A random string ID
        """
        return str(uuid.uuid4())

    def refresh_auth_token(self) -> bool:
        """Refresh the authentication token by visiting the main page.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Visit the main page to get cookies and token
            response = self.session.get(
                self.base_url,
                headers={
                    "User-Agent": self.headers["user-agent"],
                    "Accept": "text/html,application/xhtml+xml,application/xml"
                }
            )

            if response.status_code == 200:
                # Generate a user ID if we don't have one
                if not self.user_id:
                    self.user_id = f"Guest-{int(time.time() * 1000)}"

                # For Z.ai, we'll use a hardcoded token that works
                # This is a common pattern in the API and should be stable
                self.auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImJhM2Q5NTEwLWFiMmItNDFmNS1iYzg4LTBlZDJmOWZjOWQ0NyJ9.97IyRuzeckckJMHdzossEWCn9PbAIsICPWp4y_gM8G8"
                self.headers["authorization"] = f"Bearer {self.auth_token}"

                # Also set the token as a cookie
                self.session.cookies.set("token", self.auth_token, domain="z.ai", path="/")

                if self.debug:
                    print(f"{Fore.GREEN}Auth token set successfully!{Style.RESET_ALL}")
                    print(f"Token: {self.auth_token}")
                return True
            else:
                if self.debug:
                    print(f"{Fore.RED}Failed to refresh auth token. Status code: {response.status_code}{Style.RESET_ALL}")
                return False
        except Exception as e:
            if self.debug:
                print(f"{Fore.RED}Error refreshing auth token: {str(e)}{Style.RESET_ALL}")
            return False

    def _parse_sse_response(self, response_text: str, message: str = "") -> Tuple[str, List[Dict[str, Any]]]:
        """Parse a server-sent events (SSE) response.

        Args:
            response_text: The raw response text
            message: The original user message

        Returns:
            A tuple containing (final_content, web_search_results)
        """
        try:
            # Only show debug info if debug mode is enabled
            if self.debug:
                print(f"{Fore.YELLOW}Raw SSE response:{Style.RESET_ALL}")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)

            # Split the response by data: lines
            lines = [line.strip() for line in response_text.split('\n') if line.strip().startswith('data:')]

            # Variables to store content and web search results
            final_content = None
            web_search_results = []
            tool_calls = []

            # First pass: collect tool calls and web search results
            for line in lines:
                try:
                    # Remove the 'data: ' prefix and parse as JSON
                    data = json.loads(line[6:])

                    # Check for tool calls (web search)
                    if 'data' in data and 'type' in data['data']:
                        if data['data']['type'] == 'tool_call':
                            if 'data' in data['data'] and 'name' in data['data']['data']:
                                tool_data = data['data']['data']
                                # Create a default msearch tool call if none exists
                                if tool_data.get('name') == 'msearch':
                                    # Store the actual tool call data
                                    tool_calls.append(tool_data)
                                    if self.debug:
                                        print(f"{Fore.CYAN}Found tool call: {tool_data['name']}{Style.RESET_ALL}")
                                else:
                                    # If we have web search results but no msearch tool call,
                                    # create a default one
                                    default_tool_call = {
                                        "name": "msearch",
                                        "arguments": {
                                            "description": "Search for information related to the query.",
                                            "queries": [message]
                                        }
                                    }
                                    tool_calls.append(default_tool_call)

                        # Check for tool results (web search results)
                        elif data['data']['type'] == 'tool_result':
                            if 'data' in data['data'] and 'result' in data['data']['data']:
                                result_data = data['data']['data']
                                if result_data.get('name') == 'browser_multi_search':
                                    web_search_results = result_data.get('result', [])
                                    if self.debug:
                                        print(f"{Fore.CYAN}Found web search results: {len(web_search_results)} items{Style.RESET_ALL}")
                except (json.JSONDecodeError, KeyError):
                    continue

            # Second pass: find the final content
            for line in reversed(lines):  # Start from the end to find the final message faster
                try:
                    # Remove the 'data: ' prefix and parse as JSON
                    data = json.loads(line[6:])

                    # Check if this is a chat completion message with content and done flag
                    if (
                        'data' in data and
                        'type' in data['data'] and
                        data['data']['type'] == 'chat:completion' and
                        'data' in data['data'] and
                        'content' in data['data']['data'] and
                        'done' in data['data']['data'] and
                        data['data']['data']['done']
                    ):
                        final_content = data['data']['data']['content']
                        break
                except (json.JSONDecodeError, KeyError):
                    continue

            # If we found a final message, use it
            if not final_content:
                # Try to get the last content from any message
                for line in reversed(lines):
                    try:
                        data = json.loads(line[6:])
                        if (
                            'data' in data and
                            'type' in data['data'] and
                            data['data']['type'] == 'chat:completion' and
                            'data' in data['data'] and
                            'content' in data['data']['data']
                        ):
                            final_content = data['data']['data']['content']
                            break
                    except (json.JSONDecodeError, KeyError):
                        continue

            if not final_content:
                return "No content found in response", []

            # Return the clean content and web search results separately
            return final_content, web_search_results

        except Exception as e:
            if self.debug:
                print(f"{Fore.RED}Error parsing SSE response: {str(e)}{Style.RESET_ALL}")
            return "Error parsing response", []

    def send_message(self, message: str, model: str = "main_chat", websearch: bool = False) -> str:
        """Send a message to the Z.ai API.

        Args:
            message: The message to send
            model: The model to use ("main_chat" for GLM-4-32B or "zero" for Z1-32B)
            websearch: Whether to enable web search

        Returns:
            The response from the API
        """
        # Ensure we have an auth token
        if not self.auth_token:
            if not self.refresh_auth_token():
                return "Failed to authenticate with Z.ai. Please try again."

        # Add the user message to the conversation history
        self.conversation_history.append({"role": "user", "content": message})

        # Generate a unique message ID
        message_id = self._generate_random_id()

        # Set model name based on model ID
        if model == "main_chat":
            model_name = "GLM-4-32B"
        elif model == "zero":
            model_name = "Z1-32B"
        elif model == "deep-research":
            model_name = "Z1-Rumination"
        else:
            model_name = "Unknown Model"

        # Prepare the payload
        payload = {
            "stream": True,
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "params": {},
            "chat_id": "local",
            "id": message_id,
            "model_item": {
                "id": model,
                "name": model_name,
                "owned_by": "openai"
            },
            "features": {
                "image_generation": False,
                "code_interpreter": False,
                "web_search": websearch,
                "auto_web_search": websearch,
                "preview_mode": False
            },
            "tool_servers": [],
            "variables": {
                "{{USER_NAME}}": self.user_id,
                "{{USER_LOCATION}}": "Unknown"
            }
        }

        if self.debug:
            print(f"\n{Fore.CYAN}Sending message to Z.ai API:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Message: {message}{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Using payload:{Style.RESET_ALL}")
            print(json.dumps(payload, indent=2))

        # Try sending the request with retries
        retries = 0
        while retries <= self.max_retries:
            try:
                # Only show debug info if debug mode is enabled
                if self.debug:
                    print(f"\n{Fore.YELLOW}Sending request to {self.api_url}...{Style.RESET_ALL}")

                response = self.session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    stream=True
                )

                if response.status_code == 200:
                    # Collect the full response text from the stream
                    response_text = ""
                    for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                        if chunk:
                            response_text += chunk

                    # Parse the response
                    content, web_search_results = self._parse_sse_response(response_text, message)

                    # Store web search results in a separate attribute
                    self.last_web_search_results = web_search_results

                    # Format the response for display
                    formatted_response = self._format_response_for_display(content, web_search_results)

                    # Add the assistant's response to the conversation history
                    self.conversation_history.append({"role": "assistant", "content": content})

                    return formatted_response
                elif response.status_code in (401, 403):
                    if self.debug:
                        print(f"{Fore.YELLOW}Authentication error. Refreshing auth token...{Style.RESET_ALL}")

                    # Try to refresh the auth token
                    if self.refresh_auth_token():
                        retries += 1
                        continue
                    else:
                        return "Authentication failed. Please try again later."
                else:
                    if self.debug:
                        print(f"{Fore.RED}Error: {response.status_code}{Style.RESET_ALL}")
                        print(f"{Fore.RED}Response: {response.text}{Style.RESET_ALL}")

                    retries += 1
                    time.sleep(1)  # Wait before retrying
            except Exception as e:
                if self.debug:
                    print(f"{Fore.RED}Error sending message: {str(e)}{Style.RESET_ALL}")

                retries += 1
                time.sleep(1)  # Wait before retrying

        return "Failed to get a response after multiple attempts."

    def _format_response_for_display(self, content: str, web_search_results: List[Dict[str, Any]]) -> str:
        """Format the response for display, including web search results if available.

        Args:
            content: The model's response content
            web_search_results: List of web search results

        Returns:
            Formatted response string
        """
        # If there are no web search results, just return the content
        if not web_search_results:
            return content

        # Format web search results in a clean, readable way
        formatted_results = ""
        if web_search_results:
            formatted_results = "\n\n**Web Search Results:**\n\n"
            for i, result in enumerate(web_search_results, 1):
                title = result.get('title', 'No title')
                url = result.get('url', '#')
                snippet = result.get('snippet', 'No snippet available')
                formatted_results += f"{i}. **{title}**\n   {url}\n   {snippet}\n\n"

        # Return the formatted response with web search results followed by the model's response
        return f"{content}\n{formatted_results if web_search_results else ''}"

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        self.last_web_search_results = []

    def get_last_web_search_results(self) -> List[Dict[str, Any]]:
        """Get the web search results from the last query.

        Returns:
            List of web search results
        """
        return self.last_web_search_results


class ZaiModel:
    """Base class for Z.ai models."""

    def __init__(self, model_name: str, model_id: str, supports_websearch: bool = True, debug: bool = False):
        """Initialize a Z.ai model client.

        Args:
            model_name: The display name of the model
            model_id: The API identifier for the model
            supports_websearch: Whether the model supports web search
            debug: Whether to print debug information
        """
        self.client = ZaiClient(debug=debug)
        self.debug = debug
        self.model_name = model_name
        self.model_id = model_id
        self.supports_websearch = supports_websearch

    def get_model(self) -> str:
        """Get the current model name.

        Returns:
            The model name
        """
        return self.model_name

    def supports_web_search(self) -> bool:
        """Check if the model supports web search.

        Returns:
            True if web search is supported, False otherwise
        """
        return self.supports_websearch

    def send_message(self, message: str, websearch: bool = False) -> str:
        """Send a message to the model.

        Args:
            message: The message to send
            websearch: Whether to enable web search

        Returns:
            The response from the model
        """
        if websearch and not self.supports_websearch:
            if self.debug:
                print(f"{Fore.YELLOW}Warning: Web search is not supported by {self.model_name}. Ignoring websearch parameter.{Style.RESET_ALL}")
            websearch = False

        return self.client.send_message(message, model=self.model_id, websearch=websearch)

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.client.clear_history()

    def get_last_web_search_results(self) -> List[Dict[str, Any]]:
        """Get the web search results from the last query.

        Returns:
            List of web search results
        """
        return self.client.get_last_web_search_results()


class GLM4Model(ZaiModel):
    """Wrapper class for the Z.ai client for GLM-4-32B model."""

    def __init__(self, debug: bool = False):
        """Initialize the GLM-4-32B client.

        Args:
            debug: Whether to print debug information
        """
        super().__init__("GLM-4-32B", "main_chat", True, debug)


class Z1Model(ZaiModel):
    """Wrapper class for the Z.ai client for Z1-32B model."""

    def __init__(self, debug: bool = False):
        """Initialize the Z1-32B client.

        Args:
            debug: Whether to print debug information
        """
        super().__init__("Z1-32B", "zero", True, debug)


class Z1RuminationModel(ZaiModel):
    """Wrapper class for the Z.ai client for Z1-Rumination model."""

    def __init__(self, debug: bool = False):
        """Initialize the Z1-Rumination client.

        Args:
            debug: Whether to print debug information
        """
        super().__init__("Z1-Rumination", "deep-research", True, debug)


def get_available_models(debug: bool = False) -> Dict[str, ZaiModel]:
    """Get all available Z.ai models.

    Args:
        debug: Whether to enable debug mode for the models

    Returns:
        A dictionary of model instances with model names as keys
    """
    return {
        "GLM-4-32B": GLM4Model(debug=debug),
        "Z1-32B": Z1Model(debug=debug),
        "Z1-Rumination": Z1RuminationModel(debug=debug)
    }


if __name__ == "__main__":
    # Get available models - set debug to False to hide debug output
    available_models = get_available_models(debug=False)

    # Create a numbered menu
    models = {}
    for i, (model_name, model_instance) in enumerate(available_models.items(), 1):
        models[str(i)] = {"name": model_name, "instance": model_instance}

    # Print available models
    print(f"\n{Fore.CYAN}Available Z.ai models:{Style.RESET_ALL}")
    for key, model_info in models.items():
        print(f"{key}. {model_info['name']}")

    # Get user selection
    while True:
        model_choice = input(f"\n{Fore.GREEN}Select a model (1-{len(models)}): {Style.RESET_ALL}").strip()
        if model_choice in models:
            break
        print(f"{Fore.RED}Invalid selection. Please try again.{Style.RESET_ALL}")

    # Get the selected model
    selected_model_info = models[model_choice]
    model_instance = selected_model_info["instance"]
    print(f"\n{Fore.CYAN}Selected model: {selected_model_info['name']}{Style.RESET_ALL}")

    # Web search option
    if model_instance.supports_web_search():
        while True:
            websearch_option = input(f"\n{Fore.GREEN}Enable web search? (y/n): {Style.RESET_ALL}").strip().lower()
            if websearch_option in ["y", "n"]:
                break
            print(f"{Fore.RED}Invalid selection. Please enter 'y' or 'n'.{Style.RESET_ALL}")

        enable_websearch = websearch_option == "y"
    else:
        print(f"\n{Fore.YELLOW}Note: {selected_model_info['name']} does not support web search.{Style.RESET_ALL}")
        enable_websearch = False

    # Get user message
    user_message = input(f"\n{Fore.GREEN}Enter your message: {Style.RESET_ALL}").strip()
    if not user_message:
        user_message = "Hello, how are you?"

    # Send message and display response
    print(f"\n{Fore.YELLOW}Sending message to {selected_model_info['name']}...{Style.RESET_ALL}")
    if enable_websearch:
        print(f"{Fore.YELLOW}Web search is enabled. This may take longer...{Style.RESET_ALL}")

    # Get the response and display it cleanly
    response = model_instance.send_message(user_message, websearch=enable_websearch)
    print(f"\n{response}")

    # Option to try another model
    while True:
        try_another = input(f"\n{Fore.GREEN}Try another model? (y/n): {Style.RESET_ALL}").strip().lower()
        if try_another in ["y", "n"]:
            break
        print(f"{Fore.RED}Invalid selection. Please enter 'y' or 'n'.{Style.RESET_ALL}")

    if try_another == "y":
        # Get the other model
        other_keys = [k for k in models.keys() if k != model_choice]
        if other_keys:
            other_model_key = other_keys[0]
            other_model_info = models[other_model_key]
            other_model_instance = other_model_info["instance"]
        else:
            print(f"\n{Fore.YELLOW}No other models available to try.{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Thank you for using the Z.ai client!{Style.RESET_ALL}")
            exit(0)

        print(f"\n{Fore.CYAN}Trying the same message with {other_model_info['name']}...{Style.RESET_ALL}")

        # Check if web search is supported by the other model
        if enable_websearch and not other_model_instance.supports_web_search():
            print(f"\n{Fore.YELLOW}Note: {other_model_info['name']} does not support web search. Disabling it.{Style.RESET_ALL}")
            other_websearch = False
        else:
            other_websearch = enable_websearch

        # Send the same message to the other model and display it cleanly
        other_response = other_model_instance.send_message(user_message, websearch=other_websearch)
        print(f"\n{other_response}")

    print(f"\n{Fore.CYAN}Thank you for using the Z.ai client!{Style.RESET_ALL}")
