#!/usr/bin/env python3
"""Vigila el piloto de costo de wrf.exe (prod4km).

- Lee 'Timing for main: time ... : <s> elapsed seconds' del log.
- Tras `warmup` pasos proyecta el total (pasos_esperados) y, si supera
  `max_wall`, termina wrf.exe (SIGTERM y luego SIGKILL).
- Tambien corta si el reloj supera `max_wall`.
- Registra VmHWM y Threads leidos de /proc/<pid>/status.
- Escribe un JSON con el resultado del monitoreo.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import signal
import time
from pathlib import Path

PAT = re.compile(
    r"Timing for main: time (?P<time>\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2})"
    r".*?:\s+(?P<sec>[0-9.]+) elapsed seconds"
)


def read_pid(path: Path) -> int | None:
    try:
        return int(path.read_text().strip())
    except (OSError, ValueError):
        return None


def status_field(pid: int, field: str) -> int | None:
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith(field + ":"):
                return int(line.split()[1])
    except (OSError, ValueError):
        return None
    return None


def kill(pid: int, log) -> None:
    for sig, espera in ((signal.SIGTERM, 30), (signal.SIGKILL, 0)):
        try:
            os.kill(pid, sig)
            log(f"monitor: enviado {sig.name} a pid {pid}")
        except ProcessLookupError:
            return
        if sig is signal.SIGTERM:
            time.sleep(espera)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True, type=Path)
    ap.add_argument("--pidfile", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--expected-steps", type=int, default=8640)
    ap.add_argument("--warmup", type=int, default=100)
    ap.add_argument("--max-wall", type=float, default=21600.0)
    ap.add_argument("--poll", type=float, default=10.0)
    args = ap.parse_args()

    t0 = time.time()
    log_path = args.out.with_suffix(".trace.log")
    fh = log_path.open("w")

    def log(msg: str) -> None:
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
        print(line)
        fh.write(line + "\n")
        fh.flush()

    steps: list[float] = []
    pos = 0
    peak_rss = peak_threads = 0
    pid = None
    seen_pid = False
    resultado = "en_curso"
    esperado = args.expected_steps

    while True:
        if pid is None:
            pid = read_pid(args.pidfile)
        if pid:
            rss = status_field(pid, "VmHWM")
            thr = status_field(pid, "Threads")
            peak_rss = max(peak_rss, rss or 0)
            peak_threads = max(peak_threads, thr or 0)

        try:
            with args.log.open("r", errors="replace") as lf:
                lf.seek(pos)
                chunk = lf.read()
                pos = lf.tell()
        except OSError:
            chunk = ""

        for m in PAT.finditer(chunk):
            if len(steps) < esperado:
                steps.append(float(m.group("sec")))
                if len(steps) in (1, 10, 50, 100) or len(steps) % 500 == 0:
                    log(f"paso {len(steps)}: {steps[-1]:.3f} s")

        n = len(steps)
        if n >= args.warmup:
            estable = steps[1:]  # descarta el primer paso (calentamiento)
            avg = sum(estable) / len(estable)
            proyectado = avg * esperado
            if n == args.warmup or n % 500 == 0:
                log(
                    f"proyeccion n={n}: media={avg:.4f} s/paso "
                    f"-> {proyectado/3600:.2f} h para {esperado} pasos"
                )
            if proyectado > args.max_wall:
                resultado = "abortado_por_proyeccion"
                log(
                    f"PROYECCION {proyectado/3600:.2f} h > {args.max_wall/3600:.2f} h; "
                    f"se detiene wrf.exe"
                )
                if pid:
                    kill(pid, log)
                break

        if time.time() - t0 > args.max_wall:
            resultado = "abortado_por_reloj"
            log("reloj supera el maximo; se detiene wrf.exe")
            if pid:
                kill(pid, log)
            break

        if n >= esperado:
            resultado = "completado"
            break

        raw = read_pid(args.pidfile)
        if raw is not None:
            seen_pid = True
        if seen_pid and raw is None and n < esperado:
            # el pidfile desaparece cuando medir.py termina
            resultado = "proceso_terminado"
            break

        time.sleep(args.poll)

    avg = (sum(steps[1:]) / len(steps[1:])) if len(steps) > 1 else None
    data = {
        "resultado": resultado,
        "pasos_registrados": len(steps),
        "pasos_esperados": esperado,
        "media_s_por_paso": round(avg, 4) if avg else None,
        "primer_paso_s": steps[0] if steps else None,
        "proyeccion_h": round(avg * esperado / 3600, 3) if avg else None,
        "peak_rss_kbytes": peak_rss,
        "peak_threads": peak_threads,
        "elapsed_wall_s": round(time.time() - t0, 1),
    }
    args.out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    log(f"FIN: {json.dumps(data, ensure_ascii=False)}")
    fh.close()


if __name__ == "__main__":
    main()
