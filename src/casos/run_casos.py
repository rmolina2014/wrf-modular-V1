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
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
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


def descargar_obs_historico(fecha: str) -> Path:
    """Descarga el historico diario si no existe y devuelve la ruta del CSV."""
    csv = csv_historico(fecha)
    if csv.exists() and csv.stat().st_size > 100:
        logger.info(f"Historico ya descargado: {csv.name}")
        return csv
    logger.info(f"Descargando historico EcoWitt de {fecha}...")
    EcowittIngestor().descargar_historico(fecha, output_dir=str(RAW))
    if not csv.exists():
        raise RuntimeError(f"No se genero el CSV historico para {fecha}")
    return csv


def cobertura_obs(csv_path: Path, fecha: str, ciclo: str = "00", run_hours: int = 12) -> Dict[str, Any]:
    """Mide la cobertura de observaciones validas (dia completo y ventana del ciclo)."""
    df = pd.read_csv(csv_path)
    if df.empty or "temp_c" not in df.columns:
        return {"dia": 0, "ventana": 0, "estaciones": 0, "por_estacion": {}}

    ts_ini = int(datetime.strptime(f"{fecha} 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp())
    ts_fin = ts_ini + int(run_hours) * 3600
    df["ts"] = pd.to_numeric(df["hora_unix"], errors="coerce")
    df["temp_ok"] = df["temp_c"].apply(lambda v: _num(v) is not None and pd.notna(v))

    dia = int(df["temp_ok"].sum())
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
        logger.info(f"obs_flat ya existe: {salida.name}")
        return salida

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
def ejecutar_wps(fecha: str, ciclo: str = "00", timeout: int = 3600) -> Tuple[bool, str]:
    """Corre WPS (geogrid+ungrib+metgrid) para el caso. Devuelve (ok, log)."""
    log = ESTADO_DIR / f"wps_{fecha.replace('-', '')}_{ciclo}.log"
    env = dict(os.environ)
    env.update(PC_PGICH_ENV)
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


def propagar_metem(fecha: str, run_hours: int = 24) -> int:
    """Copia los met_em de WPS al directorio de corrida de real.exe.

    Construye los timestamps esperados cada 3 h desde 00Z hasta run_hours, de
    modo que incluya el archivo del dia siguiente (p.ej. 2026-08-07_00:00:00
    para un ciclo de 24 h que arranca el 2026-08-06)."""
    base = datetime.strptime(fecha, "%Y-%m-%d")
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


def ejecutar_pipeline(caso: Dict[str, Any], comun: Dict[str, Any], fecha: str,
                      obs_flat: Path, ciclo: str = "00", timeout: int = 12 * 3600) -> Tuple[int, str]:
    """Corre pipeline_wrf.py para el caso (nudged + control + validacion multi-temporal)."""
    label = f"caso{int(caso['num'])}_NvC"
    run_case = Path(caso["resultados_dir"]).name  # directorio de resultados del caso
    run_hours = int(comun.get("run_hours", 12))
    valid_times = _valid_times_iso(fecha, list(comun.get("valid_times", ["00:00:00"])))
    wrf_timeout = str(int(comun.get("wrf_timeout", 14400)))
    cmd = [
        str(PYTHON), str(PIPELINE),
        "--date", fecha, "--hour", f"{ciclo}:00",
        "--json", str(obs_flat),
        "--case", run_case,
        "--namelist", str(ROOT / comun.get("namelist_base", "namelist.input")),
        "--run-dir", str(RUN_DIR),
        "--run-real",
        "--obs-coef-wind", str(comun.get("obs_coef_wind")),
        "--obs-coef-temp", str(comun.get("obs_coef_temp")),
        "--obs-coef-mois", str(comun.get("obs_coef_mois")),
        "--valid-times", ",".join(valid_times),
        "--label", label,
        "--wrf-timeout", wrf_timeout,
    ]
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
        L.append(f"- Registros válidos: **{cobertura['dia']}** en el día, **{cobertura['ventana']}** en la ventana 00Z–{run_hours:02d}Z.")
        L.append(f"- Estaciones con datos en ventana: **{cobertura['estaciones']}**")
        pe = cobertura.get("por_estacion", {})
        if pe:
            L.append("")
            L.append(f"| Estación | Registros (00Z–{run_hours:02d}Z) |")
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
                     "00Z: N≡C por construcción.")
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
    L.append("Se reporta el RMSE y el coeficiente de correlación (r) de T2 (K) y RH (%) "
             "en la ventana de mayor divergencia (06Z, 12Z y 18Z).")
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
    ciclo = comun.get("hora_ciclo", "00")
    run_hours = int(comun.get("run_hours", 12))
    obs_min = int(comun.get("obs_min_registros", 60))
    obs_min_est = int(comun.get("obs_min_estaciones", 3))

    resultado: Dict[str, Any] = {"estado": "PENDIENTE", "detalle": "", "ts": datetime.now().isoformat(timespec="seconds")}

    flujo: Dict[str, float] = {}
    _t = time.perf_counter()

    # 1) Observaciones
    try:
        csv = descargar_obs_historico(fecha)
        cov = cobertura_obs(csv, fecha, ciclo, run_hours)
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
    fuente = gfs_disponible(fecha, ciclo)
    if fuente is None:
        resultado = {"estado": "NO EJECUTADO - SIN DATOS (gfs)", "detalle": "GFS 00Z no disponible en AWS/NOMADS",
                     "ts": datetime.now().isoformat(timespec="seconds")}
        estado[cid] = resultado
        return resultado
    n_gfs = descargar_gfs(fecha, ciclo, run_hours)
    n_gfs_min = len(range(0, run_hours + 1, 3))
    if n_gfs < n_gfs_min:
        resultado = {"estado": "NO EJECUTADO - SIN DATOS (gfs)", "detalle": f"se bajaron {n_gfs}/{n_gfs_min} ficheros GFS",
                     "ts": datetime.now().isoformat(timespec="seconds")}
        estado[cid] = resultado
        return resultado

    flujo["gfs_descarga"] = round(time.perf_counter() - _t, 3)
    _t = time.perf_counter()

    # 3) WPS
    ok_wps, log_wps = ejecutar_wps(fecha, ciclo)
    if not ok_wps:
        resultado = {"estado": "FALLIDO", "detalle": f"WPS fallo (ver {log_wps})",
                     "ts": datetime.now().isoformat(timespec="seconds")}
        estado[cid] = resultado
        return resultado
    flujo["wps"] = round(time.perf_counter() - _t, 3)
    _t = time.perf_counter()
    n_metem = propagar_metem(fecha, run_hours)
    n_metem_min = len(range(0, run_hours + 1, 3))
    if n_metem < n_metem_min:
        resultado = {"estado": "FALLIDO", "detalle": f"WPS no genero met_em suficientes ({n_metem}/{n_metem_min})",
                     "ts": datetime.now().isoformat(timespec="seconds")}
        estado[cid] = resultado
        return resultado

    flujo["met_em_propagacion"] = round(time.perf_counter() - _t, 3)
    _t = time.perf_counter()

    # 4) Pipeline WRF (nudged + control + validacion)
    rc, log_pipe = ejecutar_pipeline(caso, comun, fecha, obs_flat, ciclo)
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
    args = parser.parse_args()

    comun, casos = _leer_casos()
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

        if args.dry_run:
            # Solo disponibilidad: obs + GFS, sin WRF
            try:
                csv = descargar_obs_historico(caso["fecha"])
                cov = cobertura_obs(csv, caso["fecha"], comun.get("hora_ciclo", "00"), comun.get("run_hours", 12))
            except Exception as e:
                cov = {"dia": 0, "ventana": 0, "estaciones": 0, "por_estacion": {}}
                logger.error(f"{cid}: obs fallo: {e}")
            fuente = gfs_disponible(caso["fecha"], comun.get("hora_ciclo", "00"))
            logger.info(f"[DRY] {cid} {caso['fecha']}: obs dia={cov['dia']} ventana={cov['ventana']} "
                        f"estaciones={cov['estaciones']} | GFS={fuente or 'NO DISPONIBLE'}")
            estado[cid] = {"estado": "DRY_RUN",
                           "detalle": f"obs ventana {cov['ventana']} / {cov['estaciones']} est; gfs {fuente or 'no'}",
                           "ts": datetime.now().isoformat(timespec="seconds")}
            continue

        if args.skip_wrf:
            # Solo preparar obs/GFS/WPS sin correr el pipeline
            try:
                csv = descargar_obs_historico(caso["fecha"])
                cov = cobertura_obs(csv, caso["fecha"], comun.get("hora_ciclo", "00"), comun.get("run_hours", 12))
                obs_flat = generar_obs_flat(csv, caso["fecha"])
                fuente = gfs_disponible(caso["fecha"], comun.get("hora_ciclo", "00"))
                n_gfs = descargar_gfs(caso["fecha"], comun.get("hora_ciclo", "00"), comun.get("run_hours", 12)) if fuente else 0
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
            if entry.get("estado") == "EJECUTADO":
                try:
                    csv = csv_historico(caso["fecha"])
                    if csv.exists():
                        cobertura = cobertura_obs(csv, caso["fecha"], comun.get("hora_ciclo", "00"), comun.get("run_hours", 12))
                except Exception:
                    cobertura = None
            redactar_informe_caso(caso, entry, cobertura, run_hours=int(comun.get("run_hours", 12)))
        redactar_informe_consolidado(todos_casos, estado)
    return 0


if __name__ == "__main__":
    sys.exit(main())
