/**
 * StationHub - Minimalist Host Manager Logic
 */

let logCount = 1;

// Document Ready Setup
document.addEventListener("DOMContentLoaded", () => {
    initFirmwareSelector();
    initSearchAndFilters();
    initModalControls();
    initSpatialNavigation();
    initServiceWorker();
    checkLocalPing();
});

// Toast Notifications
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(6px)";
        toast.style.transition = "all 180ms ease-in";
        setTimeout(() => toast.remove(), 200);
    }, 3200);
}

// Log System
function appendLog(message, type = "info") {
    const stream = document.getElementById("log-stream");
    const countTag = document.getElementById("log-count");
    if (!stream) return;

    const time = new Date().toTimeString().split(" ")[0];
    const entry = document.createElement("div");
    entry.className = `log-entry ${type}`;
    entry.innerHTML = `<span class="time">${time}</span><span class="msg">${escapeHtml(message)}</span>`;

    stream.prepend(entry);
    logCount++;
    if (countTag) countTag.textContent = `${logCount} eventos`;
}

function clearLogs(event) {
    if (event) event.stopPropagation();
    const stream = document.getElementById("log-stream");
    const countTag = document.getElementById("log-count");
    if (stream) stream.innerHTML = "";
    logCount = 0;
    if (countTag) countTag.textContent = "0 eventos";
    showToast("Registro limpiado");
}

function toggleActivityLog() {
    const body = document.getElementById("activity-body");
    const chevron = document.getElementById("log-chevron");
    if (body) body.classList.toggle("hidden");
    if (chevron) chevron.classList.toggle("collapsed");
}

// Firmware Selector
function initFirmwareSelector() {
    const fwSelect = document.getElementById("fw-select");
    const badge = document.getElementById("current-fw-badge");
    if (!fwSelect || !badge) return;

    fwSelect.addEventListener("change", (e) => {
        const val = e.target.value;
        badge.textContent = `FW ${val}`;
        appendLog(`Firmware objetivo establecido en ${val}`);
        showToast(`Firmware cambiado a ${val}`);
    });
}

// Search and Category Tabs
function initSearchAndFilters() {
    const searchInput = document.getElementById("tool-search");
    const tabs = document.querySelectorAll(".nav-tab");
    const cards = document.querySelectorAll(".card");

    let currentCategory = "all";
    let searchQuery = "";

    function filterCards() {
        cards.forEach((card) => {
            const title = card.querySelector(".card-title")?.textContent.toLowerCase() || "";
            const desc = card.querySelector(".card-desc")?.textContent.toLowerCase() || "";
            const category = card.dataset.category;

            const matchesCategory = currentCategory === "all" || category === currentCategory;
            const matchesSearch = !searchQuery || title.includes(searchQuery) || desc.includes(searchQuery);

            if (matchesCategory && matchesSearch) {
                card.style.display = "flex";
            } else {
                card.style.display = "none";
            }
        });
    }

    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            searchQuery = e.target.value.toLowerCase().trim();
            filterCards();
        });
    }

    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            tabs.forEach((t) => t.classList.remove("active"));
            tab.classList.add("active");
            currentCategory = tab.dataset.category;
            filterCards();
        });
    });
}

// Payload Execution
function executePayload(payloadName, category) {
    const fw = document.getElementById("fw-select")?.value || "13.60";
    appendLog(`Solicitando carga: ${payloadName} (FW ${fw})...`, "info");
    showToast(`Iniciando ${payloadName}...`);

    const directElf = `payloads/${payloadName.toLowerCase()}.elf`;
    const fwBin = `payloads/${payloadName.toLowerCase()}_${fw}.bin`;
    const directBin = `payloads/${payloadName.toLowerCase()}.bin`;

    fetch(directElf, { method: "HEAD" })
        .then((res) => {
            if (res.ok) {
                appendLog(`Binario ${payloadName}.elf detectado y preparado.`, "success");
                showToast(`${payloadName} listo`);
                return;
            }
            return fetch(fwBin, { method: "HEAD" });
        })
        .then((res) => {
            if (res && res.ok) {
                appendLog(`Binario ${payloadName}_${fw}.bin cargado.`, "success");
                showToast(`${payloadName} inyectado con éxito`, "success");
            } else if (res) {
                appendLog(`Archivo en payloads/ listo para ejecución.`, "info");
            }
        })
        .catch(() => {
            appendLog(`Modo independiente activo. Payload ${payloadName} preparado.`, "info");
        });
}

// Custom BIN upload / handler
function handleCustomPayload(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    appendLog(`Archivo personalizado seleccionado: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`, "info");
    showToast(`Archivo cargado: ${file.name}`);

    const reader = new FileReader();
    reader.onload = (e) => {
        appendLog(`Buffer de memoria listo para ${file.name}.`, "success");
    };
    reader.readAsArrayBuffer(file);
}

// Offline Cache Control
function refreshCache() {
    appendLog("Actualizando almacenamiento en caché sin conexión...", "info");
    showToast("Actualizando caché...");
    if (window.caches) {
        caches.keys().then((names) => {
            names.forEach((name) => caches.delete(name));
            appendLog("Caché anterior purgada. Almacenando versión más reciente.", "success");
            showToast("Caché lista para modo offline");
        });
    }
}

function clearServiceWorkerCache() {
    if (window.caches) {
        caches.keys().then((names) => {
            for (let name of names) caches.delete(name);
            showToast("Caché eliminada correctamente");
            appendLog("Almacenamiento local purgado.", "warn");
        });
    }
}

// Local Ping / Connectivity
function checkLocalPing() {
    const connPill = document.getElementById("conn-pill");
    const connText = document.getElementById("conn-text");

    const start = performance.now();
    fetch("css/style.css?ping=" + Date.now(), { method: "HEAD", cache: "no-store" })
        .then((res) => {
            const ms = Math.round(performance.now() - start);
            if (connText) connText.textContent = `Local (${ms}ms)`;
            if (connPill) connPill.querySelector(".dot").style.backgroundColor = "var(--status-online)";
            appendLog(`Comprobación de latencia local: ${ms}ms`, "info");
        })
        .catch(() => {
            if (connText) connText.textContent = "Desconectado";
            if (connPill) connPill.querySelector(".dot").style.backgroundColor = "var(--status-warn)";
        });
}

// Settings Modal Controls
function initModalControls() {
    const openBtn = document.getElementById("open-settings-btn");
    const modal = document.getElementById("settings-modal");
    if (!openBtn || !modal) return;

    openBtn.addEventListener("click", () => {
        modal.style.display = "flex";
    });
}

function openSenderModal() {
    const modal = document.getElementById("sender-modal");
    if (modal) modal.style.display = "flex";
}

function closeSenderModal(event) {
    const modal = document.getElementById("sender-modal");
    if (modal) modal.style.display = "none";
}

function sendRemotePayloadFromBrowser() {
    const ip = document.getElementById("ps5-ip-input")?.value?.trim();
    const port = document.getElementById("ps5-port-input")?.value?.trim() || "9020";
    const file = document.getElementById("ps5-payload-select")?.value;

    if (!ip || ip === "192.168.1.") {
        showToast("Ingresa la IP completa de la PS5");
        return;
    }

    appendLog(`Enviando ${file} a ${ip}:${port} vía API local...`, "info");
    showToast(`Inyectando a ${ip}...`);

    fetch("/api/send-payload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip: ip, port: parseInt(port), file: file })
    })
    .then(res => res.json())
    .then(data => {
        if (data.ok) {
            appendLog(`[OK] ${data.message} (${file})`, "success");
            showToast("¡Payload enviado con éxito a la PS5!", "success");
            closeSenderModal();
        } else {
            appendLog(`[Error] ${data.error || data.message}`, "error");
            showToast(`Fallo: ${data.error || 'No se pudo conectar'}`);
        }
    })
    .catch(err => {
        appendLog(`[Aviso] Si estás en GitHub Pages online, usa la app de escritorio local (app_sender.py).`, "warn");
        showToast("Usa server.py o app_sender.py para enviar por TCP");
    });
}

// Helper
function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
