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
    addMessageToChat('LLM', reply);
  });

  function addMessageToChat(sender, message) {
    const messageElem = document.createElement('div');
    messageElem.classList.add('message');
    messageElem.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatContainer.appendChild(messageElem);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
});
