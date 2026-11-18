
// ==========================================
// DOM ELEMENTS
// ==========================================

const chatArea = document.getElementById("chatArea");

const messagesContainer = document.getElementById("messages");

const messageInput = document.getElementById("messageInput");

const sendButton = document.getElementById("sendButton");

const welcomeScreen = document.getElementById("welcomeScreen");

const usageInfo = document.getElementById("usageInfo");

const modelSelect = document.getElementById("modelSelect");

const refreshModelsButton = document.getElementById("refreshModels");

const historyList = document.getElementById("historyList");

const sidebar = document.getElementById("sidebar");


// ==========================================
// APPLICATION STATE
// ==========================================

let conversationHistory = [];

let isLoading = false;

let conversationId = Date.now();

let conversations = [];


// ==========================================
// LOAD FREE MODELS
// ==========================================

async function loadFreeModels(refresh = false) {

    const previousModel = modelSelect.value;

    modelSelect.disabled = true;

    modelSelect.innerHTML = `
        <option value="">Loading free models...</option>
    `;

    try {

        let url = "/api/models/free";

        if (refresh) {
            url += "?refresh=true";
        }

        const response = await fetch(url);

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail || "Unable to load models"
            );

        }

        modelSelect.innerHTML = "";

        if (!data.models || data.models.length === 0) {

            modelSelect.innerHTML = `
                <option value="">No free models available</option>
            `;

            usageInfo.textContent = "No models available";

            return;

        }


        // Add available models

        data.models.forEach(model => {

            const option = document.createElement("option");

            option.value = model.id;

            option.textContent = model.name;

            modelSelect.appendChild(option);

        });


        // Restore previous selection if available

        const modelExists = data.models.some(
            model => model.id === previousModel
        );

        if (modelExists) {

            modelSelect.value = previousModel;

        } else {

            modelSelect.value = data.default_model;

        }


        usageInfo.textContent =
            `${data.total} free models available`;

    }

    catch (error) {

        console.error("Model loading error:", error);

        modelSelect.innerHTML = `
            <option value="">Unable to load models</option>
        `;

        usageInfo.textContent = "Model loading failed";

    }

    finally {

        modelSelect.disabled = false;

    }

}


// ==========================================
// MODEL SWITCHING
// ==========================================

modelSelect.addEventListener("change", function () {

    const selectedModel = modelSelect.value;

    if (!selectedModel) {
        return;
    }

    usageInfo.textContent =
        "Active model: " + selectedModel;

});


// ==========================================
// REFRESH MODELS
// ==========================================

refreshModelsButton.addEventListener("click", async function () {

    refreshModelsButton.disabled = true;

    refreshModelsButton.classList.add("rotating");

    await loadFreeModels(true);

    refreshModelsButton.disabled = false;

    refreshModelsButton.classList.remove("rotating");

});


// ==========================================
// ADD MESSAGE TO CHAT
// ==========================================

function addMessage(message, sender) {

    const messageDiv = document.createElement("div");

    messageDiv.className = "message " + sender;


    const avatar = document.createElement("div");

    avatar.className = "message-avatar";

    if (sender === "user") {

        avatar.innerHTML = `
            <i class="fa-solid fa-user"></i>
        `;

    } else {

        avatar.innerHTML = `
            <i class="fa-solid fa-brain"></i>
        `;

    }


    const content = document.createElement("div");

    content.className = "message-content";

    // Use textContent to prevent HTML injection.

    content.textContent = message;


    messageDiv.appendChild(avatar);

    messageDiv.appendChild(content);

    messagesContainer.appendChild(messageDiv);

    scrollToBottom();

}


// ==========================================
// LOADING INDICATOR
// ==========================================

function showTypingIndicator() {

    const typingDiv = document.createElement("div");

    typingDiv.id = "typingIndicator";

    typingDiv.className = "message assistant";

    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fa-solid fa-brain"></i>
        </div>

        <div class="message-content typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    messagesContainer.appendChild(typingDiv);

    scrollToBottom();

}


function removeTypingIndicator() {

    const indicator = document.getElementById(
        "typingIndicator"
    );

    if (indicator) {
        indicator.remove();
    }

}


// ==========================================
// SEND MESSAGE
// ==========================================

async function sendMessage() {

    const userMessage = messageInput.value.trim();

    if (!userMessage || isLoading) {
        return;
    }


    const selectedModel = modelSelect.value;

    if (!selectedModel) {

        usageInfo.textContent = "Select an available model";

        return;

    }


    isLoading = true;

    sendButton.disabled = true;

    messageInput.disabled = true;


    // Hide welcome screen

    welcomeScreen.style.display = "none";


    // Display user message

    addMessage(userMessage, "user");


    // Clear input

    messageInput.value = "";

    messageInput.style.height = "auto";


    // Display loading indicator

    showTypingIndicator();

    usageInfo.textContent = "Generating response...";


    try {

        const response = await fetch("/agent/run", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                message: userMessage,

                model: selectedModel,

                conversation: conversationHistory

            })

        });


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail || "Unable to generate response"
            );

        }


        removeTypingIndicator();


        // Display AI response

        addMessage(data.response, "assistant");


        // Update conversation history

        conversationHistory.push({

            role: "user",

            content: userMessage

        });

        conversationHistory.push({

            role: "assistant",

            content: data.response

        });


        // Keep the latest 20 messages

        if (conversationHistory.length > 20) {

            conversationHistory =
                conversationHistory.slice(-20);

        }


        // Update usage information

        if (data.usage) {

            usageInfo.textContent =
                `Model: ${data.model} | Tokens: ${data.usage.total_tokens ?? "N/A"}`;

        }


        // Save conversation

        saveConversation();


    }

    catch (error) {

        removeTypingIndicator();

        console.error("Chat error:", error);

        addMessage(
            "Error: " + error.message,
            "assistant"
        );

        usageInfo.textContent = "Request failed";

    }

    finally {

        isLoading = false;

        sendButton.disabled = false;

        messageInput.disabled = false;

        messageInput.focus();

    }

}


// ==========================================
// SUGGESTED PROMPTS
// ==========================================

function useSuggestion(message) {

    messageInput.value = message;

    sendMessage();

}


// ==========================================
// NEW CONVERSATION
// ==========================================

function newChat() {

    if (isLoading) {
        return;
    }

    saveConversation();

    conversationHistory = [];

    conversationId = Date.now();

    messagesContainer.innerHTML = "";

    welcomeScreen.style.display = "flex";

    usageInfo.textContent = "New conversation";

    messageInput.value = "";

    messageInput.focus();

}


// ==========================================
// SAVE CONVERSATION
// ==========================================

function saveConversation() {

    if (conversationHistory.length === 0) {
        return;
    }

    const existingIndex = conversations.findIndex(
        item => item.id === conversationId
    );

    const conversation = {

        id: conversationId,

        title: conversationHistory[0].content.substring(0, 40),

        messages: [...conversationHistory]

    };


    if (existingIndex !== -1) {

        conversations[existingIndex] = conversation;

    } else {

        conversations.unshift(conversation);

    }


    localStorage.setItem(
        "llm_conversations",
        JSON.stringify(conversations)
    );

    renderHistory();

}


// ==========================================
// LOAD CONVERSATIONS
// ==========================================

function loadConversations() {

    try {

        const saved = localStorage.getItem(
            "llm_conversations"
        );

        conversations = saved ? JSON.parse(saved) : [];

        if (!Array.isArray(conversations)) {
            conversations = [];
        }

    }

    catch (error) {

        console.error("History loading error:", error);

        conversations = [];

    }

    renderHistory();

}


// ==========================================
// RENDER HISTORY
// ==========================================

function renderHistory() {

    historyList.innerHTML = "";

    if (conversations.length === 0) {

        historyList.innerHTML = `
            <div class="history-empty">
                No conversations yet
            </div>
        `;

        return;

    }


    conversations.forEach(conversation => {

        const button = document.createElement("button");

        button.className = "history-item";

        button.textContent = conversation.title;

        button.addEventListener("click", function () {

            openConversation(conversation.id);

        });

        historyList.appendChild(button);

    });

}


// ==========================================
// OPEN CONVERSATION
// ==========================================

function openConversation(id) {

    if (isLoading) {
        return;
    }

    const conversation = conversations.find(
        item => item.id === id
    );

    if (!conversation) {
        return;
    }


    conversationId = conversation.id;

    conversationHistory = [...conversation.messages];

    messagesContainer.innerHTML = "";

    welcomeScreen.style.display = "none";


    conversationHistory.forEach(message => {

        addMessage(
            message.content,
            message.role === "user" ? "user" : "assistant"
        );

    });


    usageInfo.textContent = "Previous conversation";

}


// ==========================================
// CLEAR HISTORY
// ==========================================

function clearHistory() {

    if (isLoading) {
        return;
    }

    const confirmed = confirm(
        "Are you sure you want to clear all conversations?"
    );

    if (!confirmed) {
        return;
    }

    conversations = [];

    conversationHistory = [];

    localStorage.removeItem("llm_conversations");

    conversationId = Date.now();

    messagesContainer.innerHTML = "";

    welcomeScreen.style.display = "flex";

    renderHistory();

    usageInfo.textContent = "Conversation history cleared";

}


// ==========================================
// MOBILE SIDEBAR
// ==========================================

function toggleSidebar() {

    sidebar.classList.toggle("active");

}


// ==========================================
// SCROLL CHAT
// ==========================================

function scrollToBottom() {

    chatArea.scrollTop = chatArea.scrollHeight;

}


// ==========================================
// TEXTAREA AUTO RESIZE
// ==========================================

messageInput.addEventListener("input", function () {

    messageInput.style.height = "auto";

    messageInput.style.height =
        Math.min(messageInput.scrollHeight, 180) + "px";

});


// ==========================================
// ENTER TO SEND
// SHIFT + ENTER FOR NEW LINE
// ==========================================

messageInput.addEventListener("keydown", function (event) {

    if (
        event.key === "Enter" &&
        !event.shiftKey
    ) {

        event.preventDefault();

        sendMessage();

    }

});


// ==========================================
// INITIALIZE APPLICATION
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    loadFreeModels();

    loadConversations();

});
