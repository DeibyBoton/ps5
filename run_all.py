#!/usr/bin/env python3
"""
Master Runner for PS5 Self-Host & DNS Server.
Starts both the DNS server (port 53) and HTTP server (port 80) simultaneously.
Requires root privileges (sudo).
"""

import sys
import os
import threading
import subprocess

if os.geteuid() != 0:
    print("[!] Este script requiere permisos de administrador para abrir los puertos 80 y 53.")
    print("[!] Por favor ejecuta: sudo python3 run_all.py")
    sys.exit(1)

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("=" * 60)
print("     INICIANDO SERVICIOS COMPLETOS PS5 SELF-HOST")
print("=" * 60)

def run_dns():
    from dns_server import run_dns_server
    run_dns_server()

def run_http():
    from server import start_server
    start_server(80)

t_dns = threading.Thread(target=run_dns, daemon=True)
t_dns.start()

try:
    run_http()
except KeyboardInterrupt:
    print("\n[*] Deteniendo todos los servicios...")
    sys.exit(0)
