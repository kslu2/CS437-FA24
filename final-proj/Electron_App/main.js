// Modules to control application life and create native browser window
const { app, BrowserWindow } = require("electron");
const path = require("path");
const express = require("express");
const multer = require("multer");
const fs = require("fs");

// Create Express app
const serverApp = express();
const upload = multer({ dest: path.join(__dirname, "uploads") });

// Function to create the main Electron window
function createWindow() {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 1000,
    height: 1000,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false, // Allows `require` in renderer
      preload: path.join(__dirname, "preload.js"),
    },
  });

  // Load the index.html of the app.
  mainWindow.loadFile("index.html");

  // Uncomment to open DevTools automatically:
  // mainWindow.webContents.openDevTools();

  // Setup the Express server for handling GIF uploads
  serverApp.post("/upload", upload.single("file"), (req, res) => {
    console.log(`Received file: ${req.file.originalname}`);

    // Move the uploaded file to a permanent location
    const gifPath = path.join(__dirname, "uploads", "intruder.gif");
    fs.renameSync(req.file.path, gifPath);

    // Notify the renderer process about the new GIF
    console.log(`Sending GIF path to renderer: ${gifPath}`);
    mainWindow.webContents.send("new-gif", gifPath);

    res.send("File uploaded successfully");
  });

  // Start the Express server
  serverApp.listen(3000, () => {
    console.log("Server running on port 3000...");
  });
}

// This method will be called when Electron has finished initialization
app.whenReady().then(() => {
  createWindow();

  app.on("activate", function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// Quit when all windows are closed
app.on("window-all-closed", function () {
  app.quit();
});