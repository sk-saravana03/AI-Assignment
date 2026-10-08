// Client-side interactions for College Examination FAQ Chatbot
document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const clearBtn = document.getElementById('clear-btn');
    const suggestionChips = document.querySelectorAll('.chip');

    // Auto-focus input on page load
    userInput.focus();

    // Helper: format current time (e.g. 10:15 AM)
    function getTimeString() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    // Helper: auto scroll to bottom of chat
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Append User Message to UI
    function appendUserMessage(text) {
        const row = document.createElement('div');
        row.className = 'message-row user-row';

        const avatar = document.createElement('div');
        avatar.className = 'avatar user-avatar';
        avatar.textContent = 'YOU';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble user-bubble';

        const p = document.createElement('p');
        p.textContent = text;

        const meta = document.createElement('span');
        meta.className = 'msg-meta';
        meta.textContent = `${getTimeString()}`;

        bubble.appendChild(p);
        bubble.appendChild(meta);
        row.appendChild(avatar);
        row.appendChild(bubble);

        chatMessages.appendChild(row);
        scrollToBottom();
    }

    // Append Bot Message to UI
    function appendBotMessage(text, confidence = null) {
        const row = document.createElement('div');
        row.className = 'message-row bot-row';

        const avatar = document.createElement('div');
        avatar.className = 'avatar bot-avatar';
        avatar.textContent = 'EX';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble bot-bubble';

        const p = document.createElement('p');
        p.textContent = text;

        const meta = document.createElement('span');
        meta.className = 'msg-meta';
        if (confidence !== null && confidence !== undefined && confidence > 0) {
            meta.textContent = `Match Confidence: ${(confidence * 100).toFixed(1)}% \u2022 ${getTimeString()}`;
        } else {
            meta.textContent = `System \u2022 ${getTimeString()}`;
        }

        bubble.appendChild(p);
        bubble.appendChild(meta);
        row.appendChild(avatar);
        row.appendChild(bubble);

        chatMessages.appendChild(row);
        scrollToBottom();
    }

    // Show temporary typing indicator
    function showTypingIndicator() {
        const row = document.createElement('div');
        row.className = 'message-row bot-row typing-row';
        row.id = 'typing-indicator-row';

        const avatar = document.createElement('div');
        avatar.className = 'avatar bot-avatar';
        avatar.textContent = 'EX';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble bot-bubble';

        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';

        bubble.appendChild(indicator);
        row.appendChild(avatar);
        row.appendChild(bubble);

        chatMessages.appendChild(row);
        scrollToBottom();
    }

    // Remove typing indicator
    function hideTypingIndicator() {
        const typingRow = document.getElementById('typing-indicator-row');
        if (typingRow) {
            typingRow.remove();
        }
    }

    // Send question to backend API: POST /api/chat
    async function sendQuestion(question) {
        const trimmed = question.trim();
        if (!trimmed) return;

        appendUserMessage(trimmed);
        userInput.value = '';
        showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: trimmed })
            });

            hideTypingIndicator();

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                const errMsg = errData.answer || 'An error occurred while communicating with the examination server.';
                appendBotMessage(errMsg);
                return;
            }

            const data = await response.json();
            appendBotMessage(data.answer, data.confidence);
        } catch (error) {
            hideTypingIndicator();
            appendBotMessage('Unable to connect to the examination chatbot server. Please check your network connection.');
        } finally {
            userInput.focus();
        }
    }

    // Form submission event
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = userInput.value;
        sendQuestion(text);
    });

    // Handle suggestion chips click
    suggestionChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const question = chip.getAttribute('data-question');
            if (question) {
                sendQuestion(question);
            }
        });
    });

    // Clear chat conversation
    clearBtn.addEventListener('click', () => {
        chatMessages.innerHTML = `
            <div class="message-row bot-row">
                <div class="avatar bot-avatar">EX</div>
                <div class="message-bubble bot-bubble">
                    <p>Conversation cleared. Feel free to ask another examination question!</p>
                    <span class="msg-meta">System &bull; Ready</span>
                </div>
            </div>
        `;
        userInput.value = '';
        userInput.focus();
    });
});
