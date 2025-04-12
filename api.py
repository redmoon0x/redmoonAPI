#!/usr/bin/env python3
"""
API module for Scira.ai

This module handles the core API interactions with Scira.ai.
"""

import json
import time
from typing import Dict, List, Any, Iterator, Optional, Union

import requests

from auth import SciraAuth
from utils import process_stream, generate_random_id


class SciraAPI:
    """API handler for Scira.ai."""

    def __init__(self, auth: SciraAuth, debug: bool = False):
        """Initialize the API handler.
        
        Args:
            auth: SciraAuth instance for authentication
            debug: Whether to print debug information
        """
        self.auth = auth
        self.api_url = "https://scira.ai/api/search"
        self.debug = debug
        self.max_retries = 3
        self.user_id = f"user-{generate_random_id()}"

    def search(self, query: str) -> Optional[Iterator[Dict[str, Any]]]:
        """Perform a search using the Scira.ai API.
        
        Args:
            query: The search query
            
        Returns:
            An iterator of search results, or None if the request failed
        """
        # Generate a unique message ID for this request
        message_id = generate_random_id(12)
        
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

        # Process the streaming response
        return process_stream(response.iter_content(chunk_size=1024))

    def search_with_history(self, query: str, history: List[Dict[str, Any]] = None) -> Optional[Iterator[Dict[str, Any]]]:
        """Perform a search with conversation history.
        
        Args:
            query: The search query
            history: Previous conversation history
            
        Returns:
            An iterator of search results, or None if the request failed
        """
        # Generate a unique message ID for this request
        message_id = generate_random_id(12)
        
        # Prepare messages with history
        messages = []
        
        # Add history if provided
        if history:
            messages.extend(history)
        
        # Add the current query
        messages.append({
            "role": "user", 
            "content": query,
            "parts": [
                {
                    "type": "text", 
                    "text": query
                }
            ]
        })
        
        # Prepare the payload
        payload = {
            "id": message_id,
            "group": "web",
            "messages": messages,
            "model": "scira-default",
            "timezone": "UTC",
            "user_id": self.user_id
        }

        if self.debug:
            print("\nSending request with payload:")
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

        # Process the streaming response
        return process_stream(response.iter_content(chunk_size=1024))

    def check_api_status(self) -> Dict[str, Any]:
        """Check the status of the API.
        
        Returns:
            Dictionary with status information
        """
        try:
            # Get a prepared session with authentication
            session = self.auth.prepare_session()
            
            # Make a simple request to check if the API is working
            response = session.get("https://scira.ai/api/status")
            
            if response.status_code == 200:
                return {
                    "status": "ok",
                    "message": "API is working",
                    "details": response.json() if response.headers.get("content-type") == "application/json" else None
                }
            else:
                return {
                    "status": "error",
                    "message": f"API returned status code {response.status_code}",
                    "details": None
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error checking API status: {str(e)}",
                "details": None
            }
