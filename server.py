#!/usr/bin/env python3
import http.server
import socketserver
import socket

PORT = 8080

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map.update({
    '.manifest': 'text/cache-manifest',
    '.bin': 'application/octet-stream',
})

print("=" * 55)
print("     PS5 Local Self-Host Server")
print("=" * 55)
print(f"Servidor iniciado localmente.")
print(f"Dirección en tu red local: http://{get_local_ip()}:{PORT}")
print(f"Accede a esta URL desde el navegador de tu PS5.")
print("=" * 55)
print("Presiona Ctrl+C para detener el servidor.\n")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido correctamente.")
