"""Sustituto de /usr/bin/time -v (no instalado en esta PC): mide un comando con os.wait4.

Uso: python3 -I medir.py <etiqueta> <log_salida> <timeout_s> -- <comando ...>

- stdout+stderr del comando van a <log_salida>.
- Al terminar escribe <log_salida>.time con: comando, inicio/fin, tiempo real, user, sys,
  Maximum resident set size (kbytes) (ru_maxrss de wait4, igual que GNU time) y exit status.
- Si se supera <timeout_s> envía SIGTERM y, 30 s después, SIGKILL.
"""
import datetime
import json
import os
import signal
import sys
import time

etiqueta, log_salida, timeout_s = sys.argv[1], sys.argv[2], float(sys.argv[3])
cmd = sys.argv[sys.argv.index("--") + 1:]

t0 = time.time()
inicio = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
with open(log_salida, "wb") as out:
    pid = os.fork()
    if pid == 0:
        os.dup2(out.fileno(), 1)
        os.dup2(out.fileno(), 2)
        os.execvp(cmd[0], cmd)

with open(log_salida + ".pid", "w") as f:
    f.write(str(pid))

cortado = None
while True:
    wpid, status, ru = os.wait4(pid, os.WNOHANG)
    if wpid == pid:
        break
    if cortado is None and time.time() - t0 > timeout_s:
        cortado = "timeout"
        os.kill(pid, signal.SIGTERM)
        t_term = time.time()
    if cortado and time.time() - t_term > 30:
        os.kill(pid, signal.SIGKILL)
    time.sleep(1)

real = time.time() - t0
res = {
    "etiqueta": etiqueta,
    "comando": " ".join(cmd),
    "cwd": os.getcwd(),
    "inicio": inicio,
    "fin": datetime.datetime.now().isoformat(sep=" ", timespec="seconds"),
    "elapsed_wall_s": round(real, 2),
    "user_s": round(ru.ru_utime, 2),
    "system_s": round(ru.ru_stime, 2),
    "maximum_resident_set_size_kbytes": ru.ru_maxrss,
    "exit_status": os.WEXITSTATUS(status) if os.WIFEXITED(status) else None,
    "terminado_por_senal": os.WTERMSIG(status) if os.WIFSIGNALED(status) else None,
    "cortado_por": cortado,
}
with open(log_salida + ".time", "w") as f:
    f.write(json.dumps(res, indent=2, ensure_ascii=False) + "\n")
os.remove(log_salida + ".pid")
print(json.dumps(res, ensure_ascii=False))
