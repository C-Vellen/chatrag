const app            = document.getElementById("chat-app");
let conversationId   = app.dataset.conversationId;   // "" si nouvelle conversation
const streamUrl      = app.dataset.streamUrl;
const csrfToken      = app.dataset.csrfToken;


// Formatter la date
function formatDate(dateStr) {
    const date = new Date(dateStr);
    const day     = String(date.getDate()).padStart(2, "0");
    const month   = String(date.getMonth() + 1).padStart(2, "0");
    const hours   = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    return `${day}/${month} ${hours}:${minutes}`;
}

function scrollToBottom() {
    const msgs = document.getElementById("messages");
    msgs.scrollTop = msgs.scrollHeight;
}

function addUserMessage(content) {
    const wrapper = document.createElement("div");
    wrapper.className = "flex justify-end";
    wrapper.innerHTML = `
        <div class="bg-color-header text-white px-4 py-3 rounded-2xl rounded-tr-sm max-w-xl text-sm shadow">
            ${escapeHtml(content)}
        </div>`;
    document.getElementById("messages").appendChild(wrapper);
    scrollToBottom();
}

function addAssistantMessage(content) {
    const wrapper = document.createElement("div");
    // wrapper.className = "flex flex-col gap-1 max-w-xl";
    wrapper.className = "flex flex-col gap-1 w-full";
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
    const messagesContainer = document.getElementById("messages");
    const streamingMsg     = document.getElementById("streaming-msg");
    const streamingContent = document.getElementById("streaming-content");
    
    messagesContainer.appendChild(streamingMsg);   // ← déplace à la fin du DOM
    streamingContent.textContent = "";
    streamingMsg.classList.remove("hidden");
    scrollToBottom();

    fetch(streamUrl, {
        method:  "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken":  csrfToken,
        },
        body: `question=${encodeURIComponent(question)}&conversation_id=${conversationId}`,
    })
    .then(response => {
        // Récupérer l'id de la conversation créée côté serveur
        const newId = response.headers.get("X-Conversation-Id");
        const newDate = response.headers.get("X-Conversation-Date");
        const newTitle = response.headers.get("X-Conversation-Title");
        if (newId && !conversationId) {
            conversationId = newId;
            // Mettre à jour l'URL sans recharger la page
            history.replaceState(null, "", `?conversation_id=${conversationId}`);

            // Ajouter la conversation dans la sidebar
            if (newTitle) {
                const sidebar = document.getElementById("conversations-list");
                const link    = document.createElement("a");
                link.href      = `?conversation_id=${conversationId}`;
                link.className = "block px-3 py-2 rounded-lg text-sm mb-1 truncate bg-slate-50 text-slate-600 font-semibold";
                link.textContent = `${formatDate(newDate)} --- ${newTitle || "Nouvelle conversation"}`;
                sidebar.prepend(link);
            }
        }
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


