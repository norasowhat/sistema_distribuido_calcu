import socket
import json
import threading
import sys
import uuid
import tkinter as tk
from tkinter import messagebox

HOST = '127.0.0.1'

PUERTO_NODO = int(sys.argv[1]) if len(sys.argv) > 1 else 9001
ID_GUI = sys.argv[2] if len(sys.argv) > 2 else "GUI_1"

COD_CONTENIDO = {
    '+': "SUM_PET",
    '-': "SUB_PET",
    '*': "MUL_PET",
    '/': "DIV_PET"
}

class CelulaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Calcuadora (Nodo {PUERTO_NODO})")
        self.root.resizable(False, False)
        self.root.configure(bg="#FFEC8E")

        self.mensajes_vistos = set()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((HOST, PUERTO_NODO))
        except Exception:
            messagebox.showerror("Error", f"No se pudo conectar al Nodo {PUERTO_NODO}")

        self.texto_pantalla = tk.StringVar()
        self.pantalla = tk.Entry(root, textvariable=self.texto_pantalla, font=('Arial', 20), bd=10, bg="powder blue", justify='right')
        self.pantalla.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        btn_clear = tk.Button(root, text="Limpiar", width=23, height=1, font=('Arial', 10, 'bold'), bg="#FF8080", command=self.limpiar_pantalla)
        btn_clear.grid(row=1, column=0, columnspan=4, padx=2, pady=2)

        botones = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+']
        ]

        for fila_idx, fila in enumerate(botones):
            for col_idx, texto in enumerate(fila):
                btn = tk.Button(root, text=texto, width=5, height=2, font=('Arial', 14), command=lambda t=texto: self.presionar_boton(t))
                btn.grid(row=fila_idx + 2, column=col_idx, padx=2, pady=2)
                btn.configure(bg="#C6C954", activebackground="#667436")

        lbl_hist = tk.Label(root, text="Resultados del Campo de Datos:", bg="#FFEC8E", font=('Arial', 10, 'bold'))
        lbl_hist.grid(row=6, column=0, columnspan=4, pady=(5, 0))

        self.txt_historial = tk.Text(root, height=8, width=38, font=('Consolas', 9))
        self.txt_historial.grid(row=7, column=0, columnspan=4, padx=5, pady=5)

        threading.Thread(target=self.escuchar_campo_datos, daemon=True).start()

    def presionar_boton(self, valor):
        if valor == '=':
            self.enviar_solicitud()
        else:
            self.texto_pantalla.set(self.texto_pantalla.get() + str(valor))

    def limpiar_pantalla(self):
        self.texto_pantalla.set("")

    def enviar_solicitud(self):
        expresion = self.texto_pantalla.get()
        operador = None
        for op in ['+', '-', '*', '/']:
            if op in expresion:
                operador = op
                break

        if not operador:
            messagebox.showerror("Error", "Expresión inválida")
            return

        try:
            partes = expresion.split(operador)
            num1 = float(partes[0])
            num2 = float(partes[1])
        except Exception:
            messagebox.showerror("Error", "Números mal formulados")
            return

        codigo_req = COD_CONTENIDO[operador]
        peticion = {
            "id_mensaje": str(uuid.uuid4()),
            "codigo_contenido": codigo_req,
            "id_origen": ID_GUI,
            "num1": num1,
            "num2": num2
        }

        try:
            self.sock.sendall((json.dumps(peticion) + "\n").encode('utf-8'))
            self.texto_pantalla.set("")
        except Exception:
            messagebox.showerror("Error", "Error al enviar al Campo de Datos")

    def escuchar_campo_datos(self):
        buffer = ""
        while True:
            try:
                datos = self.sock.recv(1024).decode('utf-8')
                if not datos:
                    break
                buffer += datos
                while "\n" in buffer:
                    linea, buffer = buffer.split("\n", 1)
                    linea = linea.strip()
                    if linea:
                        msg = json.loads(linea)
                        id_msg = msg.get("id_mensaje")
                        if id_msg in self.mensajes_vistos:
                            continue
                        self.mensajes_vistos.add(id_msg)

                        cod = msg.get("codigo_contenido", "")
                        if cod.endswith("_RES"):
                            linea_txt = f"[{cod}] [{msg['id_origen']}] {msg['expresion']} = {msg['resultado']}\n"
                            self.txt_historial.insert(tk.END, linea_txt)
                            self.txt_historial.see(tk.END)
            except Exception:
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = CelulaGUI(root)
    root.mainloop()