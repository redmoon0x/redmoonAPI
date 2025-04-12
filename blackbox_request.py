import requests
import json
import argparse
import sys
import time
from colorama import init, Fore, Style
from tqdm import tqdm
import pyfiglet
import os
import re

# Initialize colorama
init(autoreset=True)

url = "https://www.blackbox.ai/api/chat"

# Setup headers as observed from the network request
headers = {
    "accept": "*/*",
    "content-type": "application/json",
    "cookie": "sessionId=fcb67012-84db-4ffc-b587-557648f03e11; render_app_version_affinity=dep-cvgek6bv2p9s73dkemc0; __Host-authjs.csrf-token=123a748c0d47d91b4c6f8873f92aedfabd68ddf7be48a89fc20ba0ae5a06d493|2775cb244f70afccbaca5417e36d1fea389bf9fff4dadb76180d71120329d2ec; intercom-id-x55eda6t=3dadc7e4-75c2-4868-873e-34b03e7beeee; intercom-device-id-x55eda6t=046468bd-4bdb-4b76-be7c-5401018b16d1; __Secure-authjs.callback-url=https%3A%2F%2Fwww.blackbox.ai%2F; intercom-session-x55eda6t=MlBmcDJVNkxlbC9kaDNxYTNRcHBlZERmM24xaWc1R3ZHblVBMDJFdWw5a3JhWWl1NDAyc2Z1a3VTMzdzQjJmS3NpM2hCcXBPUlMxTXd1L2ZhdS8xM0tTdWNJODRHTWZmVFRGbTlJbEkvQmc9LS1ZRlZKOWYrYW9lYnNvUnpqeGlWR2NRPT0=--5ad4fc417f7d6f4348f23e74f055daebfcf2ee9f",
    "origin": "https://www.blackbox.ai",
    "referer": "https://www.blackbox.ai/",
    "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Brave\";v=\"134\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

def display_banner():
    """Display an ASCII art banner for the application"""
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = pyfiglet.figlet_format("BLACKBOX AI", font="slant")
    print(f"{Fore.CYAN}{banner}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Command Line Interface v1.0{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}=" * 60 + f"{Style.RESET_ALL}\n")

def spinner_animation(seconds):
    """Show a spinner animation for the given number of seconds"""
    for _ in tqdm(range(int(seconds * 10)), desc=f"{Fore.GREEN}Processing request", ncols=100):
        time.sleep(0.1)

def format_response(response_text):
    """Format the response text for better readability"""
    try:
        # Check if the response contains embedded JSON in a specific format
        web_search_pattern = r'\$~~~\$(.*?)\$~~~\$'
        web_search_match = re.search(web_search_pattern, response_text)
        
        if web_search_match:
            # Extract and parse the web search JSON
            web_search_json = web_search_match.group(1)
            try:
                web_search_results = json.loads(web_search_json)
                
                # Extract the actual response text (after the web search data)
                main_text = response_text.split('$~~~$', 2)[-1].strip()
                
                # Format the response with the web search results
                formatted_text = f"{Fore.GREEN}AI Response:{Style.RESET_ALL}\n{main_text}\n"
                
                # Add formatted web search results
                formatted_text += f"\n{Fore.BLUE}Web Search Results:{Style.RESET_ALL}\n"
                for idx, result in enumerate(web_search_results, 1):
                    formatted_text += f"\n{Fore.YELLOW}[{idx}] {result.get('title', 'No Title')}{Style.RESET_ALL}\n"
                    formatted_text += f"    {Fore.CYAN}URL:{Style.RESET_ALL} {result.get('link', 'No URL')}\n"
                    formatted_text += f"    {Fore.WHITE}{result.get('snippet', 'No snippet available')}{Style.RESET_ALL}\n"
                    if result.get('date'):
                        formatted_text += f"    {Fore.MAGENTA}Date:{Style.RESET_ALL} {result.get('date')}\n"
                
                return formatted_text
            except json.JSONDecodeError:
                # If the embedded JSON couldn't be parsed, continue with standard parsing
                pass
        
        # Try standard JSON response format
        response_data = json.loads(response_text)
        
        if "response" not in response_data:
            return f"{Fore.RED}Error: Invalid response format{Style.RESET_ALL}"
        
        result = response_data["response"]
        
        # Format normal response
        formatted_text = f"{Fore.GREEN}AI Response:{Style.RESET_ALL}\n{result}"
        
        # Check for web search results in standard format
        if "webSearch" in response_data and response_data["webSearch"]:
            formatted_text += f"\n\n{Fore.BLUE}Web Search Results:{Style.RESET_ALL}\n"
            for idx, result in enumerate(response_data["webSearch"], 1):
                formatted_text += f"\n{Fore.YELLOW}[{idx}] {result.get('title', 'No Title')}{Style.RESET_ALL}\n"
                formatted_text += f"    {Fore.CYAN}URL:{Style.RESET_ALL} {result.get('url', 'No URL')}\n"
                formatted_text += f"    {Fore.WHITE}{result.get('snippet', 'No snippet available')}{Style.RESET_ALL}\n"
        
        return formatted_text
    
    except json.JSONDecodeError:
        # If it's not a JSON response, try to format it as plain text with possible embedded web search results
        try:
            web_search_pattern = r'\$~~~\$(.*?)\$~~~\$'
            web_search_match = re.search(web_search_pattern, response_text)
            
            if web_search_match:
                # Extract web search JSON
                web_search_json = web_search_match.group(1)
                web_search_results = json.loads(web_search_json)
                
                # Get the text part (response) that follows the web search data
                text_parts = response_text.split('$~~~$')
                if len(text_parts) > 2:
                    main_text = text_parts[2].strip()
                else:
                    main_text = "No response text found."
                
                # Format the response
                formatted_text = f"{Fore.GREEN}AI Response:{Style.RESET_ALL}\n{main_text}\n"
                
                # Add formatted web search results
                formatted_text += f"\n{Fore.BLUE}Web Search Results:{Style.RESET_ALL}\n"
                for idx, result in enumerate(web_search_results, 1):
                    formatted_text += f"\n{Fore.YELLOW}[{idx}] {result.get('title', 'No Title')}{Style.RESET_ALL}\n"
                    formatted_text += f"    {Fore.CYAN}URL:{Style.RESET_ALL} {result.get('link', 'No URL')}\n"
                    formatted_text += f"    {Fore.WHITE}{result.get('snippet', 'No snippet available')}{Style.RESET_ALL}\n"
                    if result.get('date'):
                        formatted_text += f"    {Fore.MAGENTA}Date:{Style.RESET_ALL} {result.get('date')}\n"
                
                return formatted_text
            else:
                return f"{Fore.WHITE}{response_text}{Style.RESET_ALL}"
        except Exception as e:
            return f"{Fore.RED}Error processing plain text response: {str(e)}{Style.RESET_ALL}\n{response_text}"
    
    except Exception as e:
        return f"{Fore.RED}Error processing response: {str(e)}{Style.RESET_ALL}\n{response_text}"

def send_request_api(user_message, web_search=False):
    """Send request to BlackBox AI API and return raw response"""
    payload = {
        "messages": [
            {
                "role": "user",
                "content": user_message,
                "id": "fUhMZRP"
            }
        ],
        "agentMode": {},
        "beastMode": False,
        "clickedAnswer2": False,
        "clickedAnswer3": False,
        "clickedForceWebSearch": False,
        "codeInterpreterMode": False,
        "codeModelMode": True,
        "customProfile": {
            "name": "",
            "occupation": "",
            "traits": [],
            "additionalInfo": "",
            "enableNewChats": False
        },
        "deepSearchMode": False,
        "domains": None,
        "githubToken": "",
        "id": "pmcYMRM",
        "imageGenerationMode": False,
        "isChromeExt": False,
        "isMemoryEnabled": False,
        "isMicMode": False,
        "isPremium": False,
        "maxTokens": 1024,
        "mobileClient": False,
        "playgroundTemperature": None,
        "playgroundTopP": None,
        "previewToken": None,
        "reasoningMode": False,
        "session": None,
        "subscriptionCache": None,
        "trendingAgentMode": {},
        "userId": None,
        "userSelectedModel": None,
        "userSystemPrompt": None,
        "validated": "00f37b34-a166-4efb-bce5-1312d87f2f94",
        "visitFromDelta": False,
        "vscodeClient": False,
        "webSearchModePrompt": web_search
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.text
    except Exception as e:
        raise Exception(f"Error occurred: {str(e)}")

def format_response_json(response_text):
    """Format the response text as JSON for the web UI"""
    try:
        # Try standard JSON response format
        response_data = json.loads(response_text)
        
        if "response" not in response_data:
            return {"response": "Error: Invalid response format", "web_search": []}
        
        result = response_data["response"]
        web_search_results = []
        
        # Check for web search results in standard format
        if "webSearch" in response_data and response_data["webSearch"]:
            web_search_results = [
                {
                    "title": result.get("title", "No Title"),
                    "url": result.get("url", "No URL"),
                    "snippet": result.get("snippet", "No snippet available")
                }
                for result in response_data["webSearch"]
            ]
        
        return {"response": result, "web_search": web_search_results}
    
    except json.JSONDecodeError:
        # If it's not a JSON response, try to format it as plain text with possible embedded web search results
        try:
            web_search_pattern = r'\$~~~\$(.*?)\$~~~\$'
            web_search_match = re.search(web_search_pattern, response_text)
            
            if web_search_match:
                # Extract web search JSON
                web_search_json = web_search_match.group(1)
                web_search_results = json.loads(web_search_json)
                
                # Get the text part (response) that follows the web search data
                text_parts = response_text.split('$~~~$')
                if len(text_parts) > 2:
                    main_text = text_parts[2].strip()
                else:
                    main_text = "No response text found."
                
                formatted_web_results = [
                    {
                        "title": result.get("title", "No Title"),
                        "url": result.get("link", "No URL"),
                        "snippet": result.get("snippet", "No snippet available")
                    }
                    for result in web_search_results
                ]
                
                return {"response": main_text, "web_search": formatted_web_results}
            else:
                return {"response": response_text, "web_search": []}
        except Exception as e:
            return {"response": f"Error processing response: {str(e)}", "web_search": []}
    
    except Exception as e:
        return {"response": f"Error processing response: {str(e)}", "web_search": []}

def send_request(user_message, web_search=False):
    """Send request to BlackBox AI API"""
    try:
        print(f"\n{Fore.CYAN}Sending request to BlackBox AI...{Style.RESET_ALL}")
        spinner_animation(2)  # Simulate processing time
        
        response_text = send_request_api(user_message, web_search)
        
        print(f"\n{Fore.YELLOW}{'=' * 60}{Style.RESET_ALL}")
        print(format_response(response_text))
        print(f"{Fore.YELLOW}{'=' * 60}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}Error occurred: {str(e)}{Style.RESET_ALL}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="BlackBox AI Command Line Tool")
    parser.add_argument("-m", "--message", type=str, help="Message to send to BlackBox AI")
    parser.add_argument("-w", "--websearch", action="store_true", help="Enable web search mode")
    return parser.parse_args()

def main():
    """Main function to run the application"""
    display_banner()
    
    args = parse_arguments()
    
    if args.message:
        user_message = args.message
    else:
        user_message = input(f"{Fore.GREEN}Enter your message: {Style.RESET_ALL}").strip()
        if not user_message:
            user_message = "hi"
    
    web_search = args.websearch
    
    if not args.websearch and not args.message:
        web_search_input = input(f"{Fore.GREEN}Enable web search mode? (y/n): {Style.RESET_ALL}").strip().lower()
        web_search = True if web_search_input == "y" else False
    
    send_request(user_message, web_search)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Program terminated by user.{Style.RESET_ALL}")
        sys.exit(0)
