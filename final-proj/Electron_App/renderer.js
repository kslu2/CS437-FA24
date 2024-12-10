// This file is required by the index.html file and will
// be executed in the renderer process for that window.
// No Node.js APIs are available in this process because
// `nodeIntegration` is turned off. Use `preload.js` to
// selectively enable features needed in the rendering
// process.
/*
const { ipcRenderer } = require('electron');

//gif stuff, open the gif if its there before
const fs = require('fs');
const path = require('path');
// Path to the last uploaded GIF
const gifPath = path.join(__dirname, 'uploads', 'intruder.gif');

// Check if the file exists and update the `img` element
if (fs.existsSync(gifPath)) {
    const gifElement = document.getElementById('intruderGif');
    gifElement.src = `file://${gifPath}`;

    console.log(`Received GIF path: ${gifPath}`)
    console.log(`Received GIF path: ${gifElement.src}`)
} else {
    console.log('No GIF found at startup.');
}

///

// Listen for new GIF notifications from the main process
ipcRenderer.on('new-gif', (event, gifPath) => {
  console.log(`Received GIF path: ${gifPath}`)
  const gifElement = document.getElementById('intruderGif');
  gifElement.src = `file://${gifPath}`;
});
*/
