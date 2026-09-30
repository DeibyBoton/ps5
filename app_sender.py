#!/usr/bin/env python3
"""
StationHub Payload Injector - Minimalist Linux GUI Application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket
import os
import threading

class PS5PayloadSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PS5 Remote Payload Injector")
        self.root.geometry("480x420")
        self.root.minsize(440, 380)
        self.root.configure(bg="#0f1115")

        self.setup_styles()
        self.create_widgets()
        self.populate_payloads()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure(".", background="#0f1115", foreground="#f3f4f6", font=("Inter", 10))
        self.style.configure("TLabel", background="#0f1115", foreground="#9ca3af")
        self.style.configure("Header.TLabel", font=("Inter", 13, "bold"), foreground="#f3f4f6")
        self.style.configure("TEntry", fieldbackground="#161920", foreground="#f3f4f6", bordercolor="#262c38")
        self.style.configure("TButton", background="#2563eb", foreground="#ffffff", borderwidth=0, padding=8, font=("Inter", 10, "bold"))
        self.style.map("TButton", background=[("active", "#1d4ed8"), ("disabled", "#374151")])
        self.style.configure("Secondary.TButton", background="#1e222b", foreground="#f3f4f6")
        self.style.map("Secondary.TButton", background=[("active", "#262c38")])

    def create_widgets(self):
        container = tk.Frame(self.root, bg="#0f1115", padx=24, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Header
        header = ttk.Label(container, text="PS5 Payload Remote Sender", style="Header.TLabel")
        header.pack(anchor="w", pady=(0, 16))

        # Target IP & Port
        net_frame = tk.Frame(container, bg="#0f1115")
        net_frame.pack(fill=tk.X, pady=(0, 12))

        lbl_ip = ttk.Label(net_frame, text="IP de la PS5:")
        lbl_ip.pack(side=tk.LEFT, padx=(0, 8))
        self.ip_entry = ttk.Entry(net_frame, width=18)
        self.ip_entry.insert(0, "192.168.1.")
        self.ip_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))

        lbl_port = ttk.Label(net_frame, text="Puerto:")
        lbl_port.pack(side=tk.LEFT, padx=(0, 8))
        self.port_entry = ttk.Entry(net_frame, width=7)
        self.port_entry.insert(0, "9020")
        self.port_entry.pack(side=tk.LEFT)

        # Payloads list
        lbl_payloads = ttk.Label(container, text="Seleccionar Payload:")
        lbl_payloads.pack(anchor="w", pady=(8, 4))

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
            height=6,
            font=("SFMono-Regular", 10)
        )
        self.payload_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        # Custom file browse button
        browse_frame = tk.Frame(container, bg="#0f1115")
        browse_frame.pack(fill=tk.X, pady=(0, 16))
        self.browse_btn = ttk.Button(browse_frame, text="Buscar otro archivo (.bin / .elf)", style="Secondary.TButton", command=self.browse_file)
        self.browse_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Send Action Button
        self.send_btn = ttk.Button(container, text="Enviar Payload a PS5", command=self.on_send_click)
        self.send_btn.pack(fill=tk.X, pady=(0, 8))

        # Status text
        self.status_lbl = ttk.Label(container, text="Listo para conectar", font=("Inter", 9))
        self.status_lbl.pack(anchor="w")

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

    def on_send_click(self):
        ip = self.ip_entry.get().strip()
        port_str = self.port_entry.get().strip()
        selected = self.payload_listbox.curselection()

        if not ip or not port_str:
            messagebox.showwarning("Faltan datos", "Indica la dirección IP y el puerto de la PS5.")
            return

        if not selected:
            messagebox.showwarning("Selección vacía", "Selecciona un archivo payload de la lista.")
            return

        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Error", "El puerto debe ser numérico.")
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
        self.status_lbl.config(text=f"Enviando {os.path.basename(filepath)}...")

        threading.Thread(target=self.send_worker, args=(ip, port, filepath), daemon=True).start()

    def send_worker(self, ip, port, filepath):
        try:
            with open(filepath, "rb") as f:
                data = f.read()

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(8.0)
            s.connect((ip, port))
            s.sendall(data)
            s.close()

            self.root.after(0, lambda: self.status_lbl.config(text=f"Enviado con éxito a {ip}:{port}"))
            self.root.after(0, lambda: messagebox.showinfo("Éxito", f"Payload {os.path.basename(filepath)} enviado correctamente."))
        except Exception as e:
            self.root.after(0, lambda: self.status_lbl.config(text=f"Error: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Fallo de conexión", f"No se pudo conectar a {ip}:{port}\n\nDetalle: {e}"))
        finally:
            self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    app = PS5PayloadSenderApp(root)
    root.mainloop()
