async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    const chatBox = document.getElementById("chat-box");

    if (!message) return;

    // Show user message
    chatBox.innerHTML += `<div class="message user">${message}</div>`;
    input.value = "";

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        // Show bot response
        chatBox.innerHTML += `<div class="message bot">${data.response}</div>`;
    } catch (error) {
        chatBox.innerHTML += `<div class="message bot">Error connecting to server</div>`;
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}

// Press Enter to send message
document.getElementById("user-input").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});