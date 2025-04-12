import requests
import json
import argparse
import uuid
import time
import re
import os

class UncovrClient:
    def __init__(self, cookies=None, debug=False):
        self.api_url = "https://uncovr.app/api/workflows/chat"
        self.base_url = "https://uncovr.app"
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.6",
            "content-type": "application/json",
            "origin": "https://uncovr.app",
            "referer": "https://uncovr.app/thread/",
            "sec-ch-ua": '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }
        self.cookies = cookies or {}
        self.session = requests.Session()
        self.debug = debug
        self.max_retries = 2

    def refresh_cookies(self):
        """Refresh the cookies by visiting the main website"""
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

    def send_message(self, content, chat_id=None, user_message_id=None, focus=None, tools=None):
        """Send a message to the Uncovr API"""
        if not chat_id:
            chat_id = str(uuid.uuid4()).replace("-", "")[:16]
        if not user_message_id:
            user_message_id = str(uuid.uuid4()).replace("-", "")[:16]

        # Default values
        selected_focus = focus or ["web"]
        selected_tools = tools or ["quick-cards"]

        payload = {
            "content": content,
            "chatId": chat_id,
            "userMessageId": user_message_id,
            "ai_config": {
                "selectedFocus": selected_focus,
                "selectedTools": selected_tools,
                "agentId": "search",
                "modelId": "gpt-4o-mini"
            }
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
            elif response.status_code == 403 or response.status_code == 401:
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

        # Process the streamed response
        full_response = ""
        text_response = ""
        metadata = {}

        print("\nResponse from Uncovr AI:\n")
        print("-" * 50)

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                chunk_text = chunk.decode('utf-8')
                full_response += chunk_text

                # Parse the chunk
                for line in chunk_text.split('\n'):
                    if not line.strip():
                        continue

                    # Extract the prefix and content
                    match = re.match(r'^(\d+):(.*)$', line)
                    if match:
                        prefix, content = match.groups()

                        # Text content (prefix 0)
                        if prefix == "0":
                            text_content = content.strip('"')
                            # Replace escaped newlines with actual newlines
                            text_content = text_content.replace('\\n', '\n')
                            text_response += text_content
                            print(text_content, end='', flush=True)

                        # Metadata (prefix 2)
                        elif prefix == "2" and self.debug:
                            try:
                                meta_data = json.loads(content)
                                if isinstance(meta_data, list) and len(meta_data) > 0:
                                    for item in meta_data:
                                        if "type" in item:
                                            if item["type"] not in metadata:
                                                metadata[item["type"]] = item.get("content", "")
                            except json.JSONDecodeError:
                                if self.debug:
                                    print(f"\nFailed to parse metadata: {content}")

                        # Other prefixes
                        elif self.debug:
                            print(f"\n[Debug] Prefix {prefix}: {content}")

        print("\n" + "-" * 50)

        # Return both the text response and the full response
        return {
            "text": text_response,
            "full_response": full_response,
            "metadata": metadata,
            "chat_id": chat_id
        }

def main():
    # Initialize with default settings
    cookies = {}
    debug = False
    chat_id = None
    focus = None
    tools = None

    print("\n===== Uncovr.app Chat Client =====\n")
    print("Type 'exit', 'quit', or 'q' to exit the program")
    print("Type 'help' or '?' for available commands\n")

    # Initialize client
    client = UncovrClient(cookies=cookies, debug=debug)

    # Try to refresh cookies automatically at startup
    client.refresh_cookies()

    while True:
        # Show prompt with chat ID if available
        if chat_id:
            prompt = f"[Chat: {chat_id}] You: "
        else:
            prompt = "You: "

        # Get user input
        user_input = input(prompt).strip()

        # Check for exit command
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break

        # Check for help command
        elif user_input.lower() in ['help', '?']:
            print("\nAvailable commands:")
            print("  help, ? - Show this help message")
            print("  exit, quit, q - Exit the program")
            print("  debug on/off - Toggle debug mode")
            print("  refresh - Manually refresh cookies")
            print("  chat <id> - Set chat ID for conversation")
            print("  clear - Clear the chat ID and start a new conversation")
            print("  cookie add <name>=<value> - Add a cookie")
            print("  cookie list - List all cookies")
            print("  cookie clear - Clear all cookies")
            print("\nAny other input will be sent as a message to Uncovr.app AI\n")
            continue

        # Toggle debug mode
        elif user_input.lower() in ['debug on', 'debug true']:
            debug = True
            client.debug = True
            print("Debug mode enabled")
            continue
        elif user_input.lower() in ['debug off', 'debug false']:
            debug = False
            client.debug = False
            print("Debug mode disabled")
            continue

        # Manual cookie refresh
        elif user_input.lower() == 'refresh':
            if client.refresh_cookies():
                print("Cookies refreshed successfully!")
            else:
                print("Failed to refresh cookies.")
            continue

        # Set chat ID
        elif user_input.lower().startswith('chat '):
            chat_id = user_input[5:].strip()
            print(f"Chat ID set to: {chat_id}")
            continue

        # Clear chat ID
        elif user_input.lower() == 'clear':
            chat_id = None
            print("Chat ID cleared. Starting a new conversation.")
            continue

        # Cookie management
        elif user_input.lower().startswith('cookie add '):
            cookie_str = user_input[11:].strip()
            if '=' in cookie_str:
                name, value = cookie_str.split('=', 1)
                cookies[name] = value
                client.cookies = cookies
                print(f"Added cookie: {name}={value}")
            else:
                print("Invalid cookie format. Use 'cookie add name=value'")
            continue
        elif user_input.lower() == 'cookie list':
            if cookies:
                print("\nCookies:")
                for name, value in cookies.items():
                    print(f"  {name}={value}")
            else:
                print("No cookies set")
            continue
        elif user_input.lower() == 'cookie clear':
            cookies = {}
            client.cookies = cookies
            print("All cookies cleared")
            continue

        # If not a command, send as a message
        if not user_input:
            continue

        # Send message
        response = client.send_message(user_input, chat_id=chat_id, focus=focus, tools=tools)

        if debug and response:
            print("\n\nFull response metadata:")
            print(json.dumps(response["metadata"], indent=2))

        # Update chat ID for continuing the conversation
        if response and not chat_id:
            chat_id = response['chat_id']

if __name__ == "__main__":
    main()
