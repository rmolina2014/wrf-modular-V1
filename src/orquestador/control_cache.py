"""Cache/reutilización de corrida control."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _sha256(path: Path | str) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _escribir_manifest_control(control_dir: Path | str, run_dir: Path | str, namelist_path: Path | str,
                               archivos_wrfout: list[Path | str], case_dir_control: Path | str) -> None:
    control_dir_p = Path(control_dir)
    control_dir_p.mkdir(parents=True, exist_ok=True)
    datos: dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "run_dir": str(Path(run_dir).resolve()),
        "namelist": str(Path(namelist_path).resolve()),
        "archivos": [],
    }
    for a in archivos_wrfout:
        ap = Path(a)
        datos["archivos"].append({
            "nombre": ap.name,
            "size": ap.stat().st_size,
            "sha256": _sha256(ap) if ap.exists() else None,
        })
    with open(control_dir_p / "control_manifest.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


def _control_reutilizable(run_dir: Path | str, case_dir_control: Path | str, control_dir: Path | str,
                          max_horas_control: int = 6) -> bool:
    # Versión simplificada basada en lógica existente
    man_path = Path(control_dir) / "control_manifest.json"
    if not man_path.exists():
        return False
    try:
        with open(man_path, "r", encoding="utf-8") as f:
            man = json.load(f)
    except Exception:
        return False
    # Validación mínima
    archivos = man.get("archivos", [])
    if not archivos:
        return False
    for ar in archivos:
        nombre = ar.get("nombre")
        if not nombre:
            continue
        cand = Path(control_dir) / nombre
        if not cand.exists():
            return False
        sha = ar.get("sha256")
        if sha and _sha256(cand) != sha:
            return False
    return True
