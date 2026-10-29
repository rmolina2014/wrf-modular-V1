# Configuración del WRF operativo (PGICH) - 29/10/2026

## 1) Namelists utilizados por el sistema operativo

### WRF operativo diario (sin asimilación)
- **Ruta**: `/home/pgich/wrf-operativo/ejecutables/WRF/namelist.input`
- `obs_nudge_opt = 0` (nudging de observaciones apagado)
- `grid_fdda = 0`
- `run_hours = 12` (en este namelist por defecto; `runWRF.bash` calcula `end_date = start_date + RUN_HOURS` usando `RUN_HOURS=48` de `env.bash`)
- `fdda_end = 720`, `gfdda_end_h = 12`
- `auxinput11_interval_m = 30`, `auxinput11_inname = "OBS_DOMAIN101"` (configurado, pero no usado con `obs_nudge_opt=0`)

### WRF para casos / framework con asimilación
- **Ruta**: `/home/pgich/wrf-operativo/ejecutables/WRF_casos_24h/namelist.input`
- `obs_nudge_opt = 1` (nudging de observaciones activo)
- `auxinput11` configurado, `OBS_DOMAIN101` presente
- Usado por el framework modular de casos (`src/casos/run_casos.py`)

### Templates
- **WRF**: `/home/pgich/wrf-operativo/datos/namelists/namelistTemp.input`
- **WPS**: `/home/pgich/wrf-operativo/datos/namelists/namelistTemp.wps` (y `sanjuan/namelistTemp.*`)
- **Scripts**: `runWPS.bash` usa `namelistTemp.wps`, `runWRF.bash` usa `namelistTemp.input`

## 2) Versión de WRF/WPS

- **WRF**: WRF-ARW 4.5 (referenciado en código/tests del repo). Binarios en `/home/pgich/wrf-operativo/ejecutables/WRF/wrf.exe`, `/home/pgich/wrf-operativo/ejecutables/WRF_casos_24h/wrf.exe`. Symlink apunta a `/home/pgich/Build_WRF/WRF/test/em_real/wrf.exe`. Builds experimentales en `/home/pgich/wrf-operativo/ejecutables/WRF_EXP/*/`.
- **WPS**: Builds presentes en `/home/pgich/Build_WRF/WPS*` (incluido `WPS-SERIAL`). Se usa con `namelistTemp.wps` desde los scripts operativos.

## 3) Condiciones iniciales y de borde

- **Fuente de datos**: GFS 0.25° (`WRF_GFS=$WRF_DATA/datos/GFS025`). Descarga vía `descarga_GFS025.py` / `get_GFSX025_grib2.py` (AWS/NOMADS según configuración).
- **Intervalo de condiciones de borde**: `interval_seconds = 10800` (cada 3 horas)
- **Ciclos inicializados**: Según cron (`cron.bash`) - típicamente ciclos GFS operativos
- **Longitud de pronóstico**: 
  - **Operativo diario**: `RUN_HOURS=48` en `/home/pgich/wrf-operativo/ejecutables/env.bash`. `runWRF.bash` configura `end_date = start_date + RUN_HOURS`
  - **Protocolo de casos (repo)**: inicio 12h antes de t0, integración 36h (coherente con `run_hours=36` y `fdda_end=720 min`)
- **Asimilación**: 
  - **Operativo diario actual**: `obs_nudge_opt=0` (sin asimilación)
  - **Sistema con capacidad de asimilación**: Sí. `WRF_casos_24h/namelist.input` tiene `obs_nudge_opt=1`, `OBS_DOMAIN101` presente, configuración `auxinput11` para nudging observacional. Existen experimentos en `WRF_EXP/` con nudging.

## 4) Dominio

**Único dominio (max_dom=1) - Ambos configuraciones (operativo y casos)**

| Parámetro | Valor |
|-----------|-------|
| Resolución horizontal (dx, dy) | 15000 m (15 km) |
| Puntos de grilla (e_we × e_sn) | 80 × 60 |
| Niveles verticales (e_vert) | 35 |
| Proyección | Lambert Conformal |
| Centro (ref_lat, ref_lon) | -31.53, -68.53 |
| Truelat1, truelat2 | -31.53, -31.53 |
| Stand_lon | -68.53 |
| Parent grid ratio | 1 |
| Grid ID | 1 |

## 5) Física y configuración adicional

- **Physics suite**: `CONUS` (en namelist operativo WRF/)
- **Time step**: adaptativo (`use_adaptive_time_step = .true.`), inicial 90s, rango 5-120s
- **Vertical levels**: 35 niveles, `p_top_requested = 5000 Pa`
- **Metgrid levels**: `num_metgrid_levels = 34`

**Nota**: La configuración operativa diaria (`WRF/`) corre **sin nudging observacional**. El framework modular de casos y `WRF_casos_24h` sí utiliza nudging observacional (`obs_nudge_opt=1`).
