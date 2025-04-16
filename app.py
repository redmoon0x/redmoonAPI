#!/usr/bin/env python3
"""
RedMoon Web Application

A Flask web application for interacting with various AI models.
"""

import os
import sys
import json
from flask import Flask, render_template, request, jsonify, session
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

# Disable Flask logging
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Add CSRF protection
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# Generate random endpoint names to make reverse engineering harder
import random
import string

def generate_random_endpoint():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# Random endpoint names
MODELS_ENDPOINT = generate_random_endpoint()
CHAT_ENDPOINT = generate_random_endpoint()
CLEAR_ENDPOINT = generate_random_endpoint()

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
    return render_template('index.html',
                           models=AVAILABLE_MODELS,
                           MODELS_ENDPOINT=MODELS_ENDPOINT,
                           CHAT_ENDPOINT=CHAT_ENDPOINT,
                           CLEAR_ENDPOINT=CLEAR_ENDPOINT)

@app.route(f'/api/{MODELS_ENDPOINT}', methods=['GET'])
@csrf.exempt
def get_models():
    """Get the list of available models."""
    return jsonify(AVAILABLE_MODELS)

@app.route(f'/api/{CHAT_ENDPOINT}', methods=['POST'])
@csrf.exempt
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

@app.route(f'/api/{CLEAR_ENDPOINT}', methods=['POST'])
@csrf.exempt
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
