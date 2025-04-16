// Redmoon0x Web Application JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const modelSelectorBtn = document.getElementById('model-selector-btn');
    const modelDropdown = document.getElementById('model-dropdown');
    const selectedModelName = document.getElementById('selected-model-name');
    const modelOptions = document.querySelectorAll('.model-option');
    const chatContainer = document.getElementById('chat-container');
    const inputContainer = document.getElementById('input-container');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const modelStatus = document.getElementById('model-status');
    const clearBtn = document.getElementById('clear-btn');
    const menuBtn = document.getElementById('menu-btn');
    const closeMenuBtn = document.getElementById('close-menu-btn');
    const sideMenu = document.getElementById('side-menu');
    const overlay = document.getElementById('overlay');
    const websearchToggleContainer = document.getElementById('websearch-toggle-container');
    const websearchToggle = document.getElementById('websearch-toggle');

    // State
    let currentModelId = null;
    let currentModelName = null;
    let supportsWebSearch = false;
    let isGenerating = false;
    let chatHistory = [];

    // Event Listeners
    modelSelectorBtn.addEventListener('click', toggleModelDropdown);
    document.addEventListener('click', closeDropdownOnClickOutside);
    messageInput.addEventListener('keydown', handleInputKeydown);
    sendBtn.addEventListener('click', sendMessage);
    clearBtn.addEventListener('click', clearChat);
    menuBtn.addEventListener('click', openSideMenu);
    closeMenuBtn.addEventListener('click', closeSideMenu);
    overlay.addEventListener('click', closeSideMenu);

    // Auto-resize textarea
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Initialize model options
    modelOptions.forEach(option => {
        option.addEventListener('click', function() {
            const modelId = this.getAttribute('data-model-id');
            const modelName = this.getAttribute('data-model-name');
            const websearch = this.getAttribute('data-websearch') === 'true';

            selectModel(modelId, modelName, websearch);
            toggleModelDropdown();
        });
    });

    // Functions
    function toggleModelDropdown() {
        modelDropdown.classList.toggle('hidden');
    }

    function closeDropdownOnClickOutside(event) {
        if (!modelSelectorBtn.contains(event.target) && !modelDropdown.contains(event.target)) {
            modelDropdown.classList.add('hidden');
        }
    }

    function selectModel(modelId, modelName, websearch) {
        // If we're switching models, clear the chat
        if (currentModelId && currentModelId !== modelId) {
            clearChatMessages();
        }

        currentModelId = modelId;
        currentModelName = modelName;
        supportsWebSearch = websearch;

        // Update UI
        selectedModelName.textContent = modelName;
        modelStatus.textContent = `Chatting with ${modelName}`;

        // Show chat interface
        chatContainer.classList.remove('hidden');
        chatContainer.classList.add('flex', 'flex-col');
        inputContainer.classList.remove('hidden');
        clearBtn.classList.remove('hidden');

        // Handle web search toggle
        if (websearch) {
            websearchToggleContainer.classList.remove('hidden');
        } else {
            websearchToggleContainer.classList.add('hidden');
            websearchToggle.checked = false;
        }
    }

    function handleInputKeydown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    }

    function sendMessage() {
        const message = messageInput.value.trim();

        if (!message || !currentModelId || isGenerating) {
            return;
        }

        // Add user message to chat
        addMessageToChat('user', message);

        // Clear input
        messageInput.value = '';
        messageInput.style.height = 'auto';

        // Show typing indicator
        const typingIndicator = addTypingIndicator();

        // Disable send button while generating
        isGenerating = true;
        sendBtn.disabled = true;

        // Prepare request data
        const requestData = {
            model_id: currentModelId,
            message: message
        };

        // Add websearch flag if the model supports it
        if (supportsWebSearch) {
            requestData.websearch = websearchToggle.checked;
        }

        // Send to API
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            if (typingIndicator) {
                typingIndicator.remove();
            }

            // Add AI response to chat
            if (data.response) {
                addMessageToChat('ai', data.response);
            } else if (data.error) {
                addErrorMessage(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (typingIndicator) {
                typingIndicator.remove();
            }
            addErrorMessage('Failed to get a response. Please try again.');
        })
        .finally(() => {
            isGenerating = false;
            sendBtn.disabled = false;
        });
    }

    function addMessageToChat(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex w-full';

        const messageBubble = document.createElement('div');
        messageBubble.className = role === 'user' ? 'message user-message' : 'message ai-message';

        // For AI messages, we'll use a simple markdown parser
        if (role === 'ai') {
            // Convert markdown to HTML (simple version)
            const formattedContent = formatMarkdown(content);
            messageBubble.innerHTML = formattedContent;
        } else {
            messageBubble.textContent = content;
        }

        messageDiv.appendChild(messageBubble);
        chatContainer.appendChild(messageDiv);

        // Save to history
        chatHistory.push({ role, content });

        // Scroll to bottom
        scrollToBottom();
    }

    function addTypingIndicator() {
        const indicatorDiv = document.createElement('div');
        indicatorDiv.className = 'flex w-full mb-4';

        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = '<span></span><span></span><span></span>';

        indicatorDiv.appendChild(indicator);
        chatContainer.appendChild(indicatorDiv);

        scrollToBottom();

        return indicatorDiv;
    }

    function addErrorMessage(errorText) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'flex w-full';

        const errorBubble = document.createElement('div');
        errorBubble.className = 'message ai-message text-red-400';
        errorBubble.textContent = `Error: ${errorText}`;

        errorDiv.appendChild(errorBubble);
        chatContainer.appendChild(errorDiv);

        scrollToBottom();
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function clearChat() {
        if (!currentModelId) return;

        // Clear UI
        clearChatMessages();

        // Clear on server
        fetch('/api/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model_id: currentModelId
            })
        })
        .catch(error => {
            console.error('Error clearing chat history:', error);
        });
    }

    function clearChatMessages() {
        chatContainer.innerHTML = '';
        chatHistory = [];
    }

    function openSideMenu() {
        sideMenu.classList.remove('translate-x-full');
        overlay.classList.remove('hidden');
    }

    function closeSideMenu() {
        sideMenu.classList.add('translate-x-full');
        overlay.classList.add('hidden');
    }

    // Simple markdown formatter
    function formatMarkdown(text) {
        // Code blocks
        text = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

        // Inline code
        text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Headers
        text = text.replace(/^### (.*$)/gm, '<h3>$1</h3>');
        text = text.replace(/^## (.*$)/gm, '<h2>$1</h2>');
        text = text.replace(/^# (.*$)/gm, '<h1>$1</h1>');

        // Bold
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Italic
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Lists
        text = text.replace(/^\s*\d+\.\s+(.*$)/gm, '<li>$1</li>');
        text = text.replace(/^\s*[\-\*]\s+(.*$)/gm, '<li>$1</li>');

        // Links
        text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

        // Paragraphs - replace double newlines with paragraph tags
        text = text.replace(/\n\n/g, '</p><p>');

        // Wrap in paragraph tags if not already
        if (!text.startsWith('<')) {
            text = '<p>' + text + '</p>';
        }

        return text;
    }
});
