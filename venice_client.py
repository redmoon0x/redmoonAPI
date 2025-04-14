#!/usr/bin/env python3
"""
Venice.ai API Client

This module provides a client for interacting with the Venice.ai API,
which allows users to chat with various models including:
- Mistral Small 3.1 24B
- Llama 3.2 3B Akash

And image generation models:
- Fluently XL Final
"""

import json
import uuid
import requests
import time
import os
from datetime import datetime
from colorama import Fore, Style, init
from typing import Dict, List, Optional, Any, Union, Tuple

# Initialize colorama
init(autoreset=True)

class VeniceClient:
    """Client for interacting with the Venice.ai API for various models."""

    # Available models
    MODELS = {
        "mistral-small": "mistral-31-24b",
        "llama-akash": "llama-3.2-3b-akash"
    }

    def __init__(self, model_id: str = "mistral-small", debug: bool = False):
        """Initialize the Venice.ai API client.

        Args:
            model_id: The model ID to use (mistral-small or llama-akash)
            debug: Whether to print debug information
        """
        self.api_url = "https://venice.ai/api/inference/chat"
        self.base_url = "https://venice.ai"
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.7",
            "content-type": "application/json",
            "origin": "https://venice.ai",
            "referer": "https://venice.ai/chat/",
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
        self.request_id = self._generate_request_id()

        # Set the model ID
        if model_id in self.MODELS:
            self.model_id = self.MODELS[model_id]
        else:
            # Default to Mistral Small if an invalid model ID is provided
            self.model_id = self.MODELS["mistral-small"]
            if debug:
                print(f"{Fore.YELLOW}Invalid model ID '{model_id}'. Using default model.{Style.RESET_ALL}")

    def _generate_request_id(self) -> str:
        """Generate a random request ID.

        Returns:
            A random string ID
        """
        return ''.join(c for c in str(uuid.uuid4()) if c.isalnum())[:7]

    def _parse_sse_response(self, response_text: str) -> str:
        """Parse the server-sent events (SSE) response.

        Args:
            response_text: The raw response text

        Returns:
            The parsed response text
        """
        try:
            # For debugging purposes, don't show the entire response
            if self.debug:
                print(f"\n{Fore.YELLOW}Raw response (first 100 chars):{Style.RESET_ALL}")
                print(f"{response_text[:100]}...")

            # The response we're getting is a series of JSON objects, each on its own line
            # Each object has the format {"kind":"content","content":"text"}
            # We need to extract and concatenate all the "content" values

            # Initialize an empty string to store the concatenated content
            full_response = ""

            # Process each line
            for line in response_text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                try:
                    # Parse the JSON object
                    json_obj = json.loads(line)

                    # Check if it's a content object
                    if json_obj.get('kind') == 'content' and 'content' in json_obj:
                        # Add the content to our response
                        full_response += json_obj['content']
                except json.JSONDecodeError:
                    # Skip lines that aren't valid JSON
                    continue

            # If we successfully extracted content, return it
            if full_response:
                return full_response

            # If we couldn't extract content using the above method, try other approaches

            # Try to parse as hex (from the original hex viewer format)
            try:
                decoded_text = bytes.fromhex(response_text).decode('utf-8')

                # Process the decoded text the same way
                hex_response = ""
                for line in decoded_text.split('\n'):
                    if not line.strip():
                        continue

                    try:
                        json_obj = json.loads(line)
                        if json_obj.get('kind') == 'content' and 'content' in json_obj:
                            hex_response += json_obj['content']
                    except json.JSONDecodeError:
                        continue

                if hex_response:
                    return hex_response
            except (ValueError, UnicodeDecodeError):
                # Not a valid hex string
                pass

            # As a last resort, try to parse as a single JSON object
            try:
                response_data = json.loads(response_text)
                if isinstance(response_data, dict):
                    if 'response' in response_data:
                        return response_data['response']
                    elif 'content' in response_data:
                        return response_data['content']
                return str(response_data)
            except json.JSONDecodeError:
                # If all else fails, return the raw text
                return response_text

        except Exception as e:
            if self.debug:
                print(f"{Fore.RED}Error parsing response: {str(e)}{Style.RESET_ALL}")
            return "Error parsing response"

    def send_message(self, message: str, system_prompt: str = "") -> str:
        """Send a message to the Venice.ai API.

        Args:
            message: The message to send
            system_prompt: Optional system prompt to include

        Returns:
            The response from the API
        """
        # Add the user message to the conversation history
        self.conversation_history.append({"role": "user", "content": message})

        # Prepare the payload
        payload = {
            "requestId": self._generate_request_id(),
            "conversationType": "text",
            "type": "text",
            "modelId": self.model_id,  # Use the selected model ID
            "characterId": "",
            "isCharacter": False,
            "isDefault": True,
            "prompt": [{"role": "user", "content": message}],  # Just send the current message
            "systemPrompt": system_prompt,
            "includeVeniceSystemPrompt": True,
            "temperature": 0.15,
            "topP": 0.9,
            "clientProcessingTime": 4,
            "textToSpeech": {
                "voiceId": "af_sky",
                "speed": 1
            },
            "webEnabled": True,
            "userId": "user_anon_1234568910"
        }

        if self.debug:
            print(f"\n{Fore.CYAN}Sending message to Venice.ai API:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Message: {message}{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Using payload:{Style.RESET_ALL}")
            print(json.dumps(payload, indent=2))

        # Try sending the request with retries
        retries = 0
        while retries <= self.max_retries:
            try:
                response = self.session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                )

                if response.status_code == 200:
                    # Parse the response
                    response_text = response.text
                    parsed_response = self._parse_sse_response(response_text)

                    # Add the assistant's response to the conversation history
                    self.conversation_history.append({"role": "assistant", "content": parsed_response})

                    return parsed_response
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

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        if self.debug:
            print(f"{Fore.GREEN}Conversation history cleared.{Style.RESET_ALL}")


class MistralSmall:
    """Wrapper class for the Venice.ai client for Mistral Small 3.1 24B model."""

    def __init__(self, debug: bool = False):
        """Initialize the Mistral Small 3.1 24B client.

        Args:
            debug: Whether to print debug information
        """
        self.client = VeniceClient(model_id="mistral-small", debug=debug)
        self.debug = debug
        self.model_name = "Mistral Small 3.1 24B"

    def get_model(self) -> str:
        """Get the current model name.

        Returns:
            The model name
        """
        return self.model_name

    def send_message(self, message: str, system_prompt: str = "") -> str:
        """Send a message to the Mistral Small 3.1 24B model.

        Args:
            message: The message to send
            system_prompt: Optional system prompt to include

        Returns:
            The response from the model
        """
        return self.client.send_message(message, system_prompt)

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.client.clear_history()


class LlamaAkash:
    """Wrapper class for the Venice.ai client for Llama 3.2 3B Akash model."""

    def __init__(self, debug: bool = False):
        """Initialize the Llama 3.2 3B Akash client.

        Args:
            debug: Whether to print debug information
        """
        self.client = VeniceClient(model_id="llama-akash", debug=debug)
        self.debug = debug
        self.model_name = "Llama 3.2 3B Akash"

    def get_model(self) -> str:
        """Get the current model name.

        Returns:
            The model name
        """
        return self.model_name

    def send_message(self, message: str, system_prompt: str = "") -> str:
        """Send a message to the Llama 3.2 3B Akash model.

        Args:
            message: The message to send
            system_prompt: Optional system prompt to include

        Returns:
            The response from the model
        """
        return self.client.send_message(message, system_prompt)

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.client.clear_history()


class VeniceImageClient:
    """Client for interacting with the Venice.ai API for image generation."""

    # Available image models
    IMAGE_MODELS = {
        "fluently-xl": "fluently-xl-final-akash",
        "flux-standard": "flux.1-dev-akash"
    }

    # Available aspect ratios
    ASPECT_RATIOS = {
        "1:1": (1024, 1024),
        "16:9": (1024, 576),
        "9:16": (576, 1024),
        "4:3": (1024, 768),
        "3:4": (768, 1024)
    }

    def __init__(self, model_id: str = "fluently-xl", debug: bool = False):
        """Initialize the Venice.ai Image API client.

        Args:
            model_id: The model ID to use (fluently-xl)
            debug: Whether to print debug information
        """
        self.api_url = "https://outerface.venice.ai/api/inference/image"
        self.base_url = "https://venice.ai"
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.7",
            "content-type": "application/json",
            "origin": "https://venice.ai",
            "referer": "https://venice.ai/",
            "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }
        self.session = requests.Session()
        self.debug = debug
        self.max_retries = 3

        # Set the model ID
        if model_id in self.IMAGE_MODELS:
            self.model_id = self.IMAGE_MODELS[model_id]
        else:
            # Default to Fluently XL if an invalid model ID is provided
            self.model_id = self.IMAGE_MODELS["fluently-xl"]
            if debug:
                print(f"{Fore.YELLOW}Invalid model ID '{model_id}'. Using default model.{Style.RESET_ALL}")

    def _generate_request_id(self) -> str:
        """Generate a random request ID.

        Returns:
            A random string ID
        """
        return ''.join(c for c in str(uuid.uuid4()) if c.isalnum())[:7]

    def _generate_message_id(self) -> str:
        """Generate a random message ID.

        Returns:
            A random string ID
        """
        return ''.join(c for c in str(uuid.uuid4()) if c.isalnum())[:7]

    def generate_image(self, prompt: str, aspect_ratio: str = "1:1", negative_prompt: str = "",
                      save_path: Optional[str] = None) -> Union[str, bytes]:
        """Generate an image using the Venice.ai API.

        Args:
            prompt: The prompt to generate an image from
            aspect_ratio: The aspect ratio of the image (1:1, 16:9, 9:16, 4:3, 3:4)
            negative_prompt: Optional negative prompt to guide the generation
            save_path: Optional path to save the image to

        Returns:
            The path to the saved image if save_path is provided, otherwise the image bytes
        """
        # Validate aspect ratio
        if aspect_ratio not in self.ASPECT_RATIOS:
            if self.debug:
                print(f"{Fore.YELLOW}Invalid aspect ratio '{aspect_ratio}'. Using default 1:1.{Style.RESET_ALL}")
            aspect_ratio = "1:1"

        # Get dimensions based on aspect ratio
        width, height = self.ASPECT_RATIOS[aspect_ratio]

        # Prepare the payload
        payload = {
            "aspectRatio": aspect_ratio,
            "cfgScale": 5,
            "customSeed": "",
            "embedExifMetadata": True,
            "favoriteImageStyles": [],
            "format": "webp",
            "height": height,
            "width": width,
            "hideWatermark": False,
            "imageToImageCfgScale": 15,
            "imageToImageStrength": 33,
            "isConstrained": True,
            "isCustomSeed": False,
            "isDefault": False,
            "loraStrength": 75,
            "messageId": self._generate_message_id(),
            "modelId": self.model_id,
            "negativePrompt": negative_prompt,
            "parentMessageId": None,
            "prompt": prompt,
            "recentImageStyles": [],
            "requestId": self._generate_request_id(),
            "safeVenice": True,
            "seed": int(time.time()) % 100000000,  # Random seed based on current time
            "steps": 20,
            "stylePreset": "",
            "stylesTab": 0,
            "type": "image",
            "userId": "user_anon_1234568910",
            "variants": 1,
            "clientProcessingTime": 5
        }

        if self.debug:
            print(f"\n{Fore.CYAN}Generating image with prompt:{Style.RESET_ALL} {prompt}")
            print(f"\n{Fore.YELLOW}Using payload:{Style.RESET_ALL}")
            print(json.dumps(payload, indent=2))

        # Try sending the request with retries
        retries = 0
        while retries <= self.max_retries:
            try:
                response = self.session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                )

                if response.status_code == 200:
                    # If we got a successful response, it should be the image data
                    image_data = response.content

                    # If save_path is provided, save the image
                    if save_path:
                        # Create directory if it doesn't exist
                        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

                        # Save the image
                        with open(save_path, 'wb') as f:
                            f.write(image_data)

                        if self.debug:
                            print(f"{Fore.GREEN}Image saved to: {save_path}{Style.RESET_ALL}")

                        return save_path
                    else:
                        # If no save_path is provided, return the image data
                        return image_data
                else:
                    if self.debug:
                        print(f"{Fore.RED}Error: {response.status_code}{Style.RESET_ALL}")
                        print(f"{Fore.RED}Response: {response.text}{Style.RESET_ALL}")

                    retries += 1
                    time.sleep(1)  # Wait before retrying
            except Exception as e:
                if self.debug:
                    print(f"{Fore.RED}Error generating image: {str(e)}{Style.RESET_ALL}")

                retries += 1
                time.sleep(1)  # Wait before retrying

        raise Exception("Failed to generate image after multiple attempts.")


class FluentlyXL:
    """Wrapper class for the Venice.ai client for Fluently XL Final image model."""

    def __init__(self, debug: bool = False):
        """Initialize the Fluently XL Final client.

        Args:
            debug: Whether to print debug information
        """
        self.client = VeniceImageClient(model_id="fluently-xl", debug=debug)
        self.debug = debug
        self.model_name = "Fluently XL Final"

    def get_model(self) -> str:
        """Get the current model name.

        Returns:
            The model name
        """
        return self.model_name

    def generate_image(self, prompt: str, aspect_ratio: str = "1:1", negative_prompt: str = "") -> str:
        """Generate an image using the Fluently XL Final model.

        Args:
            prompt: The prompt to generate an image from
            aspect_ratio: The aspect ratio of the image (1:1, 16:9, 9:16, 4:3, 3:4)
            negative_prompt: Optional negative prompt to guide the generation

        Returns:
            The path to the saved image
        """
        # Create a directory for saving images if it doesn't exist
        save_dir = "generated_images"
        os.makedirs(save_dir, exist_ok=True)

        # Generate a filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{save_dir}/fluently_xl_{timestamp}.webp"

        # Generate the image
        return self.client.generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt,
            save_path=filename
        )


class FluxStandard:
    """Wrapper class for the Venice.ai client for Flux Standard image model."""

    def __init__(self, debug: bool = False):
        """Initialize the Flux Standard client.

        Args:
            debug: Whether to print debug information
        """
        self.client = VeniceImageClient(model_id="flux-standard", debug=debug)
        self.debug = debug
        self.model_name = "Flux Standard"

    def get_model(self) -> str:
        """Get the current model name.

        Returns:
            The model name
        """
        return self.model_name

    def generate_image(self, prompt: str, aspect_ratio: str = "1:1", negative_prompt: str = "") -> str:
        """Generate an image using the Flux Standard model.

        Args:
            prompt: The prompt to generate an image from
            aspect_ratio: The aspect ratio of the image (1:1, 16:9, 9:16, 4:3, 3:4)
            negative_prompt: Optional negative prompt to guide the generation

        Returns:
            The path to the saved image
        """
        # Create a directory for saving images if it doesn't exist
        save_dir = "generated_images"
        os.makedirs(save_dir, exist_ok=True)

        # Generate a filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{save_dir}/flux_standard_{timestamp}.webp"

        # Generate the image
        return self.client.generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt,
            save_path=filename
        )


if __name__ == "__main__":
    # Simple test if run directly
    print(f"\n{Fore.CYAN}Testing Mistral Small 3.1 24B model:{Style.RESET_ALL}")
    mistral_client = MistralSmall(debug=True)
    mistral_response = mistral_client.send_message("Hello, how are you?")
    print(f"\n{Fore.GREEN}Response:{Style.RESET_ALL} {mistral_response}")

    print(f"\n{Fore.CYAN}Testing Llama 3.2 3B Akash model:{Style.RESET_ALL}")
    llama_client = LlamaAkash(debug=True)
    llama_response = llama_client.send_message("Hello, how are you?")
    print(f"\n{Fore.GREEN}Response:{Style.RESET_ALL} {llama_response}")

    print(f"\n{Fore.CYAN}Testing Fluently XL Final image model:{Style.RESET_ALL}")
    fluently_client = FluentlyXL(debug=True)
    image_path = fluently_client.generate_image("A beautiful sunset over mountains")
    print(f"\n{Fore.GREEN}Image saved to:{Style.RESET_ALL} {image_path}")

    print(f"\n{Fore.CYAN}Testing Flux Standard image model:{Style.RESET_ALL}")
    flux_client = FluxStandard(debug=True)
    image_path = flux_client.generate_image("A futuristic cityscape at night")
    print(f"\n{Fore.GREEN}Image saved to:{Style.RESET_ALL} {image_path}")
