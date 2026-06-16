const app            = document.getElementById("chat-app");
let conversationId   = app.dataset.conversationId;   // "" si nouvelle conversation
const streamUrl      = app.dataset.streamUrl;
const chunksUrl      = `${app.dataset.chunksUrl}?conversation_id=${conversationId}`;
const csrfToken      = app.dataset.csrfToken;
const messages       = document.getElementById("messages");



// Formatter la date
function formatDate(dateStr) {
    const date = new Date(dateStr);
    const day     = String(date.getDate()).padStart(2, "0");
    const month   = String(date.getMonth() + 1).padStart(2, "0");
    const hours   = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    return `${day}/${month} ${hours}:${minutes}`;
}

// Afficher les chunks sous le stream, sans recharger la page
function displayChunks(chunks) {
    console.log(chunks)

    if (!chunks || chunks.length === 0) return;

    const container = document.createElement("div");
    container.className = "mt-2 px-2";

    const title = document.createElement("p");
    title.className   = "text-xs text-gray-400 mb-1";
    title.textContent = "📚 Sources :";
    container.appendChild(title);
    const chunksList = document.createElement("div");
    chunksList.className = "flex flex-col gap-1"
    container.appendChild(chunksList)

    chunks.forEach(chunk => {
        const tag = document.createElement("span");
        tag.className = "inline-block bg-gray-100 text-gray-500 text-xs rounded px-2";

        const titre       = chunk.titre   ? ` ${chunk.titre}`          : "";
        const page       = chunk.page       ? ` p.${chunk.page}`          : "";
        const similarity = chunk.similarity ? ` (${chunk.similarity})`    : "";
        tag.textContent  = `${titre}${page}${similarity}`;

        chunksList.appendChild(tag);
    });

    messages.appendChild(container)

    // const lastMessage = document.querySelector("#messages > div:last-child");
    // lastMessage.insertAdjacentElement("afterend", container);
}


function scrollToBottom() {
    messages.scrollTop = messages.scrollHeight;
}


function addUserMessage(content) {
    const wrapper = document.createElement("div");
    wrapper.className = "flex justify-end";
    wrapper.innerHTML = `
        <div class="bg-color-header text-white px-4 py-3 rounded-2xl rounded-tr-sm max-w-xl text-sm shadow">
            ${escapeHtml(content)}
        </div>`;
    messages.appendChild(wrapper);
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
    messages.appendChild(wrapper);

    // Récupérer les chunks du dernier message de l'assistant, sans recharger la page
    fetch(chunksUrl)
        .then(response => {
          if (!response.ok) {
            throw new Error("Erreur réseau : " + response.status);
          }
          return response.json();
        })
        .then(data => {
            displayChunks(data.chunks)
        })
        .catch(error => {
          console.error("Erreur :", error);
        });
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
    const question = input.value.trim();
    
    if (!question) return;

    addUserMessage(question);
    input.value  = "";
    btn.disabled = true;

    // Affiche la zone streaming + animation
    const streamingMsg     = document.getElementById("streaming-msg");
    const streamingContent = document.getElementById("streaming-content");
    
    messages.appendChild(streamingMsg);   // ← déplace à la fin du DOM
    streamingContent.textContent = "";
    streamingContent.dataset.raw    = "";   // reset du texte brut accumulé     +++
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

            // reader est un ReadableStreamDefaultReader — il lit le flux SSE octet par octet. reader.read() retourne une Promise qui se résout quand un nouveau morceau de données arrive. done est true quand le serveur ferme la connexion, value est un Uint8Array (tableau d'octets bruts).
            reader.read().then(({ done, value }) => {

                // Si le serveur a fermé la connexion, on cache le bloc streaming et on réactive le bouton. Le return arrête la récursion.
                if (done) {
                    streamingMsg.classList.add("hidden");
                    streamingContent.textContent = "";
                    btn.disabled = false;
                    return;
                }

                // Convertit les octets bruts Uint8Array en texte lisible via TextDecoder (UTF-8 par défaut).
                const text = decoder.decode(value);

                // Découpe le texte reçu ligne par ligne, ignore les lignes vides et celles qui ne commencent pas par data:  (format SSE), puis parse le JSON de chaque ligne utile.
                text.split("\n").forEach(line => {
                    if (!line) return;   

                    if (!line.startsWith("data: ")) return;

                    const data = line.slice(6).trim();

                    if (!data) return;

                    try {
                        const msg = JSON.parse(data);

                        if (msg.type === "token") {
                            streamingContent.textContent += msg.value.replace(/\n/g, " ");
                            scrollToBottom();

                        // // --- chunks
                        // } else if (msg.type === "chunks") {
                        //     console.log("> chunks > msg.value : ", msg.value)
                        //     pendingChunks = msg.value;
                        // // // --- 

                        } else if (msg.type === "done") {
                            const finalContent = streamingContent.textContent;
                            streamingMsg.classList.add("hidden");
                            streamingContent.textContent = "";
                            addAssistantMessage(finalContent);
                            // console.log("> displayChunks  : ", pendingChunks)
                            // if (pendingChunks) {
                            //     displayChunks(pendingChunks);
                            //     pendingChunks = null;
                            // }
                            btn.disabled = false;
                            // fetchAndDisplayChunks();
                        }

                    } catch(e) {
                        // Fallback texte brut
                        if (data !== "[DONE]") {
                            streamingContent.textContent += data;
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


