#!/usr/bin/env python3
"""Espera el control, corre nudged y valida +1..+24 h (prod4km)."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path("/home/pgich/wrf-modular-V1")
CASE = REPO / "outputs/runs/2026-07-31_0000z/caso1_zonda__prod4km"
PY_MEDIR = REPO / "outputs/prueba_costo_1km/medir.py"
MONITOR = REPO / "scripts/prod4km/monitor_timing.py"
PY_VALIDA = REPO / "src/validacion/valida_wrf_cli.py"
VALIDATION_PYTHON = "/home/pgich/anaconda3/bin/python3"
OBS_JSON = REPO / "data/raw/obs_flat_20260731.json"
EST_JSON = REPO / "config/estaciones.json"
T0 = "2026-07-31T00:00:00"
HORIZON = 24
TOTAL_STEPS = 8640
MAX_WALL_ARM = 21600
MAX_WALL_WAIT = 7 * 3600


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def log(msg: str) -> None:
    out = CASE / "informes" / "orquestacion.log"
    out.parent.mkdir(parents=True, exist_ok=True)
    line = f"{now()} {msg}"
    print(line, flush=True)
    with out.open("a") as fh:
        fh.write(line + "\n")


def read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def count_frames(arm: str) -> int:
    return len(list((CASE / arm).glob("wrfout_d01_*")))


def wait_arm(arm: str, timeout: float) -> dict:
    arm_dir = CASE / arm
    time_file = arm_dir / f"wrf_{arm}.log.time"
    pid_file = arm_dir / f"wrf_{arm}.log.pid"
    t0 = time.time()
    while time.time() - t0 < timeout:
        if time_file.exists():
            time.sleep(3)
            return read_json(time_file) or {}
        pid = None
        try:
            pid = int(pid_file.read_text().strip())
        except (OSError, ValueError):
            pass
        if pid is None and time.time() - t0 > 120:
            log(f"{arm}: sin pidfile ni .time tras 120 s")
            return {}
        time.sleep(30)
    log(f"{arm}: timeout de espera ({timeout/3600:.1f} h)")
    try:
        if pid_file.exists():
            os.kill(int(pid_file.read_text()), signal.SIGTERM)
    except (OSError, ValueError):
        pass
    return {}


def arm_ok(arm: str, info: dict) -> tuple[bool, str]:
    if not info:
        return False, "sin .time"
    if info.get("exit_status") != 0:
        return False, f"exit_status={info.get('exit_status')}"
    if info.get("terminado_por_senal") is not None:
        return False, f"senal={info.get('terminado_por_senal')}"
    if info.get("cortado_por"):
        return False, f"cortado_por={info.get('cortado_por')}"
    n = count_frames(arm)
    if n != 37:
        return False, f"wrfout={n} (esperados 37)"
    return True, "ok"


def launch_arm(arm: str) -> None:
    arm_dir = CASE / arm
    for name in (
        f"wrf_{arm}.log",
        f"wrf_{arm}.log.pid",
        f"wrf_{arm}.log.time",
        f"monitor_{arm}.json",
        f"monitor_{arm}.out",
        f"monitor_{arm}.trace.log",
        f"medir_{arm}.out",
    ):
        (arm_dir / name).unlink(missing_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS="1", GFORTRAN_UNBUFFERED_ALL="1")
    with (arm_dir / f"medir_{arm}.out").open("wb") as out:
        subprocess.Popen(
            [VALIDATION_PYTHON, "-I", str(PY_MEDIR), arm, f"wrf_{arm}.log",
             str(MAX_WALL_ARM), "--", "./wrf.exe"],
            cwd=arm_dir, env=env, stdout=out, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, start_new_session=True,
        )
    with (arm_dir / f"monitor_{arm}.out").open("wb") as out:
        subprocess.Popen(
            [VALIDATION_PYTHON, "-I", str(MONITOR),
             "--log", str(arm_dir / f"wrf_{arm}.log"),
             "--pidfile", str(arm_dir / f"wrf_{arm}.log.pid"),
             "--out", str(arm_dir / f"monitor_{arm}.json"),
             "--expected-steps", str(TOTAL_STEPS),
             "--warmup", "100", "--max-wall", str(MAX_WALL_ARM)],
            cwd=arm_dir, env=env, stdout=out, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, start_new_session=True,
        )
    log(f"{arm}: lanzado")


def run_validation() -> dict:
    times = [
        (datetime(2026, 7, 31) + timedelta(hours=h)).strftime("%Y-%m-%d_%H:%M:%S")
        for h in range(1, HORIZON + 1)
    ]
    cmd = [
        VALIDATION_PYTHON, str(PY_VALIDA),
        "--nudged-dir", str(CASE / "nudged"),
        "--control-dir", str(CASE / "control"),
        "--output-dir", str(CASE),
        "--valid-times", ",".join(times),
        "--obs-json", str(OBS_JSON),
        "--estaciones-json", str(EST_JSON),
        "--t0", T0,
        "--horizon-h", str(HORIZON),
        "--label", "prod4km",
    ]
    log("validacion: " + " ".join(cmd))
    out_path = CASE / "informes" / "validacion_stdout.log"
    with out_path.open("w") as fh:
        r = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, timeout=7200)
    log(f"validacion: returncode={r.returncode}")
    return {"returncode": r.returncode, "stdout": str(out_path)}


def main() -> int:
    status_path = CASE / "informes" / "estado_prod4km.json"
    estado = {"inicio": now(), "control": {}, "nudged": {}, "validacion": {}}
    log("esperando fin del control")
    control = wait_arm("control", MAX_WALL_WAIT)
    estado["control"] = control
    ok, motivo = arm_ok("control", control)
    log(f"control: {motivo}")
    if not ok:
        estado["resultado"] = "control_fallido"
        estado["motivo"] = motivo
        estado["fin"] = now()
        write_json(status_path, estado)
        return 1
    estado["control"]["monitor"] = read_json(CASE / "control/monitor_control.json")

    log("lanzando nudged")
    launch_arm("nudged")
    nudged = wait_arm("nudged", MAX_WALL_WAIT)
    estado["nudged"] = nudged
    ok, motivo = arm_ok("nudged", nudged)
    log(f"nudged: {motivo}")
    if not ok:
        estado["resultado"] = "nudged_fallido"
        estado["motivo"] = motivo
        estado["fin"] = now()
        write_json(status_path, estado)
        return 1
    estado["nudged"]["monitor"] = read_json(CASE / "nudged/monitor_nudged.json")

    log("validando +1..+24 h")
    estado["validacion"] = run_validation()
    estado["resultado"] = (
        "completado" if estado["validacion"]["returncode"] == 0 else "validacion_fallida"
    )
    estado["fin"] = now()
    write_json(status_path, estado)
    log(f"fin: {estado['resultado']}")
    return 0 if estado["resultado"] == "completado" else 1


if __name__ == "__main__":
    raise SystemExit(main())
