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
    from blackbox_request import send_request as blackbox_request
except ImportError:
    blackbox_request = None

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Define available models
AVAILABLE_MODELS = []

# Scira models
if SciraChat is not None:
    AVAILABLE_MODELS.extend([
        {"id": "scira-default", "name": "Scira Default", "provider": "Scira", "websearch": False},
        {"id": "scira-grok", "name": "Scira Grok", "provider": "Scira", "websearch": False},
        {"id": "scira-claude", "name": "Scira Claude", "provider": "Scira", "websearch": False},
        {"id": "scira-vision", "name": "Scira Vision", "provider": "Scira", "websearch": False},
    ])

# Qwen model
if QwenAIClient is not None:
    AVAILABLE_MODELS.append({"id": "qwen", "name": "Qwen", "provider": "Qwen", "websearch": False})

# ChatGot model
if ChatGotClient is not None:
    AVAILABLE_MODELS.append({"id": "chatgot", "name": "ChatGot", "provider": "ChatGot", "websearch": False})

# Uncovr model
if UncovrClient is not None:
    AVAILABLE_MODELS.append({"id": "uncovr", "name": "Uncovr", "provider": "Uncovr", "websearch": True})

# Blackbox AI
if blackbox_request is not None:
    AVAILABLE_MODELS.append({"id": "blackbox", "name": "Blackbox AI", "provider": "Blackbox", "websearch": True})

# Venice.ai models
if MistralSmall is not None:
    AVAILABLE_MODELS.append({"id": "mistral-small", "name": "Mistral Small 3.1 24B", "provider": "Venice", "websearch": False})

if LlamaAkash is not None:
    AVAILABLE_MODELS.append({"id": "llama-akash", "name": "Llama 3.2 3B Akash", "provider": "Venice", "websearch": False})

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
    return render_template('index.html', models=AVAILABLE_MODELS)

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get the list of available models."""
    return jsonify(AVAILABLE_MODELS)

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
            result = instance.send_message(message)
            response = result.get("text", "Error: No response from Uncovr")
        elif model_id == "blackbox":
            # Blackbox doesn't return a response directly, it prints to console
            # For web app, we need to capture the response
            response = "Blackbox AI response would appear here. This model is not fully integrated yet."
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
