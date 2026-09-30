#!/usr/bin/env python3
import http.server
import socketserver
import socket
import json
import os

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

    def do_POST(self):
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

print("=" * 60)
print("        PS5 Local Host & Remote Injector Server")
print("=" * 60)
print(f"[*] Panel web en tu red local: http://{get_local_ip()}:{PORT}")
print(f"[*] API de envío remoto TCP:   http://{get_local_ip()}:{PORT}/api/send-payload")
print("=" * 60)
print("Presiona Ctrl+C para detener el servidor.\n")

with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido correctamente.")
