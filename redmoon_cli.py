#!/usr/bin/env python3
"""
RedMoon API Command Line Interface

A comprehensive CLI for interacting with various AI services.
"""

import os
import sys
import argparse
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Try to import all available modules
try:
    from simple_scira_chat import SciraChat
except ImportError:
    SciraChat = None

try:
    from qwen_client import QwenAIClient
except ImportError:
    QwenAIClient = None

try:
    from chatgot_chat import ChatGotClient
except ImportError:
    ChatGotClient = None

try:
    from uncovr_client import UncovrClient
except ImportError:
    UncovrClient = None

try:
    from imagegen import generate_image as pixelmuse_generate
except ImportError:
    pixelmuse_generate = None

try:
    from generate_image import main as magicstudio_generate
except ImportError:
    magicstudio_generate = None

try:
    from voice_generator import generate_voice, download_audio
except ImportError:
    generate_voice = None
    download_audio = None

try:
    from blackbox_request import send_request as blackbox_request
except ImportError:
    blackbox_request = None


def print_header():
    """Print the application header."""
    header = """
    ╔═══════════════════════════════════════════╗
    ║             REDMOON API CLI               ║
    ║                                           ║
    ║  A comprehensive command-line interface   ║
    ║  for interacting with various AI services ║
    ╚═══════════════════════════════════════════╝
    """
    print_colored(header, Fore.CYAN, Style.BRIGHT)


def print_colored(text, color=Fore.WHITE, style=Style.NORMAL):
    """Print colored text using colorama."""
    print(f"{style}{color}{text}")


def print_menu():
    """Print the main menu options."""
    print("\n" + "="*50)
    print_colored("MAIN MENU", Fore.CYAN, Style.BRIGHT)
    print_colored("Please select a service:", Fore.YELLOW)

    # Chat services
    print_colored("\nChat Services:", Fore.GREEN)
    print("  1. Scira Chat")
    print("  2. Qwen Chat")
    print("  3. ChatGot Chat")
    print("  4. Uncovr Client")
    print("  5. Blackbox AI")

    # Generation services
    print_colored("\nGeneration Services:", Fore.GREEN)
    print("  6. Image Generation (PixelMuse)")
    print("  7. Image Generation (MagicStudio)")
    print("  8. Voice Generation")

    # Other options
    print_colored("\nOther Options:", Fore.GREEN)
    print("  0. Exit")
    print("  9. Clear Screen")
    print(" 10. Help")

    print("\n" + "="*50)


def get_user_choice(min_value=0, max_value=10):
    """Get a valid choice from the user."""
    while True:
        try:
            choice = input(f"{Fore.CYAN}Enter your choice [{min_value}-{max_value}]: {Style.RESET_ALL}")
            choice = int(choice)
            if min_value <= choice <= max_value:
                return choice
            else:
                print_colored(f"Please enter a number between {min_value} and {max_value}.", Fore.RED)
        except ValueError:
            print_colored("Please enter a valid number.", Fore.RED)


def run_scira_chat():
    """Run the Scira Chat client."""
    if SciraChat is None:
        print_colored("\nScira Chat module is not available.", Fore.RED)
        print_colored("Please make sure the 'simple_scira_chat.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    print_colored("\nScira Chat Models:", Fore.YELLOW)
    print("  1. Default")
    print("  2. Grok")
    print("  3. Claude")
    print("  4. Vision")

    model_choice = get_user_choice(1, 4)
    model_map = {1: "default", 2: "grok", 3: "claude", 4: "vision"}
    model = model_map[model_choice]

    # Create chat client
    client = SciraChat(model=model)

    # Print header
    print_colored("\nStarting Scira Chat...", Fore.GREEN)
    print_colored(f"Currently using model: {client.get_model()}", Fore.GREEN)
    print_colored("Type 'exit' to return to the main menu.", Fore.YELLOW)

    # Main chat loop
    while True:
        print("\n" + "="*50)
        print_colored("You:", Fore.GREEN, Style.BRIGHT)
        message = input("> ").strip()

        if not message:
            continue

        if message.lower() in ('exit', 'quit', 'q', 'back'):
            break

        # Send the message to the API
        print_colored("Scira is typing...", Fore.YELLOW)

        # Get the response
        response = client.chat(message)
        if not response:
            print_colored("Failed to get a response. Please try again.", Fore.RED)
            continue

        # Display the response
        print_colored("Scira:", Fore.CYAN, Style.BRIGHT)
        print(response)


def run_qwen_chat():
    """Run the Qwen Chat client."""
    if QwenAIClient is None:
        print_colored("\nQwen Chat module is not available.", Fore.RED)
        print_colored("Please make sure the 'qwen_client.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    # Initialize the client
    client = QwenAIClient()

    print_colored("\nStarting Qwen Chat...", Fore.GREEN)
    print_colored("Type 'exit' to return to the main menu, 'clear' to clear history.", Fore.YELLOW)

    while True:
        try:
            print("\n" + "="*50)
            print_colored("You:", Fore.GREEN, Style.BRIGHT)
            user_input = input("> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q", "back"]:
                break

            if user_input.lower() == "clear":
                client.clear_history()
                print_colored("Chat history cleared. Starting new conversation.", Fore.YELLOW)
                continue

            # Show processing message
            print_colored("Qwen is thinking...", Fore.YELLOW)

            # Send the message to the API
            response = client.send_message(user_input)

            if response["success"]:
                print_colored("Qwen:", Fore.CYAN, Style.BRIGHT)
                print(response["message"])
            else:
                print_colored(f"Error: {response['message']}", Fore.RED)

        except KeyboardInterrupt:
            print_colored("\nInterrupted by user.", Fore.RED)
            break
        except Exception as e:
            print_colored(f"Error: {str(e)}", Fore.RED)


def run_chatgot_chat():
    """Run the ChatGot Chat client."""
    if ChatGotClient is None:
        print_colored("\nChatGot Chat module is not available.", Fore.RED)
        print_colored("Please make sure the 'chatgot_chat.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    client = ChatGotClient()
    print_colored("\nStarting ChatGot Chat...", Fore.GREEN)
    print_colored("Using random device IDs to bypass rate limiting", Fore.YELLOW)
    print_colored("Type 'exit' to return to the main menu.", Fore.YELLOW)

    conversation_id = None

    while True:
        print("\n" + "="*50)
        print_colored("You:", Fore.GREEN, Style.BRIGHT)
        user_input = input("> ").strip()

        if user_input.lower() in ['exit', 'quit', 'q', 'back']:
            break

        if not user_input:
            continue

        print_colored("ChatGot is typing...", Fore.YELLOW)
        print_colored("Assistant:", Fore.CYAN, Style.BRIGHT)
        response, new_conversation_id = client.send_message(user_input)

        if response is None:
            print_colored("Failed to get a response. Please try again.", Fore.RED)
            continue

        # Update conversation ID if this is a new conversation
        if not conversation_id:
            conversation_id = new_conversation_id


def run_uncovr_client():
    """Run the Uncovr Client."""
    if UncovrClient is None:
        print_colored("\nUncovr Client module is not available.", Fore.RED)
        print_colored("Please make sure the 'uncovr_client.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    # Initialize with default settings
    cookies = {}
    debug = False
    chat_id = None
    focus = None
    tools = None

    print_colored("\nStarting Uncovr.app Chat...", Fore.GREEN)
    print_colored("Type 'exit' to return to the main menu, 'help' for commands.", Fore.YELLOW)

    # Initialize client
    client = UncovrClient(cookies=cookies, debug=debug)

    # Try to refresh cookies automatically at startup
    client.refresh_cookies()

    while True:
        print("\n" + "="*50)
        print_colored("You:", Fore.GREEN, Style.BRIGHT)
        user_input = input("> ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['exit', 'quit', 'q', 'back']:
            break

        if user_input.lower() == 'help':
            print_colored("\nAvailable commands:", Fore.CYAN)
            print_colored("  exit, quit - Return to main menu", Fore.CYAN)
            print_colored("  help - Show this help message", Fore.CYAN)
            continue

        print_colored("Uncovr is thinking...", Fore.YELLOW)

        # Send the message
        response = client.send_message(user_input, chat_id=chat_id)

        if response:
            print_colored("Uncovr:", Fore.CYAN, Style.BRIGHT)
            print(response["text"])

            # Update chat ID for conversation continuity
            chat_id = response.get("chat_id")
        else:
            print_colored("Failed to get a response. Please try again.", Fore.RED)


def run_pixelmuse_image_generation():
    """Run the PixelMuse image generation service."""
    if pixelmuse_generate is None:
        print_colored("\nPixelMuse image generation module is not available.", Fore.RED)
        print_colored("Please make sure the 'imagegen.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    print_colored("\nPixelMuse Image Generation", Fore.GREEN)

    # Get prompt from user
    print_colored("Enter image description:", Fore.YELLOW)
    prompt = input("> ").strip()

    if not prompt:
        print_colored("Prompt cannot be empty.", Fore.RED)
        return

    # Get model choice
    print_colored("\nSelect model:", Fore.YELLOW)
    print("  1. flux-schnell")
    print("  2. imagen-3-fast")
    print("  3. imagen-3")
    print("  4. recraft-v3")

    model_choice = get_user_choice(1, 4)
    model_map = {1: "flux-schnell", 2: "imagen-3-fast", 3: "imagen-3", 4: "recraft-v3"}
    model = model_map[model_choice]

    # Get aspect ratio
    print_colored("\nSelect aspect ratio:", Fore.YELLOW)
    print("  1. 1:1 (Square)")
    print("  2. 16:9 (Landscape)")
    print("  3. 9:16 (Portrait)")
    print("  4. 3:2")
    print("  5. 4:3")

    ratio_choice = get_user_choice(1, 5)
    ratio_map = {1: "1:1", 2: "16:9", 3: "9:16", 4: "3:2", 5: "4:3"}
    aspect_ratio = ratio_map[ratio_choice]

    print_colored("\nGenerating image...", Fore.YELLOW)

    # Generate the image
    result = pixelmuse_generate(
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        model=model
    )

    if result:
        print_colored("\nImage generated successfully!", Fore.GREEN)
        print_colored(f"Image URL: {result.get('output', 'No URL available')}", Fore.CYAN)
    else:
        print_colored("Failed to generate image.", Fore.RED)


def run_magicstudio_image_generation():
    """Run the MagicStudio image generation service."""
    if magicstudio_generate is None:
        print_colored("\nMagicStudio image generation module is not available.", Fore.RED)
        print_colored("Please make sure the 'generate_image.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    print_colored("\nMagicStudio Image Generation", Fore.GREEN)
    print_colored("This will save the generated image as 'generated_image.png'", Fore.YELLOW)

    # Call the main function from generate_image module
    magicstudio_generate()


def run_voice_generation():
    """Run the voice generation service."""
    if generate_voice is None or download_audio is None:
        print_colored("\nVoice generation module is not available.", Fore.RED)
        print_colored("Please make sure the 'voice_generator.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    print_colored("\nAI Voice Generator", Fore.GREEN)

    # Get text from user
    print_colored("Enter the text to convert to speech:", Fore.YELLOW)
    text = input("> ").strip()

    if not text:
        print_colored("Text cannot be empty.", Fore.RED)
        return

    # Get language
    print_colored("\nSelect language:", Fore.YELLOW)
    print("  1. English (en-US)")
    print("  2. Hindi (hi-IN)")
    print("  3. Spanish (es-ES)")
    print("  4. French (fr-FR)")
    print("  5. German (de-DE)")
    print("  6. Other (specify code)")

    lang_choice = get_user_choice(1, 6)
    lang_map = {1: "en-US", 2: "hi-IN", 3: "es-ES", 4: "fr-FR", 5: "de-DE"}

    if lang_choice == 6:
        print_colored("Enter language code (e.g., ja-JP for Japanese):", Fore.YELLOW)
        language = input("> ").strip()
    else:
        language = lang_map[lang_choice]

    print_colored("\nGenerating voice...", Fore.YELLOW)

    # Generate the voice
    result = generate_voice(text, language)

    if result['success']:
        print_colored("\nSuccess! Audio URL:", Fore.GREEN)
        print_colored(result['audio_url'], Fore.CYAN)

        print_colored("\nDownloading audio file...", Fore.YELLOW)

        # Generate filename using timestamp
        import time
        filename = f"generated_audio_{int(time.time())}.mp3"

        if download_audio(result['audio_url'], filename):
            print_colored(f"\nAudio saved as: {filename}", Fore.GREEN)
        else:
            print_colored("\nFailed to download audio file", Fore.RED)
    else:
        print_colored(f"\nError: {result['message']}", Fore.RED)


def run_blackbox_ai():
    """Run the Blackbox AI service."""
    if blackbox_request is None:
        print_colored("\nBlackbox AI module is not available.", Fore.RED)
        print_colored("Please make sure the 'blackbox_request.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    print_colored("\nBlackbox AI", Fore.GREEN)

    # Get message from user
    print_colored("Enter your message:", Fore.YELLOW)
    message = input("> ").strip()

    if not message:
        print_colored("Message cannot be empty.", Fore.RED)
        return

    # Ask about web search
    print_colored("\nEnable web search mode? (y/n):", Fore.YELLOW)
    web_search_input = input("> ").strip().lower()
    web_search = True if web_search_input == "y" else False

    # Send the request
    blackbox_request(message, web_search)


def print_help():
    """Print help information."""
    help_text = """
    RedMoon API CLI Help
    ===================

    This is a comprehensive command-line interface for interacting with various AI services.

    Available Services:
    - Chat Services: Scira, Qwen, ChatGot, Uncovr, Blackbox AI
    - Image Generation: PixelMuse, MagicStudio
    - Voice Generation

    Navigation:
    - Use numbers to select options from menus
    - Type 'exit', 'quit', or 'back' to return to previous menus
    - Type 'clear' in chat interfaces to clear conversation history
    - Press Ctrl+C to interrupt any operation

    For more information, visit the documentation or contact support.
    """
    print_colored(help_text, Fore.CYAN)


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print_header()


def main():
    """Main function to run the RedMoon API CLI."""
    parser = argparse.ArgumentParser(description="RedMoon API Command Line Interface")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    # Print header
    print_header()

    while True:
        # Display menu
        print_menu()

        # Get user choice
        choice = get_user_choice()

        # Process choice
        if choice == 0:
            print_colored("\nExiting RedMoon API CLI. Goodbye!", Fore.GREEN)
            break
        elif choice == 1:
            run_scira_chat()
        elif choice == 2:
            run_qwen_chat()
        elif choice == 3:
            run_chatgot_chat()
        elif choice == 4:
            run_uncovr_client()
        elif choice == 5:
            run_blackbox_ai()
        elif choice == 6:
            run_pixelmuse_image_generation()
        elif choice == 7:
            run_magicstudio_image_generation()
        elif choice == 8:
            run_voice_generation()
        elif choice == 9:
            clear_screen()
        elif choice == 10:
            print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\nProgram terminated by user.", Fore.RED)
        sys.exit(0)
