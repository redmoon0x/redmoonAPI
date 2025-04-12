import requests
import json
import sseclient
import time
import random

class ChatGotClient:
    @staticmethod
    def generate_device_id():
        # Generate a random device ID following the pattern: 24 hex characters
        # Example pattern: "626ce638323457696e333235"
        hex_chars = '0123456789abcdef'
        return ''.join(random.choice(hex_chars) for _ in range(24))

    def __init__(self):
        self.base_url = "https://api-preview.chatgot.io/api/v1/chat-got/conversations"
        self.device_id = self.generate_device_id()  # Generate new device ID for each session
        self.headers = {
            "accept": "text/event-stream",
            "accept-language": "en-US,en;q=0.8",
            "content-type": "application/json",
            "origin": "https://www.chatgot.io",
            "referer": "https://www.chatgot.io/",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Brave";v="134"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        }

    def send_message(self, message, model_id=1):
        # Generate new device ID for each request to help bypass rate limiting
        self.device_id = self.generate_device_id()
        
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "model_id": model_id,
            "device_id": self.device_id
        }

        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=data,
            stream=True
        )

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return None, None

        client = sseclient.SSEClient(response)
        full_response = ""
        conversation_id = None

        try:
            for event in client.events():
                try:
                    event_data = json.loads(event.data)
                    
                    # Handle initial conversation ID message
                    if event_data["type"] == "chat" and event_data["code"] == 201:
                        conversation_id = event_data["data"]["c_id"]
                        continue
                    
                    # Handle content messages
                    if event_data["type"] == "chat" and event_data["code"] == 202:
                        if event_data["data"]["content"]:
                            print(event_data["data"]["content"], end="", flush=True)
                            full_response += event_data["data"]["content"]
                    
                    # Handle completion message
                    elif event_data["type"] == "chat" and event_data["code"] == 203:
                        if event_data["data"]["content"] == "[DONE]":
                            break

                except json.JSONDecodeError:
                    continue

            print()  # New line after response
            return full_response, conversation_id
        
        finally:
            client.close()
            response.close()

def main():
    client = ChatGotClient()
    print("ChatGot CLI (Type 'quit' to exit)")
    print("Using random device IDs to bypass rate limiting")
    print("-" * 50)

    conversation_id = None

    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            break
        
        if not user_input:
            continue

        print("\nAssistant: ", end="")
        response, new_conversation_id = client.send_message(user_input)
        
        if response is None:
            continue

        # Update conversation ID if this is a new conversation
        if not conversation_id:
            conversation_id = new_conversation_id

if __name__ == "__main__":
    main()
