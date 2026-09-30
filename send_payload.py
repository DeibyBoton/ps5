#!/usr/bin/env python3
"""
PS5 Remote Payload Sender (Netcat / Socket injector).
Sends compiled .bin / .elf payloads directly over TCP to PS5 listening port (9020 / 9021).
"""

import socket
import sys
import os
import argparse

DEFAULT_PS5_PORT = 9020

def send_payload(ps5_ip, payload_path, port=DEFAULT_PS5_PORT):
    if not os.path.exists(payload_path):
        print(f"[!] Error: Payload file not found: {payload_path}")
        return False

    file_size = os.path.getsize(payload_path)
    print(f"[*] Reading: {payload_path} ({file_size / 1024:.2f} KB)")

    with open(payload_path, "rb") as f:
        payload_data = f.read()

    print(f"[*] Connecting to PS5 at {ps5_ip}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10.0)

    try:
        s.connect((ps5_ip, port))
        print("[*] Connected. Injecting payload...")
        s.sendall(payload_data)
        print("[+] Payload successfully sent to PS5!")
        return True
    except socket.timeout:
        print("[!] Connection timed out. Ensure PS5 payload receiver / ELF loader is running.")
    except ConnectionRefusedError:
        print(f"[!] Connection refused on port {port}. Verify PS5 IP address and receiver state.")
    except Exception as e:
        print(f"[!] Transmission failed: {e}")
    finally:
        s.close()

    return False

def main():
    parser = argparse.ArgumentParser(description="PS5 Remote Payload Loader / TCP Sender")
    parser.add_argument("ip", help="PS5 IP Address (e.g. 192.168.1.150)")
    parser.add_argument("payload", help="Path to .bin / .elf payload file")
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PS5_PORT, help=f"Target port (default: {DEFAULT_PS5_PORT})")

    args = parser.parse_args()
    send_payload(args.ip, args.payload, args.port)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python3 send_payload.py <PS5_IP> <PAYLOAD.bin> [-p PORT]")
        sys.exit(1)
    main()
