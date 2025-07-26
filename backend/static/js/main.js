document.addEventListener("DOMContentLoaded", () => {
    const chatbox = document.getElementById('chatbox');
    showMessage("Hello! I'm Aditi, your Pharmaceutical Assistant. How can I help you today?", "aditi");
    document.getElementById("userInput").focus();
});

async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    showMessage(message, "user");
    await showTyping();

    const endpoint = message.toLowerCase().includes("symptom") || message.toLowerCase().includes("feel") ?
        '/symptom_checker' :
        '/get_drug_info';

    const payload = message.toLowerCase().includes("symptom") ?
        {
            symptoms: message
        } :
        {
            drug_name: message
        };

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        const formattedResponse = formatResponse(data.response || "I'm here to help with your pharmaceutical questions!");
        showMessage(formattedResponse, "aditi");
    } catch (error) {
        showMessage("Sorry, I encountered an issue. Please try again.", "aditi");
    }
    document.getElementById("userInput").focus();
}

function showMessage(message, sender) {
    const chatbox = document.getElementById('chatbox');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.innerHTML = message;
    chatbox.appendChild(messageDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
}

async function showTyping() {
    const chatbox = document.getElementById('chatbox');
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('typing', 'aditi');
    typingDiv.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    chatbox.appendChild(typingDiv);
    chatbox.scrollTop = chatbox.scrollHeight;

    await new Promise(resolve => setTimeout(resolve, 1000));
    chatbox.removeChild(typingDiv);
}

function formatResponse(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/\n/g, "<br>");
}

document.getElementById("userInput").addEventListener("keypress", function(event) {
    if (event.key === "Enter") sendMessage();
});

// Toggle the profile menu visibility
function toggleProfileMenu() {
    const profileContainer = document.querySelector('.profile-container');
    profileContainer.classList.toggle('active');
}

// Logout function
function logout() {
    // Here you can add your logout logic (e.g., clearing session or redirecting to a login page)
    window.location.href = '/'; // Redirect to login page after logout
}
