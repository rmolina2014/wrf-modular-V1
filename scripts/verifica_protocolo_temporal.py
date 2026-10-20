#!/usr/bin/env python3
"""Verifica que una corrida cumple el protocolo temporal (ventana de asimilacion + pronostico libre).

Uso:
  python scripts/verifica_protocolo_temporal.py --case-dir outputs/runs/<fecha_ciclo>/<caso> \
      --t0 2026-07-31_00:00:00 [--asim-hours 12] [--horizon 24] \
      [--wrfout-nudged DIR] [--wrfout-control DIR]

Chequeos (todos deben dar OK):
  T1 inicio de la corrida = t0 - asim_hours
  T2 run_hours = asim_hours + horizon
  T3 fdda_end (nudged) = asim_hours*60 y obs_nudge_opt = 1
  T4 control: obs_nudge_opt = 0 y el resto del namelist identico al nudged
  T5 coeficientes iguales a 0.0001
  T6 OBS_DOMAIN101: estructura de 5 lineas por registro, orden cronologico
  T7 OBS_DOMAIN101: ninguna observacion posterior a t0 (separacion temporal)
  T8 OBS_DOMAIN101: ninguna observacion anterior al inicio de la corrida
  T9 (opcional) cantidad de wrfout = asim_hours + horizon + 1 en nudged y control
Sale con codigo 1 si algun chequeo falla.
"""
import argparse, re, sys
from datetime import datetime, timedelta
from pathlib import Path

def leer_namelist(p):
    return Path(p).read_text(encoding="utf-8")

def val(txt, clave):
    m = re.search(rf"^\s*{re.escape(clave)}\s*=\s*([^,\n!]+)", txt, flags=re.M)
    return m.group(1).strip() if m else None

def norm_sin_nudge(txt):
    out = []
    for l in txt.splitlines():
        l = re.sub(r"\s+", " ", l.strip())
        if not l or l.startswith("!"):
            continue
        if re.match(r"obs_nudge_opt\b", l):
            continue
        out.append(l)
    return out

def parsear_obs(path):
    L = [l.rstrip("\n") for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    return L

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-dir", required=True)
    ap.add_argument("--t0", required=True, help="YYYY-MM-DD_HH:MM:SS (UTC)")
    ap.add_argument("--asim-hours", type=int, default=12)
    ap.add_argument("--horizon", type=int, default=24)
    ap.add_argument("--coef", type=float, default=0.0001)
    ap.add_argument("--wrfout-nudged", default=None)
    ap.add_argument("--wrfout-control", default=None)
    a = ap.parse_args()

    cd = Path(a.case_dir)
    t0 = datetime.strptime(a.t0, "%Y-%m-%d_%H:%M:%S")
    ini = t0 - timedelta(hours=a.asim_hours)
    res = []
    def r(id_, desc, ok, det=""):
        res.append((id_, desc, bool(ok), det))

    nn = leer_namelist(cd / "namelist_nudged.input")
    nc = leer_namelist(cd / "namelist_control.input")

    try:
        s = datetime(int(val(nn, "start_year")), int(val(nn, "start_month")), int(val(nn, "start_day")), int(val(nn, "start_hour")))
        r("T1", "inicio = t0 - ventana", s == ini, f"start={s} esperado={ini}")
    except Exception as e:
        r("T1", "inicio = t0 - ventana", False, str(e))
    rh = val(nn, "run_hours")
    r("T2", "run_hours = ventana + horizonte", rh is not None and int(float(rh)) == a.asim_hours + a.horizon,
      f"run_hours={rh} esperado={a.asim_hours + a.horizon}")
    fe = val(nn, "fdda_end"); on = val(nn, "obs_nudge_opt")
    r("T3", "fdda_end = ventana*60 y obs_nudge_opt=1", fe is not None and int(float(fe)) == a.asim_hours * 60 and on == "1",
      f"fdda_end={fe} esperado={a.asim_hours*60}; obs_nudge_opt={on}")
    r("T4", "control = nudged salvo obs_nudge_opt", val(nc, "obs_nudge_opt") == "0" and norm_sin_nudge(nn) == norm_sin_nudge(nc),
      f"obs_nudge_opt control={val(nc,'obs_nudge_opt')}")
    cs = [val(nn, k) for k in ("obs_coef_wind", "obs_coef_temp", "obs_coef_mois")]
    r("T5", f"coeficientes = {a.coef}", all(c is not None and abs(float(c) - a.coef) < 1e-12 for c in cs), f"{cs}")

    obs = parsear_obs(cd / "input" / "OBS_DOMAIN101")
    est = len(obs) % 5 == 0
    ts = [obs[i] .strip()[:14] for i in range(0, len(obs), 5)] if est else []
    r("T6", "OBS_DOMAIN101: 5 lineas/registro y orden cronologico", est and ts == sorted(ts), f"registros={len(ts)}")
    if ts:
        tmax = datetime.strptime(max(ts), "%Y%m%d%H%M%S"); tmin = datetime.strptime(min(ts), "%Y%m%d%H%M%S")
        r("T7", "ninguna obs posterior a t0", tmax <= t0, f"ultima={tmax} t0={t0}")
        r("T8", "ninguna obs anterior al inicio", tmin >= ini, f"primera={tmin} inicio={ini}")
    else:
        r("T7", "ninguna obs posterior a t0", False, "sin registros"); r("T8", "ninguna obs anterior al inicio", False, "sin registros")

    esperado = a.asim_hours + a.horizon + 1
    for etq, d in (("nudged", a.wrfout_nudged), ("control", a.wrfout_control)):
        if d:
            n = len(list(Path(d).glob("wrfout_d01*")))
            r("T9", f"wrfout {etq} = {esperado}", n == esperado, f"encontrados={n}")

    ok_all = True
    for id_, desc, ok, det in res:
        print(f"[{'OK ' if ok else 'FALLA'}] {id_} {desc} | {det}")
        ok_all &= ok
    print("RESULTADO:", "PROTOCOLO CUMPLIDO" if ok_all else "NO CUMPLE")
    sys.exit(0 if ok_all else 1)

if __name__ == "__main__":
    main()
