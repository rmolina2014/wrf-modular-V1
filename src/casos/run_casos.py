#!/usr/bin/env python3
"""Fase 4 - Ejecución de casos de estudio WRF (ciclo 00Z->24Z, con/sin obs nudging).

Para cada caso de config/casos_estudio.json:
  1. Descarga histórico EcoWitt del día y mide la cobertura de observaciones.
  2. Si la cobertura es insuficiente -> "NO EJECUTADO - SIN DATOS (causa)".
  3. Descarga GFS 00Z, corre WPS (geogrid+ungrib+metgrid) y copia met_em al run dir.
  4. Corre el pipeline WRF (Little_R -> OBS_DOMAIN101 -> real.exe -> wrf.exe
     nudged/control -> validacion multi-temporal 00/06/12/18/24Z).
  5. Redacta informe .md por caso y un informe consolidado al final.

Uso:
    python -m src.casos.run_casos --dry-run        # solo disponibilidad
    python -m src.casos.run_casos --solo 2         # ejecutar solo el caso 2
    python -m src.casos.run_casos                  # ejecutar todos los casos
    python -m src.casos.run_casos --force          # re-ejecutar aunque existan resultados
"""

import argparse
import shlex
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from src.calidad.cleaner import ObservacionesCleaner
from src.ingesta.ecowitt_client import EcowittIngestor
from src.ingesta.gfs_downloader import GFSDownloader

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_casos")

CONFIG_JSON = Path(os.environ.get(
    "CASOS_JSON",
    ROOT / "config" / ("casos_oficiales.json" if (ROOT / "config" / "casos_oficiales.json").exists()
                       else "casos_estudio.json"),
))
RAW = ROOT / "data" / "raw"
INFORMES = ROOT / "outputs" / "informes" / "oficiales"
ESTADO_DIR = ROOT / "results" / "casos_estudio"
ESTADO_JSON = ESTADO_DIR / "estado_casos.json"
WPS_DIR = ROOT / "wps_sanjuan"
WPS_SH = WPS_DIR / "run_wps_sanjuan.sh"
RUN_DIR = Path(os.environ.get("LOCAL_WRF_DIR", "/home/pgich/wrf-operativo/ejecutables/WRF_casos_24h"))
PYTHON = Path(os.environ.get("PYTHON", sys.executable))
PIPELINE = ROOT / "pipeline_wrf.py"
EXTRA_PIPELINE_ARGS: List[str] = []   # opciones extra para pipeline_wrf.py (modo --variante)
GFS_URLS = {
    "aws": "https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.{fecha}/{ciclo}/atmos/{file}",
    "nomads": "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.{fecha}/{ciclo}/atmos/{file}",
}
PC_PGICH_ENV = {
    "WRF_BASE": "/home/pgich/Build_WRF",
    "WPS_DIR": "/home/pgich/Build_WRF/WPS",
    "WRF_EJECUTABLES": "/home/pgich/wrf-operativo/ejecutables",
    "GEOG_DATA_PATH": "/home/pgich/wrf-operativo/datos/WPS_GEOG",
}


# --------------------------------------------------------------------------
# Configuracion
# --------------------------------------------------------------------------
def _leer_casos(cfg_path: Path = CONFIG_JSON) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg.get("configuracion_comun", {}), cfg.get("casos", [])


def _estado() -> Dict[str, Any]:
    if ESTADO_JSON.exists():
        with open(ESTADO_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _guardar_estado(estado: Dict[str, Any]):
    ESTADO_DIR.mkdir(parents=True, exist_ok=True)
    with open(ESTADO_JSON, "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------
# Observaciones (EcoWitt historico -> obs_flat)
# --------------------------------------------------------------------------
def csv_historico(fecha: str) -> Path:
    fc = fecha.replace("-", "")
    return RAW / f"ecowitt_historico_{fc}.csv"


def csv_caso(fecha: str) -> Path:
    """CSV del caso: fusion de fecha-1 + fecha (dias locales) en hora UTC."""
    fc = fecha.replace("-", "")
    return RAW / f"ecowitt_historico_{fc}_ventana.csv"


def descargar_obs_historico(fecha: str) -> Path:
    """Descarga el historico local de fecha-1 y fecha y los fusiona.

    El dia simulado 00Z-24Z (UTC) de `fecha` abarca desde las 21:00 locales del
    dia anterior hasta las 21:00 locales de `fecha` (ART = UTC-3), por lo que se
    requieren observaciones de ambos dias locales. Devuelve el CSV del caso
    (ecowitt_historico_<fecha>_ventana.csv) con ambos dias fusionados y ordenados
    por `hora_unix` (epoch UTC), que es la fuente de verdad temporal del flujo.
    Los archivos diarios quedan intactos (el merge es idempotente).
    """
    previo = (datetime.strptime(fecha, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    for dia in (previo, fecha):
        csv = csv_historico(dia)
        if csv.exists() and csv.stat().st_size > 100:
            logger.info(f"Historico ya descargado: {csv.name}")
            continue
        logger.info(f"Descargando historico EcoWitt de {dia}...")
        EcowittIngestor().descargar_historico(dia, output_dir=str(RAW))
        if not csv.exists():
            raise RuntimeError(f"No se genero el CSV historico para {dia}")

    csv_prev = csv_historico(previo)
    csv_dia = csv_historico(fecha)
    csv_out = csv_caso(fecha)
    df_prev = pd.read_csv(csv_prev)
    df_dia = pd.read_csv(csv_dia)
    df_merged = pd.concat([df_prev, df_dia], ignore_index=True)
    if "hora_unix" in df_merged.columns:
        df_merged = df_merged.sort_values("hora_unix")
    df_merged.to_csv(csv_out, index=False, encoding="utf-8")
    logger.info(
        f"Fusion {df_prev.shape[0]}+{df_dia.shape[0]} registros -> {csv_out.name}"
    )
    return csv_out


def cobertura_obs(csv_path: Path, fecha: str, ciclo: str = "00", run_hours: int = 12,
                  t0_iso: Optional[str] = None, asim_horas: Optional[int] = None) -> Dict[str, Any]:
    """Mide la cobertura de observaciones validas.

    Sin protocolo temporal: ventana UTC 00Z-<run_hours>Z del dia `fecha`.
    Con protocolo (t0_iso + asim_horas): ventana de asimilacion [t0-asim, t0],
    que es la unica que debe nutrir OBS_DOMAIN101."""
    df = pd.read_csv(csv_path)
    if df.empty or "temp_c" not in df.columns:
        return {"dia": 0, "ventana": 0, "estaciones": 0, "por_estacion": {}}

    ts_dia_ini = int(datetime.strptime(f"{fecha} 00:00:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp())
    ts_dia_fin = ts_dia_ini + 24 * 3600
    if t0_iso and asim_horas:
        t0 = datetime.strptime(t0_iso.replace("Z", ""), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        ts_fin = int(t0.timestamp())
        ts_ini = ts_fin - int(asim_horas) * 3600
    else:
        ts_ini = ts_dia_ini
        ts_fin = ts_ini + int(run_hours) * 3600
    df["ts"] = pd.to_numeric(df["hora_unix"], errors="coerce")
    df["temp_ok"] = df["temp_c"].apply(lambda v: _num(v) is not None and pd.notna(v))

    dia = int((df["temp_ok"] & df["ts"].between(ts_dia_ini, ts_dia_fin)).sum())
    ventana = int((df["temp_ok"] & df["ts"].between(ts_ini, ts_fin)).sum())
    por_estacion = (
        df[df["temp_ok"] & df["ts"].between(ts_ini, ts_fin)]
        .groupby("estacion")["temp_ok"].sum().astype(int).to_dict()
    )
    return {"dia": dia, "ventana": ventana, "estaciones": len(por_estacion), "por_estacion": por_estacion}


def _num(v: Any) -> Optional[float]:
    if v is None or pd.isna(v):
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def generar_obs_flat(csv_path: Path, fecha: str, salida: Optional[Path] = None) -> Path:
    """Convierte el CSV historico (limpio/QC) al JSON obs_flat usado por el pipeline."""
    if salida is None:
        salida = RAW / f"obs_flat_{fecha.replace('-', '')}.json"
    if salida.exists() and salida.stat().st_size > 100:
        if csv_path.stat().st_mtime <= salida.stat().st_mtime:
            logger.info(f"obs_flat ya existe y esta al dia: {salida.name}")
            return salida
        logger.info(f"obs_flat desactualizado (CSV mas nuevo); regenerando: {salida.name}")

    cleaner = ObservacionesCleaner(str(RAW))
    df = cleaner.procesar_csv_historico(str(csv_path))
    df["time_unix"] = df["timestamp"].astype("int64") // 10**9

    filas = []
    hora_ok = df["hora"].astype(str).str.split(":").apply(lambda x: len(x) >= 2)
    for _, r in df[hora_ok].iterrows():
        try:
            horas = str(r["hora"]).split(":")
            hora = f"{int(horas[0]):02d}:{int(horas[1]):02d}:00"
        except (ValueError, TypeError):
            continue
        filas.append({
            "estacion": str(r["estacion"]),
            "time_unix": int(r["time_unix"]),
            "fecha": str(r["fecha"]),
            "hora": hora,
            "temp": _num(r.get("temp")),
            "humedad": _num(r.get("humedad")),
            "viento": _num(r.get("viento")),
            "viento_rafaga": _num(r.get("viento_rafaga")),
            "direcc": _num(r.get("direcc")),
            "presion_relativa": _num(r.get("presion_relativa")),
            "presion_absoluta": _num(r.get("presion_absoluta")),
            "rain_daily": _num(r.get("rain_daily")),
            "solar": _num(r.get("solar")),
        })
    salida.parent.mkdir(parents=True, exist_ok=True)
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(filas, f, indent=1)
    logger.info(f"obs_flat generado: {salida.name} ({len(filas)} registros)")
    return salida


# --------------------------------------------------------------------------
# GFS
# --------------------------------------------------------------------------
def gfs_disponible(fecha: str, ciclo: str = "00", fhour: int = 0) -> Optional[str]:
    """Verifica disponibilidad del artico pgrb2 0.25 en AWS/NOMADS. Devuelve la fuente o None."""
    fstr = f"{fhour:03d}"
    file = f"gfs.t{ciclo}z.pgrb2.0p25.f{fstr}"
    fecha_nodash = fecha.replace("-", "")
    for fuente, tpl in GFS_URLS.items():
        url = tpl.format(fecha=fecha_nodash, ciclo=ciclo, file=file)
        try:
            r = requests.head(url, timeout=30, allow_redirects=True)
            if r.status_code == 200:
                return fuente
        except Exception as e:
            logger.debug(f"HEAD {fuente} fallo: {e}")
    return None


def _tamano_esperado_gfs(fecha: str, ciclo: str, fhour: int) -> Optional[int]:
    """HEAD a AWS para conocer el Content-Length del archivo GFS."""
    fstr = f"{fhour:03d}"
    file = f"gfs.t{ciclo}z.pgrb2.0p25.f{fstr}"
    url = GFS_URLS["aws"].format(fecha=fecha.replace("-", ""), ciclo=ciclo, file=file)
    try:
        r = requests.head(url, timeout=30, allow_redirects=True)
        if r.status_code == 200:
            return int(r.headers.get("Content-Length") or 0)
    except Exception:
        pass
    return None


def descargar_gfs(fecha: str, ciclo: str = "00", run_hours: int = 24) -> int:
    """Descarga el ciclo GFS 00Z (0-run_hours) hacia wps_sanjuan/gfs_data/<fecha>_<ciclo>.

    Antes de descargar verifica tamano contra AWS y elimina archivos truncados
    (descargas interrumpidas) que el descargador consideraria completos."""
    out = WPS_DIR / "gfs_data" / f"{fecha}_{ciclo}"
    for fhour in range(0, int(run_hours) + 1, 3):
        fname = f"gfs.t{ciclo}z.pgrb2.0p25.f{fhour:03d}"
        p = out / fname
        if not p.exists():
            continue
        esperado = _tamano_esperado_gfs(fecha, ciclo, fhour)
        if esperado and abs(p.stat().st_size - esperado) > 0.02 * esperado:
            logger.warning(f"GFS corrupto/truncado ({p.stat().st_size} vs {esperado} B): re-descargando {fname}")
            p.unlink()
    desc = GFSDownloader(str(out)).descargar_ciclo(fecha, ciclo_hora=ciclo, horas_pronostico=range(0, int(run_hours) + 1, 3))
    return len(list(out.glob(f"gfs.t{ciclo}z.pgrb2.0p25.f*")))


# --------------------------------------------------------------------------
# WPS + run dir
# --------------------------------------------------------------------------
def ejecutar_wps(fecha: str, ciclo: str = "00", timeout: int = 3600,
                 run_hours: int = 24) -> Tuple[bool, str]:
    """Corre WPS (geogrid+ungrib+metgrid) para el caso. Devuelve (ok, log)."""
    log = ESTADO_DIR / f"wps_{fecha.replace('-', '')}_{ciclo}.log"
    env = dict(os.environ)
    env.update(PC_PGICH_ENV)
    env["RUN_HOURS"] = str(int(run_hours))
    try:
        with open(log, "w", encoding="utf-8") as f:
            r = subprocess.run(
                ["bash", str(WPS_SH), fecha, ciclo],
                env=env, cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT, timeout=timeout,
            )
        return r.returncode == 0, str(log)
    except subprocess.TimeoutExpired:
        logger.error(f"WPS excedio el timeout ({timeout}s)")
        return False, str(log)


def propagar_metem(fecha: str, run_hours: int = 24, hora: str = "00") -> int:
    """Copia los met_em de WPS al directorio de corrida de real.exe.

    Construye los timestamps esperados cada 3 h desde `fecha` `hora`Z hasta
    start+run_hours, de modo que incluya el archivo del dia siguiente cuando el
    ciclo cruza la medianoche (protocolo temporal: start=12Z, t0+24h=12Z)."""
    base = datetime.strptime(f"{fecha} {hora}:00:00", "%Y-%m-%d %H:%M:%S")
    n = 0
    for h in range(0, int(run_hours) + 1, 3):
        dt = base + timedelta(hours=h)
        name = f"met_em.d01.{dt.strftime('%Y-%m-%d_%H:%M:%S')}.nc"
        src = WPS_DIR / name
        if src.exists():
            shutil.copy2(src, RUN_DIR / name)
            n += 1
    return n


# --------------------------------------------------------------------------
# Pipeline WRF
# --------------------------------------------------------------------------
def _valid_times_iso(fecha: str, valid_times: List[str]) -> List[str]:
    """Convierte ['00:00:00','24:00:00',...] a fechas ISO completas (con rollover de día).

    '24:00:00' -> '<fecha+1d>_00:00:00'."""
    base = datetime.strptime(fecha, "%Y-%m-%d")
    out = []
    for t in valid_times:
        p = [int(x) for x in str(t).split(":")]
        while len(p) < 3:
            p.append(0)
        dt = base + timedelta(hours=p[0], minutes=p[1], seconds=p[2])
        out.append(dt.strftime("%Y-%m-%d_%H:%M:%S"))
    return out


def _programa_temporal(comun: Dict[str, Any], caso: Dict[str, Any]) -> Dict[str, Any]:
    """Deriva el programa del protocolo de separacion temporal para un caso.

    t0 = fin de asimilacion / inicio del pronostico libre (del campo `t0` del caso,
    o `fecha`T00:00:00Z). start = t0 - ventana_asimilacion_h. run_hours = asim + horizonte.
    Si la config no define el protocolo, cae al comportamiento clasico (ciclo 00Z,
    run_hours de configuracion_comun)."""
    asim_h = comun.get("ventana_asimilacion_h")
    horizonte_h = comun.get("horizonte_h")
    t0_txt = caso.get("t0")
    t0 = None
    if t0_txt:
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                t0 = datetime.strptime(str(t0_txt).replace("Z", ""), fmt)
                break
            except ValueError:
                continue
    if asim_h and t0 is not None:
        start = t0 - timedelta(hours=int(asim_h))
        run_hours = int(asim_h) + int(horizonte_h or 0)
        return {"protocolo": True, "start": start, "t0": t0,
                "asim_h": int(asim_h), "horizonte_h": int(horizonte_h or 0),
                "run_hours": run_hours}
    fecha = caso["fecha"]
    start = datetime.strptime(f"{fecha} {comun.get('hora_ciclo', '00')}:00:00", "%Y-%m-%d %H:%M:%S")
    rh = int(comun.get("run_hours", 12))
    return {"protocolo": False, "start": start, "t0": start + timedelta(hours=rh),
            "asim_h": rh, "horizonte_h": 0, "run_hours": rh}


def _valid_times_protocolo(t0: datetime, horizonte_h: int) -> List[str]:
    """Instantes de validacion t0+1h .. t0+horizonte_h (formato YYYY-MM-DD_HH:MM:SS)."""
    return [(t0 + timedelta(hours=h)).strftime("%Y-%m-%d_%H:%M:%S")
            for h in range(1, int(horizonte_h) + 1)]


def ejecutar_pipeline(caso: Dict[str, Any], comun: Dict[str, Any], fecha: str,
                      obs_flat: Path, ciclo: str = "00", timeout: int = 12 * 3600,
                      programa: Optional[Dict[str, Any]] = None) -> Tuple[int, str]:
    """Corre pipeline_wrf.py para el caso (nudged + control + validacion multi-temporal)."""
    programa = programa or _programa_temporal(comun, caso)
    start = programa["start"]
    label = f"caso{int(caso['num'])}_NvC"
    run_case = Path(caso["resultados_dir"]).name  # directorio de resultados del caso
    run_hours = int(programa["run_hours"])
    if programa["protocolo"]:
        valid_times = _valid_times_protocolo(programa["t0"], programa["horizonte_h"])
    else:
        valid_times = _valid_times_iso(fecha, list(comun.get("valid_times", ["00:00:00"])))
    wrf_timeout = str(int(comun.get("wrf_timeout", 14400)))
    cmd = [
        str(PYTHON), str(PIPELINE),
        "--date", start.strftime("%Y-%m-%d"), "--hour", f"{start.hour:02d}:00",
        "--json", str(obs_flat),
        "--case", run_case,
        "--case-dir", str(_ruta_resultados_caso(caso)),
        "--namelist", str(ROOT / comun.get("namelist_base", "namelist.input")),
        "--run-dir", str(RUN_DIR),
        "--run-real",
        "--run-hours", str(run_hours),
        "--obs-coef-wind", str(comun.get("obs_coef_wind")),
        "--obs-coef-temp", str(comun.get("obs_coef_temp")),
        "--obs-coef-mois", str(comun.get("obs_coef_mois")),
        "--valid-times", ",".join(valid_times),
        "--label", label,
        "--wrf-timeout", wrf_timeout,
    ]
    if programa["protocolo"]:
        cmd += [
            "--asim-hours", str(programa["asim_h"]),
            "--horizon-h", str(programa["horizonte_h"]),
            "--t0", programa["t0"].strftime("%Y-%m-%dT%H:%M:%S"),
        ]
    cmd += EXTRA_PIPELINE_ARGS
    log = ESTADO_DIR / f"pipeline_{caso['id']}.log"
    logger.info(f"Pipeline: {' '.join(cmd)} (run_hours={run_hours})")
    env = dict(os.environ)
    # Los resultados deben caer en el directorio declarado por el caso
    # (outputs/runs/...), que es donde el informe busca tabla_evolutiva.json.
    env["RESULTS_DIR"] = str(ROOT / "outputs" / "runs")
    with open(log, "w", encoding="utf-8") as f:
        r = subprocess.run(cmd, cwd=str(ROOT), env=env, stdout=f, stderr=subprocess.STDOUT, timeout=timeout)
    return r.returncode, str(log)


# --------------------------------------------------------------------------
# Informes
# --------------------------------------------------------------------------
def _leer_tabla_evolutiva(caso: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    t = Path(caso["resultados_dir"])
    if not t.is_absolute():
        t = ROOT / t
    t = t / "tabla_evolutiva.json"
    if not t.exists():
        return None
    with open(t, "r", encoding="utf-8") as f:
        return json.load(f)


def _md_tabla_variable(rows: List[Dict[str, Any]], variable: str) -> str:
    """Tabla markdown compacta de RMSE/bias Nudged vs Control para una variable."""
    subset = [r for r in rows if r["var"] == variable]
    if not subset:
        return "_Sin métricas para esta variable._\n"
    lineas = ["| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |",
              "|--------|----|--------|--------|-------|--------|--------|-----|-----|"]
    for r in sorted(subset, key=lambda x: int(x["tiempo"].replace("Z", ""))):
        n, nr, cr = r["n"], r["nudged_rmse"], r["control_rmse"]
        nb, cb = r["nudged_bias"], r["control_bias"]
        nR, cR = r.get("nudged_r"), r.get("control_r")
        d = (cr - nr) if (nr == nr and cr == cr) else float("nan")
        d_txt = f"{d:+.2f}" if d == d else "n/d"
        # nR/cR pueden venir como None (no calculado) o NaN (varianza nula); ambos -> "n/d"
        nR_txt = f"{nR:+.3f}" if nR is not None and nR == nR else "n/d"
        cR_txt = f"{cR:+.3f}" if cR is not None and cR == cR else "n/d"
        lineas.append(f"| {r['tiempo']} | {n} | {nr:.2f} | {cr:.2f} | {d_txt} | {nb:+.2f} | {cb:+.2f} | {nR_txt} | {cR_txt} |")
    return "\n".join(lineas) + "\n"


def _fmt_metric(o):
    """Formatea una metrica (float/None/NaN) o 'n/d'."""
    if o is None or not isinstance(o, (int, float)):
        return "n/d"
    if o != o:  # NaN
        return "n/d"
    return f"{o:.2f}"


def _md_tabla_holdout(por_tiempo: List[Dict[str, Any]], variable: str) -> str:
    """Tabla markdown 'Ajuste vs. Generalización' (hold-out espacial) para una variable.

    Mejora 3.1 del informe_mejoras_f4: los resultados de estaciones asimiladas
    (ajuste) y de evaluacion (generalizacion) se leen de tabla_evolutiva.json y se
    vuelcan al informe del caso."""
    def _localiza(rows, var):
        for r in rows or []:
            if r.get("var") == variable:
                return r
        return None

    if not any(t.get("rows_asimiladas") or t.get("rows_evaluacion") for t in por_tiempo):
        return "_Sin separación ajuste/hold-out (no hay estaciones de evaluación con datos en este caso)._"

    lineas = ["| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |",
              "|--------|--------|--------|---------------|---------------|---------------|---------------|"]
    for t in por_tiempo:
        a = _localiza(t.get("rows_asimiladas"), variable)
        e = _localiza(t.get("rows_evaluacion"), variable)
        lineas.append(
            f"| {t['tiempo']} | {(a or {}).get('n', 'n/d')} | {(e or {}).get('n', 'n/d')}"
            f" | {_fmt_metric((a or {}).get('nudged_rmse'))} | {_fmt_metric((a or {}).get('control_rmse'))}"
            f" | {_fmt_metric((e or {}).get('nudged_rmse'))} | {_fmt_metric((e or {}).get('control_rmse'))} |"
        )
    return "\n".join(lineas) + "\n"


VARS_HORIZONTE = {"t2": "T2 (K)", "psfc": "PSFC (hPa)", "rh": "RH (%)", "wspd": "Wind (m/s)"}
TRAMOS_ORDEN = ["+1-6h", "+7-12h", "+13-18h", "+19-24h"]


def _leer_metricas_horizonte(caso: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    ruta = _ruta_resultados_caso(caso) / "metricas_por_horizonte.csv"
    if not ruta.exists():
        return None
    import csv as _csv
    with open(ruta, encoding="utf-8") as f:
        return list(_csv.DictReader(f))


def _md_tabla_horizonte(rows: List[Dict[str, Any]], variable: str) -> str:
    """Tabla markdown de RMSE/bias por horizonte de pronostico libre (protocolo temporal)."""
    sub = [r for r in rows if r["variable"] == variable]
    if not sub:
        return "_Sin métricas por horizonte para esta variable._\n"
    lineas = ["| Horizonte | Tramo | N | RMSE N | RMSE C | RMSE Pers | Bias N | Bias C |",
              "|-----------|-------|---|--------|--------|-----------|--------|--------|"]
    for r in sorted(sub, key=lambda x: int(x["horizonte_h"])):
        def _f(k):
            try:
                v = float(r[k])
            except (TypeError, ValueError):
                return "n/d"
            return f"{v:+.2f}" if k.endswith("bias") else f"{v:.2f}"
        lineas.append(
            f"| +{r['horizonte_h']} h | {r['tramo']} | {r['n']} | {_f('nudged_rmse')} | "
            f"{_f('control_rmse')} | {_f('persist_rmse')} | {_f('nudged_bias')} | {_f('control_bias')} |")
    return "\n".join(lineas) + "\n"


def _seccion_desempeno_flujo(L: List[str], caso: Dict[str, Any]) -> None:
    """Agrega al informe la seccion de desempeno del flujo end-to-end
    (tiempos por etapa) a partir de `evaluacion_flujo.json`."""
    ruta = _ruta_resultados_caso(caso) / "evaluacion_flujo.json"
    if not ruta.exists():
        return
    try:
        data = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    orq = data.get("etapas_orquestador_s", {})
    pipe = data.get("tiempos_etapa_s", {})
    if not orq and not pipe:
        return
    etiquetas = {
        "api_ecowitt_y_cobertura": "Ingesta API EcoWitt + cobertura",
        "obs_flat_parseo_qc": "Parseo y QC -> obs_flat (Little_R)",
        "gfs_descarga": "Descarga GFS 0.25 (AWS)",
        "wps": "WPS (geogrid+ungrib+metgrid)",
        "met_em_propagacion": "Propagacion met_em al run dir",
        "pipeline_total": "Pipeline WRF completo (preflight+real+nudged+control+validacion)",
        "obs_littler_obsdomain": "Little_R -> OBS_DOMAIN101",
        "preflight": "Preflight (validacion obs/namelist)",
        "real_exe": "real.exe",
        "wrf_nudged": "wrf.exe nudged (24 h)",
        "wrf_control": "wrf.exe control (24 h)",
        "validacion": "Validacion multi-temporal + informe de evolucion",
    }

    def _fmt(s: float) -> str:
        return f"{s / 60:.1f} min" if s >= 60 else f"{s:.2f} s"

    L.append("## Desempeno del flujo (end-to-end)")
    L.append("")
    L.append("Tiempos por etapa medidos en la ejecucion (artefacto "
             "`evaluacion_flujo.json`); cubre desde la llamada a la API EcoWitt "
             "hasta el informe de validacion.")
    L.append("")
    if orq:
        L.append("| Etapa (orquestador) | Tiempo |")
        L.append("|---------------------|--------|")
        for k, v in orq.items():
            if isinstance(v, (int, float)):
                L.append(f"| {etiquetas.get(k, k)} | {_fmt(v)} |")
        L.append("")
    if pipe:
        L.append("| Etapa (pipeline WRF) | Tiempo |")
        L.append("|----------------------|--------|")
        for k, v in pipe.items():
            if isinstance(v, (int, float)):
                L.append(f"| {etiquetas.get(k, k)} | {_fmt(v)} |")
        L.append("")
    total = data.get("total_end_to_end_s")
    if isinstance(total, (int, float)):
        L.append(f"**Tiempo total end-to-end:** {_fmt(total)}.")
        L.append("")


def redactar_informe_caso(caso: Dict[str, Any], estado_entry: Dict[str, Any],
                          cobertura: Optional[Dict[str, Any]] = None, run_hours: int = 12) -> Path:
    """Escribe el informe .md de un caso."""
    ruta = ROOT / caso["informe"]
    ruta.parent.mkdir(parents=True, exist_ok=True)
    estado = estado_entry.get("estado")
    detalle = estado_entry.get("detalle", "")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    tabla = _leer_tabla_evolutiva(caso)

    L = []
    L.append(f"# {caso['titulo']}")
    L.append("")
    if caso.get("t0"):
        L.append(f"**Fecha del evento:** {caso['fecha']} | **Protocolo temporal:** "
                 f"asimilación previa a t0={caso.get('t0')} (12 h) + pronóstico libre "
                 f"24 h (run_hours={run_hours}) | **Informe generado:** {ts}")
    else:
        L.append(f"**Fecha del evento:** {caso['fecha']} | **Ciclo:** 00Z -> {run_hours:02d}Z | **Informe generado:** {ts}")
    L.append("")
    L.append("## Descripción del evento")
    L.append("")
    L.append(caso["descripcion"])
    L.append("")
    L.append(f"**Fuente:** {caso['fuente']}")
    L.append("")
    L.append("## Estado de la ejecución")
    L.append("")
    if estado == "EJECUTADO":
        L.append(f"**Estado:** ✅ EJECUTADO")
    elif estado.startswith("NO EJECUTADO"):
        L.append(f"**Estado:** ⛔ NO EJECUTADO — {detalle}")
    else:
        L.append(f"**Estado:** ❌ {estado} — {detalle}")
    L.append("")

    L.append("## Configuración aplicada")
    L.append("")
    L.append("| Parámetro | Valor |")
    L.append("|-----------|-------|")
    L.append("| Dominio | 1 dominio, 15 km, 80×60, mercator (-31.5°, -68.5°) |")
    if caso.get("t0"):
        L.append(f"| Ciclo | asimilación previa [t0−12h, t0={caso['t0']}] + pronóstico libre "
                 f"({run_hours - 12} h), run_hours={run_hours} |")
    else:
        L.append(f"| Ciclo | 00Z–{run_hours:02d}Z ({run_hours} h) |")
    L.append("| Forzante | GFS 0.25° (AWS) |")
    L.append("| Obs nudging | `obs_nudge_opt=1`, coef viento/temp/humedad=0.0001, `obs_twindo=1.0` |")
    L.append("| Nudged vs Control | misma inicialización; solo cambia `obs_nudge_opt` (1 vs 0) |")
    vt_txt = ' '.join(tabla['valid_times']) if tabla else ', '.join(f"{h:02d}Z" for h in range(0, run_hours + 1, 6))
    L.append(f"| Validación | multi-temporal {vt_txt} vs observaciones de estaciones |")
    L.append("")
    L.append("## Limitación conocida del dominio (relevant para el análisis)")
    L.append("")
    L.append("El dominio de 15 km no resuelve la topografía profunda de la precordillera "
             "(errores de altura del modelo de entre +201 m y +918 m en las estaciones, "
             "con máximos en CARACOLES +918 m, PUNTA_NEGRA +420 m y CUESTA_Viento +378 m). "
             f"Por eso el análisis de **{caso['titulo']}** se restringe a la **firma térmica** "
             "(salto de T2 y caída de RH), y el viento se interpreta solo de forma cualitativa. "
             "Ver también `documentacion_proyecto/informe_avances_fases_proyecto.md`.")
    L.append("")

    if cobertura:
        L.append("## Observaciones disponibles")
        L.append("")
        if caso.get("t0"):
            L.append(f"- Registros válidos: **{cobertura['dia']}** en el día, **{cobertura['ventana']}** "
                     f"en la ventana de asimilación (t0−12 h → t0 = {caso['t0']}).")
        else:
            L.append(f"- Registros válidos: **{cobertura['dia']}** en el día, **{cobertura['ventana']}** en la ventana 00Z–{run_hours:02d}Z.")
        L.append(f"- Estaciones con datos en ventana: **{cobertura['estaciones']}**")
        pe = cobertura.get("por_estacion", {})
        if pe:
            L.append("")
            L.append(f"| Estación | Registros en ventana |")
            L.append("|----------|--------------------|")
            for k, v in sorted(pe.items(), key=lambda kv: (-kv[1], kv[0])):
                L.append(f"| {k} | {v} |")
        L.append("")

    if estado == "EJECUTADO":
        _seccion_desempeno_flujo(L, caso)
        tabla = _leer_tabla_evolutiva(caso)
        if tabla:
            L.append("## Resultados: Nudged vs Control")
            L.append("")
            L.append("RMSE/Bias de la corrida nudgada (N) y de control (C) por tiempo de validación. "
                     "dRMSE = RMSE(C) - RMSE(N) (positivo ⇒ mejora con nudging; negativo ⇒ degrada). "
                     + ("La comparación N vs C es válida en la ventana de asimilación; a partir de t0 "
                        "ambas corridas tienen el nudging apagado y solo difieren por el estado inicial "
                        "(ver resultados por horizonte más abajo)."
                        if caso.get("t0") else "00Z: N≡C por construcción."))
            L.append("")
            for var in tabla.get("variables", []):
                L.append(f"### {var}")
                L.append("")
                rows = []
                for t in tabla.get("por_tiempo", []):
                    for r in t.get("rows", []):
                        rr = dict(r)
                        rr["tiempo"] = t["tiempo"]
                        rows.append(rr)
                L.append(_md_tabla_variable(rows, var))
                L.append("")
            if not caso.get("t0"):
                L.append("### Ajuste vs. Generalización (hold-out espacial)")
                L.append("")
                L.append("Las estaciones con `rol='evaluacion'` en `config/estaciones.json` "
                         "nunca se asimilan (quedan fuera de `OBS_DOMAIN101`); sus métricas miden "
                         "si el nudging **generaliza** a lugares sin datos, no solo si reproduce "
                         "lo que ya se le dio (estaciones 'asimiladas').")
                L.append("")
                for var in tabla.get("variables", []):
                    L.append(f"#### {var}")
                    L.append("")
                    rows_ht = []
                    for t in tabla.get("por_tiempo", []):
                        rows_ht.append(t)
                    L.append(_md_tabla_holdout(rows_ht, var))
                    L.append("")
            L.append("### Resultados por horizonte de pronóstico (protocolo temporal)")
            L.append("")
            L.append("RMSE/Bias vs horizonte desde t0 (fin de asimilación) y línea base de "
                     "**persistencia** (último valor observado en t0 sostenido). Nudged y Control "
                     "solo difieren en `obs_nudge_opt`; tras `fdda_end` el nudging está apagado.")
            L.append("")
            mh = _leer_metricas_horizonte(caso)
            if mh:
                for key, etiqueta in VARS_HORIZONTE.items():
                    L.append(f"#### {etiqueta}")
                    L.append("")
                    L.append(_md_tabla_horizonte(mh, key))
                    L.append("")
            else:
                L.append("_Sin `metricas_por_horizonte.csv` (revisar la corrida)._")
                L.append("")
            L.append("### Conclusiones del caso")
            L.append("")
            L.append("Para la interpretación completa (series, gráficos y comparación con observaciones) ver "
                     f"`{caso['resultados_dir']}/` (informe de evolución, tablas por horario y wrfouts).")
            L.append("")
        else:
            L.append("## Resultados parciales")
            L.append("")
            L.append("La corrida se ejecutó pero no se encontraron métricas en "
                     f"`{caso['resultados_dir']}/tabla_evolutiva.json` (revisar logs).")
            L.append("")

    L.append("---")
    L.append("*Informe generado automáticamente por `src/casos/run_casos.py`.*")
    ruta.write_text("\n".join(L), encoding="utf-8")
    logger.info(f"Informe del caso escrito: {ruta}")
    return ruta


def _resumen_metricas(tabla: Optional[Dict[str, Any]], variable: str, tiempo: str) -> Dict[str, Any]:
    if not tabla:
        return {}
    for t in tabla.get("por_tiempo", []):
        if t["tiempo"] == tiempo:
            for r in t.get("rows", []):
                if r["var"] == variable:
                    return r
    return {}


def redactar_informe_consolidado(casos: List[Dict[str, Any]], estado: Dict[str, Any]) -> Path:
    ts = datetime.now().strftime("%Y%m%d")
    ruta = INFORMES / f"informe_casos_estudio_{ts}.md"
    ruta.parent.mkdir(parents=True, exist_ok=True)

    L = []
    L.append(f"# Informe consolidado de casos de estudio — Fase 4")
    L.append("")
    L.append(f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')} por `src/casos/run_casos.py`.")
    L.append("")
    L.append("## Resumen de ejecución")
    L.append("")
    L.append("| Caso | Fecha | Evento | Estado | Informe |")
    L.append("|------|-------|--------|--------|---------|")
    for c in casos:
        e = estado.get(c["id"], {})
        st = e.get("estado", "PENDIENTE")
        det = e.get("detalle", "")
        estado_txt = st
        if st == "EJECUTADO":
            estado_txt = "EJECUTADO"
        elif "SIN DATOS" in st:
            estado_txt = f"NO EJECUTADO — SIN DATOS ({det})"
        L.append(f"| {c['titulo']} | {c['fecha']} | {c['evento']} | {estado_txt} | `{c['informe']}` |")
    L.append("")
    L.append("## Métricas por caso (RMSE y r del nudging vs control)")
    L.append("")
    L.append("Se reporta el RMSE y el coeficiente de correlación (r) de T2 (K) y RH (%) en cada "
             "tiempo de validación. En los casos con protocolo temporal, 'NNZ' significa "
             "horizonte de pronóstico en horas desde t0 (01Z = +1 h, 24Z = +24 h).")
    L.append("")
    for c in casos:
        e = estado.get(c["id"], {})
        L.append(f"### {c['titulo']} ({c['fecha']})")
        L.append("")
        if e.get("estado") != "EJECUTADO":
            L.append(f"_No ejecutado: {e.get('detalle', '')}_")
            L.append("")
            continue
        tabla = _leer_tabla_evolutiva(c)
        if not tabla:
            L.append("_Sin tabla de métricas._")
            L.append("")
            continue
        L.append("| Tiempo | RMSE T2 N | RMSE T2 C | r T2 N | r T2 C | RMSE RH N | RMSE RH C | r RH N | r RH C |")
        L.append("|--------|-----------|-----------|--------|--------|-----------|-----------|--------|--------|")
        def _fmt(r: Dict[str, Any], k: str) -> str:
            v = r.get(k)
            if v is None or not isinstance(v, (int, float)) or v != v:  # v != v detecta NaN
                return "n/d"
            return f"{v:+.3f}" if k.endswith("_r") else f"{v:.2f}"
        for t in tabla.get("por_tiempo", []):
            t2 = _resumen_metricas(tabla, "T2 (K)", t["tiempo"])
            rh = _resumen_metricas(tabla, "RH (%)", t["tiempo"])
            L.append(f"| {t['tiempo']} | {_fmt(t2, 'nudged_rmse')} | {_fmt(t2, 'control_rmse')}"
                     f" | {_fmt(t2, 'nudged_r')} | {_fmt(t2, 'control_r')}"
                     f" | {_fmt(rh, 'nudged_rmse')} | {_fmt(rh, 'control_rmse')}"
                     f" | {_fmt(rh, 'nudged_r')} | {_fmt(rh, 'control_r')} |")
        L.append("")
    L.append("## Limitación del dominio y criterio de análisis")
    L.append("")
    L.append("15 km, errores de terreno +201..+918 m. En todos los casos el análisis se apoya en la "
             "firma térmica (T2/RH); el viento se interpreta de forma cualitativa. "
             "Detalles en los informes por caso.")
    L.append("")
    L.append("---")
    L.append("*Informe consolidado generado automáticamente.*")
    ruta.write_text("\n".join(L), encoding="utf-8")
    logger.info(f"Informe consolidado escrito: {ruta}")
    return ruta


# --------------------------------------------------------------------------
# Orquestacion
# --------------------------------------------------------------------------
def _ruta_resultados_caso(caso: Dict[str, Any]) -> Path:
    p = Path(caso["resultados_dir"])
    return p if p.is_absolute() else ROOT / p


def _escribir_flujo_caso(caso: Dict[str, Any], fecha: str, ciclo: str,
                         run_hours: int, flujo: Dict[str, float]) -> Path:
    """Fusiona los tiempos por etapa del orquestador (API EcoWitt, obs_flat,
    GFS, WPS, met_em, pipeline) con el desglose interno del pipeline WRF
    (real/nudged/control/validacion) en un unico artefacto end-to-end."""
    case_dir = _ruta_resultados_caso(caso)
    case_dir.mkdir(parents=True, exist_ok=True)
    ruta = case_dir / "evaluacion_flujo.json"
    data: Dict[str, Any] = {}
    if ruta.exists():
        try:
            data = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
    data.update({
        "caso": caso["id"],
        "fecha": fecha,
        "hora": f"{ciclo}:00",
        "generado": datetime.now().isoformat(timespec="seconds"),
        "run_hours_namelist": run_hours,
        "etapas_orquestador_s": {k: round(v, 3) for k, v in flujo.items()},
        "total_end_to_end_s": round(sum(flujo.values()), 3),
    })
    ruta.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"  Evaluacion de flujo end-to-end guardada: {ruta}")
    return ruta


def ejecutar_caso(caso: Dict[str, Any], comun: Dict[str, Any], estado: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecuta un caso completo (obs -> GFS -> WPS -> pipeline). Actualiza estado."""
    cid = caso["id"]
    fecha = caso["fecha"]
    programa = _programa_temporal(comun, caso)
    start = programa["start"]
    gfs_fecha = start.strftime("%Y-%m-%d")
    gfs_ciclo = f"{start.hour:02d}"
    ciclo = gfs_ciclo
    run_hours = int(programa["run_hours"])
    asim_h = int(programa["asim_h"])
    obs_min = int(comun.get("obs_min_registros", 60))
    obs_min_est = int(comun.get("obs_min_estaciones", 3))
    if programa["protocolo"]:
        logger.info(f"{cid}: protocolo temporal start={start} t0={programa['t0']} "
                    f"run_hours={run_hours} (asim={asim_h} h, horizonte={programa['horizonte_h']} h)")

    resultado: Dict[str, Any] = {"estado": "PENDIENTE", "detalle": "", "ts": datetime.now().isoformat(timespec="seconds")}

    flujo: Dict[str, float] = {}
    _t = time.perf_counter()

    # 1) Observaciones
    try:
        csv = descargar_obs_historico(fecha)
        cov = cobertura_obs(csv, fecha, ciclo, run_hours,
                            t0_iso=caso.get("t0"), asim_horas=asim_h if programa["protocolo"] else None)
    except Exception as e:
        logger.exception(f"{cid}: fallo al obtener observaciones")
        resultado = {"estado": "NO EJECUTADO - SIN DATOS (obs)", "detalle": f"fallo de descarga: {e}",
                     "ts": datetime.now().isoformat(timespec="seconds")}
        return resultado

    flujo["api_ecowitt_y_cobertura"] = round(time.perf_counter() - _t, 3)
    _t = time.perf_counter()

    if cov["ventana"] < obs_min or cov["estaciones"] < obs_min_est:
        detalle = f"cobertura insuficiente ({cov['ventana']} registros, {cov['estaciones']} estaciones en ventana)"
        resultado = {"estado": "NO EJECUTADO - SIN DATOS (obs)", "detalle": detalle,
                     "ts": datetime.now().isoformat(timespec="seconds")}
        estado[cid] = resultado
        return resultado

    try:
        obs_flat = generar_obs_flat(csv, fecha)
    except Exception as e:
        logger.exception(f"{cid}: fallo al generar obs_flat")
        resultado = {"estado": "FALLIDO", "detalle": f"generar obs_flat: {e}",
                     "ts": datetime.now().isoformat(timespec="seconds")}
        estado[cid] = resultado
        return resultado

    flujo["obs_flat_parseo_qc"] = round(time.perf_counter() - _t, 3)
    _t = time.perf_counter()

    # 2) GFS
    fuente = gfs_disponible(gfs_fecha, gfs_ciclo)
    if fuente is None:
        resultado = {"estado": "NO EJECUTADO - SIN DATOS (gfs)",
                     "detalle": f"GFS {gfs_fecha} {gfs_ciclo}Z no disponible en AWS/NOMADS",
                     "ts": datetime.now().isoformat(timespec="seconds")}
        estado[cid] = resultado
        return resultado
    n_gfs = descargar_gfs(gfs_fecha, gfs_ciclo, run_hours)
    n_gfs_min = len(range(0, run_hours + 1, 3))
    if n_gfs < n_gfs_min:
        resultado = {"estado": "NO EJECUTADO - SIN DATOS (gfs)", "detalle": f"se bajaron {n_gfs}/{n_gfs_min} ficheros GFS",
                     "ts": datetime.now().isoformat(timespec="seconds")}
        estado[cid] = resultado
        return resultado

    flujo["gfs_descarga"] = round(time.perf_counter() - _t, 3)
    _t = time.perf_counter()

    # 3) WPS
    ok_wps, log_wps = ejecutar_wps(gfs_fecha, gfs_ciclo, run_hours=run_hours)
    if not ok_wps:
        resultado = {"estado": "FALLIDO", "detalle": f"WPS fallo (ver {log_wps})",
                     "ts": datetime.now().isoformat(timespec="seconds")}
        estado[cid] = resultado
        return resultado
    flujo["wps"] = round(time.perf_counter() - _t, 3)
    _t = time.perf_counter()
    n_metem = propagar_metem(gfs_fecha, run_hours, hora=gfs_ciclo)
    n_metem_min = len(range(0, run_hours + 1, 3))
    if n_metem < n_metem_min:
        resultado = {"estado": "FALLIDO", "detalle": f"WPS no genero met_em suficientes ({n_metem}/{n_metem_min})",
                     "ts": datetime.now().isoformat(timespec="seconds")}
        estado[cid] = resultado
        return resultado

    flujo["met_em_propagacion"] = round(time.perf_counter() - _t, 3)
    _t = time.perf_counter()

    # 4) Pipeline WRF (nudged + control + validacion)
    rc, log_pipe = ejecutar_pipeline(caso, comun, fecha, obs_flat, gfs_ciclo, programa=programa)
    flujo["pipeline_total"] = round(time.perf_counter() - _t, 3)
    if rc == 0:
        resultado = {"estado": "EJECUTADO", "detalle": f"fuente GFS {fuente}",
                     "ts": datetime.now().isoformat(timespec="seconds")}
    else:
        resultado = {"estado": "FALLIDO", "detalle": f"pipeline rc={rc} (ver {log_pipe})",
                     "ts": datetime.now().isoformat(timespec="seconds")}
    estado[cid] = resultado
    try:
        _escribir_flujo_caso(caso, fecha, ciclo, run_hours, flujo)
    except Exception as e:
        logger.warning(f"{cid}: no se pudo escribir evaluacion de flujo: {e}")
    return resultado


def main():
    parser = argparse.ArgumentParser(description="Casos de estudio Fase 4 (WRF con/sin obs nudging).")
    parser.add_argument("--dry-run", action="store_true", help="Solo verificar disponibilidad (obs + GFS).")
    parser.add_argument("--solo", type=int, default=None, help="Ejecutar solo el caso con ese numero.")
    parser.add_argument("--force", action="store_true", help="Re-ejecutar aunque existan resultados.")
    parser.add_argument("--skip-wrf", action="store_true", help="No correr WRF (solo obs/GFS/informes).")
    parser.add_argument("--variante", default=None,
                        help="Nombre de una variante experimental (ej. rampa). Los resultados van a "
                             "<resultados_dir>__<variante>, el estado y los informes a archivos aparte; "
                             "no se tocan los resultados oficiales.")
    parser.add_argument("--pipeline-args", default="",
                        help="Opciones extra para pipeline_wrf.py, entre comillas "
                             "(ej. \"--obs-idynin 1 --obs-dtramp -60 --obs-ipf-nudob\").")
    args = parser.parse_args()

    if args.pipeline_args and not args.variante:
        logger.error("--pipeline-args exige --variante (para no mezclar con los resultados oficiales)")
        return 1
    EXTRA_PIPELINE_ARGS[:] = shlex.split(args.pipeline_args)

    comun, casos = _leer_casos()
    if args.variante:
        g = globals()
        g["ESTADO_JSON"] = ESTADO_DIR / f"estado_casos__{args.variante}.json"
        g["INFORMES"] = INFORMES / "variantes" / args.variante
        casos = [dict(c, id=f"{c['id']}__{args.variante}",
                      resultados_dir=f"{c['resultados_dir']}__{args.variante}",
                      informe=str(Path(c["informe"]).parent / "variantes" / args.variante / Path(c["informe"]).name)
                      if c.get("informe") else c.get("informe"))
                 for c in casos]
    todos_casos = casos
    if args.solo:
        casos = [c for c in casos if c["num"] == args.solo]
        if not casos:
            logger.error(f"No existe el caso {args.solo}")
            return 1

    estado = _estado()

    for caso in casos:
        cid = caso["id"]
        prev = estado.get(cid, {})
        if not args.force and not args.dry_run and prev.get("estado") == "EJECUTADO" and not args.skip_wrf:
            logger.info(f"{cid}: ya fue EJECUTADO, salteando (--force para re-ejecutar)")
            continue

        prog = _programa_temporal(comun, caso)
        gfs_fecha = prog["start"].strftime("%Y-%m-%d")
        gfs_ciclo = f"{prog['start'].hour:02d}"

        if args.dry_run:
            # Solo disponibilidad: obs + GFS, sin WRF
            try:
                csv = descargar_obs_historico(caso["fecha"])
                cov = cobertura_obs(csv, caso["fecha"], gfs_ciclo, prog["run_hours"],
                                    t0_iso=caso.get("t0"),
                                    asim_horas=int(prog["asim_h"]) if prog["protocolo"] else None)
            except Exception as e:
                cov = {"dia": 0, "ventana": 0, "estaciones": 0, "por_estacion": {}}
                logger.error(f"{cid}: obs fallo: {e}")
            fuente = gfs_disponible(gfs_fecha, gfs_ciclo)
            logger.info(f"[DRY] {cid} {caso['fecha']}: obs dia={cov['dia']} ventana={cov['ventana']} "
                        f"estaciones={cov['estaciones']} | GFS {gfs_fecha} {gfs_ciclo}Z={fuente or 'NO DISPONIBLE'}")
            estado[cid] = {"estado": "DRY_RUN",
                           "detalle": f"obs ventana {cov['ventana']} / {cov['estaciones']} est; gfs {fuente or 'no'}",
                           "ts": datetime.now().isoformat(timespec="seconds")}
            continue

        if args.skip_wrf:
            # Solo preparar obs/GFS/WPS sin correr el pipeline
            try:
                csv = descargar_obs_historico(caso["fecha"])
                cov = cobertura_obs(csv, caso["fecha"], gfs_ciclo, prog["run_hours"],
                                    t0_iso=caso.get("t0"),
                                    asim_horas=int(prog["asim_h"]) if prog["protocolo"] else None)
                obs_flat = generar_obs_flat(csv, caso["fecha"])
                fuente = gfs_disponible(gfs_fecha, gfs_ciclo)
                n_gfs = descargar_gfs(gfs_fecha, gfs_ciclo, prog["run_hours"]) if fuente else 0
                estado[cid] = {"estado": "PREPARADO", "detalle": f"obs {cov['ventana']}, gfs {n_gfs}, obs_flat {obs_flat.name}",
                               "ts": datetime.now().isoformat(timespec="seconds")}
            except Exception as e:
                estado[cid] = {"estado": "FALLIDO", "detalle": f"preparacion: {e}",
                               "ts": datetime.now().isoformat(timespec="seconds")}
            continue

        logger.info(f"=== {caso['titulo']} ({caso['fecha']}) ===")
        ejecutar_caso(caso, comun, estado)

    _guardar_estado(estado)

    if not args.dry_run:
        for caso in casos:
            entry = estado.get(caso["id"], {})
            cobertura = None
            prog = _programa_temporal(comun, caso)
            if entry.get("estado") == "EJECUTADO":
                try:
                    csv = csv_caso(caso["fecha"])
                    if csv.exists():
                        cobertura = cobertura_obs(csv, caso["fecha"],
                                                  f"{prog['start'].hour:02d}", prog["run_hours"],
                                                  t0_iso=caso.get("t0"),
                                                  asim_horas=int(prog["asim_h"]) if prog["protocolo"] else None)
                except Exception:
                    cobertura = None
            redactar_informe_caso(caso, entry, cobertura, run_hours=int(prog["run_hours"]))
        redactar_informe_consolidado(todos_casos, estado)
    return 0


if __name__ == "__main__":
    sys.exit(main())
