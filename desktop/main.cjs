const { app, BrowserWindow, session } = require('electron');
const { URL } = require('node:url');
function createWindow() {
  const win = new BrowserWindow({ width: 1100, height: 850, webPreferences: { nodeIntegration: false, contextIsolation: true, sandbox: true } });
  win.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  win.webContents.on('will-navigate', (event, url) => { if (new URL(url).origin !== 'http://127.0.0.1:5173') event.preventDefault(); });
  win.loadURL('http://127.0.0.1:5173');
}
app.whenReady().then(() => {
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    callback(permission === 'media' && webContents.getURL().startsWith('http://127.0.0.1:5173/'));
  });
  createWindow();
});
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
