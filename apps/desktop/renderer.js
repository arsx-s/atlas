const statusBadge = document.getElementById("backend-status");
const updateBadge = document.getElementById("update-status");
const statusOutput = document.getElementById("status-output");
const sessionOutput = document.getElementById("session-output");

const setPanel = (panelId) => {
  document.querySelectorAll(".panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === panelId);
  });
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.panel === panelId);
  });
};

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => setPanel(button.dataset.panel));
});

async function refreshStatus() {
  try {
    const status = await window.atlas.status();
    statusBadge.textContent = status.backendStatus;
    updateBadge.textContent = status.updateStatus;
    statusOutput.textContent = JSON.stringify(status, null, 2);
  } catch {}
}

document.getElementById("launch-backend").addEventListener("click", async () => {
  statusBadge.textContent = "starting";
  try {
    const result = await window.atlas.launchBackend();
    statusBadge.textContent = result.backendStatus;
  } catch (e) {
    statusBadge.textContent = "error";
  }
  await refreshStatus();
});

document.getElementById("restart-backend")?.addEventListener("click", async () => {
  statusBadge.textContent = "restarting";
  try {
    const result = await window.atlas.restartBackend();
    statusBadge.textContent = result.backendStatus;
  } catch (e) {
    statusBadge.textContent = "error";
  }
  await refreshStatus();
});

document.getElementById("check-updates").addEventListener("click", async () => {
  updateBadge.textContent = "checking";
  try {
    const result = await window.atlas.checkUpdates();
    updateBadge.textContent = result.available ? `available ${result.version ?? ""}`.trim() : result.reason || "up-to-date";
  } catch {
    updateBadge.textContent = "error";
  }
});

document.getElementById("select-file").addEventListener("click", async () => {
  const filePath = await window.atlas.selectFile();
  if (filePath) {
    sessionOutput.textContent = `Selected file: ${filePath}`;
  }
});

document.getElementById("get-user-data")?.addEventListener("click", async () => {
  try {
    const path = await window.atlas.getUserDataPath();
    statusOutput.textContent = `User data path: ${path}`;
  } catch (e) {
    statusOutput.textContent = `Error: ${e.message}`;
  }
});

if (window.atlas.onBackendStatus) {
  window.atlas.onBackendStatus((status) => {
    statusBadge.textContent = status;
  });
}

refreshStatus();
setInterval(refreshStatus, 5000);
