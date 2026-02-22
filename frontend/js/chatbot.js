/**
 * AI Health Assistant - Chatbot JavaScript
 * Full chatbot functionality with message history and AI responses
 */

let chatHistory = [];
let isLoading = false;

document.addEventListener('DOMContentLoaded', function() {
    const chatToggle = document.getElementById('chatbot-toggle');
    if (chatToggle) {
        chatToggle.addEventListener('click', toggleChatbot);
    }

    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !isLoading) {
                sendChat();
            }
        });
    }

    const sendButton = document.getElementById('chatSendBtn');
    if (sendButton) {
        sendButton.addEventListener('click', sendChat);
    }

    // Load welcome message
    addBotMessage("Hello! I'm your AI Health Assistant. Ask me about health tips, symptoms, diet, exercise, stress management, or anything wellness-related. How can I help?", true);
});

/**
 * Toggle chatbot visibility
 */
function toggleChatbot() {
    const chatbotContainer = document.getElementById('chatbot-container');
    if (chatbotContainer) {
        const isVisible = chatbotContainer.style.display !== 'none';
        chatbotContainer.style.display = isVisible ? 'none' : 'flex';
        
        if (!isVisible) {
            // Focus input when opened
            setTimeout(() => {
                const input = document.getElementById('chatInput');
                if (input) input.focus();
            }, 100);
        }
    }
}

/**
 * Send chat message to backend
 */
async function sendChat() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();

    if (!message || isLoading) return;

    // Clear input
    chatInput.value = '';
    chatInput.disabled = true;

    // Add user message
    addUserMessage(message);

    try {
        isLoading = true;

        // Show typing indicator
        const typingId = addTypingIndicator();

        // Send to chatbot API
        const response = await sendChatToAPI(message);

        // Remove typing indicator
        removeTypingIndicator(typingId);

        // Add bot response with typing animation
        addBotMessage(response, false);

        // Store in history
        chatHistory.push({
            role: 'user',
            message: message,
            timestamp: new Date()
        });
        chatHistory.push({
            role: 'bot',
            message: response,
            timestamp: new Date()
        });

    } catch (error) {
        console.error('Error sending chat message:', error);
        removeTypingIndicator();
        addBotMessage('Sorry, I encountered an error. Please try again.', false, true);
    } finally {
        isLoading = false;
        chatInput.disabled = false;
        chatInput.focus();
    }
}

/**
 * Send message to backend API
 */
async function sendChatToAPI(message) {
    const response = await fetch(`${API_BASE_URL}/chatbot/message`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.response || 'I didn\'t understand that. Could you clarify?';
}

/**
 * Add user message to chat
 */
function addUserMessage(message) {
    const messagesDiv = document.getElementById('chatMessages');
    if (!messagesDiv) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.style.animation = 'slideInUp 0.3s ease-out';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = `<p>${escapeHtml(message)}</p>`;
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.appendChild(content);
    messageDiv.appendChild(time);
    messagesDiv.appendChild(messageDiv);
    
    // Auto scroll
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

/**
 * Add bot message to chat with typing animation
 */
function addBotMessage(message, isWelcome = false, isError = false) {
    const messagesDiv = document.getElementById('chatMessages');
    if (!messagesDiv) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = isError ? 'message bot-message error' : 'message bot-message';
    messageDiv.style.animation = 'slideInUp 0.3s ease-out';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Format message with line breaks
    const formattedMessage = message
        .replace(/\n/g, '<br>')
        .replace(/\(\d\)/g, '<strong>$&</strong>');
    
    content.innerHTML = `<p>${formattedMessage}</p>`;
    
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.appendChild(content);
    messageDiv.appendChild(time);
    messagesDiv.appendChild(messageDiv);
    
    // Auto scroll
    setTimeout(() => {
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }, 100);
    
    return content;
}

/**
 * Add typing indicator
 */
function addTypingIndicator() {
    const messagesDiv = document.getElementById('chatMessages');
    if (!messagesDiv) return null;

    const indicatorDiv = document.createElement('div');
    indicatorDiv.className = 'message bot-message typing';
    indicatorDiv.id = 'typing-indicator';
    indicatorDiv.style.animation = 'slideInUp 0.3s ease-out';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = '<div class="typing-animation"><span></span><span></span><span></span></div>';
    
    indicatorDiv.appendChild(content);
    messagesDiv.appendChild(indicatorDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    return 'typing-indicator';
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator(id = 'typing-indicator') {
    const indicator = document.getElementById(id || 'typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Clear chat history
 */
function clearChatHistory() {
    const messagesDiv = document.getElementById('chatMessages');
    if (messagesDiv) {
        messagesDiv.innerHTML = '';
        chatHistory = [];
        addBotMessage("Chat cleared. How can I help you today?", true);
    }
}

// Export to global
window.sendChat = sendChat;
window.clearChatHistory = clearChatHistory;
window.toggleChatbot = toggleChatbot;
