# 🌙 RedMoon API CLI

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.7+-blue.svg" alt="Python 3.7+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen.svg" alt="Status: Active">
</div>

<p align="center">
  <b>A comprehensive command-line interface for interacting with various AI services</b>
</p>

---

## 📋 Overview

RedMoon API CLI is an all-in-one command-line interface that provides seamless access to multiple AI services, including chat models, image generation, and voice synthesis. This tool allows you to interact with various AI services through a simple, intuitive menu-based interface.

## ✨ Features

- **Multiple Chat Services**
  - 💬 Scira Chat (with model selection: Default, Grok, Claude, Vision)
  - 💬 Qwen Chat
  - 💬 ChatGot Chat
  - 💬 Uncovr Client
  - 💬 Blackbox AI

- **Image Generation**
  - 🖼️ PixelMuse (with multiple models and aspect ratio options)
  - 🖼️ MagicStudio

- **Voice Generation**
  - 🔊 AI Voice Generator (with multiple language options)

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Required Python packages:
  - `requests`
  - `colorama`
  - `sseclient` (for some services)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/redmoon-api-cli.git
   cd redmoon-api-cli
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

Run the main CLI interface:

```bash
python redmoon_cli.py
```

This will display the main menu where you can select the service you want to use.

## 📖 Services Guide

### Chat Services

- **Scira Chat**: Interact with Scira AI models with options to select from different models (Default, Grok, Claude, Vision).
- **Qwen Chat**: Chat with the Qwen AI model.
- **ChatGot Chat**: Communicate with the ChatGot AI service.
- **Uncovr Client**: Use the Uncovr.app chat interface.
- **Blackbox AI**: Send requests to Blackbox AI with optional web search capability.

### Image Generation

- **PixelMuse**: Generate images using various models (flux-schnell, imagen-3-fast, imagen-3, recraft-v3) with different aspect ratio options.
- **MagicStudio**: Create images using the MagicStudio AI art generator.

### Voice Generation

- **AI Voice Generator**: Convert text to speech in multiple languages.

## 🔍 Navigation

- Use numbers to select options from menus
- Type 'exit', 'quit', or 'back' to return to previous menus
- Type 'clear' in chat interfaces to clear conversation history
- Press Ctrl+C to interrupt any operation

## 🛠️ Customization

You can customize the behavior of the CLI by modifying the `redmoon_cli.py` file. The modular design makes it easy to add new services or modify existing ones.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgements

- Thanks to all the AI services that make this CLI possible
- Special thanks to the open-source community for their invaluable tools and libraries

---

<p align="center">
  Made with ❤️ by Your Name
</p>
