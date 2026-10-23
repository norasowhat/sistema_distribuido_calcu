import socket
import threading
import json
import sys

HOST = '127.0.0.1'

PUERTO_LOCAL = int(sys.argv[1]) if len(sys.argv) > 1 else 9001
PUERTOS_VECINOS = [int(p) for p in sys.argv[2:]] if len(sys.argv) > 2 else []

conexiones = []
mensajes_procesados = set()
lock = threading.Lock()

def enviar_a_vecino(puerto, paquete_bytes):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, puerto))
        s.sendall(paquete_bytes)
        s.close()
    except Exception:
        pass

def retransmitir_broadcast(mensaje_dict, emisor_conn=None):
    id_msg = mensaje_dict.get("id_mensaje")
    with lock:
        if id_msg in mensajes_procesados:
            return
        mensajes_procesados.add(id_msg)

    paquete = (json.dumps(mensaje_dict) + "\n").encode('utf-8')

    with lock:
        for c in list(conexiones):
            if c != emisor_conn:
                try:
                    c.sendall(paquete)
                except Exception:
                    conexiones.remove(c)

    for p_vecino in PUERTOS_VECINOS:
        threading.Thread(target=enviar_a_vecino, args=(p_vecino, paquete), daemon=True).start()

def manejar_conexion(conn, addr):
    buffer = ""
    while True:
        try:
            datos = conn.recv(1024).decode('utf-8')
            if not datos:
                break
            buffer += datos
            while "\n" in buffer:
                linea, buffer = buffer.split("\n", 1)
                linea = linea.strip()
                if linea:
                    msg = json.loads(linea)
                    retransmitir_broadcast(msg, emisor_conn=conn)
        except Exception:
            break
    with lock:
        if conn in conexiones:
            conexiones.remove(conn)
    conn.close()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PUERTO_LOCAL))
    sock.listen()

    while True:
        conn, addr = sock.accept()
        with lock:
            conexiones.append(conn)
        threading.Thread(target=manejar_conexion, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()