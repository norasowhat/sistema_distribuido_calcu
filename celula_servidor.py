import socket
import json
import sys
import uuid

HOST = '127.0.0.1'

PUERTO_NODO = int(sys.argv[1]) if len(sys.argv) > 1 else 9001
TIPO_SERVICIO = sys.argv[2].upper() if len(sys.argv) > 2 else "SUM"
ID_CELULA = sys.argv[3] if len(sys.argv) > 3 else f"SRV_{TIPO_SERVICIO}_1"

COD_CONTENIDO = {
    "SUM": ("SUM_PET", "SUM_RES"),
    "SUB": ("SUB_PET", "SUB_RES"),
    "MUL": ("MUL_PET", "MUL_RES"),
    "DIV": ("DIV_PET", "DIV_RES")
}

COD_PET, COD_RES = COD_CONTENIDO.get(TIPO_SERVICIO, ("SUM_PET", "SUM_RES"))
mensajes_vistos = set()

def calcular(num1, num2):
    if TIPO_SERVICIO == "SUM": return num1 + num2
    if TIPO_SERVICIO == "SUB": return num1 - num2
    if TIPO_SERVICIO == "MUL": return num1 * num2
    if TIPO_SERVICIO == "DIV": return num1 / num2 if num2 != 0 else "Indeterminado"
    return 0

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PUERTO_NODO))
    except Exception:
        return

    buffer = ""
    while True:
        try:
            datos = sock.recv(1024).decode('utf-8')
            if not datos:
                break
            buffer += datos
            while "\n" in buffer:
                linea, buffer = buffer.split("\n", 1)
                linea = linea.strip()
                if not linea:
                    continue

                msg = json.loads(linea)
                id_msg = msg.get("id_mensaje")

                if id_msg in mensajes_vistos:
                    continue
                mensajes_vistos.add(id_msg)

                if msg.get("codigo_contenido") == COD_PET:
                    num1 = float(msg.get("num1", 0))
                    num2 = float(msg.get("num2", 0))
                    res = calcular(num1, num2)

                    respuesta = {
                        "id_mensaje": str(uuid.uuid4()),
                        "id_solicitud": id_msg,
                        "codigo_contenido": COD_RES,
                        "id_origen": ID_CELULA,
                        "expresion": f"{num1} {TIPO_SERVICIO} {num2}",
                        "resultado": res
                    }
                    
                    sock.sendall((json.dumps(respuesta) + "\n").encode('utf-8'))
        except Exception:
            break

if __name__ == "__main__":
    main()