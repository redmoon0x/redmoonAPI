import requests
import json
import uuid
import os
import sys
import time
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class QwenAIClient:
    def __init__(self, debug=False):
        self.api_url = "https://www.qwenai.chat/wp-admin/admin-ajax.php"
        self.base_url = "https://www.qwenai.chat"
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.7",
            "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryRP9azsjQAHqJ72ru",
            "origin": "https://www.qwenai.chat",
            "priority": "u=1, i",
            "referer": "https://www.qwenai.chat/",
            "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }
        self.cookies = {}
        self.session = requests.Session()
        self.debug = debug
        self.max_retries = 3  # Increase retries
        self.chat_history = []
        self.client_id = self._generate_client_id()
        self.post_id = 12  # Default post_id from the example
        self.wpnonce = None

        # Set up the session with proper headers
        self.session.headers.update({
            "User-Agent": self.headers["user-agent"],
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.7",
            "Referer": self.base_url,
            "Origin": self.base_url
        })

    def _generate_client_id(self):
        """Generate a unique client ID"""
        return str(uuid.uuid4()).replace("-", "")[:10]

    def refresh_cookies(self):
        """Refresh the cookies by visiting the main website"""
        if self.debug:
            print(f"\n{Fore.YELLOW}Attempting to refresh cookies...{Style.RESET_ALL}")

        try:
            # First, clear any existing cookies
            self.session.cookies.clear()

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

                # Try to extract the wpnonce from the page content
                self._extract_wpnonce(response.text)

                # Visit the chat page to get additional cookies if needed
                chat_response = self.session.get(
                    f"{self.base_url}/chat/",
                    headers={
                        "User-Agent": self.headers["user-agent"],
                        "Accept": "text/html,application/xhtml+xml,application/xml"
                    }
                )

                if chat_response.status_code == 200:
                    # Update cookies again
                    self.cookies = dict(self.session.cookies)
                    # Try to extract wpnonce again if we didn't find it before
                    if not self.wpnonce:
                        self._extract_wpnonce(chat_response.text)

                if self.debug:
                    print(f"{Fore.GREEN}Cookies refreshed successfully!{Style.RESET_ALL}")
                    if self.wpnonce:
                        print(f"{Fore.GREEN}Found wpnonce: {self.wpnonce}{Style.RESET_ALL}")
                    print("New cookies:")
                    print(json.dumps(self.cookies, indent=2))
                return True
            else:
                if self.debug:
                    print(f"{Fore.RED}Failed to refresh cookies. Status code: {response.status_code}{Style.RESET_ALL}")
                return False
        except Exception as e:
            if self.debug:
                print(f"{Fore.RED}Error refreshing cookies: {str(e)}{Style.RESET_ALL}")
            return False

    def _extract_wpnonce(self, html_content):
        """Extract wpnonce from the HTML content"""
        try:
            # Try different patterns to find wpnonce
            patterns = [
                'wpaicg_chat_nonce":"',
                'name="_wpnonce" value="',
                'data-nonce="'
            ]

            for pattern in patterns:
                nonce_start = html_content.find(pattern)
                if nonce_start != -1:
                    nonce_start += len(pattern)
                    nonce_end = html_content.find('"', nonce_start)
                    if nonce_end != -1:
                        self.wpnonce = html_content[nonce_start:nonce_end]
                        if self.debug:
                            print(f"{Fore.GREEN}Found wpnonce using pattern: {pattern}{Style.RESET_ALL}")
                        return

            # If we get here, we couldn't find the nonce
            # As a fallback, use a hardcoded nonce from the example
            self.wpnonce = "487f1a0210"
            if self.debug:
                print(f"{Fore.YELLOW}Using fallback wpnonce: {self.wpnonce}{Style.RESET_ALL}")

        except Exception as e:
            if self.debug:
                print(f"{Fore.RED}Error extracting wpnonce: {str(e)}{Style.RESET_ALL}")
            # Use fallback nonce
            self.wpnonce = "487f1a0210"

    def _build_multipart_data(self, message):
        """Build multipart/form-data payload"""
        # Instead of manually building multipart data, use the requests library's built-in functionality
        # Convert chat history to JSON string
        chat_history_json = json.dumps(self.chat_history)

        # Add each form field
        fields = {
            "_wpnonce": self.wpnonce or "487f1a0210",  # Use fallback if not available
            "post_id": str(self.post_id),
            "url": self.base_url,
            "action": "wpaicg_chat_shortcode_message",
            "message": message,
            "bot_id": "0",
            "chatbot_identity": "shortcode",
            "wpaicg_chat_history": chat_history_json,
            "wpaicg_chat_client_id": self.client_id
        }

        return fields

    def send_message(self, message):
        """Send a message to the Qwen AI chat API"""
        # Ensure we have cookies and wpnonce
        if not self.cookies or not self.wpnonce:
            self.refresh_cookies()

        # Build the form data
        form_data = self._build_multipart_data(message)

        if self.debug:
            print(f"\n{Fore.CYAN}Sending message: {message}{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Using form data:{Style.RESET_ALL}")
            print(json.dumps(form_data, indent=2))
            print(f"\n{Fore.YELLOW}Using cookies:{Style.RESET_ALL}")
            print(json.dumps(self.cookies, indent=2))

        # Set cookies in the session
        for key, value in self.cookies.items():
            self.session.cookies.set(key, value)

        # Create a copy of headers without the content-type for requests to handle
        headers_copy = self.headers.copy()
        if "content-type" in headers_copy:
            del headers_copy["content-type"]  # Let requests set this automatically

        # Try sending the request with retries and cookie refresh
        retries = 0
        while retries <= self.max_retries:
            try:
                # Make the request using requests' built-in form handling
                response = self.session.post(
                    self.api_url,
                    headers=headers_copy,
                    data=form_data,
                    cookies=self.cookies
                )

                if response.status_code == 200:
                    try:
                        response_data = response.json()

                        # Update chat history with the user message
                        self.chat_history.append({
                            "id": "",
                            "text": f"Human: {message}"
                        })

                        # Update chat history with the AI response if successful
                        if response_data.get("status") == "success" and response_data.get("data"):
                            ai_message = response_data.get("data")
                            self.chat_history.append({
                                "id": len(self.chat_history) + 1,
                                "text": f"AI: {ai_message}"
                            })

                            return {
                                "success": True,
                                "message": ai_message,
                                "raw_response": response_data
                            }
                        else:
                            error_msg = response_data.get("msg", "Unknown error")
                            if self.debug:
                                print(f"{Fore.RED}API Error: {error_msg}{Style.RESET_ALL}")
                            return {
                                "success": False,
                                "message": error_msg,
                                "raw_response": response_data
                            }
                    except json.JSONDecodeError:
                        if self.debug:
                            print(f"{Fore.RED}Failed to parse JSON response{Style.RESET_ALL}")
                        return {
                            "success": False,
                            "message": "Failed to parse response",
                            "raw_response": response.text
                        }
                elif response.status_code == 403 or response.status_code == 401:
                    if self.debug:
                        print(f"{Fore.YELLOW}Error: {response.status_code} - Authentication error. Refreshing cookies...{Style.RESET_ALL}")
                    if self.refresh_cookies():
                        # Update session cookies after refresh
                        for key, value in self.cookies.items():
                            self.session.cookies.set(key, value)
                        retries += 1
                        continue
                    else:
                        return {
                            "success": False,
                            "message": "Authentication failed. Could not refresh cookies.",
                            "raw_response": None
                        }
                else:
                    if self.debug:
                        print(f"{Fore.RED}Error: {response.status_code}{Style.RESET_ALL}")
                        print(response.text)
                    return {
                        "success": False,
                        "message": f"HTTP Error: {response.status_code}",
                        "raw_response": response.text
                    }
            except Exception as e:
                if self.debug:
                    print(f"{Fore.RED}Request error: {str(e)}{Style.RESET_ALL}")
                return {
                    "success": False,
                    "message": f"Request error: {str(e)}",
                    "raw_response": None
                }

            retries += 1

        return {
            "success": False,
            "message": f"Failed after {self.max_retries} retries",
            "raw_response": None
        }

    def clear_history(self):
        """Clear the chat history"""
        self.chat_history = []
        return True
