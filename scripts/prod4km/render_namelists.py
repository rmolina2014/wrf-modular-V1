#!/usr/bin/env python3
"""Renderiza los namelists de WPS/WRF del experimento prod4km (Caso 1).

Fuente EXACTA: plantillas del WRF operativo de San Juan
  /home/pgich/wrf-operativo/datos/namelists/sanjuan/namelistTemp.wps
  /home/pgich/wrf-operativo/datos/namelists/sanjuan/namelistTemp.input
con los valores de /home/pgich/wrf-operativo/ejecutables/sanjuan/env.bash.

Los unicos cambios respecto de la plantilla de produccion son los pedidos en el
protocolo prod4km:
  - fechas/t0-12h, run_hours=36, history_outname a las carpetas de la corrida
  - num_metgrid_levels=34 (la plantilla dice 32; GFS 0.25 usa 34)
  - frames_per_outfile=1 (el validador de la tesis lee un wrfout por hora)
  - brazo nudging: bloque &fdda con obs_nudge_opt=1, fdda_end=720 y auxinput11
El resto de fisica/dinamica queda identico a la plantilla operativa.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

WPS_TEMPLATE = Path("/home/pgich/wrf-operativo/datos/namelists/sanjuan/namelistTemp.wps")
INPUT_TEMPLATE = Path("/home/pgich/wrf-operativo/datos/namelists/sanjuan/namelistTemp.input")

# Valores de /home/pgich/wrf-operativo/ejecutables/sanjuan/env.bash
REF_LAT = "-31.121"
REF_LON = "-69.433"
TRUELAT1 = "-31.121"
TRUELAT2 = "-31.121"
STAND_LON = "-69.433"
WPS_GEOG = "/home/pgich/wrf-operativo/datos/WPS_GEOG"

# Defaults = Caso 1 (t0=2026-07-31 00:00 UTC, arranque t0-12 h, 36 h).
DEFAULT_START = "2026-07-30_12:00:00"
DEFAULT_END = "2026-08-01_00:00:00"
DEFAULT_RUN_HOURS = 36

FDDA_NUDGED = """ &fdda
 grid_fdda                           = 0,
 obs_nudge_opt                       = 1,
 obs_nudge_wind                      = 1,
 obs_nudge_temp                      = 1,
 obs_nudge_mois                      = 1,
 obs_no_pbl_nudge_uv                 = 0,
 obs_no_pbl_nudge_t                  = 0,
 obs_no_pbl_nudge_q                  = 0,
 obs_coef_wind                       = 0.0001,
 obs_coef_temp                       = 0.0001,
 obs_coef_mois                       = 0.0001,
 obs_rinxy                           = 50.0,
 obs_sfcfacr                         = 2.0,
 obs_twindo                          = 1.0,
 obs_sfcfact                         = 1.0,
 obs_ionf                            = 1,
 obs_npfi                            = 30,
 obs_ipf_in4dob                      = .true.,
 max_obs                             = 10000,
 obs_prt_max                         = 100,
 fdda_end                            = 720,
 gfdda_inname                        = "wrffdda_d<domain>",
 gfdda_interval_m                    = 360,
 gfdda_end_h                         = 36,
 io_form_gfdda                       = 2,
 fgdt                                = 0,
 /
"""


def parse_date(value: str) -> tuple[str, str, str, str, str, str]:
    date, clock = value.split("_")
    year, month, day = date.split("-")
    hour, minute, second = clock.split(":")
    return year, month, day, hour, minute, second


def render_wps(template: str, *, start: str, end: str) -> str:
    c = template
    c = c.replace("START_DATE", start)
    c = c.replace("END_DATE", end)
    c = c.replace("REF_LAT", REF_LAT)
    c = c.replace("REF_LON", REF_LON)
    c = c.replace("TRUELAT1", TRUELAT1)
    c = c.replace("TRUELAT2", TRUELAT2)
    c = c.replace("STAND_LON", STAND_LON)
    c = c.replace("RUTA_GEOG_DATA", WPS_GEOG)
    if "START_DATE" in c or "REF_LAT" in c or "RUTA_GEOG_DATA" in c:
        raise RuntimeError("Quedaron marcadores sin reemplazar en namelist.wps")
    return c


def render_input(
    template: str,
    *,
    start: str,
    end: str,
    run_hours: int,
    nudged: bool,
    history_outname: str,
) -> str:
    c = template
    c = c.replace("RUN_HOURS", str(run_hours))
    for key, val in zip(
        (
            "START_YEAR",
            "START_MONTH",
            "START_DAY",
            "START_HOUR",
            "START_MINUTE",
            "START_SECOND",
        ),
        parse_date(start),
    ):
        c = c.replace(key, val)
    for key, val in zip(
        ("END_YEAR", "END_MONTH", "END_DAY", "END_HOUR", "END_MINUTE", "END_SECOND"),
        parse_date(end),
    ):
        c = c.replace(key, val)
    c = c.replace("HISTORY_OUTNAME", history_outname)

    # Unica diferencia declarada con la plantilla en los niveles de metgrid.
    c = re.sub(r"(num_metgrid_levels\s*=\s*)32", r"\g<1>34", c)
    # La evaluacion de la tesis necesita un wrfout por hora.
    c = re.sub(
        r"(frames_per_outfile\s*=\s*)\d+,\s*\d+,\s*\d+",
        r"\g<1>1, 1, 1",
        c,
    )

    if nudged:
        # El nudging observacional necesita leer OBS_DOMAIN101.
        c = c.replace(
            " io_form_boundary                    = 2\n",
            " io_form_boundary                    = 2\n"
            " auxinput11_interval_m               = 30,\n"
            ' auxinput11_inname                   = "OBS_DOMAIN101",\n',
            1,
        )
        c = re.sub(r" &fdda\s*\n\s*/\s*\n", FDDA_NUDGED, c, count=1)
    # control: se deja el &fdda vacio de la plantilla operativa.

    for marker in ("START_YEAR", "END_YEAR", "RUN_HOURS", "HISTORY_OUTNAME"):
        if marker in c:
            raise RuntimeError(f"Quedo el marcador {marker} en namelist.input")
    return c


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-dir", required=True, type=Path)
    ap.add_argument("--start", default=DEFAULT_START)
    ap.add_argument("--end", default=DEFAULT_END)
    ap.add_argument("--run-hours", default=DEFAULT_RUN_HOURS, type=int)
    args = ap.parse_args()
    case = args.case_dir.resolve()
    (case / "wps").mkdir(parents=True, exist_ok=True)

    wps_text = render_wps(
        WPS_TEMPLATE.read_text(encoding="utf-8"), start=args.start, end=args.end
    )
    (case / "wps" / "namelist.wps").write_text(wps_text, encoding="utf-8")

    tpl = INPUT_TEMPLATE.read_text(encoding="utf-8")
    control = render_input(
        tpl,
        start=args.start,
        end=args.end,
        run_hours=args.run_hours,
        nudged=False,
        history_outname=str(case / "control" / "wrfout_d<domain>_<date>"),
    )
    nudged = render_input(
        tpl,
        start=args.start,
        end=args.end,
        run_hours=args.run_hours,
        nudged=True,
        history_outname=str(case / "nudged" / "wrfout_d<domain>_<date>"),
    )
    (case / "namelist_control.input").write_text(control, encoding="utf-8")
    (case / "namelist_nudged.input").write_text(nudged, encoding="utf-8")
    print(f"OK: {case/'wps'/'namelist.wps'}")
    print(f"OK: {case/'namelist_control.input'}")
    print(f"OK: {case/'namelist_nudged.input'}")


if __name__ == "__main__":
    main()
