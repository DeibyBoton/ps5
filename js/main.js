function log(message) {
    const logBox = document.getElementById("log-output");
    const timestamp = new Date().toLocaleTimeString();
    logBox.textContent = `[${timestamp}] ${message}\n` + logBox.textContent;
}

function triggerPayload(name) {
    const fw = document.getElementById("fw-select").value;
    log(`Iniciando solicitud para payload: ${name} en FW ${fw}...`);
    
    // Ruta donde se colocan los archivos .bin según el payload
    const payloadPath = `payloads/${name.toLowerCase()}_${fw}.bin`;
    
    log(`Buscando archivo de carga: ${payloadPath}`);

    fetch(payloadPath, { method: "HEAD" })
        .then(response => {
            if (response.ok) {
                log(`[OK] Binario detectado en servidor. Listo para inyección.`);
                // Aquí el exploit cargador local gestiona el buffer de memoria
            } else {
                log(`[Info] Coloca el binario correspondiente en la carpeta: payloads/`);
            }
        })
        .catch(err => {
            log(`[Aviso] Modo local offline / Payload listo para enviar.`);
        });
}

// Registro de Service Worker para soporte offline
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("sw.js").then(
            () => log("Caché sin conexión habilitada."),
            () => log("Ejecutando en modo estándar.")
        );
    });
}
