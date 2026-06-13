const app            = document.getElementById("chat-app");
let conversationId   = app.dataset.conversationId;   // "" si nouvelle conversation
const streamUrl      = app.dataset.streamUrl;
const csrfToken      = app.dataset.csrfToken;

// ------------------------------


// URL passée via data-attribute dans le template
const chunksBaseUrl = app.dataset.chunksUrl;  // "/chat/chunks/"

// async function fetchAndDisplayChunks() {
//     if (!conversationId) return;

//     const url = `${chunksBaseUrl}${conversationId}/`;
//     console.log("Fetch chunks URL:", url);

//     try {
//         const response = await fetch(url);
//         console.log("Fetch chunks status:", response.status);

//         if (!response.ok) {
//             console.error("Erreur HTTP:", response.status, await response.text());
//             return;
//         }

//         const data = await response.json();
//         console.log("Chunks reçus:", data);

//         if (data.chunks && data.chunks.length > 0) {
//             renderChunks(data.chunks);
//         }
//     } catch(e) {
//         console.error("Erreur fetch chunks :", e);
//     }
// }








async function fetchAndDisplayChunks() {
    if (!conversationId) return;

    try {
        const response = await fetch(`${chunksBaseUrl}${conversationId}/`);
        const data     = await response.json();

        if (data.chunks && data.chunks.length > 0) {
            renderChunks(data.chunks);
        }
    } catch(e) {
        console.error("Erreur fetch chunks :", e);
    }
}

function renderChunks(chunks) {
    const container = document.getElementById("chunks-container");
    container.innerHTML = "";   // reset

    const title = document.createElement("p");
    title.className   = "text-xs text-gray-400 mb-1 mt-2";
    title.textContent = "📚 Sources utilisées :";
    container.appendChild(title);

    const tagsWrapper = document.createElement("div");
    tagsWrapper.className = "flex flex-wrap gap-1";

    chunks.forEach(chunk => {
        const tag      = document.createElement("span");
        tag.className  = "inline-block bg-gray-100 text-gray-500 text-xs rounded px-2 py-0.5";
        const page       = chunk.page       ? ` p.${chunk.page}`       : "";
        const similarity = chunk.similarity ? ` — ${chunk.similarity}` : "";
        tag.textContent  = `${chunk.source}${page}${similarity}`;
        tagsWrapper.appendChild(tag);
    });

    container.appendChild(tagsWrapper);
}





// ------------------------------

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
    // const url = btn.dataset.url;                                         ---
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
            reader.read().then(({ done, value }) => {
                if (done) {
                    streamingMsg.classList.add("hidden");
                    streamingContent.textContent = "";
                    btn.disabled = false;
                    return;
                }

                const text = decoder.decode(value);
                text.split("\n").forEach(line => {
                    if (!line) return;   

                    if (!line.startsWith("data: ")) return;

                    const data = line.slice(6).trim();

                    if (!data) return;
                    console.log("RAW DATA:", data);

                    try {
                        const msg = JSON.parse(data);

                        if (msg.type === "token") {
                            streamingContent.textContent += msg.value.replace(/\n/g, " ");
                            scrollToBottom();

                        } else if (msg.type === "done") {
                            const finalContent = streamingContent.textContent;
                            streamingMsg.classList.add("hidden");
                            streamingContent.textContent = "";
                            addAssistantMessage(finalContent);
                            btn.disabled = false;
                            fetchAndDisplayChunks();
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
        // function read() {
        //     reader.read().then(({ done, value }) => {
        //         if (done) {
        //             // const finalContent = streamingContent.textContent;           ---
        //             streamingMsg.classList.add("hidden");
        //             streamingContent.dataset.raw = "";                          //  +++
        //             streamingContent.innerHTML   = "";                          //  +++
        //             // streamingContent.textContent = "";                           ---
        //             // addAssistantMessage(finalContent);                           ---
        //             btn.disabled = false;
        //             return;
        //         }
                

        //         const text = decoder.decode(value);
        //         text.split("\n").forEach(line => {


        //             // if (line.startsWith("data: ")) {
        //             //     const token = line.slice(6);
        //             //     if (token !== "[DONE]") {
        //             //         streamingContent.textContent += token;
        //             //         scrollToBottom();
        //             //     }
        //             // }


        //             if (!line.startsWith("data: ")) return;

        //             const data = line.slice(6).trim();
        //             if (!data) return;

        //             try {
        //                 const msg = JSON.parse(data);

        //                 if (msg.type === "token") {
        //                     // Accumule le texte brut et formate
        //                     const raw = (streamingContent.dataset.raw || "") + msg.value;
        //                     streamingContent.dataset.raw = raw;
        //                     streamingContent.innerHTML   = formatContent(raw);
        //                     scrollToBottom();

        //                 } else if (msg.type === "done") {
        //                     // Fin du stream : finalise le message
        //                     const finalRaw = streamingContent.dataset.raw || "";
        //                     streamingMsg.classList.add("hidden");
        //                     streamingContent.dataset.raw = "";
        //                     streamingContent.innerHTML   = "";
        //                     addAssistantMessage(finalRaw);
        //                     btn.disabled = false;
        //                     fetchAndDisplayChunks();   // ← fetch chunks après le stream
        //                 }

        //             } catch(e) {
        //                 // Ancien format texte brut (fallback)
        //                 if (data !== "[DONE]") {
        //                     const raw = (streamingContent.dataset.raw || "") + data;
        //                     streamingContent.dataset.raw = raw;
        //                     streamingContent.innerHTML   = formatContent(raw);
        //                     scrollToBottom();
        //                 }
        //             }
        //         });
        //         read();
        //     });
        // }
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


