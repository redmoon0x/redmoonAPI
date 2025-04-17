// Redmoon0x Web Application JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements - Chat Interface
    const chatTab = document.getElementById('chat-tab');
    const imageTab = document.getElementById('image-tab');
    const chatInterface = document.getElementById('chat-interface');
    const imageInterface = document.getElementById('image-interface');
    const chatModelSelector = document.getElementById('chat-model-selector');
    const imageModelSelector = document.getElementById('image-model-selector');

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

    // DOM Elements - Image Interface
    const imageModelSelectorBtn = document.getElementById('image-model-selector-btn');
    const imageModelDropdown = document.getElementById('image-model-dropdown');
    const selectedImageModelName = document.getElementById('selected-image-model-name');
    const imageModelOptions = document.querySelectorAll('.image-model-option');
    const imagePromptInput = document.getElementById('image-prompt');
    const negativePromptInput = document.getElementById('negative-prompt');
    const aspectRatioBtns = document.querySelectorAll('.aspect-ratio-btn');
    const generateImageBtn = document.getElementById('generate-image-btn');
    const imageResult = document.getElementById('image-result');
    const imageLoading = document.getElementById('image-loading');
    const generatedImage = document.getElementById('generated-image');
    const newImageBtn = document.getElementById('new-image-btn');
    const downloadImageBtn = document.getElementById('download-image-btn');

    // DOM Elements - Common
    const menuBtn = document.getElementById('menu-btn');
    const closeMenuBtn = document.getElementById('close-menu-btn');
    const sideMenu = document.getElementById('side-menu');
    const overlay = document.getElementById('overlay');
    const websearchToggleContainer = document.getElementById('websearch-toggle-container');
    const websearchToggle = document.getElementById('websearch-toggle');
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeText = document.getElementById('theme-text');

    // State - Chat
    let currentModelId = null;
    let currentModelName = null;
    let supportsWebSearch = false;
    let isGenerating = false;
    let chatHistory = [];

    // State - Image
    let currentImageModelId = null;
    let currentImageModelName = null;
    let currentImageModelProvider = null;
    let isGeneratingImage = false;
    let selectedAspectRatio = '1:1'; // Default aspect ratio

    // State - Common
    let currentTheme = localStorage.getItem('theme') || 'dark';
    let currentTab = 'chat'; // Default tab

    // Event Listeners - Tabs
    chatTab.addEventListener('click', () => switchTab('chat'));
    imageTab.addEventListener('click', () => switchTab('image'));

    // Event Listeners - Chat
    modelSelectorBtn.addEventListener('click', toggleModelDropdown);
    messageInput.addEventListener('keydown', handleInputKeydown);
    sendBtn.addEventListener('click', sendMessage);
    clearBtn.addEventListener('click', clearChat);

    // Event Listeners - Image
    imageModelSelectorBtn.addEventListener('click', toggleImageModelDropdown);
    aspectRatioBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            selectAspectRatio(this.getAttribute('data-ratio'));
        });
    });
    generateImageBtn.addEventListener('click', generateImage);
    newImageBtn.addEventListener('click', resetImageForm);

    // Event Listeners - Common
    document.addEventListener('click', closeDropdownsOnClickOutside);
    menuBtn.addEventListener('click', openSideMenu);
    closeMenuBtn.addEventListener('click', closeSideMenu);
    overlay.addEventListener('click', closeSideMenu);
    themeToggleBtn.addEventListener('click', toggleTheme);

    // Initialize theme
    applyTheme();

    // Auto-resize textareas
    const textareas = [messageInput, imagePromptInput, negativePromptInput];
    textareas.forEach(textarea => {
        if (textarea) {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
        }
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

    // Initialize image model options
    imageModelOptions.forEach(option => {
        option.addEventListener('click', function() {
            const modelId = this.getAttribute('data-model-id');
            const modelName = this.getAttribute('data-model-name');
            const provider = this.getAttribute('data-provider');

            selectImageModel(modelId, modelName, provider);
            toggleImageModelDropdown();
        });
    });

    // Tab Functions
    function switchTab(tab) {
        currentTab = tab;

        // Update tab styling
        if (tab === 'chat') {
            chatTab.classList.add('tab-active');
            imageTab.classList.remove('tab-active');
            chatTab.classList.remove('text-gray-400');
            imageTab.classList.add('text-gray-400');

            // Show chat interface, hide image interface
            chatInterface.classList.remove('hidden');
            imageInterface.classList.add('hidden');

            // Show appropriate model selector
            chatModelSelector.classList.remove('hidden');
            imageModelSelector.classList.add('hidden');

            // Update status text
            if (currentModelId) {
                modelStatus.textContent = `Chatting with ${currentModelName}`;
            } else {
                modelStatus.textContent = 'Please select a model to start chatting';
            }
        } else {
            imageTab.classList.add('tab-active');
            chatTab.classList.remove('tab-active');
            imageTab.classList.remove('text-gray-400');
            chatTab.classList.add('text-gray-400');

            // Show image interface, hide chat interface
            imageInterface.classList.remove('hidden');
            chatInterface.classList.add('hidden');

            // Show appropriate model selector
            imageModelSelector.classList.remove('hidden');
            chatModelSelector.classList.add('hidden');

            // Update status text
            if (currentImageModelId) {
                modelStatus.textContent = `Generating images with ${currentImageModelName}`;
            } else {
                modelStatus.textContent = 'Please select an image model';
            }
        }
    }

    // Dropdown Functions
    function toggleModelDropdown() {
        modelDropdown.classList.toggle('hidden');
        // Hide image model dropdown if open
        imageModelDropdown.classList.add('hidden');
    }

    function toggleImageModelDropdown() {
        imageModelDropdown.classList.toggle('hidden');
        // Hide chat model dropdown if open
        modelDropdown.classList.add('hidden');
    }

    function closeDropdownsOnClickOutside(event) {
        // Close chat model dropdown
        if (!modelSelectorBtn.contains(event.target) && !modelDropdown.contains(event.target)) {
            modelDropdown.classList.add('hidden');
        }

        // Close image model dropdown
        if (!imageModelSelectorBtn.contains(event.target) && !imageModelDropdown.contains(event.target)) {
            imageModelDropdown.classList.add('hidden');
        }
    }

    // Model Selection Functions
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
        if (currentTab === 'chat') {
            modelStatus.textContent = `Chatting with ${modelName}`;
        }

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

    function selectImageModel(modelId, modelName, provider) {
        currentImageModelId = modelId;
        currentImageModelName = modelName;
        currentImageModelProvider = provider;

        // Update UI
        selectedImageModelName.textContent = modelName;
        if (currentTab === 'image') {
            modelStatus.textContent = `Generating images with ${modelName}`;
        }

        // Enable the generate button
        generateImageBtn.disabled = false;
    }

    function selectAspectRatio(ratio) {
        selectedAspectRatio = ratio;

        // Update UI - highlight selected button
        aspectRatioBtns.forEach(btn => {
            if (btn.getAttribute('data-ratio') === ratio) {
                btn.classList.add('bg-purple-600');
                btn.classList.remove('bg-gray-700', 'dark:bg-gray-700', 'light:bg-gray-200');
            } else {
                btn.classList.remove('bg-purple-600');
                btn.classList.add('bg-gray-700', 'dark:bg-gray-700', 'light:bg-gray-200');
            }
        });
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
        // Scroll the window to the bottom of the page
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
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

    // Image Generation Functions
    function generateImage() {
        const prompt = imagePromptInput.value.trim();
        if (!prompt || !currentImageModelId || isGeneratingImage) {
            return;
        }

        // Show loading indicator
        imageResult.classList.add('hidden');
        imageLoading.classList.remove('hidden');

        // Disable generate button
        isGeneratingImage = true;
        generateImageBtn.disabled = true;

        // Prepare request data
        const requestData = {
            model_id: currentImageModelId,
            prompt: prompt,
            aspect_ratio: selectedAspectRatio
        };

        // Add negative prompt if provided
        const negativePrompt = negativePromptInput.value.trim();
        if (negativePrompt) {
            requestData.negative_prompt = negativePrompt;
        }

        // Send to API
        fetch('/api/generate-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            imageLoading.classList.add('hidden');

            if (data.error) {
                alert(`Error: ${data.error}`);
                return;
            }

            // Handle different response types
            if (data.image_url) {
                // Direct URL to image (e.g., PixelMuse)
                generatedImage.src = data.image_url;
                downloadImageBtn.href = data.image_url;
                downloadImageBtn.download = `redmoon0x_${currentImageModelId}_${Date.now()}.png`;
            } else if (data.image_data && data.content_type) {
                // Base64 encoded image data
                const imageData = `data:${data.content_type};base64,${data.image_data}`;
                generatedImage.src = imageData;
                downloadImageBtn.href = imageData;
                downloadImageBtn.download = `redmoon0x_${currentImageModelId}_${Date.now()}.${data.content_type.split('/')[1]}`;
            } else {
                alert('Error: Invalid response from server');
                return;
            }

            // Show the result
            imageResult.classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error:', error);
            imageLoading.classList.add('hidden');
            alert('Failed to generate image. Please try again.');
        })
        .finally(() => {
            isGeneratingImage = false;
            generateImageBtn.disabled = false;
        });
    }

    function resetImageForm() {
        // Hide result, show form
        imageResult.classList.add('hidden');

        // Clear the image
        generatedImage.src = '';

        // Reset form fields if desired
        // imagePromptInput.value = '';
        // negativePromptInput.value = '';
    }

    function openSideMenu() {
        sideMenu.classList.remove('translate-x-full');
        overlay.classList.remove('hidden');
    }

    function closeSideMenu() {
        sideMenu.classList.add('translate-x-full');
        overlay.classList.add('hidden');
    }

    // Theme functions
    function toggleTheme() {
        currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('theme', currentTheme);
        applyTheme();
    }

    function applyTheme() {
        // Update all elements with theme classes
        const themeElements = document.querySelectorAll('[class*="dark:"], [class*="light:"]');

        if (currentTheme === 'light') {
            // Apply light theme
            document.documentElement.setAttribute('data-theme', 'light');
            document.body.classList.add('light-mode');
            document.body.classList.remove('dark-mode');

            // Update theme toggle button
            themeText.textContent = 'Light Mode';
            themeToggleBtn.innerHTML = `
                <span id="theme-text">Light Mode</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
                </svg>
            `;

            // Update theme-specific elements
            themeElements.forEach(el => {
                const classes = el.className.split(' ');
                classes.forEach(cls => {
                    if (cls.startsWith('light:')) {
                        const lightClass = cls.replace('light:', '');
                        el.classList.add(lightClass);
                    }
                    if (cls.startsWith('dark:')) {
                        const darkClass = cls.replace('dark:', '');
                        el.classList.remove(darkClass);
                    }
                });
            });

            // Update model dropdown text color
            const modelOptions = document.querySelectorAll('.model-option');
            modelOptions.forEach(option => {
                option.classList.remove('text-white');
                option.classList.add('text-gray-800');
            });

        } else {
            // Apply dark theme
            document.documentElement.removeAttribute('data-theme');
            document.body.classList.add('dark-mode');
            document.body.classList.remove('light-mode');

            // Update theme toggle button
            themeText.textContent = 'Dark Mode';
            themeToggleBtn.innerHTML = `
                <span id="theme-text">Dark Mode</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
            `;

            // Update theme-specific elements
            themeElements.forEach(el => {
                const classes = el.className.split(' ');
                classes.forEach(cls => {
                    if (cls.startsWith('dark:')) {
                        const darkClass = cls.replace('dark:', '');
                        el.classList.add(darkClass);
                    }
                    if (cls.startsWith('light:')) {
                        const lightClass = cls.replace('light:', '');
                        el.classList.remove(lightClass);
                    }
                });
            });

            // Update model dropdown text color
            const modelOptions = document.querySelectorAll('.model-option');
            modelOptions.forEach(option => {
                option.classList.add('text-white');
                option.classList.remove('text-gray-800');
            });
        }
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
