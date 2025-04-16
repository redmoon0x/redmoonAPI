# 🌙 Redmoon0x - AI Chat Interface

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.7+-blue.svg" alt="Python 3.7+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen.svg" alt="Status: Active">
</div>

<p align="center">
  <b>A modern web interface and command-line tool for interacting with various AI services</b>
</p>

---

## 📋 Overview

Redmoon0x is an all-in-one platform that provides seamless access to multiple AI services, including chat models, image generation, and voice synthesis. This tool allows you to interact with various AI services through either a modern web interface or a simple, intuitive command-line interface.

## ✨ Features

- **Modern Web Interface**
  - 🌓 Dark and light themes
  - 📱 Responsive design for mobile and desktop
  - 🔍 Web search capability for supported models
  - ✨ Smooth animations and transitions

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

### Web Interface

The web interface is deployed and accessible at:

[https://redmoon0x.onrender.com](https://redmoon0x.onrender.com)

Simply visit the URL to start chatting with various AI models.

### Deploying to Render

To deploy your own instance of the web interface on Render's free tier:

1. Fork or clone this repository to your GitHub account
2. Create a new Render account at https://render.com if you don't have one
3. In the Render dashboard, click "New +" and select "Web Service"
4. Connect your GitHub account and select this repository
5. Use the following settings:
   - Name: redmoon0x (or any name you prefer)
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
6. Click "Create Web Service"

The application will be deployed and available at a URL provided by Render.

### Prerequisites

- Python 3.7 or higher
- Required Python packages:
  - `requests`
  - `colorama`
  - `sseclient` (for some services)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/redmoon0x/redmoonAPI.git
   cd redmoon-api-cli
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

#### Command-Line Interface

Run the main CLI interface:

```bash
python redmoon_cli.py
```

This will display the main menu where you can select the service you want to use.

#### Web Interface

Run the Flask web application locally:

```bash
python app.py
```

Then open your browser and navigate to `http://127.0.0.1:5000` to access the web interface.

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
  Made with ❤️ by <a href="https://github.com/redmoon0x">redmoon0x</a>
</p>

<p align="center">
  <i>Disclaimer: These are reverse engineered APIs and I don't own them. This application is for educational purposes only.</i>
</p>
