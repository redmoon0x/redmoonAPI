#!/usr/bin/env python3
"""
Authentication module for Scira.ai API

This module handles authentication and cookie management for the Scira.ai API.
"""

import os
import json
import time
import requests
from typing import Dict, Optional, Tuple


class SciraAuth:
    """Authentication handler for Scira.ai API."""

    def __init__(self, cookies_path: Optional[str] = None, debug: bool = False):
        """Initialize the authentication handler.
        
        Args:
            cookies_path: Path to the cookies file
            debug: Whether to print debug information
        """
        self.base_url = "https://scira.ai"
        self.cookies_path = cookies_path or self._get_default_cookies_path()
        self.cookies = {}
        self.session = requests.Session()
        self.debug = debug
        self.last_refresh_time = 0
        self.refresh_interval = 3600  # Refresh cookies every hour
        
        # Set up the session with proper headers
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "en-US,en;q=0.6"
        })
        
        # Try to load cookies from file
        self._load_cookies()

    def _get_default_cookies_path(self) -> str:
        """Get the default path for cookies file.
        
        Returns:
            Path to the cookies file
        """
        # Use user's home directory for cookies
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".scira_cookies.json")

    def _load_cookies(self) -> bool:
        """Load cookies from file.
        
        Returns:
            True if cookies were successfully loaded, False otherwise
        """
        if not os.path.exists(self.cookies_path):
            if self.debug:
                print(f"Cookies file not found at {self.cookies_path}")
            return False
        
        try:
            with open(self.cookies_path, 'r') as f:
                cookie_data = json.load(f)
                
                # Check if the cookie data includes a timestamp
                if isinstance(cookie_data, dict) and "timestamp" in cookie_data and "cookies" in cookie_data:
                    self.last_refresh_time = cookie_data["timestamp"]
                    self.cookies = cookie_data["cookies"]
                else:
                    # Legacy format - just cookies
                    self.cookies = cookie_data
                    self.last_refresh_time = time.time()  # Assume they're fresh
                
                # Update session cookies
                for key, value in self.cookies.items():
                    self.session.cookies.set(key, value)
                
                if self.debug:
                    print(f"Cookies loaded from {self.cookies_path}")
                return True
        except Exception as e:
            if self.debug:
                print(f"Error loading cookies: {str(e)}")
            return False

    def _save_cookies(self) -> bool:
        """Save cookies to file.
        
        Returns:
            True if cookies were successfully saved, False otherwise
        """
        try:
            # Save cookies with timestamp
            cookie_data = {
                "timestamp": time.time(),
                "cookies": self.cookies
            }
            
            with open(self.cookies_path, 'w') as f:
                json.dump(cookie_data, f, indent=2)
            
            if self.debug:
                print(f"Cookies saved to {self.cookies_path}")
            return True
        except Exception as e:
            if self.debug:
                print(f"Error saving cookies: {str(e)}")
            return False

    def refresh_cookies(self, force: bool = False) -> bool:
        """Refresh the cookies by visiting the main website.
        
        Args:
            force: Whether to force refresh even if the refresh interval hasn't passed
            
        Returns:
            True if cookies were successfully refreshed, False otherwise
        """
        current_time = time.time()
        
        # Check if we need to refresh
        if not force and self.cookies and current_time - self.last_refresh_time < self.refresh_interval:
            if self.debug:
                print("Using cached cookies (refresh not needed)")
            return True
        
        if self.debug:
            print("Refreshing cookies...")
        
        try:
            # Clear existing session cookies
            self.session.cookies.clear()
            
            # Visit the main page to get cookies
            response = self.session.get(self.base_url)
            
            if response.status_code == 200:
                # Update the cookies dictionary with the new cookies
                self.cookies = dict(self.session.cookies)
                self.last_refresh_time = current_time
                
                # Save the updated cookies
                self._save_cookies()
                
                if self.debug:
                    print("Cookies refreshed successfully!")
                    print(f"Got {len(self.cookies)} cookies")
                return True
            else:
                if self.debug:
                    print(f"Failed to refresh cookies. Status code: {response.status_code}")
                return False
        except Exception as e:
            if self.debug:
                print(f"Error refreshing cookies: {str(e)}")
            return False

    def get_auth_headers(self) -> Dict[str, str]:
        """Get headers needed for authentication.
        
        Returns:
            Dictionary of headers
        """
        return {
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

    def get_auth_cookies(self) -> Dict[str, str]:
        """Get cookies needed for authentication.
        
        This will refresh cookies if needed based on the refresh interval.
        
        Returns:
            Dictionary of cookies
        """
        # Refresh cookies if needed
        self.refresh_cookies()
        return self.cookies

    def prepare_session(self) -> requests.Session:
        """Prepare a session with authentication headers and cookies.
        
        Returns:
            Prepared requests.Session object
        """
        # Refresh cookies if needed
        self.refresh_cookies()
        
        # Create a new session
        session = requests.Session()
        
        # Set headers
        session.headers.update(self.get_auth_headers())
        
        # Set cookies
        for key, value in self.cookies.items():
            session.cookies.set(key, value)
        
        return session

    def check_auth(self) -> Tuple[bool, Optional[str]]:
        """Check if authentication is working.
        
        Returns:
            Tuple of (success, error_message)
        """
        # Refresh cookies if needed
        self.refresh_cookies()
        
        if not self.cookies:
            return False, "No cookies available"
        
        try:
            # Try to access a page that requires authentication
            session = self.prepare_session()
            response = session.get(f"{self.base_url}/api/user")
            
            if response.status_code == 200:
                return True, None
            else:
                return False, f"Authentication check failed with status code: {response.status_code}"
        except Exception as e:
            return False, f"Authentication check error: {str(e)}"
