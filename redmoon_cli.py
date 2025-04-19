#!/usr/bin/env python3
"""
RedMoon API Command Line Interface

A comprehensive CLI for interacting with various AI services.
"""

import os
import sys
import time
import argparse
import shutil
from colorama import Fore, Style, Back, init

# Initialize colorama
init(autoreset=True)

# Get terminal size
terminal_width, terminal_height = shutil.get_terminal_size()

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
    from venice_client import MistralSmall, LlamaAkash, FluentlyXL, FluxStandard
except ImportError:
    MistralSmall = None
    LlamaAkash = None
    FluentlyXL = None
    FluxStandard = None

try:
    from mitraai_image import MitraAI
except ImportError:
    MitraAI = None

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

try:
    from phi4_chat import Phi4ChatClient
except ImportError:
    Phi4ChatClient = None


def print_header():
    """Print the application header with ASCII art."""
    # Clear screen first
    clear_screen()

    # ASCII art logo
    logo = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║  ██████╗ ███████╗██████╗ ███╗   ███╗ ██████╗  ██████╗ ███╗   ║
    ║  ██╔══██╗██╔════╝██╔══██╗████╗ ████║██╔═══██╗██╔═══██╗████╗  ║
    ║  ██████╔╝█████╗  ██║  ██║██╔████╔██║██║   ██║██║   ██║██╔██╗ ║
    ║  ██╔══██╗██╔══╝  ██║  ██║██║╚██╔╝██║██║   ██║██║   ██║██║╚██╗║
    ║  ██║  ██║███████╗██████╔╝██║ ╚═╝ ██║╚██████╔╝╚██████╔╝██║ ╚██║║
    ║  ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝║
    ║                                                              ║
    ╚═══════════════════════════════════════════════════════════════╝
    """

    # Center the logo
    centered_logo = '\n'.join(line.center(terminal_width) for line in logo.split('\n'))

    # Print the logo with a gradient effect
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    lines = centered_logo.split('\n')

    for i, line in enumerate(lines):
        color = colors[i % len(colors)]
        print(f"{Style.BRIGHT}{color}{line}")

    # Subtitle
    subtitle = "[ Advanced AI Interaction Platform ]"
    centered_subtitle = subtitle.center(terminal_width)
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{centered_subtitle}")

    # GitHub info
    github_info = "github.com/redmoon0x"
    centered_github = github_info.center(terminal_width)
    print(f"{Fore.CYAN}{centered_github}")

    # Version and info
    version_info = "v1.0.0 | Developed by RedMoon AI Team"
    centered_version = version_info.center(terminal_width)
    print(f"{Fore.LIGHTBLACK_EX}{centered_version}")

    # Decorative line
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'═' * terminal_width}\n")


def print_colored(text, color=Fore.WHITE, style=Style.NORMAL, background=None):
    """Print colored text using colorama with optional background."""
    bg = background if background else ""
    print(f"{style}{color}{bg}{text}")


def print_spinner(text, duration=2, color=Fore.CYAN):
    """Display a spinner animation with text."""
    spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    i = 0

    while time.time() < end_time:
        sys.stdout.write(f"\r{color}{spinner_chars[i % len(spinner_chars)]} {text}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1

    sys.stdout.write(f"\r{' ' * (len(text) + 2)}\r")
    sys.stdout.flush()


def print_menu():
    """Print the main menu options with a modern UI."""
    # Menu title
    menu_title = "MAIN MENU"
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.BLUE} {menu_title} {Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Select a service by entering its number{Style.RESET_ALL}")

    # Create a box for the menu
    box_width = terminal_width - 10

    # Chat services section
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.GREEN} 💬 CHAT SERVICES {Style.RESET_ALL}")
    print(f"{Fore.CYAN}┌{'─' * (box_width - 2)}┐")
    print(f"{Fore.CYAN}│{' ' * (box_width - 2)}│")
    print(f"{Fore.CYAN}│{Fore.WHITE}  1. {Fore.CYAN}🔮 {Fore.WHITE}Scira Chat{' ' * (box_width - 18)}│")
    print(f"{Fore.CYAN}│{Fore.WHITE}  2. {Fore.CYAN}🌐 {Fore.WHITE}Qwen Chat{' ' * (box_width - 18)}│")
    print(f"{Fore.CYAN}│{Fore.WHITE}  3. {Fore.CYAN}💭 {Fore.WHITE}ChatGot Chat{' ' * (box_width - 21)}│")
    print(f"{Fore.CYAN}│{Fore.WHITE}  4. {Fore.CYAN}🔍 {Fore.WHITE}Uncovr Client{' ' * (box_width - 22)}│")
    print(f"{Fore.CYAN}│{Fore.WHITE}  5. {Fore.CYAN}⚡ {Fore.WHITE}Blackbox AI{' ' * (box_width - 19)}│")
    print(f"{Fore.CYAN}│{Fore.WHITE}  6. {Fore.CYAN}🧠 {Fore.WHITE}Mistral Small 3.1 24B{' ' * (box_width - 29)}│")
    print(f"{Fore.CYAN}│{Fore.WHITE}  7. {Fore.CYAN}🦙 {Fore.WHITE}Llama 3.2 3B Akash{' ' * (box_width - 26)}│")
    print(f"{Fore.CYAN}│{Fore.WHITE}  8. {Fore.CYAN}🔷 {Fore.WHITE}Phi 4 Chat{' ' * (box_width - 18)}│")
    print(f"{Fore.CYAN}│{' ' * (box_width - 2)}│")
    print(f"{Fore.CYAN}└{'─' * (box_width - 2)}┘")

    # Generation services section
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.MAGENTA} 🎨 GENERATION SERVICES {Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}┌{'─' * (box_width - 2)}┐")
    print(f"{Fore.MAGENTA}│{' ' * (box_width - 2)}│")
    print(f"{Fore.MAGENTA}│{Fore.WHITE}  9. {Fore.MAGENTA}🖼️ {Fore.WHITE}Image Generation (PixelMuse){' ' * (box_width - 36)}│")
    print(f"{Fore.MAGENTA}│{Fore.WHITE} 10. {Fore.MAGENTA}🎭 {Fore.WHITE}Image Generation (MagicStudio){' ' * (box_width - 37)}│")
    print(f"{Fore.MAGENTA}│{Fore.WHITE} 11. {Fore.MAGENTA}🌄 {Fore.WHITE}Image Generation (Fluently XL){' ' * (box_width - 38)}│")
    print(f"{Fore.MAGENTA}│{Fore.WHITE} 12. {Fore.MAGENTA}✨ {Fore.WHITE}Image Generation (Flux Standard){' ' * (box_width - 40)}│")
    print(f"{Fore.MAGENTA}│{Fore.WHITE} 13. {Fore.MAGENTA}🌙 {Fore.WHITE}Image Generation (MitraAI){' ' * (box_width - 35)}│")
    print(f"{Fore.MAGENTA}│{Fore.WHITE} 14. {Fore.MAGENTA}🔊 {Fore.WHITE}Voice Generation{' ' * (box_width - 25)}│")
    print(f"{Fore.MAGENTA}│{' ' * (box_width - 2)}│")
    print(f"{Fore.MAGENTA}└{'─' * (box_width - 2)}┘")

    # Other options section
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.RED} ⚙️ SYSTEM OPTIONS {Style.RESET_ALL}")
    print(f"{Fore.RED}┌{'─' * (box_width - 2)}┐")
    print(f"{Fore.RED}│{' ' * (box_width - 2)}│")
    print(f"{Fore.RED}│{Fore.WHITE}  0. {Fore.RED}🚪 {Fore.WHITE}Exit{' ' * (box_width - 13)}│")
    print(f"{Fore.RED}│{Fore.WHITE} 15. {Fore.RED}🧹 {Fore.WHITE}Clear Screen{' ' * (box_width - 21)}│")
    print(f"{Fore.RED}│{Fore.WHITE} 16. {Fore.RED}❓ {Fore.WHITE}Help{' ' * (box_width - 13)}│")
    print(f"{Fore.RED}│{' ' * (box_width - 2)}│")
    print(f"{Fore.RED}└{'─' * (box_width - 2)}┘")

    # Status bar at the bottom
    current_time = time.strftime("%H:%M:%S")
    status = f"System Ready | Time: {current_time} | Press Ctrl+C to exit anytime"
    print(f"\n{Style.BRIGHT}{Fore.BLACK}{Back.WHITE} {status} {Style.RESET_ALL}")


def get_user_choice(min_value=0, max_value=16):
    """Get a valid choice from the user with improved UI."""
    prompt = f"\n{Style.BRIGHT}{Fore.CYAN}┌─ Enter your choice [{min_value}-{max_value}]\n└─❯ {Style.RESET_ALL}"

    while True:
        try:
            choice = input(prompt)
            choice = int(choice)
            if min_value <= choice <= max_value:
                # Show a brief loading animation
                print_spinner("Processing your selection...", 0.5)
                return choice
            else:
                print(f"{Fore.RED}⚠️ Please enter a number between {min_value} and {max_value}.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}⚠️ Please enter a valid number.{Style.RESET_ALL}")


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
    # Print stylish header for the chat
    model_name = client.get_model()
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.GREEN} SCIRA CHAT - {model_name.upper()} {Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'exit' to return to the main menu{Style.RESET_ALL}")

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
        print_spinner("Scira is thinking...", 1.5, Fore.YELLOW)

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

    # Print stylish header for the chat
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.GREEN} QWEN CHAT {Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'exit' to return to the main menu, 'clear' to clear history{Style.RESET_ALL}")

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
            print_spinner("Qwen is thinking...", 1.5, Fore.YELLOW)

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
    # Print stylish header for the chat
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.GREEN} CHATGOT CHAT {Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Using random device IDs to bypass rate limiting{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'exit' to return to the main menu{Style.RESET_ALL}")

    conversation_id = None

    while True:
        print("\n" + "="*50)
        print_colored("You:", Fore.GREEN, Style.BRIGHT)
        user_input = input("> ").strip()

        if user_input.lower() in ['exit', 'quit', 'q', 'back']:
            break

        if not user_input:
            continue

        print_spinner("ChatGot is thinking...", 1.5, Fore.YELLOW)
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

    # Print stylish header for the chat
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.GREEN} UNCOVR CHAT {Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'exit' to return to the main menu, 'help' for commands{Style.RESET_ALL}")

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

        print_spinner("Uncovr is thinking...", 1.5, Fore.YELLOW)

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

    # Print stylish header
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.MAGENTA} PIXELMUSE IMAGE GENERATION {Style.RESET_ALL}")

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

    print_spinner("Generating image with PixelMuse...", 1.5, Fore.MAGENTA)

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


def run_fluently_xl():
    """Run the Fluently XL Final image generation service."""
    if FluentlyXL is None:
        print_colored("\nFluently XL Final image generation module is not available.", Fore.RED)
        print_colored("Please make sure the 'venice_client.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    # Print stylish header
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.MAGENTA} FLUENTLY XL IMAGE GENERATION {Style.RESET_ALL}")

    # Get prompt from user
    print_colored("Enter image description:", Fore.YELLOW)
    prompt = input("> ").strip()

    if not prompt:
        print_colored("Prompt cannot be empty.", Fore.RED)
        return

    # Get aspect ratio choice
    print_colored("\nSelect aspect ratio:", Fore.YELLOW)
    print("  1. 1:1 (Square)")
    print("  2. 16:9 (Landscape)")
    print("  3. 9:16 (Portrait)")
    print("  4. 4:3")
    print("  5. 3:4")

    ratio_choice = get_user_choice(1, 5)
    ratio_map = {1: "1:1", 2: "16:9", 3: "9:16", 4: "4:3", 5: "3:4"}
    aspect_ratio = ratio_map[ratio_choice]

    # Get negative prompt (optional)
    print_colored("\nEnter negative prompt (optional):", Fore.YELLOW)
    negative_prompt = input("> ").strip()

    print_spinner("Generating image with Fluently XL...", 1.5, Fore.MAGENTA)

    # Initialize the client
    client = FluentlyXL(debug=False)

    try:
        # Generate the image
        image_path = client.generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt
        )

        print_colored("\nImage generated successfully!", Fore.GREEN)
        print_colored(f"Image saved to: {image_path}", Fore.CYAN)
    except Exception as e:
        print_colored(f"\nError generating image: {str(e)}", Fore.RED)


def run_flux_standard():
    """Run the Flux Standard image generation service."""
    if FluxStandard is None:
        print_colored("\nFlux Standard image generation module is not available.", Fore.RED)
        print_colored("Please make sure the 'venice_client.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    # Print stylish header
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.MAGENTA} FLUX STANDARD IMAGE GENERATION {Style.RESET_ALL}")

    # Get prompt from user
    print_colored("Enter image description:", Fore.YELLOW)
    prompt = input("> ").strip()

    if not prompt:
        print_colored("Prompt cannot be empty.", Fore.RED)
        return

    # Get aspect ratio choice
    print_colored("\nSelect aspect ratio:", Fore.YELLOW)
    print("  1. 1:1 (Square)")
    print("  2. 16:9 (Landscape)")
    print("  3. 9:16 (Portrait)")
    print("  4. 4:3")
    print("  5. 3:4")

    ratio_choice = get_user_choice(1, 5)
    ratio_map = {1: "1:1", 2: "16:9", 3: "9:16", 4: "4:3", 5: "3:4"}
    aspect_ratio = ratio_map[ratio_choice]

    # Get negative prompt (optional)
    print_colored("\nEnter negative prompt (optional):", Fore.YELLOW)
    negative_prompt = input("> ").strip()

    print_spinner("Generating image with Flux Standard...", 1.5, Fore.MAGENTA)

    # Initialize the client
    client = FluxStandard(debug=False)

    try:
        # Generate the image
        image_path = client.generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            negative_prompt=negative_prompt
        )

        print_colored("\nImage generated successfully!", Fore.GREEN)
        print_colored(f"Image saved to: {image_path}", Fore.CYAN)
    except Exception as e:
        print_colored(f"\nError generating image: {str(e)}", Fore.RED)


def run_mitraai_image_generation():
    """Run the MitraAI image generation service."""
    if MitraAI is None:
        print_colored("\nMitraAI image generation module is not available.", Fore.RED)
        print_colored("Please make sure the 'mitraai_image.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    # Print stylish header
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.MAGENTA} MITRAAI IMAGE GENERATION {Style.RESET_ALL}")

    # Get prompt from user
    print_colored("Enter image description:", Fore.YELLOW)
    prompt = input("> ").strip()

    if not prompt:
        print_colored("Prompt cannot be empty.", Fore.RED)
        return

    print_spinner("Generating image with MitraAI...", 1.5, Fore.MAGENTA)

    # Initialize the client
    client = MitraAI(debug=False)

    try:
        # Generate the image
        image_path = client.generate_image(prompt=prompt)

        print_colored("\nImage generated successfully!", Fore.GREEN)
        print_colored(f"Image saved to: {image_path}", Fore.CYAN)
    except Exception as e:
        print_colored(f"\nError generating image: {str(e)}", Fore.RED)


def run_voice_generation():
    """Run the voice generation service."""
    if generate_voice is None or download_audio is None:
        print_colored("\nVoice generation module is not available.", Fore.RED)
        print_colored("Please make sure the 'voice_generator.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    # Print stylish header
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.MAGENTA} AI VOICE GENERATOR {Style.RESET_ALL}")

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

    print_spinner("Generating voice...", 1.5, Fore.YELLOW)

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

    # Print stylish header
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.GREEN} BLACKBOX AI {Style.RESET_ALL}")

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
    print_spinner("Blackbox AI is processing your request...", 1.5, Fore.YELLOW)
    blackbox_request(message, web_search)


def run_mistral_small():
    """Run the Mistral Small 3.1 24B client."""
    if MistralSmall is None:
        print_colored("\nMistral Small 3.1 24B module is not available.", Fore.RED)
        print_colored("Please make sure the 'venice_client.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    # Initialize the client
    client = MistralSmall(debug=False)

    # Print stylish header for the chat
    model_name = client.get_model()
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.GREEN} MISTRAL CHAT - {model_name} {Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'exit' to return to the main menu, 'clear' to clear history{Style.RESET_ALL}")

    # Main chat loop
    while True:
        print("\n" + "="*50)
        print_colored("You:", Fore.GREEN, Style.BRIGHT)
        message = input("> ").strip()

        if not message:
            continue

        if message.lower() in ('exit', 'quit', 'q', 'back'):
            break

        if message.lower() == 'clear':
            client.clear_history()
            print_colored("Chat history cleared. Starting new conversation.", Fore.YELLOW)
            continue

        # Send the message to the API
        print_spinner("Mistral is thinking...", 1.5, Fore.YELLOW)

        # Get the response
        response = client.send_message(message)
        if not response:
            print_colored("Failed to get a response. Please try again.", Fore.RED)
            continue

        # Display the response
        print_colored("Mistral:", Fore.CYAN, Style.BRIGHT)
        print(response)


def run_llama_akash():
    """Run the Llama 3.2 3B Akash client."""
    if LlamaAkash is None:
        print_colored("\nLlama 3.2 3B Akash module is not available.", Fore.RED)
        print_colored("Please make sure the 'venice_client.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    # Initialize the client
    client = LlamaAkash(debug=False)

    # Print stylish header for the chat
    model_name = client.get_model()
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.GREEN} LLAMA CHAT - {model_name} {Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'exit' to return to the main menu, 'clear' to clear history{Style.RESET_ALL}")

    # Main chat loop
    while True:
        print("\n" + "="*50)
        print_colored("You:", Fore.GREEN, Style.BRIGHT)
        message = input("> ").strip()

        if not message:
            continue

        if message.lower() in ('exit', 'quit', 'q', 'back'):
            break

        if message.lower() == 'clear':
            client.clear_history()
            print_colored("Chat history cleared. Starting new conversation.", Fore.YELLOW)
            continue

        # Send the message to the API
        print_spinner("Llama is thinking...", 1.5, Fore.YELLOW)

        # Get the response
        response = client.send_message(message)
        if not response:
            print_colored("Failed to get a response. Please try again.", Fore.RED)
            continue

        # Display the response
        print_colored("Llama:", Fore.CYAN, Style.BRIGHT)
        print(response)


def run_phi4_chat():
    """Run the Phi4 Chat client."""
    if Phi4ChatClient is None:
        print_colored("\nPhi4 Chat module is not available.", Fore.RED)
        print_colored("Please make sure the 'phi4_chat.py' module is in the same directory.", Fore.YELLOW)
        input("\nPress Enter to return to the main menu...")
        return

    # Create chat client
    client = Phi4ChatClient()

    # Print header
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.BLUE} PHI4 CHAT {Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'exit' to return to the main menu, 'clear' to clear history{Style.RESET_ALL}")

    # Main chat loop
    while True:
        print("\n" + "="*50)
        print_colored("You:", Fore.GREEN, Style.BRIGHT)
        message = input("> ").strip()

        if not message:
            continue

        if message.lower() in ('exit', 'quit', 'q', 'back'):
            break

        if message.lower() == 'clear':
            client.clear_history()
            print_colored("Chat history cleared. Starting new conversation.", Fore.YELLOW)
            continue

        # Send the message to the API
        print_spinner("Phi4 is thinking...", 1.5, Fore.YELLOW)

        # Get the response
        print_colored("Phi4:", Fore.CYAN, Style.BRIGHT)
        response = client.send_message(message)

        if not response or response.startswith("Error:"):
            print_colored("Failed to get a response. Please try again.", Fore.RED)
            continue

        # No need to print the response here as it's already printed in real-time by the client


def print_help():
    """Print help information."""
    help_text = """
    RedMoon API CLI Help
    ===================

    This is a comprehensive command-line interface for interacting with various AI services.

    Available Services:
    - Chat Services: Scira, Qwen, ChatGot, Uncovr, Blackbox AI, Mistral Small 3.1 24B, Llama 3.2 3B Akash, Phi4
    - Image Generation: PixelMuse, MagicStudio, Fluently XL Final, Flux Standard
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
    """Clear the terminal screen with animation."""
    # Show a brief clearing animation
    print_spinner("Clearing screen...", 0.5)

    # Clear the screen based on OS
    os.system('cls' if os.name == 'nt' else 'clear')


def print_help():
    """Print help information with improved formatting."""
    clear_screen()

    # Help header
    help_title = "REDMOON API CLI HELP"
    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.BLUE} {help_title} {Style.RESET_ALL}")

    # Create a box for the help content
    box_width = terminal_width - 10

    print(f"{Fore.CYAN}┌{'─' * (box_width - 2)}┐")
    print(f"{Fore.CYAN}│{' ' * (box_width - 2)}│")

    # About section
    print(f"{Fore.CYAN}│ {Style.BRIGHT}{Fore.WHITE}ABOUT{' ' * (box_width - 8)}│{Style.RESET_ALL}")
    about_text = "RedMoon API CLI is a comprehensive command-line interface for interacting with various AI services."
    # Wrap text to fit in the box
    words = about_text.split()
    line = ""
    for word in words:
        if len(line + word) + 1 <= box_width - 4:
            line += word + " "
        else:
            print(f"{Fore.CYAN}│ {Fore.WHITE}{line}{' ' * (box_width - len(line) - 3)}│")
            line = word + " "
    if line:
        print(f"{Fore.CYAN}│ {Fore.WHITE}{line}{' ' * (box_width - len(line) - 3)}│")

    print(f"{Fore.CYAN}│{' ' * (box_width - 2)}│")

    # Available Services section
    print(f"{Fore.CYAN}│ {Style.BRIGHT}{Fore.WHITE}AVAILABLE SERVICES{' ' * (box_width - 20)}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│ {Fore.WHITE}💬 Chat Services:{' ' * (box_width - 17)}│")
    print(f"{Fore.CYAN}│   {Fore.WHITE}• Scira, Qwen, ChatGot, Uncovr, Blackbox AI{' ' * (box_width - 48)}│")
    print(f"{Fore.CYAN}│   {Fore.WHITE}• Mistral Small 3.1 24B, Llama 3.2 3B Akash, Phi4{' ' * (box_width - 54)}│")
    print(f"{Fore.CYAN}│ {Fore.WHITE}🎨 Generation Services:{' ' * (box_width - 24)}│")
    print(f"{Fore.CYAN}│   {Fore.WHITE}• Image: PixelMuse, MagicStudio, Fluently XL, Flux Standard, MitraAI{' ' * (box_width - 73)}│")
    print(f"{Fore.CYAN}│   {Fore.WHITE}• Voice Generation{' ' * (box_width - 21)}│")

    print(f"{Fore.CYAN}│{' ' * (box_width - 2)}│")

    # Navigation section
    print(f"{Fore.CYAN}│ {Style.BRIGHT}{Fore.WHITE}NAVIGATION{' ' * (box_width - 12)}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│ {Fore.WHITE}• Use numbers to select options from menus{' ' * (box_width - 42)}│")
    print(f"{Fore.CYAN}│ {Fore.WHITE}• Type 'exit', 'quit', or 'back' to return to previous menus{' ' * (box_width - 62)}│")
    print(f"{Fore.CYAN}│ {Fore.WHITE}• Press Ctrl+C to exit the application at any time{' ' * (box_width - 52)}│")

    print(f"{Fore.CYAN}│{' ' * (box_width - 2)}│")

    # Keyboard shortcuts section
    print(f"{Fore.CYAN}│ {Style.BRIGHT}{Fore.WHITE}KEYBOARD SHORTCUTS{' ' * (box_width - 20)}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│ {Fore.WHITE}• 0: Exit to main menu{' ' * (box_width - 22)}│")
    print(f"{Fore.CYAN}│ {Fore.WHITE}• 13: Clear screen{' ' * (box_width - 19)}│")
    print(f"{Fore.CYAN}│ {Fore.WHITE}• 14: Show this help{' ' * (box_width - 21)}│")

    print(f"{Fore.CYAN}│{' ' * (box_width - 2)}│")
    print(f"{Fore.CYAN}└{'─' * (box_width - 2)}┘")

    # Footer
    print(f"\n{Style.BRIGHT}{Fore.WHITE}Press Enter to return to the main menu...{Style.RESET_ALL}")
    input()


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
            run_mistral_small()
        elif choice == 7:
            run_llama_akash()
        elif choice == 8:
            run_phi4_chat()
        elif choice == 9:
            run_pixelmuse_image_generation()
        elif choice == 10:
            run_magicstudio_image_generation()
        elif choice == 11:
            run_fluently_xl()
        elif choice == 12:
            run_flux_standard()
        elif choice == 13:
            run_mitraai_image_generation()
        elif choice == 14:
            run_voice_generation()
        elif choice == 15:
            clear_screen()
        elif choice == 16:
            print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\nProgram terminated by user.", Fore.RED)
        sys.exit(0)
