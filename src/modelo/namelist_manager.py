"""Gestor de plantillas y parámetros para namelist.input y namelist.wps."""

import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("modelo.namelist")


class NamelistManager:
    """Modifica y genera archivos de configuración namelist.input para WRF."""

    def __init__(self, template_path: Optional[str] = None):
        self.template_path = Path(template_path or "config/namelist.input.template")
        self.contenido = self._cargar_template()

    def _cargar_template(self) -> str:
        if not self.template_path.exists():
            # Intentar buscar namelist.input en raíz si el template no existe
            alt = Path("namelist.input")
            if alt.exists():
                return alt.read_text(encoding="utf-8")
            raise FileNotFoundError(f"Template de namelist no encontrado en {self.template_path}")
        return self.template_path.read_text(encoding="utf-8")

    def actualizar_fechas(
        self,
        start_year: int,
        start_month: int,
        start_day: int,
        start_hour: int,
        end_year: int,
        end_month: int,
        end_day: int,
        end_hour: int,
        run_hours: Optional[int] = None,
    ) -> "NamelistManager":
        """Actualiza las fechas de inicio y fin de la simulación."""
        c = self.contenido
        c = re.sub(r"start_year\s*=\s*\d+", f"start_year = {start_year}", c)
        c = re.sub(r"start_month\s*=\s*\d+", f"start_month = {start_month:02d}", c)
        c = re.sub(r"start_day\s*=\s*\d+", f"start_day = {start_day:02d}", c)
        c = re.sub(r"start_hour\s*=\s*\d+", f"start_hour = {start_hour:02d}", c)

        c = re.sub(r"end_year\s*=\s*\d+", f"end_year = {end_year}", c)
        c = re.sub(r"end_month\s*=\s*\d+", f"end_month = {end_month:02d}", c)
        c = re.sub(r"end_day\s*=\s*\d+", f"end_day = {end_day:02d}", c)
        c = re.sub(r"end_hour\s*=\s*\d+", f"end_hour = {end_hour:02d}", c)

        if run_hours is not None:
            c = re.sub(r"run_hours\s*=\s*\d+", f"run_hours = {run_hours}", c)

        self.contenido = c
        return self

    @staticmethod
    def _fmt_val(val) -> str:
        if isinstance(val, float):
            val_str = f"{val:.6f}".rstrip("0").rstrip(".") if "." in f"{val}" else f"{val}"
            if "." not in val_str:
                val_str += "."
            return val_str
        return str(val)

    def _insertar_en_fdda(self, c: str, param: str, val) -> str:
        """Inserta (o reemplaza) `param` dentro del bloque &fdda del namelist.

        Si el parámetro ya existe se reemplaza; si no, se agrega antes del cierre
        del bloque &fdda. Necesario para parámetros de fin de nudging
        (obs_idynin, obs_dtramp) que la plantilla puede no declarar explícitamente.
        """
        patron = rf"({param}\s*=\s*)[^,;\n]+"
        if re.search(patron, c):
            return re.sub(patron, rf"\g<1>{self._fmt_val(val)}", c)
        m = re.search(r"(&fdda\b.*?)(\n\s*/\s*)", c, flags=re.DOTALL)
        if not m:
            return c
        ins = f" {param:<35} = {self._fmt_val(val)},\n"
        pos = m.start(2)
        return c[:pos] + ins + c[pos:]

    def _poner_en_bloque(self, c: str, bloque: str, param: str, val_str: str) -> str:
        """Reemplaza `param` si existe (línea completa) o lo agrega al final del `&bloque`."""
        patron = rf"^([ \t]*{param}[ \t]*=[ \t]*)[^,;\n]+"
        if re.search(patron, c, flags=re.MULTILINE):
            return re.sub(patron, rf"\g<1>{val_str}", c, count=1, flags=re.MULTILINE)
        m = re.search(rf"(&{bloque}\b.*?)(\n[ \t]*/[ \t]*(?:\n|$))", c, flags=re.DOTALL)
        if not m:
            logger.warning(f"No se encontró el bloque &{bloque}; no se agregó {param}")
            return c
        ins = f"\n {param:<35} = {val_str},"
        return c[:m.end(1)] + ins + c[m.end(1):]

    def configurar_lectura_obs(self, end_h: int, interval_s: Optional[int] = None) -> "NamelistManager":
        """Configura la lectura del archivo OBS_DOMAIN101 (stream auxinput11) en &time_control.

        - `auxinput11_end_h` debe cubrir toda la ventana de nudging. Si no se declara,
          WRF usa su valor por defecto (6 h según la guía de namelist) y deja de leer
          observaciones antes de que termine una ventana de asimilación de 12 h.
        - `auxinput11_interval_s` debe tener la misma frecuencia que `obs_ionf` o mayor
          (guía de WRF): por defecto `obs_ionf * time_step` segundos. Se elimina
          `auxinput11_interval_m` para no declarar dos intervalos a la vez.
        """
        c = self.contenido
        m_dt = re.search(r"^[ \t]*time_step[ \t]*=[ \t]*(\d+)", c, flags=re.MULTILINE)
        m_ionf = re.search(r"^[ \t]*obs_ionf[ \t]*=[ \t]*(\d+)", c, flags=re.MULTILINE)
        dt = int(m_dt.group(1)) if m_dt else None
        ionf = int(m_ionf.group(1)) if m_ionf else 1
        if interval_s is None:
            interval_s = ionf * dt if dt else 180
        # quitar auxinput11_interval y auxinput11_interval_m (minutos) para evitar conflicto
        c = re.sub(r"^[ \t]*auxinput11_interval(?:_m)?[ \t]*=[^\n]*\n", "", c, flags=re.MULTILINE)
        c = self._poner_en_bloque(c, "time_control", "auxinput11_interval_s", str(int(interval_s)))
        c = self._poner_en_bloque(c, "time_control", "auxinput11_end_h", str(int(end_h)))
        self.contenido = c
        return self

    def configurar_diagnosticos(self) -> "NamelistManager":
        """Activa los diagnósticos de obs-nudging (IN4DOB, ERROB, NUDOB) en rsl.out.*.

        Sin estos mensajes no se puede comprobar que las observaciones se leen, que
        se calculan errores y que se aplican tendencias, ni cuándo se apaga el nudging.
        """
        c = self.contenido
        for p in ("obs_ipf_in4dob", "obs_ipf_errob", "obs_ipf_nudob"):
            c = self._poner_en_bloque(c, "fdda", p, ".true.")
        self.contenido = c
        return self

    def configurar_fdda(
        self,
        obs_nudge_opt: int = 1,
        obs_coef_temp: float = 0.0005,
        obs_coef_wind: float = 0.0005,
        obs_coef_mois: float = 0.0005,
        obs_rinxy: float = 50.0,
        obs_rinfxy: float = 500.0,
        obs_twindo: float = 1.0,
        obs_npfi: int = 30,
        obs_ionf: int = 1,
        max_obs: int = 10000,
        obs_idynin: Optional[int] = None,
        obs_dtramp: Optional[float] = None,
        obs_ipf_nudob: Optional[bool] = None,
    ) -> "NamelistManager":
        """Configura los parámetros del namelist &fdda para Observational Nudging.

        `obs_idynin` (inicialización dinámica) y `obs_dtramp` (rampa de salida del
        nudging, en minutos) son opcionales: por defecto (None) no se tocan y se
        mantiene el valor de la plantilla. En la guía de WRF, para el protocolo de
        separación temporal conviene revisar `obs_idynin=1` y una rampa `obs_dtramp`
        para que el nudging no siga pesando en el inicio del pronóstico libre.
        """
        c = self.contenido

        reemplazos = {
            "obs_nudge_opt": obs_nudge_opt,
            "obs_coef_temp": obs_coef_temp,
            "obs_coef_wind": obs_coef_wind,
            "obs_coef_mois": obs_coef_mois,
            "obs_rinxy": obs_rinxy,
            "obs_rinfxy": obs_rinfxy,
            "obs_twindo": obs_twindo,
            "obs_npfi": obs_npfi,
            "obs_ionf": obs_ionf,
            "max_obs": max_obs,
        }

        for param, val in reemplazos.items():
            val_str = self._fmt_val(val)
            patron = rf"({param}\s*=\s*)[^,;\n]+"
            if re.search(patron, c):
                c = re.sub(patron, rf"\g<1>{val_str}", c)

        if obs_idynin is not None:
            c = self._insertar_en_fdda(c, "obs_idynin", int(obs_idynin))
        if obs_dtramp is not None:
            c = self._insertar_en_fdda(c, "obs_dtramp", float(obs_dtramp))
        if obs_ipf_nudob is not None:
            # diagnostico de la guia de Reen: imprime en rsl.out.* cuando el nudging esta activo
            c = self._insertar_en_fdda(c, "obs_ipf_nudob", ".true." if obs_ipf_nudob else ".false.")

        self.contenido = c
        return self

    def guardar(self, output_path: str) -> Path:
        """Guarda el namelist modificado en la ruta especificada."""
        dst = Path(output_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(self.contenido, encoding="utf-8")
        logger.info(f"Namelist guardado en {dst}")
        return dst
