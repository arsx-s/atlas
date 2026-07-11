import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("atlas", {
  status: () => ipcRenderer.invoke("atlas:status"),
  launchBackend: () => ipcRenderer.invoke("atlas:launch-backend"),
  restartBackend: () => ipcRenderer.invoke("atlas:restart-backend"),
  openExternal: (url) => ipcRenderer.invoke("atlas:open-external", url),
  selectFile: () => ipcRenderer.invoke("atlas:select-file"),
  selectFiles: () => ipcRenderer.invoke("atlas:select-files"),
  checkUpdates: () => ipcRenderer.invoke("atlas:check-updates"),
  getUserDataPath: () => ipcRenderer.invoke("atlas:get-user-data-path"),
  onBackendStatus: (callback) => {
    ipcRenderer.on("backend-status", (_event, status) => callback(status));
  },
});
