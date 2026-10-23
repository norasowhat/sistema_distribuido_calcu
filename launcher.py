import subprocess
import time
import sys

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0

def desplegar_sistema():
    puertos = [9001, 9002, 9003, 9004]

    for puerto in puertos:
        vecinos = [p for p in puertos if p != puerto]
        cmd = ["python", "nodo.py", str(puerto)] + [str(v) for v in vecinos]
        subprocess.Popen(cmd, creationflags=CREATE_NO_WINDOW)
    
    time.sleep(1)
    
    for idx, puerto in enumerate(puertos, start=1):
        for srv in ["SUM", "SUB", "MUL", "DIV"]:
            cmd_srv = ["python", "celula_servidor.py", str(puerto), srv, f"SRV_{srv}_N{idx}"]
            subprocess.Popen(cmd_srv, creationflags=CREATE_NO_WINDOW)
         
        cmd_gui = ["python", "celula_gui.py", str(puerto), f"GUI_N{idx}"]
        subprocess.Popen(cmd_gui, creationflags=CREATE_NO_WINDOW)

    print("20 células y 4 nodos arriba")

if __name__ == "__main__":
    desplegar_sistema()