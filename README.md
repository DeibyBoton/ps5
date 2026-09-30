# PS5 Local Self-Host Template

Plantilla lista para inicializar como repositorio Git y servir herramientas de homebrew para PlayStation 5 de forma local y sin depender de servidores externos.

## 📁 Estructura

* `index.html`: Interfaz web para el navegador de la PS5.
* `server.py`: Servidor HTTP ligero en Python para compartir el menú en tu red local.
* `payloads/`: Carpeta donde depositar los archivos binarios compilados (`.bin`) de etaHEN, kstuff, etc.
* `js/` y `css/`: Lógica del menú y estilos visuales.

## 🚀 Uso Rápido

1. **Iniciar el servidor local:**
   ```bash
   python3 server.py
   ```
2. **Conectar la PS5:**
   * Abre la URL que muestra el script (ejemplo: `http://192.168.1.50:8080`) desde el navegador o la Guía del usuario de tu PS5.

## ⚙️ Inicializar como repositorio Git

```bash
git init
git add .
git commit -m "Initial commit: PS5 self-host repository template"
```
