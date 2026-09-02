// ==========================================
// KASHMIR AI CHAT ASSISTANT
// ==========================================

const chatMessages =
    document.getElementById("chatMessages");

const chatInput =
    document.getElementById("chatInput");

const sendButton =
    document.getElementById("sendMessage");

const quickPrompts =
    document.querySelectorAll(
        ".quick-prompts button"
    );


// ==========================================
// SEND MESSAGE
// ==========================================

async function sendMessage(message = null) {

    const userMessage =
        message ||
        chatInput.value.trim();


    if (!userMessage) {
        return;
    }


    // Add user message

    addMessage(
        userMessage,
        "user"
    );


    chatInput.value = "";


    // Loading message

    const loading =
        addLoadingMessage();


    sendButton.disabled = true;


    try {

        const response =
            await fetch(
                "/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message:
                            userMessage
                    })
                }
            );


        const data =
            await response.json();


        loading.remove();


        if (!data.success) {

            addMessage(
                "Sorry, I couldn't process that request. " +
                data.error,
                "ai"
            );

            return;
        }


        addMessage(
            data.response,
            "ai"
        );

    }


    catch (error) {

        loading.remove();

        addMessage(
            "I couldn't connect to the AI service. " +
            "Please make sure Ollama is running.",
            "ai"
        );

    }


    finally {

        sendButton.disabled =
            false;

        chatInput.focus();

    }

}



// ==========================================
// ADD MESSAGE
// ==========================================

function addMessage(
    text,
    type
) {

    const wrapper =
        document.createElement("div");


    wrapper.className =
        `message ${type}-message`;


    if (type === "user") {

        wrapper.innerHTML = `

            <div class="message-content">

                <span class="message-name">
                    You
                </span>

                <div class="message-bubble">

                    ${formatText(text)}

                </div>

            </div>

        `;

    }

    else {

        wrapper.innerHTML = `

            <div class="message-avatar">
                ✦
            </div>

            <div class="message-content">

                <span class="message-name">
                    Kashmir AI
                </span>

                <div class="message-bubble">

                    ${formatText(text)}

                </div>

            </div>

        `;

    }


    chatMessages.appendChild(
        wrapper
    );


    scrollChat();

}



// ==========================================
// FORMAT RESPONSE
// ==========================================

function formatText(text) {

    return text

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        )

        .replace(
            /^### (.*)$/gm,
            "<h4>$1</h4>"
        )

        .replace(
            /^## (.*)$/gm,
            "<h3>$1</h3>"
        )

        .replace(
            /^# (.*)$/gm,
            "<h3>$1</h3>"
        )

        .replace(
            /^\- (.*)$/gm,
            "• $1"
        )

        .replace(
            /\n/g,
            "<br>"
        );

}



// ==========================================
// LOADING
// ==========================================

function addLoadingMessage() {

    const wrapper =
        document.createElement("div");


    wrapper.className =
        "message ai-message";


    wrapper.innerHTML = `

        <div class="message-avatar">
            ✦
        </div>

        <div class="message-content">

            <span class="message-name">
                Kashmir AI
            </span>

            <div class="message-bubble typing">

                <span></span>
                <span></span>
                <span></span>

            </div>

        </div>

    `;


    chatMessages.appendChild(
        wrapper
    );


    scrollChat();


    return wrapper;

}



// ==========================================
// SCROLL
// ==========================================

function scrollChat() {

    chatMessages.scrollTo({
        top:
            chatMessages.scrollHeight,

        behavior:
            "smooth"
    });

}



// ==========================================
// SEND BUTTON
// ==========================================

sendButton.addEventListener(
    "click",
    () => sendMessage()
);



// ==========================================
// ENTER TO SEND
// ==========================================

chatInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);



// ==========================================
// QUICK PROMPTS
// ==========================================

quickPrompts.forEach(button => {

    button.addEventListener(
        "click",
        () => {

            const prompt =
                button.dataset.prompt;

            sendMessage(prompt);

        }
    );

});