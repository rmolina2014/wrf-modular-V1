"""Watchdog de memoria: cada 2 s registra RSS total de un ejecutable y MemAvailable; corta con SIGTERM si se pasa.

Uso: python3 -I watchdog_mem.py <nombre_proc> <cwd_run> <csv> [rss_max_GB=34] [memavail_min_GB=3]

- Solo mira procesos cuyo comm == <nombre_proc> y cuyo cwd == <cwd_run> (no toca nada fuera de la prueba).
- CSV: fecha_hora, t_s, n_proc, rss_total_kB, memavailable_kB, swapfree_kB, accion
- Si rss_total > rss_max o MemAvailable < memavail_min: SIGTERM a esos procesos (y SIGKILL a los 20 s si siguen).
- Termina cuando, después de haber visto el proceso, deja de existir durante 6 s; o tras 30 min sin verlo nunca.
- Al final escribe <csv>.resumen.json con el pico y si cortó.
"""
import csv
import datetime
import json
import os
import signal
import sys
import time

nombre, cwd_run, salida = sys.argv[1], os.path.realpath(sys.argv[2]), sys.argv[3]
rss_max_kb = float(sys.argv[4] if len(sys.argv) > 4 else 34) * 1024 * 1024
avail_min_kb = float(sys.argv[5] if len(sys.argv) > 5 else 3) * 1024 * 1024


def meminfo():
    d = {}
    with open("/proc/meminfo") as f:
        for line in f:
            k, v = line.split(":")
            d[k] = int(v.split()[0])
    return d


def procesos():
    out = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/comm") as f:
                if f.read().strip() != nombre:
                    continue
            if os.path.realpath(f"/proc/{pid}/cwd") != cwd_run:
                continue
            with open(f"/proc/{pid}/status") as f:
                rss = next((int(l.split()[1]) for l in f if l.startswith("VmRSS:")), 0)
            out.append((int(pid), rss))
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
    return out


t0 = time.time()
visto = False
ultimo_visto = None
pico = {"rss_total_kB": 0, "momento": None}
min_avail = None
cortado = None
t_term = None
with open(salida, "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["fecha_hora", "t_s", "n_proc", "rss_total_kB", "memavailable_kB", "swapfree_kB", "accion"])
    while True:
        ps = procesos()
        mi = meminfo()
        rss = sum(r for _, r in ps)
        ahora = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
        accion = ""
        if ps:
            visto, ultimo_visto = True, time.time()
            if rss > pico["rss_total_kB"]:
                pico = {"rss_total_kB": rss, "momento": ahora}
            min_avail = mi["MemAvailable"] if min_avail is None else min(min_avail, mi["MemAvailable"])
            if cortado is None and (rss > rss_max_kb or mi["MemAvailable"] < avail_min_kb):
                cortado = "rss>limite" if rss > rss_max_kb else "MemAvailable<limite"
                for pid, _ in ps:
                    os.kill(pid, signal.SIGTERM)
                t_term = time.time()
                accion = f"SIGTERM ({cortado})"
            elif cortado and time.time() - t_term > 20:
                for pid, _ in ps:
                    os.kill(pid, signal.SIGKILL)
                accion = "SIGKILL"
        w.writerow([ahora, round(time.time() - t0, 1), len(ps), rss, mi["MemAvailable"], mi["SwapFree"], accion])
        fh.flush()
        if visto and not ps and time.time() - ultimo_visto > 6:
            break
        if not visto and time.time() - t0 > 1800:
            break
        time.sleep(2)

res = {"proceso": nombre, "cwd": cwd_run, "pico_rss_total_kB": pico["rss_total_kB"],
       "pico_rss_total_GB": round(pico["rss_total_kB"] / 1024 / 1024, 2), "momento_pico": pico["momento"],
       "min_memavailable_kB": min_avail, "cortado_por_watchdog": cortado,
       "limites": {"rss_max_GB": rss_max_kb / 1024 / 1024, "memavail_min_GB": avail_min_kb / 1024 / 1024}}
with open(salida + ".resumen.json", "w") as f:
    json.dump(res, f, indent=2)
print(json.dumps(res))
