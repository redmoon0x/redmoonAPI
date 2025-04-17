#!/usr/bin/env python3
"""
RedMoon Web Application

A Flask web application for interacting with various AI models.
"""

import os
import sys
import json
import base64
import io
import requests
from flask import Flask, render_template, request, jsonify, session, send_file, Response
from flask_cors import CORS

# Import model clients
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
    from blackbox_request import send_request_api, format_response_json
except ImportError:
    send_request_api = None
    format_response_json = None

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Define available models
AVAILABLE_MODELS = []

# Scira models
if SciraChat is not None:
    AVAILABLE_MODELS.extend([
        {"id": "scira-default", "name": "Scira Default", "websearch": False},
        {"id": "scira-grok", "name": "Scira Grok", "websearch": False},
        {"id": "scira-claude", "name": "Scira Claude", "websearch": False},
        {"id": "scira-vision", "name": "Scira Vision", "websearch": False},
    ])

# Qwen model
if QwenAIClient is not None:
    AVAILABLE_MODELS.append({"id": "qwen", "name": "Qwen 2 Turbo", "websearch": False})

# ChatGot model
if ChatGotClient is not None:
    AVAILABLE_MODELS.append({"id": "chatgot", "name": "ChatGot GPT-4", "websearch": False})

# Uncovr model
if UncovrClient is not None:
    AVAILABLE_MODELS.append({"id": "uncovr", "name": "Uncovr GPT-4o Mini", "websearch": True})

# Blackbox AI
if send_request_api is not None:
    AVAILABLE_MODELS.append({"id": "blackbox", "name": "Blackbox Claude 3.5", "websearch": True})

# Venice.ai models
if MistralSmall is not None:
    AVAILABLE_MODELS.append({"id": "mistral-small", "name": "Mistral Small 3.1 24B", "websearch": False})

if LlamaAkash is not None:
    AVAILABLE_MODELS.append({"id": "llama-akash", "name": "Llama 3.2 3B Akash", "websearch": False})

# Define available image models
AVAILABLE_IMAGE_MODELS = []

# PixelMuse models
if pixelmuse_generate is not None:
    AVAILABLE_IMAGE_MODELS.extend([
        {"id": "pixelmuse-flux", "name": "PixelMuse Flux Schnell", "provider": "pixelmuse"},
        {"id": "pixelmuse-imagen-fast", "name": "PixelMuse Imagen 3 Fast", "provider": "pixelmuse"},
        {"id": "pixelmuse-imagen", "name": "PixelMuse Imagen 3", "provider": "pixelmuse"},
        {"id": "pixelmuse-recraft", "name": "PixelMuse Recraft V3", "provider": "pixelmuse"},
    ])

# Venice.ai image models
if FluentlyXL is not None:
    AVAILABLE_IMAGE_MODELS.append({"id": "fluently-xl", "name": "Fluently XL Final", "provider": "venice"})

if FluxStandard is not None:
    AVAILABLE_IMAGE_MODELS.append({"id": "flux-standard", "name": "Flux Standard", "provider": "venice"})

# MagicStudio model
if magicstudio_generate is not None:
    AVAILABLE_IMAGE_MODELS.append({"id": "magicstudio", "name": "MagicStudio", "provider": "magicstudio"})

# Model instances cache
model_instances = {}

def get_model_instance(model_id):
    """Get or create a model instance for the given model ID."""
    if model_id in model_instances:
        return model_instances[model_id]

    # Create a new instance based on the model ID
    if model_id.startswith("scira-"):
        model_map = {
            "scira-default": "default",
            "scira-grok": "grok",
            "scira-claude": "claude",
            "scira-vision": "vision"
        }
        model_type = model_map.get(model_id, "default")
        instance = SciraChat(model=model_type)
    elif model_id == "qwen":
        instance = QwenAIClient()
    elif model_id == "chatgot":
        instance = ChatGotClient()
    elif model_id == "uncovr":
        instance = UncovrClient()
    elif model_id == "blackbox":
        # Blackbox doesn't have a persistent instance
        instance = None
    elif model_id == "mistral-small":
        instance = MistralSmall()
    elif model_id == "llama-akash":
        instance = LlamaAkash()
    else:
        return None

    # Cache the instance
    model_instances[model_id] = instance
    return instance

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', models=AVAILABLE_MODELS, image_models=AVAILABLE_IMAGE_MODELS)

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get the list of available models."""
    return jsonify(AVAILABLE_MODELS)

@app.route('/api/image-models', methods=['GET'])
def get_image_models():
    """Get the list of available image generation models."""
    return jsonify(AVAILABLE_IMAGE_MODELS)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Send a message to the selected model."""
    data = request.json
    model_id = data.get('model_id')
    message = data.get('message')
    websearch = data.get('websearch', False)

    if not model_id or not message:
        return jsonify({"error": "Missing model_id or message"}), 400

    # Find the model in the available models
    model_info = next((m for m in AVAILABLE_MODELS if m['id'] == model_id), None)
    if not model_info:
        return jsonify({"error": f"Model {model_id} not found"}), 404

    try:
        # Handle the message based on the model type
        if model_id.startswith("scira-"):
            instance = get_model_instance(model_id)
            response = instance.chat(message)
        elif model_id == "qwen":
            instance = get_model_instance(model_id)
            result = instance.send_message(message)
            response = result.get("message", "Error: No response from Qwen")
        elif model_id == "chatgot":
            instance = get_model_instance(model_id)
            response, _ = instance.send_message(message)
        elif model_id == "uncovr":
            instance = get_model_instance(model_id)
            # For Uncovr, we need to modify the focus parameter based on websearch
            # The default focus is ["web"], but we can add more if needed
            focus = ["web", "search"] if websearch else ["web"]
            result = instance.send_message(message, focus=focus)
            response = result.get("text", "Error: No response from Uncovr")
        elif model_id == "blackbox":
            # For Blackbox, we need to call the send_request_api function
            # and capture its output
            try:
                # Get the raw response from the API
                raw_response = send_request_api(message, websearch)

                # Format the response for the web UI
                formatted_response = format_response_json(raw_response)

                # Extract the main response text
                response = formatted_response.get("response", "No response from Blackbox AI.")

                # If there are web search results, append them to the response
                web_search_results = formatted_response.get("web_search", [])
                if web_search_results and websearch:
                    response += "\n\nWeb Search Results:\n"
                    for idx, result in enumerate(web_search_results, 1):
                        response += f"\n[{idx}] {result.get('title', 'No Title')}\n"
                        response += f"    URL: {result.get('url', 'No URL')}\n"
                        response += f"    {result.get('snippet', 'No snippet available')}\n"
            except Exception as e:
                response = f"Error from Blackbox AI: {str(e)}"
                print(f"Blackbox error: {str(e)}")
        elif model_id == "mistral-small":
            instance = get_model_instance(model_id)
            response = instance.send_message(message)
        elif model_id == "llama-akash":
            instance = get_model_instance(model_id)
            response = instance.send_message(message)
        else:
            return jsonify({"error": f"Model {model_id} not implemented"}), 501

        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Generate an image using the selected model."""
    data = request.json
    model_id = data.get('model_id')
    prompt = data.get('prompt')
    aspect_ratio = data.get('aspect_ratio', '1:1')
    negative_prompt = data.get('negative_prompt', '')

    if not model_id or not prompt:
        return jsonify({"error": "Missing model_id or prompt"}), 400

    # Find the model in the available image models
    model_info = next((m for m in AVAILABLE_IMAGE_MODELS if m['id'] == model_id), None)
    if not model_info:
        return jsonify({"error": f"Image model {model_id} not found"}), 404

    try:
        # Handle the image generation based on the provider
        provider = model_info.get('provider')

        if provider == 'pixelmuse':
            # Map model_id to PixelMuse model name
            model_map = {
                "pixelmuse-flux": "flux-schnell",
                "pixelmuse-imagen-fast": "imagen-3-fast",
                "pixelmuse-imagen": "imagen-3",
                "pixelmuse-recraft": "recraft-v3"
            }
            model = model_map.get(model_id)

            # Generate the image
            result = pixelmuse_generate(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                model=model
            )

            if result and 'output' in result:
                # Return the image URL
                return jsonify({"image_url": result['output']})
            else:
                return jsonify({"error": "Failed to generate image with PixelMuse"}), 500

        elif provider == 'venice':
            # Create the appropriate Venice client
            if model_id == 'fluently-xl':
                client = FluentlyXL()
            elif model_id == 'flux-standard':
                client = FluxStandard()
            else:
                return jsonify({"error": f"Unknown Venice model: {model_id}"}), 400

            # Generate the image but don't save it to disk
            image_bytes = client.client.generate_image(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                negative_prompt=negative_prompt,
                save_path=None  # Don't save to disk
            )

            # Convert image bytes to base64 for embedding in response
            if isinstance(image_bytes, bytes):
                encoded_image = base64.b64encode(image_bytes).decode('utf-8')
                return jsonify({
                    "image_data": encoded_image,
                    "content_type": "image/webp"
                })
            else:
                return jsonify({"error": "Failed to generate image with Venice"}), 500

        elif provider == 'magicstudio':
            # For MagicStudio, we need to modify the main function to return image data
            # instead of saving to disk
            url = "https://ai-api.magicstudio.com/api/ai-art-generator"
            headers = {
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-US,en;q=0.7",
                "origin": "https://magicstudio.com",
                "referer": "https://magicstudio.com/",
                "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Brave\";v=\"134\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "sec-gpc": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
            }

            import time
            data = {
                "prompt": prompt,
                "output_format": "bytes",
                "user_profile_id": "null",
                "anonymous_user_id": "bbc381a1-0924-4b70-a08a-64508b871262",
                "request_timestamp": str(time.time()),
                "user_is_subscribed": "false",
                "client_id": "pSgX7WgjukXCBoYwDM8G8GLnRRkvAoJlqa5eAVvj95o"
            }

            response = requests.post(url, headers=headers, data=data)

            if response.status_code == 200:
                # Convert image bytes to base64 for embedding in response
                encoded_image = base64.b64encode(response.content).decode('utf-8')
                return jsonify({
                    "image_data": encoded_image,
                    "content_type": "image/png"
                })
            else:
                return jsonify({"error": f"Failed to generate image with MagicStudio: {response.text}"}), 500
        else:
            return jsonify({"error": f"Unknown provider: {provider}"}), 400

    except Exception as e:
        return jsonify({"error": f"Error generating image: {str(e)}"}), 500

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear the conversation history for the selected model."""
    data = request.json
    model_id = data.get('model_id')

    if not model_id:
        return jsonify({"error": "Missing model_id"}), 400

    instance = get_model_instance(model_id)
    if instance and hasattr(instance, 'clear_history'):
        instance.clear_history()
        return jsonify({"success": True})

    return jsonify({"error": "Cannot clear history for this model"}), 400

if __name__ == '__main__':
    app.run(debug=True)
