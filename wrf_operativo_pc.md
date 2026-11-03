# Configuración del WRF operativo en la PC (San Juan) - 03/11/2026

Informe técnico sobre la configuración con la que se ejecuta el WRF operativo en
`/home/pgich/wrf-operativo`, derivado de los scripts y namelists efectivamente
usados por el sistema (no de configuraciones experimentales).

## 1. Resumen ejecutivo

El operativo se lanza mediante `cron.bash`, que carga `env.bash`, crea los
directorios de trabajo y ejecuta `runEureka.bash`. Este descarga el GFS 0.25°,
corre WPS (`runWPS.bash`) y WRF (`runWRF.bash`), y luego genera mapas, datos
meteorológicos e informes.

La configuración operativa vigente es:

- Región **San Juan**, centrada en `-31.53, -68.53`.
- **Un solo dominio** (`max_dom = 1`), **600 x 600** puntos, **dx = dy = 1000 m**.
- **35 niveles verticales**, tope `p_top = 5000 Pa`.
- **48 horas** de pronóstico, salida cada **60 minutos**.
- Física: Thompson (mp=8), RRTMG (ra_lw/sw=4), Eta/MYJ (sf_sfclay=2),
  Noah (sf_surface=2), MYJ (bl_pbl=2), sin cúmulos (cu=0), BEP urbano
  (sf_urban=2).
- **Sin asimilación / sin nudging** de observaciones.
- Forzante **GFS 0.25°**, cada 3 h, 17 archivos para 48 h.

Advertencia importante: **no hay archivos `wrfout` del operativo de San Juan
guardados**. Las salidas archivadas en `salidas/wrfout/` corresponden a un
dominio distinto (`CEN_LAT=-23.411`, `CEN_LON=-58.368`) y son anteriores al
cambio de configuración a San Juan. Ver sección 6.

## 2. Cadena de ejecución

```
cron.bash
  -> source env.bash                 (variables de entorno y región)
  -> crearDirectorios.bash          (GFS, logs, mapas, meteo, wrfout, parte)
  -> runEureka.bash <fecha> <descarga>
       -> descarga_GFS025.py         (GFS 0.25° desde NOMADS)
       -> runWPS.bash <fecha>        (geogrid + ungrib + metgrid)
       -> runWRF.bash <fecha>        (real.exe + wrf.exe)
       -> productos_eureka.py        (mapas PNG)
       -> tabla_datos.py             (datos-meteo)
       -> gif*.py                    (animaciones)
```

Archivos clave:

| Etapa | Script | Namelist usado |
|---|---|---|
| Orquestación | `/home/pgich/wrf-operativo/ejecutables/cron.bash` | - |
| Entorno | `/home/pgich/wrf-operativo/ejecutables/env.bash` | - |
| WPS | `/home/pgich/wrf-operativo/ejecutables/runWPS.bash` | `datos/namelists/namelistTemp.wps` |
| WRF | `/home/pgich/wrf-operativo/ejecutables/runWRF.bash` | `datos/namelists/namelistTemp.input` |
| Descarga GFS | `/home/pgich/wrf-operativo/ejecutables/descarga_GFS025.py` | - |

`runWPS.bash` y `runWRF.bash` copian las plantillas `namelistTemp.*` a sus
respectivos directorios de ejecución y sustituyen fechas, coordenadas y
`RUN_HOURS` con `sed` antes de lanzar los binarios.

## 3. Región y dominio (env.bash + namelistTemp.wps)

Definido en `/home/pgich/wrf-operativo/ejecutables/env.bash`:

| Variable | Valor |
|---|---|
| `REGION` | `SAN_JUAN` |
| `CODIGO` | `A` |
| `REF_LAT` | `-31.53` |
| `REF_LON` | `-68.53` |
| `TRUELAT1` | `-31.53` |
| `TRUELAT2` | `-31.53` |
| `STAND_LON` | `-68.53` |
| `RUN_HOURS` | `48` |
| `NUM_FILES` | `17` |
| Bounding box región | lon `-70.50` a `-66.50`, lat `-33.00` a `-28.50` |
| Hilos OpenMP | `12` |
| Tiles WRF | `1 x 8` |

Parámetros de grilla en `namelistTemp.wps`:

| Parámetro | Valor |
|---|---|
| `wrf_core` | `ARW` |
| `max_dom` | `1` (solo d01) |
| `e_we` (d01) | `600` |
| `e_sn` (d01) | `600` |
| `dx`, `dy` | `1000 m` |
| `map_proj` | `lambert` |
| `ref_lat`, `ref_lon` | `-31.53`, `-68.53` |
| `truelat1`, `truelat2` | `-31.53`, `-31.53` |
| `stand_lon` | `-68.53` |
| `interval_seconds` | `10800` (3 h) |
| `geog_data_res` | `default` |
| `out_format` (ungrib) | `WPS` |
| `prefix` | `GFS` |
| `Vtable` | `Vtable.GFS` |

Nota: la plantilla contiene columnas para un segundo dominio, pero
`max_dom = 1` hace que el operativo corra **únicamente d01**.

## 4. Configuración de WRF (namelistTemp.input)

### 4.1 Time control

| Parámetro | Valor |
|---|---|
| `run_hours` | `RUN_HOURS` = `48` |
| `start_*` / `end_*` | calculados en `runWRF.bash` a partir de la fecha y `RUN_HOURS` |
| `interval_seconds` | `10800` |
| `history_interval` | `60` min |
| `frames_per_outfile` | `1000` |
| `restart` | `.false.` |
| `io_form_history` | `2` (NetCDF) |
| `history_outname` | `$WRF_WRFOUT/YYYY_MM/wrfout_d<domain>_<date>` |

### 4.2 Dominios

| Parámetro | Valor |
|---|---|
| `time_step` | `6 s` |
| `max_dom` | `1` |
| `e_we` | `600` |
| `e_sn` | `600` |
| `e_vert` | `35` |
| `dx`, `dy` | `1000 m` |
| `p_top_requested` | `5000 Pa` |
| `num_metgrid_levels` | `34` |
| `num_metgrid_soil_levels` | `4` |
| `feedback` | `1` |
| `smooth_option` | `0` |
| `sfcp_to_sfcp` | `.true.` |

### 4.3 Física

| Parámetro | Valor | Esquema |
|---|---|---|
| `mp_physics` | `8` | Thompson |
| `ra_lw_physics` | `4` | RRTMG |
| `ra_sw_physics` | `4` | RRTMG |
| `sf_sfclay_physics` | `2` | Eta similarity (MYJ) |
| `sf_surface_physics` | `2` | Noah LSM |
| `bl_pbl_physics` | `2` | MYJ |
| `cu_physics` | `0` | Sin cúmulos (explícito) |
| `sf_urban_physics` | `2` | BEP |
| `radt` | `4` min | Llamado de radiación |
| `cudt` | `5` min | Llamado de cúmulos (no usado) |
| `bldt` | `0` | PBL en cada paso |
| `ghg_input` | `1` | Gases de efecto invernadero RRTMG |
| `isfflx`, `ifsnow`, `icloud` | `1`, `1`, `1` | - |
| `num_soil_layers` | `4` | - |
| `num_land_cat` | `21` | MODIS |

### 4.4 Dinámica y bordes

| Parámetro | Valor |
|---|---|
| `w_damping` | `0` |
| `diff_opt` | `1` |
| `km_opt` | `4` (Smagorinsky 2D) |
| `diff_6th_opt` | `0` |
| `base_temp` | `290 K` |
| `damp_opt` | `0` |
| `non_hydrostatic` | `.true.` |
| `spec_bdy_width` | `5` |
| `spec_zone` | `1` |
| `relax_zone` | `4` |
| `specified` | `.true.` para d01 |
| `nested` | `.false.` |

### 4.5 Asimilación

El bloque `&fdda` está vacío y **no** se define `obs_nudge_opt`, por lo que el
operativo corre **sin nudging de observaciones**. Esto coincide con lo
observado en las salidas archivadas (`OBS_NUDGE_OPT = 0`).

## 5. Forzante y salidas

- **Fuente**: GFS 0.25° vía NOMADS (`descarga_GFS025.py`, `filter_gfs_0p25.pl`).
- **Frecuencia**: cada 3 h (`interval_seconds = 10800`).
- **Cantidad**: 17 archivos para 48 h (`NUM_FILES = 17`).
- **Salida WRF**: `$WRF_WRFOUT/YYYY_MM/wrfout_d01_<fecha>`; un archivo por hora
  de pronóstico (`history_interval = 60`, `frames_per_outfile = 1000`).
- **Productos**: mapas PNG en `salidas/mapas/`, datos en `salidas/datos-meteo/`,
  animaciones GIF y parte en `salidas/parte/`.

## 6. Hallazgos y advertencias

### 6.1 El `namelist.input` presente no es el operativo

El archivo que hoy está en
`/home/pgich/wrf-operativo/ejecutables/WRF/namelist.input` (y el symlink
`/home/pgich/Build_WRF/WRF/test/em_real/namelist.input`) muestra otra
configuración: `e_we=80`, `e_sn=60`, `dx=15000`, `use_adaptive_time_step=.true.`,
`time_step=90`, física con `-1` (suite). Esa es una corrida de **experimento**,
no el operativo. El operativo se regenera desde
`datos/namelists/namelistTemp.input` en cada ejecución de `runWRF.bash`, por lo
que ese archivo no debe usarse como fuente de verdad de la configuración
operativa.

### 6.2 No hay `wrfout` del operativo de San Juan

Se revisaron todas las salidas en `/home/pgich/wrf-operativo/salidas/wrfout/`
(`2025_03/` y `2025_09/`): **todas** tienen
`CEN_LAT = -23.411`, `CEN_LON = -58.368`, es decir, un dominio distinto al de
San Juan (`-31.53, -68.53`).

Además, `ejecutables/sanjuan/` contiene **solo** `env.bash`
(`REF_LAT=-31.121`, `REF_LON=-69.433`), sin salidas propias.

Los únicos dominios con `CEN_LAT ≈ -31.5` corresponden a corridas de
experimento, no al operativo:

- `ejecutables/WRF_casos_24h/` y `WRF_casos_24h/control/`: `dx=15000`,
  `DT=45`, `MAP_PROJ=3` (Mercator), `CEN_LAT=-31.5`, `CEN_LON=-68.5`.
- `wrf-modular-V1/outputs/runs/2026-09-24_0000z/sanjuan_0924__diag/control/`:
  idénticos parámetros.

### 6.3 Por qué las salidas archivadas no coinciden

`env.bash` fue modificado el **10/09/2025 09:25**, mientras que la última
corrida archivada (`salidas/logs/2025_09/09_06/`) es del **09/09/2025**. Es
decir, el `wrfout` de `2025_09` se generó **antes** de la configuración actual
de San Juan, con un dominio centrado en `-23.411, -58.368`.

### 6.4 Implicancia para la tesis

No es posible documentar diferencias control-vs-operativo con datos de San Juan,
porque el operativo no tiene salidas guardadas comparables. La comparación debe
formularse como **línea base controlada** (el control del framework de casos) y
no como una comparación contra el operativo. Las frases de las secciones 2.x y
3.3 que equiparan control y operativo deben reformularse en consecuencia.

## 7. Archivos de referencia

| Archivo | Rol |
|---|---|
| `/home/pgich/wrf-operativo/ejecutables/env.bash` | Región, coordenadas, `RUN_HOURS` |
| `/home/pgich/wrf-operativo/ejecutables/cron.bash` | Orquestación |
| `/home/pgich/wrf-operativo/ejecutables/runEureka.bash` | Descarga + WPS + WRF + productos |
| `/home/pgich/wrf-operativo/ejecutables/runWPS.bash` | WPS |
| `/home/pgich/wrf-operativo/ejecutables/runWRF.bash` | WRF |
| `/home/pgich/wrf-operativo/datos/namelists/namelistTemp.wps` | Plantilla WPS |
| `/home/pgich/wrf-operativo/datos/namelists/namelistTemp.input` | Plantilla WRF |
| `/home/pgich/wrf-operativo/salidas/logs/2025_09/09_06/wps.log` | Última corrida archivada (48 h, 2025-09-09 06Z a 2025-09-11 06Z) |
