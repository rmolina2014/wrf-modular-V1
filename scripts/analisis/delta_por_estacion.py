"""RMSE, dRMSE y Mejora (%) por estacion y por grupo de error de altura (+1 a +24 h, 4 casos).

Responde: la mejora del nudging depende del error de altura estacion-grilla? No requiere nuevas
corridas: usa errores_largo.csv de los cuatro casos oficiales.
dRMSE = RMSE_C - RMSE_N ; Mejora = dRMSE / RMSE_C * 100.
IC95: bootstrap pareado por bloques circulares de 6 horizontes (B=2000, semilla 42), remuestreando
cada caso por separado, igual que calc_delta.py. Los IC recogen la variabilidad horaria dentro de
cada dia, no la variabilidad entre dias ni eventos.
Error de altura (grilla - real, m): Tabla 5.3 de la tesis. Grupos fijados antes de mirar resultados
por estacion: |dh| <= 200 m ('bajo') y > 200 m ('alto')."""
import numpy as np, pandas as pd
from pathlib import Path
BASE = Path(__file__).resolve().parents[2]
ROOT = BASE / "outputs" / "runs"
CASOS = {"1 Zonda": "2026-07-31_0000z/caso1_zonda", "2 Calor": "2026-01-01_0000z/caso2_calor",
         "3 Frente frio": "2026-05-16_0000z/caso3_frentefrio", "4 San Juan 24/09": "2026-09-24_0000z/sanjuan_0924"}
DH = {"ECOHUMUS": -1, "VALLE_FERTIL": 135, "ULLUM_EMBALSE": 149, "INTA_POCITO": 194,
      "INTA_SANMARTIN": 308, "CUESTA_Viento": 387, "PUNTA_NEGRA": 507, "CARACOLES": 970}
UMBRAL = 200
VARS = ["t2", "rh", "wspd", "psfc"]
B, L = 2000, 6
rng = np.random.default_rng(42)

def cargar():
    d = {}
    for c, p in CASOS.items():
        e = pd.read_csv(ROOT / p / "errores_largo.csv").dropna(subset=["obs", "nudged", "control"])
        e["eN2"] = (e.nudged - e.obs) ** 2; e["eC2"] = (e.control - e.obs) ** 2
        d[c] = e
    return d

def tabla(e):
    g = e.groupby("horizonte_h").agg(n=("obs", "size"), sN=("eN2", "sum"), sC=("eC2", "sum"))
    return g.reindex(range(1, 25), fill_value=0)

def resumen(tabs):
    n = sum(t.n.sum() for t in tabs)
    if n == 0: return None
    sN = sum(t.sN.sum() for t in tabs); sC = sum(t.sC.sum() for t in tabs)
    rN, rC = np.sqrt(sN / n), np.sqrt(sC / n)
    dN = np.zeros(B); dC = np.zeros(B); nn = np.zeros(B)
    for t in tabs:
        if t.n.sum() == 0: continue
        k = len(t); nb = int(np.ceil(k / L))
        idx = ((rng.integers(0, k, size=(B, nb))[:, :, None] + np.arange(L)[None, None, :]) % k).reshape(B, -1)[:, :k]
        dN += t.sN.values[idx].sum(1); dC += t.sC.values[idx].sum(1); nn += t.n.values[idx].sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        m = 100 * (np.sqrt(dC / nn) - np.sqrt(dN / nn)) / np.sqrt(dC / nn)
    m = m[np.isfinite(m)]
    lo, hi = np.percentile(m, [2.5, 97.5])
    return dict(n=int(n), rmse_C=rC, rmse_N=rN, dRMSE=rC - rN, mejora_pct=100 * (rC - rN) / rC, mejora_lo=lo, mejora_hi=hi)

datos = cargar(); rows = []
for v in VARS:
    for s in DH:
        tabs = [tabla(e[(e.variable == v) & (e.estacion == s)]) for e in datos.values()]
        casos_con = sum(t.n.sum() > 0 for t in tabs)
        r = resumen(tabs)
        if r: rows.append(dict(nivel="estacion", unidad=s, dh_m=DH[s], variable=v, casos=casos_con, **r))
    for g, cond in (("bajo (|dh|<=200 m)", lambda s: abs(DH[s]) <= UMBRAL), ("alto (|dh|>200 m)", lambda s: abs(DH[s]) > UMBRAL)):
        tabs = [tabla(e[(e.variable == v) & (e.estacion.map(lambda s: cond(s) if s in DH else False))]) for e in datos.values()]
        r = resumen(tabs)
        if r: rows.append(dict(nivel="grupo", unidad=g, dh_m=np.nan, variable=v, casos=4, **r))
R = pd.DataFrame(rows)
out = BASE / "outputs" / "analisis"; out.mkdir(parents=True, exist_ok=True)
R.to_csv(out / "delta_por_estacion.csv", index=False)
pd.set_option("display.width", 200)
for v in VARS:
    s = R[R.variable == v].copy()
    print(f"\n=== {v} (+1 a +24 h, 4 casos) ===")
    print(s[["nivel", "unidad", "dh_m", "casos", "n", "rmse_C", "rmse_N", "mejora_pct", "mejora_lo", "mejora_hi"]].round(2).to_string(index=False))
    e = s[(s.nivel == "estacion") & (s.n >= 20)]
    if len(e) >= 4:
        rho = e.dh_m.rank().corr(e.mejora_pct.rank())
        print(f"Correlacion de rangos (Spearman) dh vs mejora, {len(e)} estaciones: {rho:+.2f}")
