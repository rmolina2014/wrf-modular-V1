#!/usr/bin/env python3
"""Regenera obs_flat_<fecha>.json (y el CSV intermedio) a partir del crudo EcoWitt.

Fuente de verdad: data/raw/ecowitt_historico_<AAAAMMDD>.json (dict anidado
{estaciones: {NOMBRE: {mac, datos: {grupo: {variable: {list: {ts: valor}}}}}}}).

Reutiliza el mapeo canonico del proyecto (`EcowittIngestor._convertir_a_csv`)
para reconstruir el CSV historico y luego `run_casos.generar_obs_flat` para el
JSON obs_flat que consume el pipeline. Asi el resultado es identico al flujo
original, pero partiendo del crudo (no de un obs_flat previo posiblemente viejo).

Uso:
    python scripts/regenerar_obs_flat_historico.py                 # 4 fechas oficiales
    python scripts/regenerar_obs_flat_historico.py 2026-08-06      # una fecha
"""

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.ingesta.ecowitt_client import EcowittIngestor, cargar_catalogo_estaciones
from src.casos.run_casos import RAW, generar_obs_flat

FECHAS_OFICIALES = ["2026-07-31", "2026-01-01", "2026-05-16", "2026-08-06"]


def _respuestas_desde_crudo(ruta_json: Path):
    """Reconstruye {nombre: {code:0, data:...}} desde el JSON crudo (dict)."""
    with open(ruta_json, "r", encoding="utf-8") as f:
        crudo = json.load(f)
    respuestas = {}
    for nombre, st in crudo.get("estaciones", {}).items():
        datos = st.get("datos")
        respuestas[nombre] = {"code": 0, "data": datos} if datos else None
    return respuestas, crudo.get("fechadatos")


def regenerar(fecha: str) -> dict:
    fc = fecha.replace("-", "")
    ruta_json = RAW / f"ecowitt_historico_{fc}.json"
    if not ruta_json.exists():
        raise FileNotFoundError(f"No existe el crudo: {ruta_json}")

    respuestas, fechadatos = _respuestas_desde_crudo(ruta_json)
    if fechadatos and fechadatos != fecha:
        print(f"  [aviso] fechadatos={fechadatos} != {fecha} en {ruta_json.name}")

    catalogo = cargar_catalogo_estaciones()
    ing = EcowittIngestor.__new__(EcowittIngestor)  # sin credenciales: solo metodo estatico
    filas = ing._convertir_a_csv(respuestas, catalogo, fecha)

    csv_path = RAW / f"ecowitt_historico_{fc}.csv"
    csv_viejo = None
    if csv_path.exists():
        csv_viejo = sum(1 for _ in open(csv_path, encoding="utf-8")) - 1
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)

    obs_flat_path = RAW / f"obs_flat_{fc}.json"
    flat_viejo = None
    if obs_flat_path.exists():
        try:
            flat_viejo = len(json.load(open(obs_flat_path, encoding="utf-8")))
        except Exception:
            flat_viejo = "?"
        obs_flat_path.unlink()

    generar_obs_flat(csv_path, fecha)

    flat_nuevo = json.load(open(obs_flat_path, encoding="utf-8"))
    por_est = Counter(o["estacion"] for o in flat_nuevo)
    resumen = {
        "fecha": fecha,
        "csv_filas_antes": csv_viejo,
        "csv_filas_ahora": len(filas),
        "obs_flat_antes": flat_viejo,
        "obs_flat_ahora": len(flat_nuevo),
        "por_estacion": dict(sorted(por_est.items())),
    }
    print(f"  {fecha}: CSV {csv_viejo}->{len(filas)} | obs_flat {flat_viejo}->{len(flat_nuevo)}")
    for est, n in sorted(por_est.items()):
        print(f"      {est:15s} {n}")
    return resumen


def main():
    ap = argparse.ArgumentParser(description="Regenera obs_flat desde el crudo historico EcoWitt.")
    ap.add_argument("fechas", nargs="*", default=None, help="Fechas YYYY-MM-DD (default: 4 oficiales).")
    args = ap.parse_args()
    fechas = args.fechas or FECHAS_OFICIALES
    resumenes = [regenerar(f) for f in fechas]
    print("\n=== resumen ===")
    for r in resumenes:
        print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    main()
