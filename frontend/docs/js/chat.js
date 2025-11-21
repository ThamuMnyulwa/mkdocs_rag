// Chat interface for documentation assistant

(function() {
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    const modelSelector = document.getElementById('model-selector');
    
    if (!chatMessages || !chatInput || !chatSend) {
        return;
    }

    const API_BASE_URL = window.mkdocs_config?.extra?.backend_api_url || 'http://localhost:8001';
    const SESSION_STORAGE_KEY = 'chat_session_id';
    
    let currentSessionId = sessionStorage.getItem(SESSION_STORAGE_KEY);

    function renderMarkdown(text) {
        if (!text) return '';
        
        if (typeof marked !== 'undefined') {
            return marked.parse(text, {
                breaks: true,
                gfm: true
            });
        }
        
        return text.replace(/\n/g, '<br>');
    }

    function addMessage(content, type = 'assistant', sources = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (type === 'assistant' || type === 'error') {
            contentDiv.innerHTML = renderMarkdown(content);
        } else {
            contentDiv.textContent = content;
        }
        
        messageDiv.appendChild(contentDiv);
        
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'sources';
            
            const sourcesTitle = document.createElement('h4');
            sourcesTitle.textContent = 'Sources:';
            sourcesDiv.appendChild(sourcesTitle);
            
            sources.forEach(source => {
                const chip = document.createElement('a');
                chip.className = 'source-chip';
                chip.textContent = source.title || source.doc_path;
                chip.href = source.url || `../${source.doc_path.replace('.md', '/')}`;
                chip.target = '_blank';
                sourcesDiv.appendChild(chip);
            });
            
            messageDiv.appendChild(sourcesDiv);
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addLoadingMessage() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading';
        loadingDiv.id = 'loading-indicator';
        loadingDiv.textContent = 'Thinking...';
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeLoadingMessage() {
        const loading = document.getElementById('loading-indicator');
        if (loading) {
            loading.remove();
        }
    }

    async function loadConversationHistory() {
        if (!currentSessionId) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/sessions/${currentSessionId}/messages`);
            
            if (response.ok) {
                const data = await response.json();
                const messages = data.messages || [];
                
                messages.forEach(msg => {
                    if (msg.role === 'user') {
                        addMessage(msg.content, 'user');
                    } else if (msg.role === 'assistant') {
                        addMessage(msg.content, 'assistant', msg.sources);
                    }
                });
                
                if (messages.length > 0) {
                    console.log(`Loaded ${messages.length} messages from session ${currentSessionId}`);
                }
            } else if (response.status === 404) {
                console.log('Session not found, will create new one');
                currentSessionId = null;
                sessionStorage.removeItem(SESSION_STORAGE_KEY);
            }
        } catch (error) {
            console.error('Error loading conversation history:', error);
        }
    }

    async function sendMessage() {
        const question = chatInput.value.trim();
        if (!question) return;
        
        const selectedModel = modelSelector ? modelSelector.value : null;
        
        addMessage(question, 'user');
        chatInput.value = '';
        chatSend.disabled = true;
        chatInput.disabled = true;
        if (modelSelector) modelSelector.disabled = true;
        
        addLoadingMessage();
        
        try {
            const requestBody = { question };
            if (selectedModel && selectedModel !== 'gemini') {
                requestBody.model = selectedModel;
            }
            if (currentSessionId) {
                requestBody.session_id = currentSessionId;
            }
            
            const response = await fetch(`${API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
            
            removeLoadingMessage();
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.session_id) {
                currentSessionId = data.session_id;
                sessionStorage.setItem(SESSION_STORAGE_KEY, currentSessionId);
            }
            
            addMessage(data.answer, 'assistant', data.sources);
            
        } catch (error) {
            removeLoadingMessage();
            console.error('Error:', error);
            addMessage(
                `Sorry, I encountered an error: ${error.message}. Please make sure the backend server is running.`,
                'error'
            );
        } finally {
            chatSend.disabled = false;
            chatInput.disabled = false;
            if (modelSelector) modelSelector.disabled = false;
            chatInput.focus();
        }
    }

    chatSend.addEventListener('click', sendMessage);
    
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    async function initialize() {
        await loadConversationHistory();
        
        if (chatMessages.children.length === 0) {
            addMessage(
                'Hello! I can help you find information in the documentation. Ask me anything about our runbooks, processes, or policies.',
                'assistant'
            );
        }
    }

    initialize();
})();
