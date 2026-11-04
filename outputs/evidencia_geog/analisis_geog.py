"""Puntos 4, 5 y 6 de evidencia_geog: control de grilla, estadísticas de HGT_M e IDW de 4 nodos por estación.

Uso (desde la raíz del repo):
    python3 -I outputs/evidencia_geog/analisis_geog.py

Solo lee archivos. Escribe en outputs/evidencia_geog/: resultados_geog.json y tabla_estaciones.csv
"""
import csv
import json
import os
import sys
from pathlib import Path

import numpy as np
import xarray as xr

ROOT = Path("/home/pgich/wrf-modular-V1")
sys.path.insert(0, str(ROOT / "src"))
from validacion.spatial_interp import SpatialInterpolator  # mismo algoritmo IDW de 4 nodos

E = ROOT / "outputs" / "evidencia_geog"
GEO = {v: E / f"geogrid_{v}" / "geo_em.d01.nc" for v in ("lowres", "default")}
WRFOUT = ROOT / "outputs/runs/2026-09-24_0000z/sanjuan_0924/control/wrfout_d01_2026-09-24_00:00:00"
EST_JSON = ROOT / "config" / "estaciones.json"
# LOS_PIONEROS no está en config/estaciones.json; única fuente con coordenadas y elevación:
PIONEROS_SRC = ROOT / "documentacion_proyecto" / "implementacion_arquitectura_27082026.md"
PIONEROS = {"lat": -32.1234, "lon": -67.1234, "elev": 890}  # copiado literal de PIONEROS_SRC:96

TESIS = {  # real / grilla / dif, tabla dada por el usuario
    "INTA_POCITO": (615, 809, 194), "ECOHUMUS": (600, 599, -1), "PUNTA_NEGRA": (800, 1307, 507),
    "VALLE_FERTIL": (900, 1035, 135), "LOS_PIONEROS": (890, 618, -272), "CUESTA_Viento": (1530, 1917, 387),
    "ULLUM_EMBALSE": (768, 917, 149), "INTA_SANMARTIN": (600, 908, 308), "CARACOLES": (942, 1912, 970),
}


def mtime(p):
    import datetime
    return datetime.datetime.fromtimestamp(os.stat(p).st_mtime).isoformat(sep=" ")


def geo_como_wrfout(path):
    """geo_em usa XLAT_M/XLONG_M/HGT_M; se renombran para pasar al interpolador sin tocar el algoritmo."""
    ds = xr.open_dataset(path)
    return ds[["XLAT_M", "XLONG_M", "HGT_M"]].rename({"XLAT_M": "XLAT", "XLONG_M": "XLONG", "HGT_M": "HGT"})


res = {"archivos": {}}
for p in [*GEO.values(), WRFOUT, EST_JSON, PIONEROS_SRC, ROOT / "src/validacion/spatial_interp.py"]:
    res["archivos"][str(p)] = mtime(p)

ds = {v: geo_como_wrfout(p) for v, p in GEO.items()}
h = {v: ds[v].HGT.values[0].astype("float64") for v in ds}

# --- Punto 4: control lowres vs HGT del wrfout de la tesis (primer tiempo)
w = xr.open_dataset(WRFOUT)
hgt_w = w.HGT.values[0].astype("float64")
res["punto4"] = {
    "shape_geo_lowres": list(h["lowres"].shape), "shape_wrfout": list(hgt_w.shape),
    "Time_wrfout_0": str(w.Times.values[0].decode() if hasattr(w.Times.values[0], "decode") else w.Times.values[0]),
}
if h["lowres"].shape == hgt_w.shape:
    d = h["lowres"] - hgt_w
    res["punto4"]["max_abs_dif_HGT_M_lowres_vs_HGT_wrfout_m"] = float(np.max(np.abs(d)))
    res["punto4"]["max_abs_dif_XLAT"] = float(np.max(np.abs(ds["lowres"].XLAT.values[0] - w.XLAT.values[0])))
    res["punto4"]["max_abs_dif_XLONG"] = float(np.max(np.abs(ds["lowres"].XLONG.values[0] - w.XLONG.values[0])))

# --- Punto 5
res["punto5"] = {v: {"min": float(h[v].min()), "max": float(h[v].max()), "media": float(h[v].mean())} for v in h}
dd = h["default"] - h["lowres"]
j, i = np.unravel_index(np.argmax(np.abs(dd)), dd.shape)
res["punto5"]["default_menos_lowres"] = {
    "max_abs": float(np.abs(dd).max()), "media_abs": float(np.abs(dd).mean()),
    "rms": float(np.sqrt(np.mean(dd ** 2))), "media_con_signo": float(dd.mean()),
    "punto_max": {"j_sn_0based": int(j), "i_we_0based": int(i),
                  "lat": float(ds["lowres"].XLAT.values[0][j, i]), "lon": float(ds["lowres"].XLONG.values[0][j, i]),
                  "HGT_M_lowres": float(h["lowres"][j, i]), "HGT_M_default": float(h["default"][j, i]),
                  "dif": float(dd[j, i])},
}

# --- Punto 6
est = json.loads(EST_JSON.read_text(encoding="utf-8"))
est = {k: {"lat": v["lat"], "lon": v["lon"], "elev": v["elev"], "fuente": str(EST_JSON)} for k, v in est.items()}
est["LOS_PIONEROS"] = {**PIONEROS, "fuente": f"{PIONEROS_SRC}:96"}
si = SpatialInterpolator()
filas = []
for nombre, e in est.items():
    gl = si.interpolar_4_nodos(ds["lowres"], "HGT", e["lat"], e["lon"])
    gd = si.interpolar_4_nodos(ds["default"], "HGT", e["lat"], e["lon"])
    gw = si.interpolar_4_nodos(w, "HGT", e["lat"], e["lon"])
    f = {"estacion": nombre, "lat": e["lat"], "lon": e["lon"], "real": e["elev"],
         "grilla_lowres": round(gl, 1), "dif_lowres": round(gl - e["elev"], 1),
         "grilla_default": round(gd, 1), "dif_default": round(gd - e["elev"], 1),
         "grilla_wrfout_tesis": round(gw, 1), "fuente_coords": e["fuente"]}
    t = TESIS.get(nombre)
    if t:
        f.update({"tesis_real": t[0], "tesis_grilla": t[1], "tesis_dif": t[2],
                  "discrep_grilla_lowres_vs_tesis": round(gl - t[1], 1),
                  "discrep_real_vs_tesis": e["elev"] - t[0],
                  "MARCA_>5m": abs(gl - t[1]) > 5 or abs(e["elev"] - t[0]) > 5})
    filas.append(f)
res["punto6"] = filas

(E / "resultados_geog.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
with open(E / "tabla_estaciones.csv", "w", newline="", encoding="utf-8") as fh:
    cols = sorted({k for f in filas for k in f}, key=lambda k: list(filas[0]).index(k) if k in filas[0] else 99)
    wr = csv.DictWriter(fh, fieldnames=cols)
    wr.writeheader()
    wr.writerows(filas)
print(json.dumps(res, indent=2, ensure_ascii=False))
