#!/usr/bin/env python3
import argparse
import sys
import os
from colorama import Fore, Style, init
from qwen_client import QwenAIClient

# Initialize colorama
init(autoreset=True)

def display_banner():
    """Display a banner for the application"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗
{Fore.CYAN}║                                                           ║
{Fore.CYAN}║  {Fore.YELLOW}  ██████  ██     ██ ███████ ███    ██     {Fore.CYAN}           ║
{Fore.CYAN}║  {Fore.YELLOW} ██    ██ ██     ██ ██      ████   ██     {Fore.CYAN}           ║
{Fore.CYAN}║  {Fore.YELLOW} ██    ██ ██  █  ██ █████   ██ ██  ██     {Fore.CYAN}           ║
{Fore.CYAN}║  {Fore.YELLOW} ██ ▄▄ ██ ██ ███ ██ ██      ██  ██ ██     {Fore.CYAN}           ║
{Fore.CYAN}║  {Fore.YELLOW}  ██████   ███ ███  ███████ ██   ████     {Fore.CYAN}           ║
{Fore.CYAN}║  {Fore.YELLOW}     ▀▀                                   {Fore.CYAN}           ║
{Fore.CYAN}║                                                           ║
{Fore.CYAN}║  {Fore.GREEN}Qwen AI Chat CLI - Interact with Qwen2.5-Max{Fore.CYAN}           ║
{Fore.CYAN}║  {Fore.WHITE}Type 'exit', 'quit', or Ctrl+C to exit{Fore.CYAN}                 ║
{Fore.CYAN}║  {Fore.WHITE}Type 'clear' to start a new conversation{Fore.CYAN}               ║
{Fore.CYAN}╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Qwen AI Chat CLI")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--message", "-m", type=str, help="Single message to send (non-interactive mode)")
    return parser.parse_args()

def format_response(response_text):
    """Format the AI response for better readability"""
    return f"{Fore.GREEN}Qwen AI: {Fore.WHITE}{response_text}"

def spinner_animation(seconds):
    """Display a spinner animation for the given number of seconds"""
    import itertools
    import time
    import threading
    import sys
    
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    stop_spinner = False
    
    def spin():
        sys.stdout.write(f"{Fore.YELLOW}Processing ")
        while not stop_spinner:
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b')
        sys.stdout.write(f"\r{' ' * 20}\r")  # Clear the spinner line
    
    spinner_thread = threading.Thread(target=spin)
    spinner_thread.start()
    
    time.sleep(seconds)
    stop_spinner = True
    spinner_thread.join()

def interactive_mode(client):
    """Run the chat client in interactive mode"""
    display_banner()
    
    print(f"{Fore.YELLOW}Initializing session...{Style.RESET_ALL}")
    client.refresh_cookies()
    print(f"{Fore.GREEN}Session initialized. You can start chatting!{Style.RESET_ALL}\n")
    
    while True:
        try:
            user_input = input(f"{Fore.CYAN}You: {Style.RESET_ALL}").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
                break
                
            if user_input.lower() == "clear":
                client.clear_history()
                print(f"\n{Fore.YELLOW}Chat history cleared. Starting new conversation.{Style.RESET_ALL}\n")
                continue
            
            # Show a spinner while waiting for the response
            print()  # Add a newline for better formatting
            spinner_animation(1)  # Simulate processing time
            
            # Send the message to the API
            response = client.send_message(user_input)
            
            if response["success"]:
                print(format_response(response["message"]))
            else:
                print(f"\n{Fore.RED}Error: {response['message']}{Style.RESET_ALL}")
            
            print()  # Add a newline for better formatting
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Interrupted by user. Goodbye!{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}")
            continue

def single_message_mode(client, message):
    """Send a single message and display the response"""
    print(f"{Fore.YELLOW}Initializing session...{Style.RESET_ALL}")
    client.refresh_cookies()
    
    print(f"\n{Fore.CYAN}You: {message}{Style.RESET_ALL}")
    
    # Show a spinner while waiting for the response
    spinner_animation(1)  # Simulate processing time
    
    # Send the message to the API
    response = client.send_message(message)
    
    if response["success"]:
        print(format_response(response["message"]))
    else:
        print(f"\n{Fore.RED}Error: {response['message']}{Style.RESET_ALL}")

def main():
    """Main function to run the application"""
    args = parse_arguments()
    
    # Initialize the client
    client = QwenAIClient(debug=args.debug)
    
    if args.message:
        # Single message mode
        single_message_mode(client, args.message)
    else:
        # Interactive mode
        interactive_mode(client)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Program terminated by user.{Style.RESET_ALL}")
        sys.exit(0)
