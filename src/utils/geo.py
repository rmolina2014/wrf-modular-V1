"""Utilidades geográficas comunes (conversiones viento u/v)."""
import math


def uv_from_wswd(vel_viento_m_s: float, dir_grados_deg: float) -> tuple[float, float]:
    """Convierte velocidad/dirección a componentes u,v (convención meteorológica).

    Convención utilizada en Little_R, OBS_DOMAIN (FORMAT 105) y validación:
      u = -v * sin(rad)
      v = -v * cos(rad)
      donde v es velocidad (m/s), dir es dirección del viento (grados, 0° Norte).
    """
    if vel_viento_m_s is None or dir_grados_deg is None:
        return 0.0, 0.0
    try:
        v = float(vel_viento_m_s)
        d = float(dir_grados_deg)
    except (TypeError, ValueError):
        return 0.0, 0.0
    rad = math.radians(d)
    u = -v * math.sin(rad)
    v_comp = -v * math.cos(rad)
    return u, v_comp


def wswd_from_uv(u: float, v: float) -> tuple[float, float]:
    """Convierte componentes u,v a velocidad (m/s) y dirección (grados 0-360)."""
    if u is None or v is None:
        return 0.0, 0.0
    try:
        u_f = float(u)
        v_f = float(v)
    except (TypeError, ValueError):
        return 0.0, 0.0
    vel = math.hypot(u_f, v_f)
    if vel < 1e-10:
        return 0.0, 0.0
    ang = math.degrees(math.atan2(-u_f, -v_f))
    if ang < 0:
        ang += 360.0
    return vel, ang
