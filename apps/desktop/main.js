import { app, BrowserWindow, dialog, ipcMain, Menu, Tray, shell, nativeImage } from "electron";
import electronUpdater from "electron-updater";
const { autoUpdater } = electronUpdater;
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const BACKEND_MODULE = "atlas_backend.main:app";
const DEFAULT_BACKEND_URL = process.env.ATLAS_BACKEND_URL || "http://127.0.0.1:8000";

let mainWindow;
let tray;
let backendProcess;
let backendStatus = "starting";
let backendUrl = DEFAULT_BACKEND_URL;
let updateStatus = "idle";
let isQuitting = false;

function resolvePythonCommand() {
  if (process.env.ATLAS_PYTHON_PATH) return process.env.ATLAS_PYTHON_PATH;
  if (process.platform === "win32") {
    const bundled = path.join(process.resourcesPath || "", "backend", "python", "python.exe");
    if (existsSync(bundled)) return bundled;
    const localAppData = path.join(process.env.LOCALAPPDATA || "", "Programs", "Python", "Python312", "python.exe");
    if (existsSync(localAppData)) return localAppData;
    return "python";
  }
  return "python3";
}

function getBackendPath() {
  if (app.isPackaged) {
    const bundled = path.join(process.resourcesPath || "", "backend");
    if (existsSync(bundled)) return bundled;
  }
  return path.resolve(__dirname, "..", "..", "backend");
}

function getUserDataPath() {
  const atlasDir = path.join(app.getPath("documents"), "Atlas");
  const dirs = ["Projects", "Documents", "Exports", "Cache", "Logs", "Settings", "Models", "Temp"];
  for (const dir of dirs) {
    const p = path.join(atlasDir, dir);
    if (!existsSync(p)) mkdirSync(p, { recursive: true });
  }
  const settingsPath = path.join(atlasDir, "Settings", "atlas-local.db");
  return { atlasDir, settingsPath };
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1480, height: 980,
    minWidth: 1024, minHeight: 700,
    title: "Atlas",
    backgroundColor: "#0b1020",
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  mainWindow.loadFile(path.join(__dirname, "index.html"));
  mainWindow.once("ready-to-show", () => mainWindow?.show());
  mainWindow.on("close", (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow?.hide();
    }
  });
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });
}

function createTray() {
  const iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#1a1d27"/><text x="32" y="44" font-family="Arial" font-size="36" font-weight="bold" fill="#86a0ff" text-anchor="middle">A</text></svg>`;
  const iconPath = path.join(__dirname, "build", "tray-icon.png");
  if (!existsSync(path.dirname(iconPath))) mkdirSync(path.dirname(iconPath), { recursive: true });
  if (!existsSync(iconPath)) writeFileSync(iconPath, iconSvg);

  tray = new Tray(nativeImage.createFromPath(iconPath));
  tray.setToolTip("Atlas - AI Research Workspace");
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: "Show Atlas", click: () => { mainWindow?.show(); mainWindow?.focus(); } },
    { type: "separator" },
    { label: "Launch Backend", click: () => startBackend() },
    { type: "separator" },
    { label: "Quit", click: () => { isQuitting = true; app.quit(); } },
  ]));
  tray.on("click", () => { mainWindow?.show(); mainWindow?.focus(); });
}

function startBackend() {
  if (backendProcess && !backendProcess.killed) return;

  const command = resolvePythonCommand();
  const backendPath = getBackendPath();
  const dbPath = getUserDataPath().settingsPath;
  const args = ["-m", "uvicorn", BACKEND_MODULE, "--host", "127.0.0.1", "--port", "8000"];

  backendStatus = "starting";
  backendProcess = spawn(command, args, {
    cwd: backendPath,
    env: {
      ...process.env,
      PYTHONPATH: path.join(backendPath, "src"),
      ATLAS_SQLITE_PATH: dbPath,
      ATLAS_DOCUMENTS_PATH: path.join(getUserDataPath().atlasDir, "Documents"),
      ATLAS_LOCAL_MODE_ENABLED: "true",
    },
    windowsHide: true,
    stdio: "pipe",
  });

  backendProcess.stdout?.on("data", (chunk) => {
    const text = String(chunk);
    if (text.includes("Uvicorn running on")) backendStatus = "ready";
    if (mainWindow && !mainWindow.isDestroyed()) mainWindow.webContents.send("backend-status", backendStatus);
  });

  backendProcess.stderr?.on("data", (chunk) => {
    const text = String(chunk).toLowerCase();
    if (text.includes("error") || text.includes("traceback")) {
      backendStatus = "error";
      if (mainWindow && !mainWindow.isDestroyed()) mainWindow.webContents.send("backend-status", "error");
    }
  });

  backendProcess.on("exit", (code) => {
    backendStatus = "stopped";
    backendProcess = undefined;
    if (mainWindow && !mainWindow.isDestroyed()) mainWindow.webContents.send("backend-status", "stopped");
    if (!isQuitting && code !== 0) {
      setTimeout(() => startBackend(), 3000);
    }
  });
}

async function waitForBackend(timeoutMs = 60000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    try {
      const response = await fetch(`${backendUrl}/api/v1/health`);
      if (response.ok) { backendStatus = "ready"; return true; }
    } catch {}
    await new Promise((r) => setTimeout(r, 500));
  }
  return false;
}

function registerIpc() {
  ipcMain.handle("atlas:status", async () => ({
    backendUrl, backendStatus, updateStatus,
    platform: process.platform,
    versions: process.versions,
    userDataPath: getUserDataPath().atlasDir,
  }));

  ipcMain.handle("atlas:launch-backend", async () => {
    startBackend();
    const ready = await waitForBackend();
    return { ready, backendUrl, backendStatus };
  });

  ipcMain.handle("atlas:restart-backend", async () => {
    if (backendProcess && !backendProcess.killed) { backendProcess.kill(); }
    startBackend();
    const ready = await waitForBackend();
    return { ready, backendUrl, backendStatus };
  });

  ipcMain.handle("atlas:open-external", async (_event, url) => {
    await shell.openExternal(url);
    return true;
  });

  ipcMain.handle("atlas:select-file", async () => {
    const result = await dialog.showOpenDialog({
      properties: ["openFile"],
      filters: [
        { name: "Documents", extensions: ["pdf", "docx", "md", "txt"] },
        { name: "All Files", extensions: ["*"] },
      ],
    });
    return result.canceled ? null : result.filePaths[0];
  });

  ipcMain.handle("atlas:select-files", async () => {
    const result = await dialog.showOpenDialog({
      properties: ["openFile", "multiSelections"],
      filters: [
        { name: "Documents", extensions: ["pdf", "docx", "md", "txt"] },
        { name: "All Files", extensions: ["*"] },
      ],
    });
    return result.canceled ? [] : result.filePaths;
  });

  ipcMain.handle("atlas:get-user-data-path", () => getUserDataPath().atlasDir);

  ipcMain.handle("atlas:check-updates", async () => {
    if (!app.isPackaged) return { available: false, reason: "development-build" };
    updateStatus = "checking";
    try {
      const result = await autoUpdater.checkForUpdates();
      updateStatus = result?.updateInfo ? "available" : "up-to-date";
      return { available: Boolean(result?.updateInfo), version: result?.updateInfo.version };
    } catch (error) {
      updateStatus = "error";
      return { available: false, error: error instanceof Error ? error.message : "Update check failed" };
    }
  });
}

function registerDeepLinking() {
  if (process.defaultApp) {
    if (process.platform === "win32")
      app.setAsDefaultProtocolClient("atlas", process.execPath, [path.resolve(process.argv[1])]);
    else app.setAsDefaultProtocolClient("atlas");
  } else {
    app.setAsDefaultProtocolClient("atlas");
  }
}

function handleOpenUrl(url) {
  try {
    const parsed = new URL(url);
    const targetBackend = parsed.searchParams.get("backend");
    if (targetBackend) backendUrl = targetBackend;
  } catch {}
}

const hasSingleInstanceLock = app.requestSingleInstanceLock();
if (!hasSingleInstanceLock) app.quit();

app.on("second-instance", (_event, argv) => {
  const deepLink = argv.find((a) => a.startsWith("atlas://"));
  if (deepLink) handleOpenUrl(deepLink);
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.show();
    mainWindow.focus();
  }
});

app.whenReady().then(async () => {
  getUserDataPath();
  registerDeepLinking();
  registerIpc();
  createTray();
  startBackend();
  const ready = await waitForBackend();
  createWindow();
  if (!ready) backendStatus = "error";

  autoUpdater.autoDownload = false;
  autoUpdater.on("checking-for-update", () => { updateStatus = "checking"; });
  autoUpdater.on("update-available", () => { updateStatus = "available"; });
  autoUpdater.on("update-not-available", () => { updateStatus = "up-to-date"; });
  autoUpdater.on("error", () => { updateStatus = "error"; });
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") { isQuitting = true; app.quit(); }
});

app.on("before-quit", () => {
  isQuitting = true;
  if (backendProcess && !backendProcess.killed) {
    try { backendProcess.kill("SIGTERM"); } catch {}
  }
});

app.on("open-url", (_event, url) => { handleOpenUrl(url); });
