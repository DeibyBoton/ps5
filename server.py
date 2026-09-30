#!/usr/bin/env python3
"""
PS5 Local Host & Remote Injector Server
Listens on Port 80 (standard HTTP requested by PS5 User's Guide) and 8080.
Routes PlayStation User Guide paths (/document/...) to index.html.
"""

import http.server
import socketserver
import socket
import json
import os
import sys

DEFAULT_PORT = 80

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

def send_tcp_payload(ps5_ip, port, payload_data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(8.0)
    try:
        s.connect((ps5_ip, port))
        s.sendall(payload_data)
        return True, "Payload inyectado correctamente vía TCP"
    except Exception as e:
        return False, str(e)
    finally:
        s.close()

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        # Redirect PS5 User Guide default paths (e.g. /document/es/ps5/index.html) to root index.html
        if self.path.startswith('/document/') or self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/verify-connection':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                ps5_ip = data.get('ip')
                port = int(data.get('port', 9020))
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3.5)
                s.connect((ps5_ip, port))
                s.close()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "message": f"Conexión exitosa con {ps5_ip}:{port}"}).encode())
                return
            except Exception as e:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
                return

        if self.path == '/api/send-payload':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                ps5_ip = data.get('ip')
                port = int(data.get('port', 9020))
                payload_file = data.get('file')

                if not ps5_ip or not payload_file:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": False, "error": "Falta IP o nombre de archivo"}).encode())
                    return

                filepath = os.path.join('payloads', os.path.basename(payload_file))
                if not os.path.exists(filepath):
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"ok": False, "error": f"Archivo no encontrado: {filepath}"}).encode())
                    return

                with open(filepath, 'rb') as f:
                    payload_bytes = f.read()

                ok, msg = send_tcp_payload(ps5_ip, port, payload_bytes)
                
                self.send_response(200 if ok else 500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": ok, "message": msg}).encode())
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
                return

        super().do_POST()

CustomHandler.extensions_map.update({
    '.manifest': 'text/cache-manifest',
    '.bin': 'application/octet-stream',
    '.elf': 'application/octet-stream',
})

def start_server(port=DEFAULT_PORT):
    local_ip = get_local_ip()
    print("=" * 60)
    print("        PS5 Local Host & Remote Injector Server")
    print("=" * 60)
    print(f"[*] Escuchando en Puerto {port} (HTTP Estándar)")
    print(f"[*] Panel web en red local:   http://{local_ip}")
    print(f"[*] Enlace Guía de usuario:   http://manuals.playstation.net")
    print("=" * 60)
    print("Presiona Ctrl+C para detener el servidor.\n")

    try:
        with socketserver.TCPServer(("", port), CustomHandler) as httpd:
            httpd.serve_forever()
    except PermissionError:
        print(f"[!] Error: El puerto {port} requiere permisos de administrador (root).")
        print(f"[!] Ejecuta: sudo python3 server.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[*] Servidor detenido.")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    start_server(port)
