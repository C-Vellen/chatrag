function scrollToBottom() {
    const msgs = document.getElementById("messages");
    msgs.scrollTop = msgs.scrollHeight;
}

function addUserMessage(content) {
    const wrapper = document.createElement("div");
    wrapper.className = "flex justify-end";
    wrapper.innerHTML = `
        <div class="bg-header text-white px-4 py-3 rounded-2xl rounded-tr-sm max-w-xl text-sm shadow">
            ${escapeHtml(content)}
        </div>`;
    document.getElementById("messages").appendChild(wrapper);
    scrollToBottom();
}

function addAssistantMessage(content) {
    const wrapper = document.createElement("div");
    wrapper.className = "flex flex-col gap-1 max-w-xl";
    wrapper.innerHTML = `
        <div class="bg-white text-gray-800 px-4 py-3 rounded-2xl rounded-tl-sm text-sm shadow">
            ${escapeHtml(content)}
        </div>`;
    document.getElementById("messages").appendChild(wrapper);
    scrollToBottom();
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\n/g, "<br>");
}

function sendMessage() {
    const input    = document.getElementById("question");
    const btn      = document.getElementById("send-btn");
    const url = btn.dataset.url;
    const question = input.value.trim();
    if (!question) return;

    addUserMessage(question);
    input.value  = "";
    btn.disabled = true;

    // Affiche la zone streaming + animation
    const streamingMsg     = document.getElementById("streaming-msg");
    const streamingContent = document.getElementById("streaming-content");
    streamingContent.textContent = "";
    streamingMsg.classList.remove("hidden");
    scrollToBottom();

    fetch(url, {
        method:  "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken":  document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: `question=${encodeURIComponent(question)}&conversation_id=${conversationId}`,
    })
    .then(response => {
        const reader  = response.body.getReader();
        const decoder = new TextDecoder();

        function read() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    const finalContent = streamingContent.textContent;
                    streamingMsg.classList.add("hidden");
                    streamingContent.textContent = "";
                    addAssistantMessage(finalContent);
                    btn.disabled = false;
                    return;
                }

                const text = decoder.decode(value);
                text.split("\n").forEach(line => {
                    if (line.startsWith("data: ")) {
                        const token = line.slice(6);
                        if (token !== "[DONE]") {
                            streamingContent.textContent += token;
                            scrollToBottom();
                        }
                    }
                });
                read();
            });
        }
        read();
    })
    .catch(() => {
        streamingMsg.classList.add("hidden");
        addAssistantMessage("❌ Erreur de connexion.");
        btn.disabled = false;
    });
}

document.getElementById("question").addEventListener("keydown", e => {
    if (e.key === "Enter" && e.ctrlKey) sendMessage();
});

document.getElementById("send-btn").addEventListener("click", sendMessage);

scrollToBottom();