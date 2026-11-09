#!/usr/bin/env python3
"""Genera control_manifest.json y nudged_manifest.json de prod4km."""
from __future__ import annotations

import hashlib
import json
import argparse
from datetime import datetime
from pathlib import Path

DEFAULT_CASE = Path(
    "/home/pgich/wrf-modular-V1/outputs/runs/2026-07-31_0000z/caso1_zonda__prod4km"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def frames(case: Path, arm: str) -> int:
    return len(list((case / arm).glob("wrfout_d01_*")))


def build(
    case: Path,
    arm: str,
    *,
    caso: str,
    start: str,
    end: str,
    t0: str,
    run_hours: int,
    asim_horas: float,
    asim_end: str,
    obs_file: Path,
) -> dict:
    nml = case / f"namelist_{arm}.input"
    time_file = case / arm / f"wrf_{arm}.log.time"
    monitor_file = case / arm / f"monitor_{arm}.json"
    tiempo = read_json(time_file)
    monitor = read_json(monitor_file) if monitor_file.exists() else {}
    data = {
        "caso": caso,
        "brazo": arm,
        "creado": datetime.now().isoformat(timespec="seconds"),
        "start": start,
        "run_hours": run_hours,
        "end": end,
        "t0": t0,
        "asim_horas": asim_horas,
        "asim_end": asim_end,
        "namelist": str(nml),
        "namelist_sha256": sha256(nml),
        "wrfout_count": frames(case, arm),
        "historial_archivos": "un wrfout por hora (frames_per_outfile=1)",
        "elapsed_wall_s": tiempo.get("elapsed_wall_s"),
        "maximum_resident_set_size_kbytes": tiempo.get("maximum_resident_set_size_kbytes"),
        "exit_status": tiempo.get("exit_status"),
        "terminado_por_senal": tiempo.get("terminado_por_senal"),
        "omp_num_threads": 1,
        "tiles": "1x1",
        "monitor": monitor,
    }
    if arm == "nudged":
        data.update(
            {
                "obs_nudge_opt": 1,
                "fdda_end": 720.0,
                "gfdda_end_h": float(run_hours),
                "obs_coef_wind": 0.0001,
                "obs_coef_temp": 0.0001,
                "obs_coef_mois": 0.0001,
                "obs_rinxy": 50.0,
                "obs_sfcfacr": 2.0,
                "auxinput11_interval_m": 30,
                "auxinput11_inname": "OBS_DOMAIN101",
                "obs_files": str(obs_file),
                "obs_files_sha256": sha256(obs_file),
            }
        )
    else:
        data["obs_nudge_opt"] = 0
    return data


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-dir", type=Path, default=DEFAULT_CASE)
    ap.add_argument("--caso", default="caso1_zonda__prod4km")
    ap.add_argument("--start", default="2026-07-30_12:00:00")
    ap.add_argument("--end", default="2026-08-01_00:00:00")
    ap.add_argument("--t0", default="2026-07-31_00:00:00")
    ap.add_argument("--run-hours", type=int, default=36)
    ap.add_argument("--asim-horas", type=float, default=12.0)
    ap.add_argument("--asim-end", default="2026-07-31_00:00:00")
    ap.add_argument("--obs-file", type=Path, default=None)
    ap.add_argument("--arms", default="control,nudged")
    args = ap.parse_args()
    case = args.case_dir.resolve()
    obs_file = (args.obs_file or (case / "input" / "OBS_DOMAIN101")).resolve()
    for arm in [a.strip() for a in args.arms.split(",") if a.strip()]:
        data = build(
            case,
            arm,
            caso=args.caso,
            start=args.start,
            end=args.end,
            t0=args.t0,
            run_hours=args.run_hours,
            asim_horas=args.asim_horas,
            asim_end=args.asim_end,
            obs_file=obs_file,
        )
        out = case / f"{arm}_manifest.json"
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"OK -> {out}")


if __name__ == "__main__":
    main()
