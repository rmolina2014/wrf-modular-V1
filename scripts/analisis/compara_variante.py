"""Compara una variante experimental contra la corrida oficial del mismo caso.

Uso: python scripts/analisis/compara_variante.py <dir_oficial> <dir_variante>
Usa errores_largo.csv de ambos. Informa: (1) si el control de la variante es identico al oficial
(debe serlo: el control no usa nudging); (2) en que horizontes difiere el nudged; (3) RMSE por
tramo de control, nudged oficial y nudged de la variante, con la Mejora (%) de cada uno."""
import sys
import numpy as np
import pandas as pd

TRAMOS = {"+1-6h": (1, 6), "+7-12h": (7, 12), "+13-18h": (13, 18), "+19-24h": (19, 24), "+1-24h": (1, 24)}


def rmse(x, y):
    return float(np.sqrt(((x - y) ** 2).mean()))


def main(a, b):
    o = pd.read_csv(f"{a}/errores_largo.csv")
    v = pd.read_csv(f"{b}/errores_largo.csv")
    k = ["hora", "horizonte_h", "estacion", "variable"]
    m = o.merge(v, on=k, suffixes=("_o", "_v")).dropna(
        subset=["obs_o", "nudged_o", "nudged_v", "control_o", "control_v"])
    print(f"Pares comparados: {len(m)} (oficial {len(o)}, variante {len(v)})")
    dc = (m.control_o - m.control_v).abs().max()
    print(f"1) max |control oficial - control variante| = {dc:.3e} -> {'IDENTICO' if dc == 0 else 'DIFIERE'}")
    m["dn"] = (m.nudged_o - m.nudged_v).abs()
    print("2) max |nudged oficial - nudged variante| por horizonte:")
    print(m.groupby("horizonte_h").dn.max().to_string())
    print("3) RMSE por variable y tramo; Mejora % = (RMSE_C - RMSE_N)/RMSE_C*100:")
    rows = []
    for var, g in m.groupby("variable"):
        for t, (h0, h1) in TRAMOS.items():
            s = g[(g.horizonte_h >= h0) & (g.horizonte_h <= h1)]
            if s.empty:
                continue
            rc, ro, rv = rmse(s.control_o, s.obs_o), rmse(s.nudged_o, s.obs_o), rmse(s.nudged_v, s.obs_o)
            rows.append(dict(variable=var, tramo=t, n=len(s), rmse_control=rc, rmse_nudged_oficial=ro,
                             rmse_nudged_variante=rv, mejora_oficial_pct=100 * (rc - ro) / rc,
                             mejora_variante_pct=100 * (rc - rv) / rc))
    R = pd.DataFrame(rows)
    print(R.round(3).to_string(index=False))
    R.to_csv(f"{b}/comparacion_con_oficial.csv", index=False)
    print(f"Guardado: {b}/comparacion_con_oficial.csv")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
