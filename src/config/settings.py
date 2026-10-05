"""Configuración centralizada del sistema WRF."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional


class Settings:
    def __init__(self) -> None:
        self.root = Path(__file__).resolve().parents[2]
        # Paths WRF
        self.local_wrf_dir = Path(os.getenv("LOCAL_WRF_DIR", self.root / "run_dir") if False else os.getenv("LOCAL_WRF_DIR", "/home/roberto/pgich-wrf-modular/wrf_run"))
        # Intentamos usar valores razonables si existen
        env_wrf = os.getenv("LOCAL_WRF_DIR")
        if env_wrf:
            self.local_wrf_dir = Path(env_wrf)
        else:
            # fallback común en repo
            cand = self.root / "wps_sanjuan"
            self.local_wrf_dir = cand.parent / "run_dir"  # placeholder
        self.wrf_env_bash = os.getenv("WRF_ENV_BASH")
        self.mpirun = os.getenv("MPIRUN", "mpirun")
        self.wrf_np = int(os.getenv("WRF_NP", "4"))
        self.validation_python = os.getenv("VALIDATION_PYTHON", "python3")
        # Data/outputs
        self.data_raw = self.root / "data" / "raw"
        self.outputs_runs = self.root / "outputs" / "runs"
        self.outputs_validacion = self.root / "outputs" / "validacion"
        self.outputs_informes = self.root / "outputs" / "informes"
        self.outputs_artefactos = self.root / "outputs" / "artefactos"
        self.logs_dir = self.root / "logs"
        # Config
        self.estaciones_json = self.root / "config" / "estaciones.json"
        self.casos_oficiales_json = self.root / "config" / "casos_oficiales.json"
        # WRF run
        self.wrf_timeout = int(os.getenv("WRF_TIMEOUT", "7200"))
        self.wrf_retries = int(os.getenv("WRF_RETRIES", "5"))


settings = Settings()
