#!/usr/bin/env python3
"""PASO 5 ampliado: altura del terreno en las grillas tesis15, op15km y prod4km."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from netCDF4 import Dataset
from scipy.interpolate import griddata


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def haversine(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def extract(geo: Path, est: dict) -> tuple[dict, dict]:
    ds = Dataset(geo)
    hgt = np.asarray(ds.variables["HGT_M"][0])
    lat = np.asarray(ds.variables["XLAT_M"][0])
    lon = np.asarray(ds.variables["XLONG_M"][0])
    meta = {}
    for key in (
        "MAP_PROJ",
        "CEN_LAT",
        "CEN_LON",
        "TRUELAT1",
        "TRUELAT2",
        "STAND_LON",
        "DX",
        "DY",
        "GRID_ID",
        "PARENT_ID",
    ):
        if key in ds.ncattrs():
            value = ds.getncattr(key)
            meta[key] = value.item() if hasattr(value, "item") else value
    meta["HGT_M_shape"] = list(hgt.shape)
    ds.close()

    out = {}
    for name, info in est.items():
        d2 = (lat - info["lat"]) ** 2 + ((lon - info["lon"]) * math.cos(math.radians(info["lat"]))) ** 2
        j, i = np.unravel_index(np.argmin(d2), d2.shape)
        hb = float(
            griddata(
                (lat.ravel(), lon.ravel()),
                hgt.ravel(),
                (info["lat"], info["lon"]),
                method="linear",
            )
        )
        out[name] = {
            "i_vecino": int(i),
            "j_vecino": int(j),
            "lat_modelo": float(lat[j, i]),
            "lon_modelo": float(lon[j, i]),
            "dist_vecino_m": haversine(info["lat"], info["lon"], float(lat[j, i]), float(lon[j, i])),
            "hgt_vecino": float(hgt[j, i]),
            "hgt_interp": hb,
        }
    return out, meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--estaciones", required=True, type=Path)
    ap.add_argument("--tesis-geo", required=True, type=Path)
    ap.add_argument("--tesis-namelist", required=True, type=Path)
    ap.add_argument("--op15km-geo", required=True, type=Path)
    ap.add_argument("--op15km-namelist", required=True, type=Path)
    ap.add_argument("--prod4km-geo", required=True, type=Path)
    ap.add_argument("--prod4km-namelist", required=True, type=Path)
    ap.add_argument("--prod4km-csv", required=True, type=Path)
    ap.add_argument("--out-csv", required=True, type=Path)
    ap.add_argument("--out-meta", required=True, type=Path)
    args = ap.parse_args()

    est = json.loads(args.estaciones.read_text())
    tesis, tesis_meta = extract(args.tesis_geo, est)
    op15, op15_meta = extract(args.op15km_geo, est)
    prod4, prod4_meta = extract(args.prod4km_geo, est)

    with args.prod4km_csv.open(newline="") as fh:
        prod4_prev = {row["estacion"]: row for row in csv.DictReader(fh)}

    rows = []
    for name, info in est.items():
        p = prod4_prev[name]
        hgt_prod_vec = float(p["hgt_modelo_vecino_m"])
        hgt_prod_int = float(p["hgt_modelo_interp_m"])
        rows.append(
            {
                "estacion": name,
                "elev_real_m": info["elev"],
                "HGT_tesis15": round(tesis[name]["hgt_interp"], 1),
                "HGT_op15km": round(op15[name]["hgt_interp"], 1),
                "HGT_prod4km": round(hgt_prod_int, 1),
                "HGT_tesis15_vecino": round(tesis[name]["hgt_vecino"], 1),
                "HGT_tesis15_interp": round(tesis[name]["hgt_interp"], 1),
                "HGT_op15km_vecino": round(op15[name]["hgt_vecino"], 1),
                "HGT_op15km_interp": round(op15[name]["hgt_interp"], 1),
                "HGT_prod4km_vecino": round(hgt_prod_vec, 1),
                "HGT_prod4km_interp": round(hgt_prod_int, 1),
                "delta_tesis15_vecino": round(tesis[name]["hgt_vecino"] - info["elev"], 1),
                "delta_tesis15_interp": round(tesis[name]["hgt_interp"] - info["elev"], 1),
                "delta_op15km_vecino": round(op15[name]["hgt_vecino"] - info["elev"], 1),
                "delta_op15km_interp": round(op15[name]["hgt_interp"] - info["elev"], 1),
                "delta_prod4km_vecino": round(hgt_prod_vec - info["elev"], 1),
                "delta_prod4km_interp": round(hgt_prod_int - info["elev"], 1),
            }
        )

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    meta = {
        "metodo": {
            "vecino": "celda mas cercana en lat/lon (distancia euclidiana local)",
            "interp": "scipy.interpolate.griddata(method='linear'), mismo metodo del PASO5 prod4km",
            "columnas_HGT": "HGT_<grilla> = valor interpolado; HGT_<grilla>_vecino/_interp explicitos",
            "deltas": "HGT_modelo - elev_real_m",
        },
        "prod4km_copiado_de": str(args.prod4km_csv),
        "prod4km_csv_sha256": sha256(args.prod4km_csv),
        "estaciones_json": str(args.estaciones),
        "estaciones_sha256": sha256(args.estaciones),
        "grillas": {
            "tesis15": {
                "geo_em": str(args.tesis_geo),
                "geo_em_sha256": sha256(args.tesis_geo),
                "namelist_wps": str(args.tesis_namelist),
                "namelist_wps_sha256": sha256(args.tesis_namelist),
                "config": "15 km Mercator geog lowres",
                "regenerado": False,
                "attrs": tesis_meta,
                "estaciones": tesis,
            },
            "op15km": {
                "geo_em": str(args.op15km_geo),
                "geo_em_sha256": sha256(args.op15km_geo),
                "namelist_wps": str(args.op15km_namelist),
                "namelist_wps_sha256": sha256(args.op15km_namelist),
                "config": "15 km Lambert -31.53/-68.53 geog default",
                "regenerado": False,
                "attrs": op15_meta,
                "estaciones": op15,
            },
            "prod4km": {
                "geo_em": str(args.prod4km_geo),
                "geo_em_sha256": sha256(args.prod4km_geo),
                "namelist_wps": str(args.prod4km_namelist),
                "namelist_wps_sha256": sha256(args.prod4km_namelist),
                "config": "4 km Lambert -31.121/-69.433",
                "regenerado": False,
                "attrs": prod4_meta,
                "estaciones": prod4,
            },
        },
    }
    args.out_meta.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(rows, indent=2, ensure_ascii=False))
    print(f"OK -> {args.out_csv}")
    print(f"OK -> {args.out_meta}")


if __name__ == "__main__":
    main()
