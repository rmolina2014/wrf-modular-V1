"""Comprueba en el log de WRF hasta cuando actuo el nudging (guia de Reen, 2016).

Uso: python scripts/analisis/revisa_rsl_nudging.py <dir_del_caso>
Lee <dir>/namelist_nudged.input y <dir>/rsl_nudged.out.0000 o <dir>/wrf_nudged.log (copiados por pipeline_wrf.py).
Con obs_ipf_nudob = .true. WRF imprime 'OBS NUDGING FOR IN,J,KTAU,XTIME,...' mientras el
nudging esta activo; si hay lineas con XTIME > fdda_end, siguio actuando despues del fin previsto.
Salida: 0 = sin nudging despues de fdda_end; 1 = hay nudging posterior; 2 = sin diagnostico."""
import re
import sys
from pathlib import Path


def main(d):
    d = Path(d)
    nl = (d / "namelist_nudged.input").read_text(encoding="utf8")

    def val(p):
        m = re.search(rf"\b{p}\s*=\s*([^,\n]+)", nl)
        return m.group(1).strip() if m else None

    fdda_end = float(val("fdda_end"))
    print(f"fdda_end={fdda_end:g} min | obs_idynin={val('obs_idynin') or '(no fijado)'} | "
          f"obs_dtramp={val('obs_dtramp') or '(no fijado)'} | obs_ipf_nudob={val('obs_ipf_nudob') or '(no fijado)'}")
    # Con wrf.exe serial/OpenMP no se generan rsl.*: la salida queda en wrf_nudged.log
    rsl = next((d / f for f in ("rsl_nudged.out.0000", "wrf_nudged.log") if (d / f).exists()), None)
    if rsl is None:
        print("Sin rsl_nudged.out.0000 ni wrf_nudged.log: la corrida no guardo el log.")
        return 2
    print(f"Log analizado: {rsl.name}")
    xs, dyn = [], []
    for l in rsl.read_text(errors="replace").splitlines():
        m = re.search(r"OBS NUDGING FOR IN,J,KTAU,XTIME,IVAR,IPL:\s+\d+\s+\d+\s+\d+\s+([\d.]+)", l)
        if m:
            xs.append(float(m.group(1)))
        if "DYNINOBS" in l:
            dyn.append(l.strip())
    if not xs:
        print("El log no tiene lineas 'OBS NUDGING FOR': obs_ipf_nudob no estaba activo, o el formato "
              "del log difiere. Sin diagnostico (revisar el rsl a mano).")
        return 2
    post = [x for x in xs if x > fdda_end + 1e-6]
    print(f"Lineas de nudging: {len(xs)} | XTIME maximo con nudging: {max(xs):g} min | "
          f"lineas con XTIME > fdda_end: {len(post)}")
    if dyn:
        print("Primera linea DYNINOBS:", dyn[0])
    if post:
        print(f"RESULTADO: el nudging siguio activo hasta {max(post):g} min (fdda_end={fdda_end:g}).")
        return 1
    print("RESULTADO: el nudging no actuo despues de fdda_end.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
