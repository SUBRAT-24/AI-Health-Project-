/**
 * AI Health Assistant - Chatbot (Gemini-Powered)
 * Full chatbot with AI responses, image/file upload, suggestions, and markdown rendering
 */

let chatHistory = [];
let isLoading = false;
let selectedFile = null;

document.addEventListener('DOMContentLoaded', function () {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter' && !isLoading) sendChat();
        });
    }

    const sendButton = document.getElementById('chatSendBtn');
    if (sendButton) sendButton.addEventListener('click', sendChat);

    // Welcome message
    addBotMessage("Hello! 👋 I'm **HealthAI**, your personal health assistant powered by AI.\n\nI can help with:\n• Health questions & symptoms\n• Diet & nutrition advice\n• Exercise recommendations\n• Analyze medical reports & images\n• Mental wellness tips\n\n📎 Upload an image or PDF for analysis!", true);

    // Load suggestions
    loadSuggestions();
});

// ─── SUGGESTIONS ────────────────────────────────────────────────────────────────

async function loadSuggestions() {
    const container = document.getElementById('chatSuggestions');
    if (!container) return;

    const suggestions = [
        { icon: '💓', text: 'Healthy heart rate?' },
        { icon: '🥗', text: 'Healthy breakfast ideas' },
        { icon: '🏃', text: 'Exercises for beginners' },
        { icon: '😴', text: 'Better sleep tips' },
        { icon: '💊', text: 'Manage blood pressure' },
        { icon: '🧘', text: 'Stress relief techniques' },
    ];

    container.innerHTML = suggestions.map(s =>
        `<button class="suggestion-chip" onclick="useSuggestion('${s.text}')">${s.icon} ${s.text}</button>`
    ).join('');
}

function useSuggestion(text) {
    const input = document.getElementById('chatInput');
    if (input) {
        input.value = text;
        sendChat();
    }
    // Hide suggestions after first use
    const container = document.getElementById('chatSuggestions');
    if (container) container.style.display = 'none';
}

// ─── FILE HANDLING ──────────────────────────────────────────────────────────────

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf'];
    if (!validTypes.includes(file.type)) {
        window.healthAssistant && window.healthAssistant.showToast('Please upload an image (JPG, PNG) or PDF', 'error');
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        window.healthAssistant && window.healthAssistant.showToast('File size must be under 10MB', 'error');
        return;
    }

    selectedFile = file;
    showFilePreview(file);
}

function showFilePreview(file) {
    const preview = document.getElementById('chatFilePreview');
    const img = document.getElementById('filePreviewImg');
    const name = document.getElementById('filePreviewName');
    if (!preview) return;

    preview.style.display = 'flex';
    name.textContent = file.name;

    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => { img.src = e.target.result; img.style.display = 'block'; };
        reader.readAsDataURL(file);
    } else {
        img.style.display = 'none';
        name.textContent = `📄 ${file.name}`;
    }
}

function removeFilePreview() {
    selectedFile = null;
    const preview = document.getElementById('chatFilePreview');
    const img = document.getElementById('filePreviewImg');
    const fileInput = document.getElementById('chatFileInput');
    if (preview) preview.style.display = 'none';
    if (img) { img.src = ''; img.style.display = 'none'; }
    if (fileInput) fileInput.value = '';
}

// ─── SEND MESSAGE ───────────────────────────────────────────────────────────────

async function sendChat() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();

    if (!message && !selectedFile) return;
    if (isLoading) return;

    chatInput.value = '';
    chatInput.disabled = true;

    // Hide suggestions
    const sugContainer = document.getElementById('chatSuggestions');
    if (sugContainer) sugContainer.style.display = 'none';

    // Show user message
    if (selectedFile && selectedFile.type.startsWith('image/')) {
        addUserMessageWithImage(message || 'Analyze this image', selectedFile);
    } else if (selectedFile) {
        addUserMessage(`📄 ${selectedFile.name}${message ? '\n' + message : ''}`);
    } else {
        addUserMessage(message);
    }

    try {
        isLoading = true;
        const typingId = addTypingIndicator();

        let response;
        if (selectedFile) {
            response = await sendFileToAPI(selectedFile, message || 'Please analyze this file and provide health insights.');
            removeFilePreview();
        } else {
            response = await sendChatToAPI(message);
        }

        removeTypingIndicator(typingId);
        addBotMessage(response, false);

        chatHistory.push({ role: 'user', message, timestamp: new Date() });
        chatHistory.push({ role: 'bot', message: response, timestamp: new Date() });

    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator();
        addBotMessage('Sorry, I encountered an error. Please try again.', false, true);
    } finally {
        isLoading = false;
        chatInput.disabled = false;
        chatInput.focus();
    }
}

// ─── API CALLS ──────────────────────────────────────────────────────────────────

async function sendChatToAPI(message) {
    const token = localStorage.getItem('userToken');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_BASE_URL}/chatbot/message`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ message })
    });

    if (!response.ok) {
        if (response.status === 401 || response.status === 422) {
            return 'Please log in to use the health assistant chatbot.';
        }
        throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.response || data.reply || "I didn't understand that. Could you clarify?";
}

async function sendFileToAPI(file, message) {
    const token = localStorage.getItem('userToken');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('message', message);

    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_BASE_URL}/chatbot/analyze`, {
        method: 'POST',
        headers,
        body: formData
    });

    if (!response.ok) {
        if (response.status === 401 || response.status === 422) {
            return 'Please log in to use file analysis.';
        }
        throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.response || data.reply || "I couldn't analyze this file. Please try again.";
}

// ─── MESSAGE RENDERING ──────────────────────────────────────────────────────────

function renderMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/^### (.*$)/gm, '<h4>$1</h4>')
        .replace(/^## (.*$)/gm, '<h3 style="font-size:1rem;margin:.5rem 0 .25rem;">$1</h3>')
        .replace(/^# (.*$)/gm, '<h3 style="font-size:1.1rem;margin:.5rem 0 .25rem;">$1</h3>')
        .replace(/^[•\-] (.*$)/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/s, '<ul style="padding-left:1.2rem;margin:.25rem 0;">$1</ul>')
        .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
        .replace(/`([^`]+)`/g, '<code style="background:#f0f0f0;padding:1px 4px;border-radius:3px;font-size:.82rem;">$1</code>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
}

function addUserMessage(message) {
    const messagesDiv = document.getElementById('chatMessages');
    if (!messagesDiv) return;

    const div = document.createElement('div');
    div.className = 'message user-message';
    div.style.animation = 'slideInUp 0.3s ease-out';
    div.innerHTML = `
        <div class="message-content"><p>${escapeHtml(message).replace(/\n/g, '<br>')}</p></div>
        <div class="message-time">${timeNow()}</div>
    `;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addUserMessageWithImage(message, file) {
    const messagesDiv = document.getElementById('chatMessages');
    if (!messagesDiv) return;

    const div = document.createElement('div');
    div.className = 'message user-message';
    div.style.animation = 'slideInUp 0.3s ease-out';

    const reader = new FileReader();
    reader.onload = (e) => {
        div.innerHTML = `
            <div class="message-content">
                <img src="${e.target.result}" alt="Uploaded" style="max-width:100%;border-radius:8px;margin-bottom:.5rem;">
                <p>${escapeHtml(message)}</p>
            </div>
            <div class="message-time">${timeNow()}</div>
        `;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    };
    reader.readAsDataURL(file);
    messagesDiv.appendChild(div);
}

function addBotMessage(message, isWelcome = false, isError = false) {
    const messagesDiv = document.getElementById('chatMessages');
    if (!messagesDiv) return;

    const div = document.createElement('div');
    div.className = isError ? 'message bot-message error' : 'message bot-message';
    div.style.animation = 'slideInUp 0.3s ease-out';

    const formattedMessage = renderMarkdown(message);

    div.innerHTML = `
        <div class="message-content"><p>${formattedMessage}</p></div>
        <div class="message-time">${timeNow()}</div>
    `;
    messagesDiv.appendChild(div);
    setTimeout(() => { messagesDiv.scrollTop = messagesDiv.scrollHeight; }, 100);
}

function addTypingIndicator() {
    const messagesDiv = document.getElementById('chatMessages');
    if (!messagesDiv) return null;

    const div = document.createElement('div');
    div.className = 'message bot-message typing';
    div.id = 'typing-indicator';
    div.style.animation = 'slideInUp 0.3s ease-out';
    div.innerHTML = '<div class="message-content"><div class="typing-animation"><span></span><span></span><span></span></div></div>';
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return 'typing-indicator';
}

function removeTypingIndicator(id = 'typing-indicator') {
    const el = document.getElementById(id || 'typing-indicator');
    if (el) el.remove();
}

// ─── UTILITIES ──────────────────────────────────────────────────────────────────

function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function timeNow() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function clearChatHistory() {
    const messagesDiv = document.getElementById('chatMessages');
    if (messagesDiv) {
        messagesDiv.innerHTML = '';
        chatHistory = [];
        addBotMessage("Chat cleared. How can I help you today?", true);
    }
    // Also clear server-side history
    const token = localStorage.getItem('userToken');
    if (token) {
        fetch(`${API_BASE_URL}/chatbot/clear`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        }).catch(() => {});
    }
    // Show suggestions again
    const sug = document.getElementById('chatSuggestions');
    if (sug) { sug.style.display = 'flex'; loadSuggestions(); }
}

// Export to global
window.sendChat = sendChat;
window.clearChatHistory = clearChatHistory;
window.toggleChatbot = toggleChatbot;
window.handleFileSelect = handleFileSelect;
window.removeFilePreview = removeFilePreview;
window.useSuggestion = useSuggestion;

// Keyboard shortcut (Alt+C to toggle)
document.addEventListener('keydown', function (e) {
    if (e.altKey && e.key === 'c') {
        e.preventDefault();
        toggleChatbot();
    }
});
