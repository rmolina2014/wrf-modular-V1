"""Calcula RMSE, dRMSE y Mejora(%) con IC95 por bootstrap por bloques de horizontes (pareado).

Unidad de remuestreo: el horizonte (todas las estaciones de esa hora juntas), para respetar la
dependencia entre estaciones y entre horas consecutivas. Bloques circulares de L horizontes
(L=6 para las 24 h; L=3 dentro de un tramo de 6 h). B=2000, semilla 42.
dRMSE = RMSE_C - RMSE_N ; Mejora = dRMSE / RMSE_C * 100. Percentiles 2.5 y 97.5."""
import numpy as np, pandas as pd, json, sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
ROOT=str(BASE/"outputs"/"runs")+"/"
CASOS={"1 Zonda":"2026-07-31_0000z/caso1_zonda","2 Calor":"2026-01-01_0000z/caso2_calor",
       "3 Frente frío":"2026-05-16_0000z/caso3_frentefrio","4 San Juan 24/09":"2026-09-24_0000z/sanjuan_0924"}
TRAMOS={"+1-6h":range(1,7),"+7-12h":range(7,13),"+13-18h":range(13,19),"+19-24h":range(19,25),"+1-24h":range(1,25)}
VARS=["t2","rh","psfc","wspd"]
B=2000; rng=np.random.default_rng(42)

def cargar(path):
    e=pd.read_csv(path)
    e=e.dropna(subset=["obs","nudged","control"])
    e["eN"]=e.nudged-e.obs; e["eC"]=e.control-e.obs
    return e

def tabla_por_horizonte(e,var):
    s=e[e.variable==var].groupby("horizonte_h").agg(n=("obs","size"),sN=("eN",lambda x:(x**2).sum()),sC=("eC",lambda x:(x**2).sum()))
    return s.reindex(range(1,25),fill_value=0)

def bloques(hs,L,nrep):
    """índices de horizontes remuestreados con bloques circulares de longitud L (nrep remuestreos)."""
    k=len(hs); nb=int(np.ceil(k/L))
    starts=rng.integers(0,k,size=(nrep,nb))
    idx=(starts[:,:,None]+np.arange(L)[None,None,:])%k
    return idx.reshape(nrep,-1)[:,:k]

def est(sN,sC,n):
    N=n.sum()
    if N==0: return np.nan,np.nan
    return np.sqrt(sN.sum()/N),np.sqrt(sC.sum()/N)

def ic(hs_tabs,L):
    """hs_tabs: lista de DataFrames (un caso cada uno) ya recortados al tramo; remuestrea cada caso por separado."""
    dN=np.zeros(B);dC=np.zeros(B);nn=np.zeros(B)
    for t in hs_tabs:
        idx=bloques(t.index.values,L,B)
        sN=t.sN.values[idx].sum(1); sC=t.sC.values[idx].sum(1); n=t.n.values[idx].sum(1)
        dN+=sN; dC+=sC; nn+=n
    with np.errstate(invalid="ignore",divide="ignore"):
        rN=np.sqrt(dN/nn); rC=np.sqrt(dC/nn)
    d=rC-rN; m=100*d/rC
    ok=np.isfinite(d)
    return np.percentile(d[ok],[2.5,97.5]),np.percentile(m[ok],[2.5,97.5])

def fila(tabs,var,tr,caso):
    L=6 if tr=="+1-24h" else 3
    rec=[t.loc[list(TRAMOS[tr])] for t in tabs]
    n=sum(t.n.sum() for t in rec); sN=sum(t.sN.sum() for t in rec); sC=sum(t.sC.sum() for t in rec)
    if n==0: return None
    rN=np.sqrt(sN/n); rC=np.sqrt(sC/n); d=rC-rN
    (dl,dh),(ml,mh)=ic(rec,L)
    return dict(caso=caso,variable=var,tramo=tr,n=int(n),rmse_N=rN,rmse_C=rC,dRMSE=d,dRMSE_lo=dl,dRMSE_hi=dh,
                mejora_pct=100*d/rC,mejora_lo=ml,mejora_hi=mh,sig=("mejora" if dl>0 else "degrada" if dh<0 else "n.s."))

rows=[]; cobertura=[]
datos={c:cargar(ROOT+p+"/errores_largo.csv") for c,p in CASOS.items()}
tabs={(c,v):tabla_por_horizonte(e,v) for c,e in datos.items() for v in VARS}
for c,e in datos.items():
    for v in VARS:
        for tr in TRAMOS:
            r=fila([tabs[(c,v)]],v,tr,c)
            if r: rows.append(r)
    for (s,v),g in e.groupby(["estacion","variable"]):
        cobertura.append(dict(caso=c,estacion=s,variable=v,horas=int(g.horizonte_h.nunique()),pares=len(g)))
for v in VARS:
    for tr in TRAMOS:
        r=fila([tabs[(c,v)] for c in CASOS],v,tr,"Conjunto (4 casos)")
        if r: rows.append(r)
R=pd.DataFrame(rows)
# IC solo para el agregado +1-24 h: 6 horizontes por tramo son pocos para un bootstrap por bloques
m=R.tramo!="+1-24h"
R.loc[m,["dRMSE_lo","dRMSE_hi","mejora_lo","mejora_hi"]]=np.nan
R.loc[m,"sig"]="sin IC (6 horizontes)"
R.to_csv(str(BASE/"outputs"/"analisis"/"delta_rmse_ic.csv"),index=False)
pd.DataFrame(cobertura).to_csv(str(BASE/"outputs"/"analisis"/"cobertura_eval.csv"),index=False)
print(len(R),"filas")
E=lambda x:f"{x:+.2f}"
for v in VARS:
    print("\n== ",v)
    sub=R[(R.variable==v)&(R.tramo.isin(["+1-6h","+7-12h","+13-18h","+19-24h","+1-24h"]))]
    for c in list(CASOS)+["Conjunto (4 casos)"]:
        s=sub[sub.caso==c].set_index("tramo")
        print(f"{c:20s}", " | ".join(f"{t}: {s.loc[t,'mejora_pct']:+5.1f}% [{s.loc[t,'mejora_lo']:+5.1f},{s.loc[t,'mejora_hi']:+5.1f}] {s.loc[t,'sig'][:3]}" for t in s.index))
