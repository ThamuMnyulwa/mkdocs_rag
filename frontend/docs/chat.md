# Chat Assistant

Ask questions about our documentation in natural language. The assistant will search through all available documentation and provide answers with citations to the relevant sections.

## Model Selection

Choose from multiple AI models to power your queries:
- **Gemini (default)** - Google's Gemini 2.5 Flash model, fast and accurate
- **Groq Llama 3.1 8B** - Fast inference with Meta's Llama 3.1 8B model via Groq
- **Groq Llama 3.1 70B** - More powerful Llama model for complex queries
- **Groq Mixtral 8x7B** - Mistral's mixture-of-experts model

*Note: Groq models require a GROQ_API_KEY to be configured in the backend. Embeddings always use Gemini for consistency.*

<div id="chat-container">
    <div id="chat-messages"></div>
    <div id="chat-input-container">
        <div id="chat-controls">
            <select id="model-selector">
                <option value="gemini">Gemini (default)</option>
                <option value="groq-llama3">Groq Llama 3.1 8B</option>
                <option value="groq-llama-70b">Groq Llama 3.1 70B</option>
                <option value="groq-mixtral">Groq Mixtral 8x7B</option>
            </select>
            <input type="text" id="chat-input" placeholder="Ask a question about the documentation..." />
            <button id="chat-send">Send</button>
        </div>
    </div>
</div>

<style>
#chat-container {
    max-width: 900px;
    margin: 2rem auto;
    border: 1px solid var(--md-default-fg-color--lightest);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    height: 600px;
}

#chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.message {
    padding: 1rem;
    border-radius: 8px;
    max-width: 80%;
}

.message.user {
    background-color: var(--md-primary-fg-color);
    color: white;
    align-self: flex-end;
    margin-left: auto;
}

.message.assistant {
    background-color: var(--md-default-bg-color);
    border: 1px solid var(--md-default-fg-color--lightest);
    align-self: flex-start;
}

.message-content {
    line-height: 1.6;
}

.message-content h1,
.message-content h2,
.message-content h3 {
    margin: 0.5rem 0;
    font-weight: 600;
}

.message-content h1 {
    font-size: 1.5rem;
}

.message-content h2 {
    font-size: 1.25rem;
}

.message-content h3 {
    font-size: 1.1rem;
}

.message-content code {
    background-color: var(--md-code-bg-color);
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-size: 0.9em;
    font-family: var(--md-code-font);
}

.message-content pre {
    background-color: var(--md-code-bg-color);
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
    margin: 0.5rem 0;
}

.message-content pre code {
    background-color: transparent;
    padding: 0;
}

.message-content ul,
.message-content ol {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
}

.message-content li {
    margin: 0.25rem 0;
}

.message-content a {
    color: var(--md-primary-fg-color);
    text-decoration: underline;
}

.message-content a:hover {
    text-decoration: none;
}

.message-content strong {
    font-weight: 600;
}

.message-content em {
    font-style: italic;
}

.message.error {
    background-color: #ffebee;
    color: #c62828;
    border: 1px solid #ef9a9a;
}

.sources {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--md-default-fg-color--lightest);
}

.sources h4 {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    color: var(--md-default-fg-color--light);
}

.source-chip {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    margin: 0.25rem;
    background-color: var(--md-code-bg-color);
    border-radius: 16px;
    font-size: 0.85rem;
    text-decoration: none;
    color: var(--md-primary-fg-color);
    border: 1px solid var(--md-primary-fg-color--light);
}

.source-chip:hover {
    background-color: var(--md-primary-fg-color--light);
    color: white;
}

#chat-input-container {
    padding: 1rem;
    border-top: 1px solid var(--md-default-fg-color--lightest);
}

#chat-controls {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

#model-selector {
    padding: 0.75rem;
    border: 1px solid var(--md-default-fg-color--lightest);
    border-radius: 4px;
    font-size: 0.9rem;
    font-family: inherit;
    background-color: var(--md-default-bg-color);
    color: var(--md-default-fg-color);
    cursor: pointer;
    min-width: 180px;
}

#chat-input {
    flex: 1;
    padding: 0.75rem;
    border: 1px solid var(--md-default-fg-color--lightest);
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
}

#chat-send {
    padding: 0.75rem 1.5rem;
    background-color: var(--md-primary-fg-color);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
}

#chat-send:hover {
    opacity: 0.9;
}

#chat-send:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.loading {
    padding: 1rem;
    text-align: center;
    color: var(--md-default-fg-color--light);
}
</style>

