"""Pruebas del protocolo de separación temporal (asimilación previa + pronóstico libre)."""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from src.asimilacion.obsnud_writer import ObsNudWriter
from src.casos.run_casos import _programa_temporal, _valid_times_protocolo, cobertura_obs
from src.modelo.namelist_manager import NamelistManager
from src.preflight.preflight import Estado, correr_preflight_observaciones
from pipeline_wrf import preparar_namelist


COMUN = {
    "ventana_asimilacion_h": 12,
    "horizonte_h": 24,
    "run_hours": 36,
    "hora_ciclo": "00",
    "obs_coef_wind": 0.0001,
    "obs_coef_temp": 0.0001,
    "obs_coef_mois": 0.0001,
}
CASO = {"id": "c1", "num": 1, "fecha": "2026-07-31", "t0": "2026-07-31T00:00:00Z"}


class TestProgramaTemporal(unittest.TestCase):
    def test_start_es_t0_menos_asim(self):
        p = _programa_temporal(COMUN, CASO)
        self.assertTrue(p["protocolo"])
        self.assertEqual(p["start"], datetime(2026, 7, 30, 12, 0, 0))
        self.assertEqual(p["t0"], datetime(2026, 7, 31, 0, 0, 0))
        self.assertEqual(p["run_hours"], 36)

    def test_valid_times_horizonte(self):
        p = _programa_temporal(COMUN, CASO)
        vt = _valid_times_protocolo(p["t0"], p["horizonte_h"])
        self.assertEqual(len(vt), 24)
        self.assertEqual(vt[0], "2026-07-31_01:00:00")
        self.assertEqual(vt[-1], "2026-08-01_00:00:00")

    def test_sin_protocolo_cae_a_clasico(self):
        p = _programa_temporal({"hora_ciclo": "00", "run_hours": 12}, {"fecha": "2026-05-16"})
        self.assertFalse(p["protocolo"])
        self.assertEqual(p["start"], datetime(2026, 5, 16, 0, 0, 0))
        self.assertEqual(p["run_hours"], 12)


class TestNamelistTemporal(unittest.TestCase):
    def test_obs_idynin_y_dtramp_insertados(self):
        with tempfile.TemporaryDirectory() as tmp:
            tpl = Path(tmp) / "nl.input"
            tpl.write_text("&fdda\n obs_nudge_opt = 1,\n obs_coef_temp = 0.0001,\n /\n", encoding="utf-8")
            mgr = NamelistManager(template_path=str(tpl))
            mgr.configurar_fdda(obs_nudge_opt=1, obs_idynin=1, obs_dtramp=360)
            self.assertIn("obs_idynin", mgr.contenido)
            self.assertIn("obs_dtramp", mgr.contenido)

    def test_preparar_namelist_fdda_end_igual_asim(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "namelist_nudged.input"
            start = datetime(2026, 7, 30, 12, 0, 0)
            preparar_namelist("namelist.input", 1, out, start_dt=start,
                              run_hours=36, asim_hours=12)
            txt = out.read_text(encoding="utf-8")
            self.assertIn("run_hours = 36", txt)
            self.assertIn("fdda_end = 720", txt)
            import re
            self.assertIn("start_hour", txt)


class TestCoberturaVentana(unittest.TestCase):
    def test_ventana_asimilacion(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv = Path(tmp) / "hist.csv"
            # Dos registros: uno dentro de [t0-12h, t0], uno despues de t0.
            ts_in = int(datetime(2026, 7, 30, 18, 0, 0).replace(tzinfo=__import__("datetime").timezone.utc).timestamp())
            ts_out = int(datetime(2026, 7, 31, 3, 0, 0).replace(tzinfo=__import__("datetime").timezone.utc).timestamp())
            with open(csv, "w", encoding="utf-8") as f:
                f.write("estacion,fecha,hora_unix,temp_c\n")
                f.write(f"EST_A,2026-07-30,{ts_in},20.0\n")
                f.write(f"EST_B,2026-07-31,{ts_out},21.0\n")
            cov = cobertura_obs(csv, "2026-07-31", "12", 36,
                                t0_iso="2026-07-31T00:00:00Z", asim_horas=12)
            self.assertEqual(cov["ventana"], 1)
            self.assertEqual(cov["estaciones"], 1)


def _obs_domain101(path, timestamps):
    """Escribe un OBS_DOMAIN101 mínimo (5 líneas por registro)."""
    with open(path, "w", encoding="utf-8") as f:
        for ts in timestamps:
            f.write(f" {ts}\n")
            f.write("   -31.6500  -68.5833 \n")
            f.write("  INTA_POCITO                                SURFACE                                    \n")
            f.write("  FM-12 SYNOP       INTA_POCITO            615  F     F         1\n")
            f.write(" -888888.000 -888888.000 -888888.000 -888888.000     615.000       0.000"
                    "     288.150       0.000      -0.000     129.000       2.778     129.000"
                    "      50.000       0.000   94000.000       0.000 -888888.000 -888888.000\n")


class TestPreflightSeparacion(unittest.TestCase):
    def test_falla_si_hay_obs_posterior_a_t0(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            obsdomain = tmp / "OBS_DOMAIN101"
            # Una obs dentro de la ventana y otra DESPUES de t0 (fuga).
            _obs_domain101(obsdomain, ["20260730180000", "20260731060000"])
            namelist = tmp / "namelist_nudged.input"
            namelist.write_text("run_hours = 36,\nfdda_end = 720,\nobs_nudge_opt = 1,\n", encoding="utf-8")
            obs_json = tmp / "obs.json"
            obs_json.write_text("[]", encoding="utf-8")
            informe = correr_preflight_observaciones(
                obs_json, obsdomain, namelist,
                start_dt=datetime(2026, 7, 30, 12, 0, 0),
                t0=datetime(2026, 7, 31, 0, 0, 0), asim_horas=12, horizonte_h=24,
            )
            chequeo = [c for c in informe.chequeos if c.id == "2.2.8"][0]
            self.assertEqual(chequeo.estado, Estado.BLOQUEANTE)

    def test_ok_cuando_ventana_respetada(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            obsdomain = tmp / "OBS_DOMAIN101"
            _obs_domain101(obsdomain, ["20260730130000", "20260730230000"])
            namelist = tmp / "namelist_nudged.input"
            namelist.write_text("run_hours = 36,\nfdda_end = 720,\nobs_nudge_opt = 1,\n", encoding="utf-8")
            obs_json = tmp / "obs.json"
            obs_json.write_text("[]", encoding="utf-8")
            informe = correr_preflight_observaciones(
                obs_json, obsdomain, namelist,
                start_dt=datetime(2026, 7, 30, 12, 0, 0),
                t0=datetime(2026, 7, 31, 0, 0, 0), asim_horas=12, horizonte_h=24,
            )
            chequeo = [c for c in informe.chequeos if c.id == "2.2.8"][0]
            self.assertEqual(chequeo.estado, Estado.OK)


if __name__ == "__main__":
    unittest.main()
