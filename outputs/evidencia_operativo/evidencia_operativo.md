# Evidencia: configuración del WRF operativo PGICH y de las corridas de la tesis

- Recolectado: 2026-11-04 ~10:54–11:10 (-03), usuario `pgich`, host `idih48-wrf`.
- Modo: solo lectura sobre `/home/pgich/wrf-operativo`. No se modificó, movió ni borró nada ahí. No se ejecutaron `wrf.exe` ni `real.exe`. No se hizo commit.
- Las copias se hicieron con `cp -p` (conservan el mtime) y se verificaron byte a byte con `cmp` contra el original (todas idénticas).
- Las fechas son mtime (`stat -c %y`), zona -0300.

---

## 1. Copias de archivos del operativo

**Nota:** `cron.bash`, `runEureka.bash`, `runWPS.bash` y `runWRF.bash` **no existen en la raíz** `/home/pgich/wrf-operativo` (`stat`: "No existe el fichero o el directorio"). Están en `/home/pgich/wrf-operativo/ejecutables/`. Esas son las versiones que se copiaron.

| Original (ruta absoluta) | mtime | Bytes | Copia | sha256 |
|---|---|---|---|---|
| /home/pgich/wrf-operativo/datos/namelists/namelistTemp.wps | 2025-03-21 12:42:34 | 1428 | namelistTemp.wps | 845eb27d…a3d |
| /home/pgich/wrf-operativo/datos/namelists/namelistTemp.input | 2025-03-21 12:42:55 | 4710 | namelistTemp.input | 4c98f2a6…7f5 |
| /home/pgich/wrf-operativo/ejecutables/env.bash | 2026-09-10 09:25:10 | 2236 | env.bash | 72645ab6…2f4 |
| /home/pgich/wrf-operativo/ejecutables/sanjuan/env.bash | 2023-10-24 12:04:29 | 2045 | sanjuan/env.bash | 29933cd0…bd |
| /home/pgich/wrf-operativo/ejecutables/cron.bash | 2023-10-30 14:19 | 2410 | cron.bash | eedebeb6…e98 |
| /home/pgich/wrf-operativo/ejecutables/runEureka.bash | 2025-03-20 22:49 | 2955 | runEureka.bash | 61f9be2e…df |
| /home/pgich/wrf-operativo/ejecutables/runWPS.bash | 2025-03-20 09:07 | 1776 | runWPS.bash | 391771cd…bd |
| /home/pgich/wrf-operativo/ejecutables/runWRF.bash | 2025-03-20 09:10 | 3176 | runWRF.bash | 29c96a63…bd |

Otros archivos relacionados que existen en `ejecutables/` y **no** se copiaron (solo se listaron): `cron.bash.save` (2023-10-24), `cron_test.bash` (2023-10-24), `crearDirectorios.bash`, `limpiar.bash`, `log.cron`.

## 2. Qué env.bash usa el cron y valores finales

Cadena, tal como está escrita en los scripts:

- `ejecutables/cron.bash:18`: `source env.bash`. Es una ruta **relativa**, así que depende del directorio de trabajo desde el que se invoque `cron.bash`.
- `cron.bash` también invoca `./crearDirectorios.bash` (l.25), `./runEureka.bash` (l.33) y `./limpiar.bash` (l.75) con rutas relativas. Esos tres archivos solo existen en `/home/pgich/wrf-operativo/ejecutables/`. `ejecutables/sanjuan/` contiene únicamente `env.bash`.
- `runEureka.bash`, `runWPS.bash` y `runWRF.bash` **no** hacen `source` de ningún env.bash. Usan las variables exportadas por `cron.bash`.
- No hay crontab activo (ver punto 3), así que no se pudo confirmar el `cd` ni la línea de invocación real.

Según la cadena de scripts, el archivo que resuelve `source env.bash` cuando se corre desde `ejecutables/` es **/home/pgich/wrf-operativo/ejecutables/env.bash** (mtime 2026-09-10 09:25:10). Valores literales:

| Variable | ejecutables/env.bash (línea) | ejecutables/sanjuan/env.bash (línea), solo como referencia |
|---|---|---|
| REF_LAT | `-31.53` (l.29) | `-31.121` (l.25) |
| REF_LON | `-68.53` (l.30) | `-69.433` (l.26) |
| RUN_HOURS | `48` (l.25; l.23 comentada `#export RUN_HOURS=48`) | `48` (l.22) |
| REGION | `SAN_JUAN` (l.27) | `CUYO` (l.23) |
| TRUELAT1 / TRUELAT2 / STAND_LON | `-31.53` / `-31.53` / `-68.53` | `-31.121` / `-31.121` / `-69.433` |
| REGION_LON_MIN/MAX, LAT_MIN/MAX | `-70.50` / `-66.50`, `-33.00` / `-28.50` | `-69.4` / `-69`, `-31.1` / `-31` |
| NUM_FILES | `17` | `17` |
| OMP_NUM_THREADS | `12` | `22` |

Cómo se define el dominio. Esto es lo que dicen los scripts, sin interpretación:
- `runWPS.bash:35-39` reemplaza en `namelistTemp.wps` los textos `REF_LAT`, `REF_LON`, `TRUELAT1`, `TRUELAT2` y `STAND_LON` con las variables de entorno del mismo nombre.
- `REGION` (`SAN_JUAN`) se usa en `runEureka.bash:85` (`--configuracion $REGION'_'$CODIGO'_'...`) para el postproceso. No aparece en los namelists.
- El tamaño y la resolución del dominio están fijos en la plantilla, no vienen de variables: `namelistTemp.wps` tiene `e_we = 600, 112,`, `e_sn = 600, 97,`, `dx = 1000,`, `dy = 1000,`, `map_proj = 'lambert'` y `max_dom = 1`. `namelistTemp.input` tiene `e_we = 600, 112, 94,`, `e_sn = 600, 97, 91,`, `dx = 1000, 10000, 3333.33,` y `time_step = 6,`.
- `RUN_HOURS` se sustituye en `namelistTemp.input` (`runWRF.bash:62`) y se usa para calcular `end_date` (`runWPS.bash:18`, `runWRF.bash:19`).

## 3. Crontab activo y logs del operativo

### crontab

```
$ crontab -l      # usuario pgich, 2026-11-04
no crontab for pgich
(exit 1)
```

- `/var/spool/cron/crontabs`: "Permiso denegado". `sudo -n crontab -l -u root`: "a password is required". **No se pudo ver el crontab de root.**
- `/etc/cron.d` solo contiene `anacron`, `e2scrub_all` y `.placeholder`. Ninguno menciona wrf ni cron.bash.
- `systemctl list-timers --all`: ningún timer relacionado con WRF (anacron, apt-daily, plocate, fwupd, dpkg-db-backup, logrotate, apt-daily-upgrade, man-db, tmpfiles-clean, e2scrub_all, fstrim).
- `journalctl -t CRON`: sin entradas con "wrf" ni "cron.bash". `/var/log/syslog*` no existe.
- `ps` a las 10:54: ningún proceso wrf.exe, real.exe, metgrid, ungrib ni cron.bash.

Copia: `punto3_crontab.txt`.

### Logs de la cadena operativa (`salidas/logs/<AAAA_MM>/<DD_HH>/`), últimas 5 líneas

Corrida más reciente con logs: **2025_09/09_06**. Antes de esa están 2025_04/21_06 (solo `descarga.log`) y varias de 2025_03.

**/home/pgich/wrf-operativo/salidas/logs/2025_09/09_06/descarga.log**, mtime 2025-09-09 11:50:37
```
dowloading error=  0
Requested remote file downloaded in local file /home/pgich/wrf-operativo/datos/GFS025/2025_09/09_06/GFS_2025090906+048.grib2
*******************************************************
 All requested grib2 files downloaded ! 20250909 6 UTC
*******************************************************
```

**/home/pgich/wrf-operativo/salidas/logs/2025_09/09_06/wps.log**, mtime 2025-09-09 11:54:09
```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!  Successful completion of metgrid.  !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

			******************FIN*****************
```

**/home/pgich/wrf-operativo/salidas/logs/2025_09/09_06/wrfplot.log**, mtime 2025-09-11 10:29:38
```
Se generan los PNG de t2 para el webmet
Se generan los PNG de ppn para el webmet
Se generan los PNG de max_dbz para el webmet
Se generan los PNG de wspd10 para el webmet
Se generan los PNG de wdir10 para el webmet
```

**/home/pgich/wrf-operativo/salidas/logs/2025_09/09_06/datos_meteo.log**, mtime 2025-09-11 10:37:18
```
barreal no está en dominio
valle-fertil no está en dominio
media-agua no está en dominio
hugo-crescentino no está en dominio
INTA-POCITO no está en dominio
```

`informe.log` y `limpiar.log` de 2025_09/09_06 (mtime 2025-09-11 10:37:25) tienen 0 bytes.

**/home/pgich/wrf-operativo/salidas/logs/2025_04/21_06/descarga.log**, mtime 2025-04-21 13:06:05 (las líneas son largas; las URL se reproducen completas en el original)
```
Request in server:  nomads.ncep.noaa.gov/
Attempt number:  1
FILE_LOCAL/home/pgich/wrf-operativo/datos/GFS025/2025_04/21_06/GFS_2025042106+000.grib2
FILE_REMOTEhttp://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t06z.pgrb2.0p25.f000&...&dir=%2Fgfs.20250421%2F06%2Fatmos
Request remote file:  http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t06z.pgrb2.0p25.f000&...&dir=%2Fgfs.20250421%2F06%2Fatmos
```

**/home/pgich/wrf-operativo/ejecutables/log.cron**, mtime 2023-10-24 12:04:29
```
sys	0m7,736s

real	0m30,939s
user	1m16,284s
sys	0m3,932s
```

Salidas del operativo, en `/home/pgich/wrf-operativo/salidas/wrfout/`:
- Último wrfout: `2025_09/wrfout_d01_2025-09-09_06:00:00.nc`, mtime 2025-09-11 10:18.
- Último directorio en `salidas/parte` y en `salidas/mapas`: `2025_09/09_06`.

Logs más recientes encontrados en todo el árbol (`find -name '*.log'`):
- `/home/pgich/wrf-operativo/ejecutables/WRF_casos_24h/wrf_control.log`, mtime 2026-11-02 11:15:50. Última línea: `wrf: SUCCESS COMPLETE WRF`, precedida de `Timing for Writing wrfout_d01_2026-09-25_00:00:00`.
- `/home/pgich/wrf-operativo/ejecutables/WRF/wrf_control.log`, mtime 2026-09-13 00:57:29. Última línea: `wrf: SUCCESS COMPLETE WRF`, precedida de `wrfout_d01_2026-05-16_12:00:00`.

`WRF_casos_24h` es el `RUN_DIR` por defecto del pipeline de la tesis (`src/casos/run_casos.py:58`). No pertenece a la cadena `cron.bash`.

**Lo que muestra la evidencia sobre "¿corre hoy y desde cuándo?":**
- No hay crontab para `pgich`.
- No hay procesos WRF activos.
- El último log y el último wrfout de la cadena `cron.bash` → `salidas/` son de la corrida 2025-09-09 06Z, con archivos terminados el 2025-09-11 10:37.

## 4. wrfout_d01_* en /home/pgich/wrf-operativo con CEN_LAT entre -33 y -30

Comando: `find /home/pgich/wrf-operativo -name 'wrfout_d01_*' -type f`, y sobre cada archivo `ncdump -h … | grep ":CEN_LAT ="`. El `ncdump` usado es `/home/pgich/Build_WRF/libraries/NETCDF/bin/ncdump`.

Se revisaron 524 archivos. **513 tienen CEN_LAT en [-33, -30].** Agrupados por directorio:

| Directorio | n | CEN_LAT | mtime mín – máx |
|---|---|---|---|
| /home/pgich/wrf-operativo/wrfplot_v2 | 2 | -31.543f | 2023-10-24 13:36 – 2023-10-25 11:09 |
| /home/pgich/wrf-operativo/ejecutables/wrfplot_v2 | 2 | -31.543f | 2023-10-24 13:36 – 2023-10-25 11:09 |
| /home/pgich/wrf-operativo/ejecutables/WRF_EXP/0.0001 | 1 | -31.50001f | 2026-08-27 09:23 |
| /home/pgich/wrf-operativo/ejecutables/WRF_EXP/0.0005, 0.0010, 0.0020, 0.0050 | 2 c/u | -31.50001f | 2026-08-26 14:26 – 20:20 |
| /home/pgich/wrf-operativo/ejecutables/WRF | 13 | -31.50001f | 2026-09-13 00:55 – 00:57 |
| /home/pgich/wrf-operativo/ejecutables/WRF/control | 52 | -31.50001f | 2026-09-10 09:40 – 2026-09-13 00:57 |
| /home/pgich/wrf-operativo/ejecutables/WRF/nudged | 52 | -31.50001f | 2026-09-10 09:37 – 2026-09-13 00:55 |
| /home/pgich/wrf-operativo/ejecutables/WRF_casos_24h | 37 | -31.50001f | 2026-11-02 10:59 – 11:15 |
| /home/pgich/wrf-operativo/ejecutables/WRF_casos_24h/control | 173 | -31.50001f | 2026-10-11 22:19 – 2026-11-02 11:15 |
| /home/pgich/wrf-operativo/ejecutables/WRF_casos_24h/nudged | 173 | -31.50001f | 2026-10-11 22:08 – 2026-11-02 10:59 |

Fuera del rango:
- **Todos los wrfout de `salidas/wrfout/` (la salida de la cadena operativa) tienen `:CEN_LAT = -23.41101f ;`.** Son 8 de 2025_03 y 1 de 2025_09.
- `ejecutables/wrfplot_v2/wrfout_d01_2025-03-21_06:00:00` también tiene -23.41101f.
- `salidas/wrfout/2025_03/wrfout_d01_2025-03-22_06:00:00.tar.xz` no se puede leer con ncdump porque está comprimido.

Listados completos (ruta | mtime | línea CEN_LAT):
- `punto4_cenlat_todos_wrfout_d01.txt`
- `punto4_cenlat_entre_-33_y_-30.txt`

## 5. Atributos globales de un wrfout de la tesis

Archivo: `/home/pgich/wrf-modular-V1/outputs/runs/2026-09-24_0000z/sanjuan_0924/control/wrfout_d01_2026-09-24_00:00:00`, mtime 2026-10-20 11:00:01. grep usado: `":NOMBRE ="`.

```
		:MAP_PROJ = 3 ;
		:DX = 15000.f ;
		:DT = 45.f ;
		:CEN_LAT = -31.50001f ;
		:CEN_LON = -68.5f ;
		:WEST-EAST_GRID_DIMENSION = 80 ;
		:SOUTH-NORTH_GRID_DIMENSION = 60 ;
		:BOTTOM-TOP_GRID_DIMENSION = 35 ;
		:MP_PHYSICS = 8 ;
		:RA_LW_PHYSICS = 4 ;
		:RA_SW_PHYSICS = 4 ;
		:BL_PBL_PHYSICS = 2 ;
		:SF_SFCLAY_PHYSICS = 2 ;
		:SF_SURFACE_PHYSICS = 2 ;
		:CU_PHYSICS = 6 ;
		:SF_URBAN_PHYSICS = 0 ;
		:OBS_NUDGE_OPT = 0 ;
```

El volcado completo de atributos globales está en `punto5_ncdump_atributos_globales.txt`.

## 6. namelist.wps / namelist.input del repo de la tesis

Qué archivos usan las corridas de la tesis, según el código:
- `src/casos/run_casos.py:398` pasa `--namelist ROOT/<namelist_base>`, y `config/casos_oficiales.json:20` define `"namelist_base": "namelist.input"`. Resultado: `/home/pgich/wrf-modular-V1/namelist.input`.
- WPS: `run_casos.py:56-57` usa `wps_sanjuan/run_wps_sanjuan.sh`, que genera `wps_sanjuan/namelist.wps` a partir de `wps_sanjuan/namelist.wps.template` con sed (solo cambia fechas y geog_data_path).

Valores literales (`grep -nE "^\s*(clave)\s*="`):

| Archivo (ruta absoluta) | mtime | Valores |
|---|---|---|
| /home/pgich/wrf-modular-V1/wps_sanjuan/namelist.wps | 2026-11-02 10:39:31 | l.17 `geog_data_res     = 'lowres',` · l.20 `map_proj  = 'mercator',` |
| /home/pgich/wrf-modular-V1/wps_sanjuan/namelist.wps.template | 2026-10-11 19:24:04 | l.17 `geog_data_res     = 'lowres',` · l.20 `map_proj  = 'mercator',` |
| /home/pgich/wrf-modular-V1/namelist.wps | 2026-10-11 19:24:04 | l.17 `geog_data_res     = 'lowres',` · l.20 `map_proj  = 'mercator',` |
| /home/pgich/wrf-modular-V1/namelist.input | 2026-10-11 21:53:46 | l.29 `time_step                           = 45,` · l.61 `physics_suite                       = 'CONUS'` · l.63 `cu_physics                          = -1,` · l.69 `radt                                = 15,` |
| /home/pgich/wrf-modular-V1/outputs/runs/2026-09-24_0000z/sanjuan_0924/namelist_control.input | 2026-10-20 10:53:57 | l.29 `time_step = 45,` · l.61 `physics_suite = 'CONUS'` · l.63 `cu_physics = -1,` · l.69 `radt = 15,` |
| /home/pgich/wrf-modular-V1/outputs/runs/2026-09-24_0000z/sanjuan_0924/namelist_nudged.input | 2026-10-20 10:36:24 | igual que namelist_control.input |
| /home/pgich/wrf-modular-V1/config/namelist.input.template (no la usa run_casos) | 2026-10-11 19:24:04 | l.29 `time_step = 90,` · l.53 `physics_suite = 'CONUS'` · l.55 `cu_physics = -1,` · l.61 `radt = 15,` |

- `geog_data_res` y `map_proj` no aparecen en los namelist.input.
- `radt`, `cu_physics`, `physics_suite` y `time_step` no aparecen en los namelist.wps.
- sha256 de `namelist_control.input` del caso: `83ebc895…a79d`. Coincide con `namelist_sha256` en `control_manifest.json`.

Copias en `repo_tesis/`.

---

## Archivos creados (todos en /home/pgich/wrf-modular-V1/outputs/evidencia_operativo/)

- evidencia_operativo.md
- namelistTemp.wps, namelistTemp.input, env.bash, sanjuan/env.bash, cron.bash, runEureka.bash, runWPS.bash, runWRF.bash
- punto3_crontab.txt
- punto4_cenlat_todos_wrfout_d01.txt, punto4_cenlat_entre_-33_y_-30.txt
- punto5_ncdump_atributos_globales.txt
- repo_tesis/namelist.input, repo_tesis/namelist.wps, repo_tesis/wps_sanjuan__namelist.wps, repo_tesis/wps_sanjuan__namelist.wps.template
