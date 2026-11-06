#!/usr/bin/env python3
"""PASO 5: altura del terreno del modelo vs altura real de cada estacion."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from netCDF4 import Dataset
from scipy.interpolate import griddata


def haversine(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--geo", required=True, type=Path)
    ap.add_argument("--estaciones", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    ds = Dataset(args.geo)
    hgt = np.asarray(ds.variables["HGT_M"][0])
    lat = np.asarray(ds.variables["XLAT_M"][0])
    lon = np.asarray(ds.variables["XLONG_M"][0])
    est = json.loads(args.estaciones.read_text())

    rows = []
    for name, info in est.items():
        d2 = (lat - info["lat"]) ** 2 + ((lon - info["lon"]) * math.cos(math.radians(info["lat"]))) ** 2
        j, i = np.unravel_index(np.argmin(d2), d2.shape)
        dist = haversine(info["lat"], info["lon"], float(lat[j, i]), float(lon[j, i]))
        hb = float(
            griddata(
                (lat.ravel(), lon.ravel()),
                hgt.ravel(),
                (info["lat"], info["lon"]),
                method="linear",
            )
        )
        rows.append(
            {
                "estacion": name,
                "rol": info["rol"],
                "lat_real": info["lat"],
                "lon_real": info["lon"],
                "elev_real_m": info["elev"],
                "i_vecino": int(i),
                "j_vecino": int(j),
                "lat_modelo": round(float(lat[j, i]), 5),
                "lon_modelo": round(float(lon[j, i]), 5),
                "dist_vecino_m": round(dist, 1),
                "hgt_modelo_vecino_m": round(float(hgt[j, i]), 1),
                "delta_vecino_m": round(float(hgt[j, i]) - info["elev"], 1),
                "hgt_modelo_interp_m": round(hb, 1),
                "delta_interp_m": round(hb - info["elev"], 1),
                "brazos": "control y nudged (misma geo_em.d01)",
            }
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(rows, indent=2, ensure_ascii=False))
    print(f"OK -> {args.out}")


if __name__ == "__main__":
    main()
