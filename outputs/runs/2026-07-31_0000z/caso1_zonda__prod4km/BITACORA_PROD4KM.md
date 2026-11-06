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

## Pendiente

- Completar nudged (lanzado 17:44:23, fin estimado ~21:05).
- Validacion +1..+24 h con `src/validacion/valida_wrf_cli.py`.
- Manifiesto nudged, tiempos/RSS finales y hashes de commit.
