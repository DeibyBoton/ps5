#!/usr/bin/env python3
"""
StationHub Payload Injector - Minimalist Linux GUI Application
Includes IP/Port verification test before sending.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket
import os
import threading
import time

class PS5PayloadSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PS5 Remote Payload Injector")
        self.root.geometry("500x480")
        self.root.minsize(460, 440)
        self.root.configure(bg="#0f1115")

        self.setup_styles()
        self.create_widgets()
        self.populate_payloads()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure(".", background="#0f1115", foreground="#f3f4f6", font=("Inter", 10))
        self.style.configure("TLabel", background="#0f1115", foreground="#9ca3af")
        self.style.configure("Header.TLabel", font=("Inter", 14, "bold"), foreground="#f3f4f6")
        self.style.configure("TEntry", fieldbackground="#161920", foreground="#f3f4f6", bordercolor="#262c38")
        
        self.style.configure("TButton", background="#2563eb", foreground="#ffffff", borderwidth=0, padding=8, font=("Inter", 10, "bold"))
        self.style.map("TButton", background=[("active", "#1d4ed8"), ("disabled", "#374151")])
        
        self.style.configure("Secondary.TButton", background="#1e222b", foreground="#f3f4f6", font=("Inter", 9))
        self.style.map("Secondary.TButton", background=[("active", "#262c38")])
        
        self.style.configure("Verify.TButton", background="#15803d", foreground="#ffffff", font=("Inter", 9, "bold"))
        self.style.map("Verify.TButton", background=[("active", "#166534"), ("disabled", "#374151")])

    def create_widgets(self):
        container = tk.Frame(self.root, bg="#0f1115", padx=24, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Header
        header = ttk.Label(container, text="PS5 Payload Remote Sender", style="Header.TLabel")
        header.pack(anchor="w", pady=(0, 16))

        # Target IP & Port Frame
        net_frame = tk.Frame(container, bg="#0f1115")
        net_frame.pack(fill=tk.X, pady=(0, 8))

        lbl_ip = ttk.Label(net_frame, text="IP PS5:")
        lbl_ip.pack(side=tk.LEFT, padx=(0, 6))
        self.ip_entry = ttk.Entry(net_frame, width=15)
        self.ip_entry.insert(0, "192.168.1.")
        self.ip_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        lbl_port = ttk.Label(net_frame, text="Puerto:")
        lbl_port.pack(side=tk.LEFT, padx=(0, 6))
        self.port_entry = ttk.Entry(net_frame, width=6)
        self.port_entry.insert(0, "9020")
        self.port_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Test Connection Button
        self.verify_btn = ttk.Button(net_frame, text="Probar Conexión", style="Secondary.TButton", command=self.on_verify_click)
        self.verify_btn.pack(side=tk.LEFT)

        # Connection Status Badge
        self.conn_indicator_frame = tk.Frame(container, bg="#161920", padx=12, pady=6, highlightbackground="#262c38", highlightthickness=1)
        self.conn_indicator_frame.pack(fill=tk.X, pady=(0, 12))

        self.conn_dot = tk.Label(self.conn_indicator_frame, text="●", fg="#6b7280", bg="#161920", font=("Inter", 12))
        self.conn_dot.pack(side=tk.LEFT, padx=(0, 8))

        self.conn_status_text = tk.Label(self.conn_indicator_frame, text="Sin verificar (Pulsa 'Probar Conexión')", fg="#9ca3af", bg="#161920", font=("Inter", 9))
        self.conn_status_text.pack(side=tk.LEFT)

        # Payloads List
        lbl_payloads = ttk.Label(container, text="Seleccionar Payload:")
        lbl_payloads.pack(anchor="w", pady=(4, 4))

        self.payload_listbox = tk.Listbox(
            container,
            bg="#161920",
            fg="#f3f4f6",
            selectbackground="#2563eb",
            selectforeground="#ffffff",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor="#3b82f6",
            highlightbackground="#262c38",
            height=5,
            font=("SFMono-Regular", 10)
        )
        self.payload_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        # Browse Custom File
        browse_frame = tk.Frame(container, bg="#0f1115")
        browse_frame.pack(fill=tk.X, pady=(0, 14))
        self.browse_btn = ttk.Button(browse_frame, text="Buscar otro archivo (.bin / .elf)", style="Secondary.TButton", command=self.browse_file)
        self.browse_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Send Action Button
        self.send_btn = ttk.Button(container, text="Verificar y Enviar Payload", command=self.on_send_click)
        self.send_btn.pack(fill=tk.X, pady=(0, 8))

        # Footer info
        self.status_lbl = ttk.Label(container, text="El receptor ELF de la PS5 debe estar esperando en el puerto indicado.", font=("Inter", 8))
        self.status_lbl.pack(anchor="w")

    def validate_ip_port(self):
        ip = self.ip_entry.get().strip()
        port_str = self.port_entry.get().strip()

        if not ip or ip == "192.168.1.":
            messagebox.showwarning("IP Inválida", "Escribe la dirección IP completa de tu PS5.")
            return None, None

        try:
            socket.inet_aton(ip)
            if ip.count(".") != 3:
                raise ValueError
        except Exception:
            messagebox.showerror("IP Inválida", f"'{ip}' no es una dirección IPv4 válida.")
            return None, None

        try:
            port = int(port_str)
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            messagebox.showerror("Puerto Inválido", "El puerto debe ser un número entre 1 y 65535.")
            return None, None

        return ip, port

    def populate_payloads(self):
        self.payload_listbox.delete(0, tk.END)
        payloads_dir = os.path.join(os.path.dirname(__file__), "payloads")
        if os.path.exists(payloads_dir):
            for fname in sorted(os.listdir(payloads_dir)):
                if fname.endswith((".elf", ".bin")):
                    self.payload_listbox.insert(tk.END, fname)
        if self.payload_listbox.size() > 0:
            self.payload_listbox.selection_set(0)

    def browse_file(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar payload ELF o BIN",
            filetypes=[("Payloads", "*.bin *.elf"), ("Todos los archivos", "*.*")]
        )
        if filepath:
            self.payload_listbox.insert(tk.END, filepath)
            self.payload_listbox.selection_clear(0, tk.END)
            self.payload_listbox.selection_set(tk.END)

    def on_verify_click(self):
        ip, port = self.validate_ip_port()
        if not ip:
            return

        self.verify_btn.config(state=tk.DISABLED)
        self.conn_dot.config(fg="#f59e0b")
        self.conn_status_text.config(text=f"Probando conexión con {ip}:{port}...", fg="#f59e0b")

        threading.Thread(target=self.verify_worker, args=(ip, port), daemon=True).start()

    def verify_worker(self, ip, port):
        start_time = time.time()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3.5)
            s.connect((ip, port))
            s.close()
            latency = int((time.time() - start_time) * 1000)

            self.root.after(0, lambda: self.set_conn_status(True, f"Conexión exitosa con PS5 ({latency} ms)"))
        except socket.timeout:
            self.root.after(0, lambda: self.set_conn_status(False, f"Tiempo agotado. La PS5 no responde en {ip}:{port}"))
        except ConnectionRefusedError:
            self.root.after(0, lambda: self.set_conn_status(False, f"Conexión rechazada. ¿Está el receptor activo en el puerto {port}?"))
        except Exception as e:
            self.root.after(0, lambda: self.set_conn_status(False, f"Error de red: {e}"))
        finally:
            self.root.after(0, lambda: self.verify_btn.config(state=tk.NORMAL))

    def set_conn_status(self, success, text):
        if success:
            self.conn_dot.config(fg="#10b981")
            self.conn_status_text.config(text=text, fg="#10b981")
        else:
            self.conn_dot.config(fg="#ef4444")
            self.conn_status_text.config(text=text, fg="#ef4444")

    def on_send_click(self):
        ip, port = self.validate_ip_port()
        if not ip:
            return

        selected = self.payload_listbox.curselection()
        if not selected:
            messagebox.showwarning("Selección vacía", "Selecciona un archivo payload de la lista.")
            return

        chosen_item = self.payload_listbox.get(selected[0])
        if os.path.isabs(chosen_item) or os.path.exists(chosen_item):
            filepath = chosen_item
        else:
            filepath = os.path.join(os.path.dirname(__file__), "payloads", chosen_item)

        if not os.path.exists(filepath):
            messagebox.showerror("Error", f"No se encuentra el archivo:\n{filepath}")
            return

        self.send_btn.config(state=tk.DISABLED)
        self.verify_btn.config(state=tk.DISABLED)
        self.conn_dot.config(fg="#f59e0b")
        self.conn_status_text.config(text=f"1/2 Verificando conexión antes de enviar...", fg="#f59e0b")

        threading.Thread(target=self.send_with_precheck_worker, args=(ip, port, filepath), daemon=True).start()

    def send_with_precheck_worker(self, ip, port, filepath):
        # Step 1: Pre-check handshake
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.settimeout(3.5)
            test_sock.connect((ip, port))
            test_sock.close()
        except Exception as e:
            self.root.after(0, lambda: self.set_conn_status(False, f"Fallo en pre-verificación: {e}"))
            self.root.after(0, lambda: messagebox.showerror(
                "Error de conexión previa",
                f"No se pudo conectar a la PS5 ({ip}:{port}).\n\nVerifica que la IP sea correcta y que la consola tenga el loader activo."
            ))
            self.root.after(0, lambda: self.enable_buttons())
            return

        # Step 2: Send Payload
        self.root.after(0, lambda: self.conn_status_text.config(text=f"2/2 IP verificada. Transfiriendo {os.path.basename(filepath)}...", fg="#3b82f6"))
        
        try:
            with open(filepath, "rb") as f:
                data = f.read()

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(8.0)
            s.connect((ip, port))
            s.sendall(data)
            s.close()

            fname = os.path.basename(filepath)
            self.root.after(0, lambda: self.set_conn_status(True, f"Payload {fname} enviado con éxito ({len(data)} bytes)"))
            self.root.after(0, lambda: messagebox.showinfo("Éxito", f"¡Payload '{fname}' transferido e inyectado correctamente!"))
        except Exception as e:
            self.root.after(0, lambda: self.set_conn_status(False, f"Error durante la transferencia: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Error al enviar", f"Fallo enviando payload: {e}"))
        finally:
            self.root.after(0, lambda: self.enable_buttons())

    def enable_buttons(self):
        self.send_btn.config(state=tk.NORMAL)
        self.verify_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = PS5PayloadSenderApp(root)
    root.mainloop()
