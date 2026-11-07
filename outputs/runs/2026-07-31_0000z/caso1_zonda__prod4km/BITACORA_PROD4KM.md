# Bitacora EXPERIMENTO prod4km - Caso 1 Zonda 2026-07-31

Rama: `prod4km` (creada desde `origin/op15km`, HEAD `73cc427ed7feb9677703e92537c04bb646423e83`).
Directorio: `outputs/runs/2026-07-31_0000z/caso1_zonda__prod4km/`.

## Protocolo temporal

- t0 = `2026-07-31_00:00:00` UTC.
- Arranque de ambas corridas: t0 - 12 h = `2026-07-30_12:00:00`.
- Duracion: 36 h, hasta `2026-08-01_00:00:00`.
- Evaluacion: +1 a +24 h desde t0.
- GFS 0.25: 13 archivos cada 3 h, `2026-07-30_12` a `2026-08-01_00`.

## PASO 0 - Namelists de la ultima corrida operativa

Copias textuales con `cp -L` en `documentacion_proyecto/prod_namelists_ultimo/`.
No se interpretaron ni editaron. Fechas y sha256 en `FECHAS.txt`.

- `/home/pgich/namelist_ultimo.wps` -> `Build_WRF/WPS/namelist.wps`
  (mtime destino 2025-03-21 12:42:34 -0300).
- `/home/pgich/namelist_ultimo.input` -> `Build_WRF/WRF/test/em_real/namelist.input`
  (mtime destino 2026-08-14 10:56:38 -0300).

## Configuracion usada

Renderizada por `scripts/prod4km/render_namelists.py` desde las plantillas
operativas de `/home/pgich/wrf-operativo/datos/namelists/sanjuan/`.
Verificacion automatica: `informes/namelist_check.json` (OK en ambos brazos).

Parametros comunes: `max_dom=1`, `e_we=141`, `e_sn=200`, `dx=dy=4000`,
`map_proj=lambert`, `ref_lat=ref_lon=truelat1=truelat2=-31.121`,
`stand_lon=-69.433`, `geog_data_res='default'`,
`geog_data_path=/home/pgich/wrf-operativo/datos/WPS_GEOG`, `time_step=15`,
`e_vert=35`, `p_top_requested=5000`, `num_metgrid_levels=34`,
`num_metgrid_soil_levels=4`, `history_interval=60`, `frames_per_outfile=1`,
`run_hours=36`, `interval_seconds=10800`.

Fisica/dinamica exactamente la de la plantilla operativa: `mp=8`, `ra_lw=1`,
`ra_sw=2`, `radt=4`, `sf_sfclay=2`, `sf_surface=2`, `bl_pbl=2`, `bldt=0`,
`cu=0`, `cudt=5`, `isfflx=1`, `ifsnow=1`, `icloud=1`,
`surface_input_source=1`, `num_soil_layers=4`, `num_land_cat=21`,
`sf_urban=0`, `diff_opt=1`, `km_opt=4`, `diff_6th_opt=0`, `damp_opt=0`,
`w_damping=0`, `khdif=0`, `kvdif=0`, `non_hydrostatic=.true.`,
`moist_adv_opt=1`, `scalar_adv_opt=1`, `spec_bdy_width=5`, `spec_zone=1`,
`relax_zone=4`.

### Diferencias declaradas respecto de la plantilla operativa

1. `num_metgrid_levels=34` (la plantilla dice 32; el GFS 0.25 de este caso
   tiene 34 niveles). Sin este cambio real.exe no es consistente con met_em.
2. `frames_per_outfile=1` (la plantilla dice 1000). El validador de la tesis
   `src/validacion/valida_wrf_cli.py` busca un archivo por hora con nombre
   `wrfout_d01_YYYY-MM-DD_HH:MM:SS`; se conserva el formato de salida de la tesis.
3. `history_outname` apunta a `control/` y `nudged/` de este caso.
4. Brazo nudged: bloque `&fdda` con `obs_nudge_opt=1`, `fdda_end=720`,
   `obs_coef_wind/temp/mois=0.0001`, `obs_rinxy=50`, `obs_sfcfacr=2.0`,
   y `auxinput11_interval_m=30`, `auxinput11_inname="OBS_DOMAIN101"`.
   No se nudgea PSFC (WRF no lo soporta). El control deja `&fdda` vacio.

## WPS

- `geogrid.exe`, `ungrib.exe`, `metgrid.exe` del build `/home/pgich/Build_WRF/WPS`.
- Dominio verificado en `geo_em.d01.nc`: `MAP_PROJ=1` (Lambert),
  `CEN_LAT=-31.120998`, `CEN_LON=-69.43298`, `DX=DY=4000`,
  masa 140x199, staggered 141x200, 21 categorias de suelo.
- `met_em.d01.*`: 13 tiempos (12Z 30-jul a 00Z 01-ago), 34 niveles.
- Logs: `wps/geogrid.log`, `wps/ungrib.log`, `wps/metgrid.log`.

## real.exe

- Ejecutado con el namelist de control en `real/`.
- Salida: `real/wrfinput_d01` (29 MB) y `real/wrfbdy_d01` (42 MB).
- `real.log` termina con `real_em: SUCCESS COMPLETE REAL_EM INIT`.
- Mensaje no bloqueante en el log: `ERROR: ghg_input available only for these
  radiation schemes: CAM, RRTM, RRTMG, RRTMG_fast` (la plantilla trae
  `ghg_input=0`; no afecta la corrida).

## Lanzamiento

- Binario: `/home/pgich/Build_WRF/WRF/test/em_real/wrf.exe` (destino de los
  symlinks de `/home/pgich/wrf-operativo/ejecutables/WRF_casos_24h/`).
- `OMP_NUM_THREADS=1`, un tile (1x1), igual que la corrida op15km que completo
  con este binario. El `env.bash` operativo define OMP=22; se registra el valor
  usado para trazabilidad. No se modifico el namelist.
- `GFORTRAN_UNBUFFERED_ALL=1` solo para que el log sea legible en tiempo real.

## PASO 4 - Piloto de costo (control)

Medicion sobre los primeros 100 pasos (`control/pilot_projection_control.json`):

- Primer paso: 7.135 s (incluye inicializacion de tablas Thompson).
- Media pasos 2..100: 1.3723 s/paso.
- Proyeccion a 8640 pasos: 3.293 h (< 6 h). Se continua sin cambios.
- Pico RSS observado: ~3.47 GB (`VmHWM`); hilos: 1.
- Las tablas Thompson (`qr_acr_qg_V4.dat`, `qr_acr_qsV2.dat`, `freezeH2O.dat`)
  se calcularon una vez y se reutilizan en el brazo nudged.

## Resultado control

- Inicio 2026-11-06 14:24:43, fin 17:44:08; `elapsed_wall_s=11965.22`.
- 8640 pasos, media 1.3604 s/paso, 37 wrfout (12Z 30-jul a 00Z 01-ago).
- Pico RSS 3.80 GB (`maximum_resident_set_size_kbytes=3797716`), 1 hilo.
- `exit_status=0`, sin senal, sin corte. Log: `control/wrf_control.log`.
- Sanidad en t0 y +24 h: sin NaN en T2/PSFC/U10/V10/QVAPOR;
  T2 253.5-294.7 K en t0 y 246.2-301.2 K en +24 h.
- Manifiesto: `control_manifest.json` (sha256 del namelist incluido).

## PASO 5 - Alturas del modelo en las estaciones

`informes/PASO5_alturas_estaciones.csv` (misma geo_em para ambos brazos).
Columnas: altura real, vecino de grilla, interpolacion lineal, y deltas.
Deltas grandes a reportar sin corregir: CARACOLES +386 m, PUNTA_NEGRA +244 m,
INTA_SANMARTIN +121 m; el resto entre -23 y +46 m (interpolado).

## Resultado nudged

- Inicio 2026-11-06 17:44:23, fin 20:58:26; `elapsed_wall_s=11643.34`.
- 8640 pasos, media 1.3466 s/paso, 37 wrfout (12Z 30-jul a 00Z 01-ago).
- Pico RSS 3.84 GB (`maximum_resident_set_size_kbytes=3840056`), 1 hilo.
- `exit_status=0`, sin senal, sin corte. Log: `nudged/wrf_nudged.log`.
- Sanidad en +24 h: sin NaN en T2/PSFC/U10/V10/QVAPOR.
- Manifiesto: `nudged_manifest.json` (sha256 del namelist y de OBS_DOMAIN101).

### Corte del nudging

El ultimo incremento con observaciones ocurre en `XTIME=720.00` (t0) y afecta
al paso que termina a las `2026-07-31_00:00:15`; despues no aparecen mas lineas
`OBS NUDGING`/`CALL IN4DOB`. El sobrepaso es de 15 s (un dt) y queda fuera de la
ventana evaluada (+1 a +24 h).

## Validacion +1..+24 h

Ejecutada con `/home/pgich/anaconda3/bin/python3 src/validacion/valida_wrf_cli.py`
(24 tiempos, `--t0 2026-07-31T00:00:00 --horizon-h 24`,
`--obs-json data/raw/obs_flat_20260731.json`).
`returncode=0`; `errores_largo.csv` tiene 748 filas (24 horizontes, 8 estaciones,
4 variables; N menor en algunos tramos por datos faltantes).
Salidas: `errores_largo.csv`, `metricas_por_horizonte.csv`,
`metricas_por_tramo.csv`, `informe_evolucion_nudging.txt`,
`tabla_evolutiva.json`.

RMSE por variable y tramo (prod4km):

| variable | tramo | n | control | nudged | persistencia |
|---|---|---:|---:|---:|---:|
| t2 | +1-6h | 42 | 4.899 | 4.759 | 2.880 |
| t2 | +7-12h | 42 | 7.439 | 7.417 | 5.452 |
| t2 | +13-18h | 42 | 4.236 | 4.240 | 9.592 |
| t2 | +19-24h | 37 | 2.484 | 2.479 | 8.278 |
| rh | +1-6h | 42 | 42.149 | 40.265 | 7.223 |
| rh | +7-12h | 42 | 55.106 | 54.864 | 21.540 |
| rh | +13-18h | 42 | 23.490 | 23.500 | 46.121 |
| rh | +19-24h | 37 | 3.695 | 3.704 | 54.715 |
| psfc | +1-6h | 48 | 16.627 | 16.591 | 1.455 |
| psfc | +7-12h | 48 | 16.517 | 16.517 | 2.706 |
| psfc | +13-18h | 48 | 15.795 | 15.780 | 2.227 |
| psfc | +19-24h | 43 | 12.785 | 12.780 | 3.131 |
| wspd | +1-6h | 42 | 6.957 | 7.036 | 0.426 |
| wspd | +7-12h | 42 | 12.286 | 12.304 | 0.975 |
| wspd | +13-18h | 42 | 12.556 | 12.543 | 5.085 |
| wspd | +19-24h | 37 | 8.368 | 8.543 | 3.622 |

Lectura sin sobreinterpretar: el nudging mejora T2 en 3 de 4 tramos (maximo
-0.14 K), mejora RH en +1-6h (+7-12h) y es neutro despues; en viento queda
levemente peor en 3 de 4 tramos (maximo +0.17 m/s). La persistencia es una linea
base de referencia, no un pronostico, y domina en +1-6h. El sesgo de PSFC del
modelo es ~-11.9 hPa y no se corrigio por altura; los deltas de terreno del
PASO 5 son parte del contexto.

## Comparacion con op15km (misma fecha, configuracion de tesis)

`informes/comparacion_op15km_prod4km.csv`. RMSE nudged/control:

| variable | tramo | prod4km control | prod4km nudged | op15km control | op15km nudged |
|---|---|---:|---:|---:|---:|
| t2 | +1-6h | 4.899 | 4.759 | 5.861 | 5.589 |
| t2 | +7-12h | 7.439 | 7.417 | 7.766 | 7.786 |
| t2 | +13-18h | 4.236 | 4.240 | 6.669 | 6.657 |
| t2 | +19-24h | 2.484 | 2.479 | 4.356 | 4.367 |
| rh | +1-6h | 42.149 | 40.265 | 35.736 | 33.588 |
| rh | +7-12h | 55.106 | 54.864 | 43.927 | 43.803 |
| rh | +13-18h | 23.490 | 23.500 | 22.050 | 22.091 |
| rh | +19-24h | 3.695 | 3.704 | 4.677 | 4.716 |
| psfc | +1-6h | 16.627 | 16.591 | 59.037 | 58.989 |
| psfc | +7-12h | 16.517 | 16.517 | 59.197 | 59.166 |
| psfc | +13-18h | 15.795 | 15.780 | 58.470 | 58.439 |
| psfc | +19-24h | 12.785 | 12.780 | 43.108 | 43.105 |
| wspd | +1-6h | 6.957 | 7.036 | 2.861 | 2.706 |
| wspd | +7-12h | 12.286 | 12.304 | 6.621 | 6.483 |
| wspd | +13-18h | 12.556 | 12.543 | 8.468 | 8.224 |
| wspd | +19-24h | 8.368 | 8.543 | 9.544 | 9.578 |

En esta comparacion directa, prod4km mejora T2 (0.3-2.4 K de RMSE) y PSFC
(30-43 hPa) respecto de op15km, pero empeora RH en +1-6h/+7-12h (6-11 puntos)
y viento en +1-18h (4-6 m/s). Son corridas con resolucion y fisica distintas;
la tabla no aísla la causa.

## Entregables

- Namelists y plantillas PASO 0: `documentacion_proyecto/prod_namelists_ultimo/`.
- WPS/real/logs: `wps/`, `real/`.
- Manifiestos: `control_manifest.json`, `nudged_manifest.json`.
- Tiempos/RSS: `control/wrf_control.log.time`, `nudged/wrf_nudged.log.time`,
  `monitor_*.json`, `*.trace.log`.
- Validacion: CSVs, `informe_evolucion_nudging.txt`, `tabla_evolutiva.json`.
- PASO 5: `informes/PASO5_alturas_estaciones.csv`.
- Scripts reproducibles: `scripts/prod4km/`.

## Checkpoints de la rama

- `9cee00d4390db05e8f467e491b24864082e85b1a`: WPS 4 km, real y piloto.
- `fb3534ab83cf91786075283d1a53621730857791`: control completado y manifiesto.
- Commit de resultados finales: el HEAD de `prod4km` que contiene esta bitacora.
