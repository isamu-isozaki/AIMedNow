const chatInput = document.querySelector("#chat-input");
const sendButton = document.querySelector("#send-btn");
const chatContainer = document.querySelector(".chat-container");
const themeButton = document.querySelector("#theme-btn");
const deleteButton = document.querySelector("#delete-btn");

const attachButton = document.querySelector("#attach-btn");
const attachmentInput = document.querySelector("#attachment-input");

let userText = null;

// Function to create file attachment display
const createFileAttachment = (file) => {
  const filename = file.name;
  let filePreview = '';
  
  // Create a compact preview for images
  if (file.type.startsWith('image/')) {
    filePreview = `
      <div class="file-attachment compact-image">
        <div class="image-thumbnail">
          <img src="${URL.createObjectURL(file)}" alt="Image preview">
        </div>
        <div class="file-info">
          <span class="material-symbols-rounded">image</span>
          <span class="filename">${filename}</span>
        </div>
      </div>
    `;
  } else {
    // For non-image files, show appropriate icon
    let icon = 'description';
    if (file.type.includes('pdf')) {
      icon = 'picture_as_pdf';
    } else if (file.type.includes('word') || file.type.includes('document')) {
      icon = 'article';
    } else if (file.type.includes('excel') || file.type.includes('sheet')) {
      icon = 'table_chart';
    }
    
    filePreview = `
      <div class="file-attachment">
        <span class="material-symbols-rounded">${icon}</span>
        <span class="filename">${filename}</span>
      </div>
    `;
  }
  
  return filePreview;
};

const loadDataFromLocalstorage = () => {
    // Load saved chats and theme from local storage and apply/add on the page
    const themeColor = localStorage.getItem("themeColor");
    document.body.classList.toggle("light-mode", themeColor === "light_mode");
    themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";
    const defaultText = `<div class="default-text">
                            <h1>ChatGPT Clone</h1>
                            <p>Start a conversation and explore the power of AI.<br> Your chat history will be displayed here.</p>
                        </div>`
    chatContainer.innerHTML = localStorage.getItem("all-chats") || defaultText;
    chatContainer.scrollTo(0, chatContainer.scrollHeight); // Scroll to bottom of the chat container
}

const createChatElement = (content, className) => {
    // Create new div and apply chat, specified class and set html content of div
    const chatDiv = document.createElement("div");
    chatDiv.classList.add("chat", className);
    chatDiv.innerHTML = content;
    return chatDiv; // Return the created chat div
}

const getChatResponse = async (incomingChatDiv) => {
    const API_URL = "http://localhost:5000/api/qna";
    const pElement = document.createElement("p");
    // Define the properties and data for the API request
    const ehrResponses = JSON.parse(localStorage.getItem("EHRAnswers")) || [];
    let prompt = ""
    if(ehrResponses.length > 0) {
        prompt = "If needed reference the following EHRs to answer the user's question. Ignore if not relevant "
        let ehrNum = 0;
        for(let i = 0; i< ehrResponses.length;i++) {
            if (ehrResponses[i].length == 0){
                continue;
            } 
            prompt += "EHR "+ehrNum+ "\n\n"+ehrResponses[i] + "\n\n"
            ehrNum++;
        }
    }
    prompt += userText;
    console.log("Prompt is "+prompt)
    const requestOptions = {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: prompt })  // Convert the text to JSON
    }
    // Send POST request to API, get response and set the reponse as paragraph element text
    try {
        const response = await (await fetch(API_URL, requestOptions)).json();
        pElement.textContent = response.answer.trim();
    } catch (error) { // Add error class to the paragraph element and set error text
        pElement.classList.add("error");
        pElement.textContent = "Oops! Something went wrong while retrieving the response. Please try again.";
    }
    // Remove the typing animation, append the paragraph element and save the chats to local storage
    incomingChatDiv.querySelector(".typing-animation").remove();
    incomingChatDiv.querySelector(".chat-details").appendChild(pElement);
    localStorage.setItem("all-chats", chatContainer.innerHTML);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
}

const copyResponse = (copyBtn) => {
    // Copy the text content of the response to the clipboard
    const reponseTextElement = copyBtn.parentElement.querySelector("p");
    navigator.clipboard.writeText(reponseTextElement.textContent);
    copyBtn.textContent = "done";
    setTimeout(() => copyBtn.textContent = "content_copy", 1000);
}

const showTypingAnimation = () => {
    // Display the typing animation and call the getChatResponse function
    const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="static/images/chatbot.png" alt="chatbot-img">
                        <div class="typing-animation">
                            <div class="typing-dot" style="--delay: 0.2s"></div>
                            <div class="typing-dot" style="--delay: 0.3s"></div>
                            <div class="typing-dot" style="--delay: 0.4s"></div>
                        </div>
                    </div>
                    <span onclick="copyResponse(this)" class="material-symbols-rounded">content_copy</span>
                </div>`;
    // Create an incoming chat div with typing animation and append it to chat container
    const incomingChatDiv = createChatElement(html, "incoming");
    chatContainer.appendChild(incomingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
    getChatResponse(incomingChatDiv);
}

const handleOutgoingChat = () => {
    userText = chatInput.value.trim(); // Get chatInput value and remove extra spaces
    if(!userText) return; // If chatInput is empty return from here
    // Clear the input field and reset its height
    chatInput.value = "";
    chatInput.style.height = `${initialInputHeight}px`;
    const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="static/images/user.jpg" alt="user-img">
                        <p>${userText}</p>
                    </div>
                </div>`;
    // Create an outgoing chat div with user's message and append it to chat container
    const outgoingChatDiv = createChatElement(html, "outgoing");
    chatContainer.querySelector(".default-text")?.remove();
    chatContainer.appendChild(outgoingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
    setTimeout(showTypingAnimation, 500);
}

deleteButton.addEventListener("click", () => {
    // Remove the chats from local storage and call loadDataFromLocalstorage function
    if(confirm("Are you sure you want to delete all the chats?")) {
        localStorage.removeItem("all-chats");
        loadDataFromLocalstorage();
    }
});

themeButton.addEventListener("click", () => {
    // Toggle body's class for the theme mode and save the updated theme to the local storage 
    document.body.classList.toggle("light-mode");
    localStorage.setItem("themeColor", themeButton.innerText);
    themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";
});

const initialInputHeight = chatInput.scrollHeight;
chatInput.addEventListener("input", () => {   
    // Adjust the height of the input field dynamically based on its content
    chatInput.style.height =  `${initialInputHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    // If the Enter key is pressed without Shift and the window width is larger 
    // than 800 pixels, handle the outgoing chat
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleOutgoingChat();
    }
});

// loadDataFromLocalstorage();
sendButton.addEventListener("click", handleOutgoingChat);

// Add click event for attachment button
attachButton.addEventListener("click", () => {
    attachmentInput.click();
});

attachmentInput.addEventListener("change", function() {
    if (this.files && this.files[0]) {
        const file = this.files[0];
        
        // Create file attachment display
        const fileAttachment = createFileAttachment(file);
        
        // Create outgoing message with file attachment
        const html = `<div class="chat-content">
                        <div class="chat-details">
                            <img src="static/images/user.jpg" alt="user-img">
                            <p>Uploaded: ${file.name}</p>
                            ${fileAttachment}
                        </div>
                    </div>`;
        
        // Create an outgoing chat div and append it to chat container
        const outgoingChatDiv = createChatElement(html, "outgoing");
        chatContainer.querySelector(".default-text")?.remove();
        chatContainer.appendChild(outgoingChatDiv);
        chatContainer.scrollTo(0, chatContainer.scrollHeight);
        
        // Process the file as an EHR if it's an image
        if (file.type.startsWith('image/')) {
            let data = new FormData();
            data.append('file', file);
            
            // Create a custom typing animation for image uploads
            const animationHtml = `<div class="chat-content">
                                    <div class="chat-details">
                                        <img src="static/images/chatbot.png" alt="chatbot-img">
                                        <div class="typing-animation">
                                            <div class="typing-dot" style="--delay: 0.2s"></div>
                                            <div class="typing-dot" style="--delay: 0.3s"></div>
                                            <div class="typing-dot" style="--delay: 0.4s"></div>
                                        </div>
                                    </div>
                                    <span onclick="copyResponse(this)" class="material-symbols-rounded">content_copy</span>
                                </div>`;
            
            // Create a dedicated incoming chat div for image response
            const imageResponseDiv = createChatElement(animationHtml, "incoming");
            chatContainer.appendChild(imageResponseDiv);
            chatContainer.scrollTo(0, chatContainer.scrollHeight);
            
            const url = "http://localhost:5000/api/upload_ehr";
            
            fetch(url, {
                method: "POST",
                body: data
            }).then(response => response.json())
            .then(data => {
                const answer = data.answer;
                console.log("Image Description: " + answer);
                
                // Retrieve existing answers from localStorage
                let ehrAnswers = JSON.parse(localStorage.getItem("EHRAnswers")) || [];
                
                // Add the new answer
                if(answer != "") {
                    ehrAnswers.push(answer);
                }
                
                // Store the updated array back in localStorage
                localStorage.setItem("EHRAnswers", JSON.stringify(ehrAnswers));
                
                // Remove the loading indicator (if it exists)
                const typingAnimation = imageResponseDiv.querySelector(".typing-animation");
                if (typingAnimation) {
                    typingAnimation.remove();
                    
                    // Create a new p element with the answer text
                    const pElement = document.createElement("p");
                    pElement.textContent = answer.trim() + "\n\nPlease provide your questions about this image, and I'll do my best to assist you!";
                    
                    // Add the p element to the chat details
                    imageResponseDiv.querySelector(".chat-details").appendChild(pElement);
                    localStorage.setItem("all-chats", chatContainer.innerHTML);
                    chatContainer.scrollTo(0, chatContainer.scrollHeight);
                }
            })
            .catch(error => {
                console.error("Error processing file:", error);
                // Handle error - remove typing animation and show error
                const typingAnimation = imageResponseDiv.querySelector(".typing-animation");
                if (typingAnimation) {
                    const pElement = document.createElement("p");
                    pElement.classList.add("error");
                    pElement.textContent = "Error processing the file. Please try again.";
                    typingAnimation.remove();
                    imageResponseDiv.querySelector(".chat-details").appendChild(pElement);
                }
            });
        }
    }
});