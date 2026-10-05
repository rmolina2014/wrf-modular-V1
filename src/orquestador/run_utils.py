"""Utilidades de ejecución del orquestador."""
from __future__ import annotations
import shutil
import time
from pathlib import Path
from typing import Optional


def copiar_archivo(src: Path | str, dst: Path | str, timeout: int = 60) -> Path:
    src_p = Path(src)
    dst_p = Path(dst)
    dst_p.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            shutil.copy2(src_p, dst_p)
            return dst_p
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"No se pudo copiar {src_p} a {dst_p} tras {timeout}s")


def copiar_wrfout(run_dir: Path | str, dest_dir: Path | str, valid_time: Optional[str] = None) -> None:
    run_dir_p = Path(run_dir)
    dest_dir_p = Path(dest_dir)
    dest_dir_p.mkdir(parents=True, exist_ok=True)
    patron = "wrfout_d01_*"
    archivos = sorted(run_dir_p.glob(patron))
    for a in archivos:
        try:
            shutil.copy2(a, dest_dir_p / a.name)
        except Exception:
            pass
