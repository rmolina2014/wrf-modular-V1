"""Pruebas de la lectura de OBS_DOMAIN101 (auxinput11) y diagnósticos de nudging."""

import tempfile
import unittest
from pathlib import Path

from src.modelo.namelist_manager import NamelistManager
from src.preflight.preflight import ChequeosObservaciones, Estado, InformePreflight

BASE = """ &time_control
 run_hours                           = 36,
 auxinput11_interval_m               = 30,
 auxinput11_inname                   = "OBS_DOMAIN101",
 /

 &domains
 time_step                           = 45,
 time_step_fract_num                 = 0,
 /

 &fdda
 grid_fdda                           = 0,
 obs_nudge_opt                       = 1,
 obs_ionf                            = 1,
 obs_ipf_in4dob                      = .true.,
 fdda_end                            = 720,
 /
"""


def _mgr(texto=BASE) -> NamelistManager:
    p = Path(tempfile.mkdtemp()) / "namelist.input"
    p.write_text(texto, encoding="utf-8")
    return NamelistManager(template_path=str(p))


def _preflight_2229(texto: str):
    nl = Path(tempfile.mkdtemp()) / "namelist.input"
    nl.write_text(texto, encoding="utf-8")
    chk = ChequeosObservaciones(Path("x.json"), Path("OBS_DOMAIN101"), nl, None, {})
    inf = InformePreflight(caso="t")
    chk.check_2229_lectura_observaciones(inf)
    return [c for c in inf.chequeos if c.id == "2.2.9"][0]


class TestConfigurarLecturaObs(unittest.TestCase):
    def test_agrega_end_h_y_intervalo_s(self):
        c = _mgr().configurar_lectura_obs(end_h=12).contenido
        self.assertRegex(c, r"auxinput11_end_h\s*=\s*12,")
        self.assertRegex(c, r"auxinput11_interval_s\s*=\s*45,")   # obs_ionf(1) * time_step(45)
        self.assertNotIn("auxinput11_interval_m", c)
        self.assertIn('auxinput11_inname', c)

    def test_respeta_obs_ionf(self):
        c = _mgr(BASE.replace("obs_ionf                            = 1", "obs_ionf                            = 4")
                 ).configurar_lectura_obs(end_h=12).contenido
        self.assertRegex(c, r"auxinput11_interval_s\s*=\s*180,")

    def test_idempotente(self):
        m = _mgr().configurar_lectura_obs(end_h=12).configurar_lectura_obs(end_h=12)
        self.assertEqual(m.contenido.count("auxinput11_end_h"), 1)
        self.assertEqual(m.contenido.count("auxinput11_interval_s"), 1)

    def test_actualiza_end_h_existente(self):
        m = _mgr().configurar_lectura_obs(end_h=6).configurar_lectura_obs(end_h=12)
        self.assertRegex(m.contenido, r"auxinput11_end_h\s*=\s*12,")
        self.assertNotRegex(m.contenido, r"auxinput11_end_h\s*=\s*6,")

    def test_no_toca_time_step_fract_num(self):
        c = _mgr().configurar_lectura_obs(end_h=12).contenido
        self.assertRegex(c, r"time_step_fract_num\s*=\s*0,")

    def test_diagnosticos(self):
        c = _mgr().configurar_diagnosticos().contenido
        for p in ("obs_ipf_in4dob", "obs_ipf_errob", "obs_ipf_nudob"):
            self.assertRegex(c, rf"{p}\s*=\s*\.true\.,")
        self.assertEqual(c.count("obs_ipf_in4dob"), 1)
        # los parámetros nuevos quedan dentro de &fdda
        self.assertLess(c.index("&fdda"), c.index("obs_ipf_errob"))


class TestPreflight2229(unittest.TestCase):
    def test_sin_end_h_bloquea(self):
        self.assertEqual(_preflight_2229(BASE.replace(" auxinput11_interval_m               = 30,\n", "")).estado,
                         Estado.BLOQUEANTE)

    def test_end_h_menor_que_fdda_end_bloquea(self):
        m = _mgr().configurar_lectura_obs(end_h=6)
        self.assertEqual(_preflight_2229(m.contenido).estado, Estado.BLOQUEANTE)

    def test_correcto_ok(self):
        m = _mgr().configurar_lectura_obs(end_h=12)
        self.assertEqual(_preflight_2229(m.contenido).estado, Estado.OK)

    def test_intervalo_30min_advierte(self):
        txt = BASE.replace("/\n\n &domains", " auxinput11_end_h = 12,\n /\n\n &domains", 1)
        self.assertEqual(_preflight_2229(txt).estado, Estado.ADVERTENCIA)

    def test_sin_nudging_no_aplica(self):
        self.assertEqual(_preflight_2229(BASE.replace("obs_nudge_opt                       = 1",
                                                      "obs_nudge_opt                       = 0")).estado,
                         Estado.OK)


if __name__ == "__main__":
    unittest.main()
