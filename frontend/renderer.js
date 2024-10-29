const { ipcRenderer } = require('electron');

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('chat-form');
  const input = document.getElementById('user-input');
  const chatContainer = document.getElementById('chat-container');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const userMessage = input.value;
    addMessageToChat('User', userMessage);
    input.value = '';

    const reply = await ipcRenderer.invoke('query-llm', userMessage);
    const formattedReply = formatReplyArray(reply);
    addMessageToChat('LLM', formattedReply);
  });

  function formatReplyArray(replyArray) {
    if (!Array.isArray(replyArray)) return replyArray; // Handle non-array responses

    // Generate HTML for all records in the array as a single block
    let formattedReply = "<div class='llm-response'>";
    replyArray.forEach((item, index) => {
      formattedReply += `<div class='record'><strong>Record ${index + 1}:</strong><br>`;
      formattedReply += formatMessageObject(item);
      formattedReply += "</div><hr>";  // Divider between records
    });
    formattedReply += "</div>";

    return formattedReply;
  }

  function formatMessageObject(item) {
    // Dynamically format each key-value pair in the object
    let formattedMessage = "<div class='record-data'>";
    for (const [key, value] of Object.entries(item)) {
      formattedMessage += `<p><strong>${key}:</strong> ${value}</p>`;
    }
    formattedMessage += "</div>";
    return formattedMessage;
  }

  function addMessageToChat(sender, message) {
    const messageElem = document.createElement('div');
    messageElem.classList.add('message');
    messageElem.innerHTML = `<strong>${sender}:</strong><br>${message}`;
    chatContainer.appendChild(messageElem);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
});
