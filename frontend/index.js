const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const axios = require('axios');

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'renderer.js'),
    },
  });

  win.loadFile('index.html');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('query-llm', async (event, userMessage) => {
  try {
    const response = await axios.post('http://localhost:5000/api/llm-query', { message: userMessage });
    return response.data.reply;
  } catch (error) {
    console.error('Error querying LLM:', error);
    return { error: 'There was an error connecting to the LLM backend.' };
  }
});
