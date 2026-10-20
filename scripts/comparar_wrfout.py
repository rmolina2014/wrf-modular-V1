#!/usr/bin/env python3
"""Compara dos directorios de wrfout (misma corrida repetida) campo por campo.

Uso:
  python scripts/comparar_wrfout.py DIR_A DIR_B [--vars T2 Q2 PSFC U10 V10]

Para cada archivo wrfout_d01_* presente en ambos directorios y cada variable,
informa si son identicos bit a bit, la diferencia absoluta maxima y la cantidad
de celdas distintas. Sale con codigo 1 si algun archivo falta o si hay diferencias.
La tolerancia aceptable debe fijarse antes de correr el test (Seccion 5.6)."""
import argparse, sys
from pathlib import Path
import numpy as np
import xarray as xr

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir_a"); ap.add_argument("dir_b")
    ap.add_argument("--vars", nargs="+", default=["T2", "Q2", "PSFC", "U10", "V10"])
    a = ap.parse_args()
    da, db = Path(a.dir_a), Path(a.dir_b)
    fa = sorted(p.name for p in da.glob("wrfout_d01_*"))
    fb = sorted(p.name for p in db.glob("wrfout_d01_*"))
    solo_a, solo_b = sorted(set(fa) - set(fb)), sorted(set(fb) - set(fa))
    comunes = sorted(set(fa) & set(fb))
    ok = True
    if solo_a or solo_b:
        ok = False
        print(f"ARCHIVOS SIN PAR: solo en A={solo_a} solo en B={solo_b}")
    print(f"Archivos comparados: {len(comunes)}")
    peor = {v: 0.0 for v in a.vars}
    difs = {v: 0 for v in a.vars}
    for n in comunes:
        with xr.open_dataset(da / n) as x, xr.open_dataset(db / n) as y:
            for v in a.vars:
                if v not in x or v not in y:
                    print(f"  {n}: variable {v} ausente"); ok = False; continue
                u, w = x[v].values, y[v].values
                if u.shape != w.shape:
                    print(f"  {n} {v}: formas distintas {u.shape} {w.shape}"); ok = False; continue
                d = np.abs(u.astype("float64") - w.astype("float64"))
                nd = int(np.count_nonzero(~((u == w) | (np.isnan(u) & np.isnan(w)))))
                if nd:
                    ok = False; difs[v] += nd
                    peor[v] = max(peor[v], float(np.nanmax(d)))
    for v in a.vars:
        print(f"  {v:5s} celdas distintas={difs[v]:>10d}  |dif| max={peor[v]:.3e}")
    print("RESULTADO:", "IDENTICOS (bit a bit)" if ok else "HAY DIFERENCIAS")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
