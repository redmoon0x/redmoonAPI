#!/usr/bin/env python3
"""
MitraAI Image Generation Client

This module provides a client for interacting with the MitraAI image generation API.
"""

import json
import os
import requests
import time
from datetime import datetime
from colorama import Fore, Style, init
from typing import Dict, Optional, Union

# Initialize colorama
init(autoreset=True)

class MitraAIImageClient:
    """Client for interacting with the MitraAI API for image generation."""

    def __init__(self, debug: bool = False):
        """Initialize the MitraAI Image API client.

        Args:
            debug: Whether to print debug information
        """
        self.api_url = "https://t2i.mitraai.xyz/generate-image"
        self.base_url = "https://t2i.mitraai.xyz"
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.6",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://t2i.mitraai.xyz",
            "referer": "https://t2i.mitraai.xyz/",
            "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
        }
        self.session = requests.Session()
        self.debug = debug
        self.max_retries = 3
        self.model_name = "MitraAI Image Generator"

    def generate_image(self, prompt: str, save_path: Optional[str] = None) -> Union[str, Dict]:
        """Generate an image using the MitraAI API.

        Args:
            prompt: The prompt to generate an image from
            save_path: Optional path to save the image to

        Returns:
            The path to the saved image if save_path is provided, 
            otherwise the response data containing the image path
        """
        if self.debug:
            print(f"\n{Fore.CYAN}Generating image with prompt:{Style.RESET_ALL} {prompt}")

        # Prepare the payload
        payload = {
            "prompt": prompt
        }

        # Try sending the request with retries
        retries = 0
        while retries <= self.max_retries:
            try:
                response = self.session.post(
                    self.api_url,
                    headers=self.headers,
                    data=payload
                )

                if response.status_code == 200:
                    # Parse the response JSON
                    response_data = response.json()
                    
                    if 'imagePath' in response_data:
                        image_path = response_data['imagePath']
                        full_image_url = f"{self.base_url}{image_path}"
                        
                        if self.debug:
                            print(f"{Fore.GREEN}Image generated successfully{Style.RESET_ALL}")
                            print(f"{Fore.GREEN}Image URL: {full_image_url}{Style.RESET_ALL}")
                        
                        # If save_path is provided, download and save the image
                        if save_path:
                            # Download the image
                            image_response = self.session.get(full_image_url)
                            if image_response.status_code == 200:
                                # Create directory if it doesn't exist
                                os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                                
                                # Save the image
                                with open(save_path, 'wb') as f:
                                    f.write(image_response.content)
                                
                                if self.debug:
                                    print(f"{Fore.GREEN}Image saved to: {save_path}{Style.RESET_ALL}")
                                
                                return save_path
                            else:
                                if self.debug:
                                    print(f"{Fore.RED}Failed to download image: {image_response.status_code}{Style.RESET_ALL}")
                                retries += 1
                                time.sleep(1)
                                continue
                        else:
                            # If no save_path is provided, return the response data
                            return {
                                "image_url": full_image_url,
                                "prompt": response_data.get('prompt', prompt)
                            }
                    else:
                        if self.debug:
                            print(f"{Fore.RED}Error: Response does not contain image path{Style.RESET_ALL}")
                            print(f"{Fore.RED}Response: {response_data}{Style.RESET_ALL}")
                        
                        retries += 1
                        time.sleep(1)
                else:
                    if self.debug:
                        print(f"{Fore.RED}Error: {response.status_code}{Style.RESET_ALL}")
                        print(f"{Fore.RED}Response: {response.text}{Style.RESET_ALL}")
                    
                    retries += 1
                    time.sleep(1)
            except Exception as e:
                if self.debug:
                    print(f"{Fore.RED}Error generating image: {str(e)}{Style.RESET_ALL}")
                
                retries += 1
                time.sleep(1)
        
        raise Exception("Failed to generate image after multiple attempts.")


class MitraAI:
    """Wrapper class for the MitraAI image generation client."""
    
    def __init__(self, debug: bool = False):
        """Initialize the MitraAI client.
        
        Args:
            debug: Whether to print debug information
        """
        self.client = MitraAIImageClient(debug=debug)
        self.debug = debug
        self.model_name = "MitraAI Image Generator"
    
    def get_model(self) -> str:
        """Get the current model name.
        
        Returns:
            The model name
        """
        return self.model_name
    
    def generate_image(self, prompt: str) -> str:
        """Generate an image using the MitraAI model.
        
        Args:
            prompt: The prompt to generate an image from
        
        Returns:
            The path to the saved image
        """
        # Create a directory for saving images if it doesn't exist
        save_dir = "generated_images"
        os.makedirs(save_dir, exist_ok=True)
        
        # Generate a filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{save_dir}/mitraai_{timestamp}.jpg"
        
        # Generate the image
        return self.client.generate_image(
            prompt=prompt,
            save_path=filename
        )


if __name__ == "__main__":
    # Simple test if run directly
    print(f"\n{Fore.CYAN}Testing MitraAI Image Generator:{Style.RESET_ALL}")
    mitraai_client = MitraAI(debug=True)
    image_path = mitraai_client.generate_image("A cat doing a presentation about replacing idli with pizza")
    print(f"\n{Fore.GREEN}Image saved to:{Style.RESET_ALL} {image_path}")
