#!/usr/bin/env python3
"""
Lightweight DNS Server for PS5 Local Host.
Redirects User's Guide (manuals.playstation.net) to local IP and blocks telemetry.
"""

import socket
import sys

LOCAL_HOST_IP = "127.0.0.1"
DNS_PORT = 53

BLOCK_DOMAINS = [
    "playstation.net",
    "playstation.com",
    "sonyentertainmentnetwork.com"
]

REDIRECT_DOMAINS = [
    "manuals.playstation.net",
    "userguide.playstation.net"
]

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

def build_dns_response(data, target_ip):
    # Transaction ID
    tid = data[:2]
    # Standard query response, No error
    flags = b"\x81\x80"
    # Questions count = 1, Answers = 1, Auth = 0, Additional = 0
    qdcount = b"\x00\x01"
    ancount = b"\x00\x01"
    nscount = b"\x00\x00"
    arcount = b"\x00\x00"
    
    header = tid + flags + qdcount + ancount + nscount + arcount

    # Extract Question Section
    q_end = 12
    while data[q_end] != 0:
        q_end += 1
    q_end += 5 # 0-byte + QTYPE (2 bytes) + QCLASS (2 bytes)
    question = data[12:q_end]

    # Answer Section (Pointer to question name 0xc00c, Type A 0x0001, Class IN 0x0001, TTL 60s 0x0000003c, Len 4 0x0004)
    answer = b"\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04" + socket.inet_aton(target_ip)
    return header + question + answer

def run_dns_server():
    local_ip = get_local_ip()
    print(f"[*] Starting PS5 DNS Server on port {DNS_PORT}...")
    print(f"[*] Local Host Target IP: {local_ip}")
    print("[*] Redirecting manuals.playstation.net -> Host")
    print("[*] Blocking telemetry/updates")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("", DNS_PORT))
    except PermissionError:
        print("[!] Error: Port 53 requires root permissions. Run with sudo python3 dns_server.py")
        sys.exit(1)

    while True:
        try:
            data, addr = sock.recvfrom(512)
            # Parse domain from DNS question
            domain_parts = []
            idx = 12
            length = data[idx]
            while length != 0 and idx < len(data):
                idx += 1
                domain_parts.append(data[idx:idx+length].decode("latin-1", errors="ignore"))
                idx += length
                if idx < len(data):
                    length = data[idx]

            query_domain = ".".join(domain_parts).lower()

            target_ip = "0.0.0.0" # Default block
            for red in REDIRECT_DOMAINS:
                if red in query_domain:
                    target_ip = local_ip
                    break

            response = build_dns_response(data, target_ip)
            sock.sendto(response, addr)
            print(f"[DNS Query] {query_domain} -> {target_ip}")
        except KeyboardInterrupt:
            print("\n[*] Stopping DNS Server.")
            break
        except Exception as e:
            continue

if __name__ == "__main__":
    run_dns_server()
