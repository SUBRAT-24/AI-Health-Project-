/**
 * Help Page JavaScript
 * Handles FAQ, support tickets, and feedback
 */

document.addEventListener('DOMContentLoaded', function () {
    if (!window.healthAssistant.isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }
    populateUserBar();
    loadTickets();
});

function populateUserBar() {
    const userName = localStorage.getItem('userName') || 'User';
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    const el = (id) => document.getElementById(id);
    if (el('topbarUserName')) el('topbarUserName').textContent = userName;
    if (el('topbarUserEmail')) el('topbarUserEmail').textContent = userData.email || '';
    if (el('userAvatar')) el('userAvatar').textContent = userName.charAt(0).toUpperCase();
}

// ─── TAB SWITCHING ──────────────────────────────────────────────────────────────

function switchHelpTab(tab) {
    document.querySelectorAll('.settings-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.settings-panel').forEach(p => p.classList.remove('active'));
    document.querySelector(`.settings-tab[data-tab="${tab}"]`).classList.add('active');
    document.getElementById('help-' + tab).classList.add('active');
}

// ─── FAQ ────────────────────────────────────────────────────────────────────────

function toggleFAQ(element) {
    const item = element.parentElement;
    const wasOpen = item.classList.contains('open');
    // Close all
    document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
    // Toggle clicked
    if (!wasOpen) item.classList.add('open');
}

function filterFAQCategory(category, btn) {
    document.querySelectorAll('.faq-cat-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    document.querySelectorAll('.faq-item').forEach(item => {
        if (category === 'all' || item.dataset.category === category) {
            item.classList.remove('hidden');
        } else {
            item.classList.add('hidden');
        }
    });
}

function filterFAQ(searchText) {
    const query = searchText.toLowerCase().trim();
    document.querySelectorAll('.faq-item').forEach(item => {
        const q = item.querySelector('.faq-question span').textContent.toLowerCase();
        const a = item.querySelector('.faq-answer').textContent.toLowerCase();
        if (!query || q.includes(query) || a.includes(query)) {
            item.classList.remove('hidden');
        } else {
            item.classList.add('hidden');
        }
    });
}

// ─── SUPPORT TICKETS ────────────────────────────────────────────────────────────

async function loadTickets() {
    const container = document.getElementById('ticketsList');
    if (!container) return;
    try {
        const data = await window.healthAssistant.apiRequest('/settings/support/tickets');
        if (!data || !data.tickets || data.tickets.length === 0) {
            container.innerHTML = '<p class="empty-state">No support tickets yet. Submit one above if you need help!</p>';
            return;
        }
        container.innerHTML = data.tickets.map(t => `
            <div class="ticket-item">
                <div class="ticket-info">
                    <div class="ticket-subject">${escHtml(t.subject)}</div>
                    <div class="ticket-meta">${t.category} · ${new Date(t.created_at).toLocaleDateString()}</div>
                </div>
                <span class="ticket-status ${t.status}">${t.status.replace('_', ' ')}</span>
            </div>
        `).join('');
    } catch (e) {
        container.innerHTML = '<p class="empty-state">Failed to load tickets</p>';
    }
}

async function submitTicket() {
    const el = (id) => document.getElementById(id);
    const subject = el('ticketSubject').value.trim();
    const message = el('ticketMessage').value.trim();
    if (!subject || !message) return window.healthAssistant.showToast('Subject and message are required', 'error');
    try {
        await window.healthAssistant.apiRequest('/settings/support/tickets', 'POST', {
            subject, message,
            category: el('ticketCategory').value,
            priority: el('ticketPriority').value,
        });
        window.healthAssistant.showToast('Ticket submitted successfully!', 'success');
        el('ticketSubject').value = '';
        el('ticketMessage').value = '';
        loadTickets();
    } catch (e) {}
}

// ─── FEEDBACK ───────────────────────────────────────────────────────────────────

async function submitFeedback() {
    const el = (id) => document.getElementById(id);
    const msg = el('feedbackMsg').value.trim();
    if (!msg) return window.healthAssistant.showToast('Please write your feedback', 'error');
    try {
        await window.healthAssistant.apiRequest('/settings/feedback', 'POST', {
            subject: el('feedbackType').value + ' Feedback',
            message: msg,
        });
        window.healthAssistant.showToast('Thank you for your feedback!', 'success');
        el('feedbackMsg').value = '';
    } catch (e) {}
}

// ─── UTILITY ────────────────────────────────────────────────────────────────────

function escHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
