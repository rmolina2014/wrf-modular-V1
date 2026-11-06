#!/usr/bin/env python3
"""Verifica que los namelists renderizados tengan la configuracion pedida."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

EXPECTED = {
    "run_hours": 36,
    "start_year": 2026,
    "start_month": 7,
    "start_day": 30,
    "start_hour": 12,
    "start_minute": 0,
    "start_second": 0,
    "end_year": 2026,
    "end_month": 8,
    "end_day": 1,
    "end_hour": 0,
    "end_minute": 0,
    "end_second": 0,
    "interval_seconds": 10800,
    "history_interval": 60,
    "frames_per_outfile": 1,
    "time_step": 15,
    "max_dom": 1,
    "e_we": 141,
    "e_sn": 200,
    "e_vert": 35,
    "p_top_requested": 5000,
    "num_metgrid_levels": 34,
    "num_metgrid_soil_levels": 4,
    "dx": 4000,
    "dy": 4000,
    "mp_physics": 8,
    "ra_lw_physics": 1,
    "ra_sw_physics": 2,
    "radt": 4,
    "sf_sfclay_physics": 2,
    "sf_surface_physics": 2,
    "bl_pbl_physics": 2,
    "bldt": 0,
    "cu_physics": 0,
    "cudt": 5,
    "isfflx": 1,
    "ifsnow": 1,
    "icloud": 1,
    "surface_input_source": 1,
    "num_soil_layers": 4,
    "num_land_cat": 21,
    "sf_urban_physics": 0,
    "w_damping": 0,
    "diff_opt": 1,
    "km_opt": 4,
    "diff_6th_opt": 0,
    "damp_opt": 0,
    "khdif": 0,
    "kvdif": 0,
    "non_hydrostatic": True,
    "moist_adv_opt": 1,
    "scalar_adv_opt": 1,
    "spec_bdy_width": 5,
    "spec_zone": 1,
    "relax_zone": 4,
    "specified": True,
    "nested": False,
}

NUDGED = {
    "obs_nudge_opt": 1,
    "obs_nudge_wind": 1,
    "obs_nudge_temp": 1,
    "obs_nudge_mois": 1,
    "obs_coef_wind": 0.0001,
    "obs_coef_temp": 0.0001,
    "obs_coef_mois": 0.0001,
    "obs_rinxy": 50.0,
    "obs_sfcfacr": 2.0,
    "fdda_end": 720,
    "auxinput11_interval_m": 30,
    "auxinput11_inname": "OBS_DOMAIN101",
}


def parse_value(raw: str):
    raw = raw.split(",")[0].strip()
    if raw.startswith(("'", '"')):
        return raw.strip("'\"")
    low = raw.lower()
    if low in (".true.", "true"):
        return True
    if low in (".false.", "false"):
        return False
    try:
        return int(raw)
    except ValueError:
        return float(raw)


def parse_namelist(path: Path) -> dict:
    text = "\n".join(line.split("!")[0] for line in path.read_text().splitlines())
    out = {}
    for key in re.findall(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=", text, flags=re.M):
        m = re.search(rf"^\s*{re.escape(key)}\s*=\s*(.+)$", text, flags=re.M)
        if m:
            out[key] = parse_value(m.group(1))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-dir", required=True, type=Path)
    args = ap.parse_args()
    case = args.case_dir.resolve()

    all_ok = True
    report = {}
    for arm in ("control", "nudged"):
        vals = parse_namelist(case / f"namelist_{arm}.input")
        expected = dict(EXPECTED)
        if arm == "nudged":
            expected.update(NUDGED)
        mismatches = {}
        for key, exp in expected.items():
            got = vals.get(key, "<ausente>")
            ok = got == exp
            all_ok &= ok
            if not ok:
                mismatches[key] = {"esperado": exp, "obtenido": got}
        if arm == "control" and vals.get("obs_nudge_opt", 0) != 0:
            mismatches["obs_nudge_opt"] = {"esperado": 0, "obtenido": vals["obs_nudge_opt"]}
            all_ok = False
        report[arm] = {"ok": not mismatches, "mismatches": mismatches}

    out = case / "informes" / "namelist_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"Resultado: {'OK' if all_ok else 'FALLA'} -> {out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
