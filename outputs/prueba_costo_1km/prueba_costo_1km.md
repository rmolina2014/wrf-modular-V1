# Prueba de costo de cómputo: WRF configuración operativa a 1 km (04-11-2026)

**Estado: INCOMPLETA.** wrf.exe no llegó a ejecutarse.
- Con 600×600, real.exe no termina por falta de memoria.
- Con 300×300, real.exe se detiene por `FATAL`: la `end time` debe quedar al menos un `interval_seconds` después del inicio.

Este documento registra todo lo hecho y medido hasta ese punto.

- Directorio de trabajo: `/home/pgich/wrf-modular-V1/outputs/prueba_costo_1km/`
- Caso: Caso 4 (sanjuan_0924), ciclo GFS 2026-09-23 12Z. Solo control, sin nudging. Prueba de 1 h simulada (12:00 a 13:00).
- No se modificó ni borró ningún archivo existente del repo ni del operativo. No se descargó nada. No se usaron los scripts del cron.
- Las fechas son mtime en hora -0300.

## 0. Hardware y carga (2026-11-04 12:33:45)

| Recurso | Valor |
|---|---|
| nproc | 10 |
| CPU (lscpu) | 12th Gen Intel(R) Core(TM) i7-12700, 1 socket, CPUs 0-9 |
| Memoria (`free -g`) | total 40, usado 4, libre 33, disponible 36 (GB) |
| Memoria (`free -m`, 12:4x) | total 41204 MiB; swap total 974 MiB |
| Disco `/` (`df -h`) | 491G total, 414G usados, **52G libres (89%)** al inicio; 49G libres (90%) al final |
| load average | 0,49, 0,51, 0,31 |

`top -b -n1 | head -10`:
```
top - 12:33:45 up  2:23,  1 user,  load average: 0,49, 0,51, 0,31
Tareas: 242 total,   2 running, 240 sleeping,   0 stopped,   0 zombie
%Cpu(s): 33,3 us, 11,1 sy,  0,0 ni, 55,6 id,  0,0 wa,  0,0 hi,  0,0 si,  0,0 st 
MiB Mem :  41204,1 total,  34191,4 free,   4311,1 used,   3254,7 buff/cache     
MiB Intercambio:    975,0 total,    975,0 free,      0,0 used.  36893,0 avail Me

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
   1530 pgich     20   0 5772840 338428 138428 S  37,5   0,8   6:28.33 gnome-s+
   2356 pgich     20   0   11,8g 678200 266200 S   6,2   1,6   7:43.81 firefox+
   3213 pgich     20   0 2704176 245720 122412 S   6,2   0,6   0:13.06 Isolate+
```
No había procesos de cómputo pesados. Estaban abiertos gnome-shell y Firefox; en `ps` ninguno superaba el 6% de CPU promedio.

## 1 y A. Cómo se lanzan real.exe y wrf.exe

### Operativo

`/home/pgich/wrf-operativo/ejecutables/runWRF.bash` (mtime 2025-03-20 09:10:43):
```
83:time $RUN_COMMAND ./real.exe
96:time $RUN_COMMAND ./wrf.exe 
```

`/home/pgich/wrf-operativo/ejecutables/env.bash` (mtime 2026-09-10 09:25:10), que se carga con `source env.bash` desde `cron.bash:18`:
```
19:export RUN_COMMAND=
73:ulimit -s unlimited
74:export KMP_STACKSIZE=128m
75:export KMP_LIBRARY=turnaround
76:export KMP_BLOCKTIME=infinite
77:export KMP_HW_SUBSET=4c,2t
80:export WRF_NUM_TILES_X=1
81:export WRF_NUM_TILES_Y=8
85:export OMP_NUM_THREADS=12
```

Resultado: el binario se ejecuta directo, sin mpirun, con 12 hilos OpenMP, tiles 1×8 y stack ilimitado.

### Tesis (framework)

- `/home/pgich/wrf-modular-V1/.env` (mtime 2026-10-11 20:20:18) define:
  - `LOCAL_WRF_DIR=/home/pgich/wrf-operativo/ejecutables/WRF_casos_24h`
  - `WRF_ENV_BASH=/home/pgich/wrf-operativo/ejecutables/env.bash`
  - `MPIRUN=/home/pgich/Build_WRF/libraries/MPICH/bin/mpirun`
  - `WRF_NP=1`
- `pipeline_wrf.py:42` lo carga con `load_dotenv`.
- `src/modelo/wrf_runner.py` (mtime 2026-10-11 21:10:25), en las líneas 118-121 y 153-156:
  ```
  if str(self.np) == "1":
      comando = "./real.exe"      # (idem "./wrf.exe")
  else:
      comando = f"{self.mpirun} -np {self.np} ./real.exe"
  ```
- `wrf_runner.py:63-67` arma el entorno así:
  ```
  full_cmd = ("export LD_LIBRARY_PATH='' "
              "&& unset OMP_NUM_THREADS OMP_STACKSIZE KMP_STACKSIZE 2>/dev/null || true "
              f"&& {env_load}"            # source env.bash
              "export OMP_NUM_THREADS=1 WRF_NUM_TILES_X=1 WRF_NUM_TILES_Y=1 "
              f"&& {{ {cmd} ; }} > {_BASH_LOG} 2>&1")
  ```
- `results/casos_estudio/pipeline_caso4_sanjuan_0924.log` (mtime 2026-10-20 11:12:06) registra `Ejecutando: ./real.exe (Log: real.log)` y `Ejecutando: ./wrf.exe (Log: wrf_control.log)`.

Resultado: el binario se ejecuta directo, 1 proceso, 1 hilo, tiles 1×1. Se carga env.bash, pero OMP y tiles se sobrescriben después.

### Log de una corrida existente

`/home/pgich/wrf-operativo/ejecutables/WRF_casos_24h/wrf_control.log` (mtime 2026-11-02 11:15:50):
```
1: Ntasks in X            1 , ntasks in Y            1
14:WRF V4.5 MODEL
60:*             PROGRAM:WRF-Chem V4.5 MODEL
73:WRF NUMBER OF TILES FROM OMP_GET_MAX_THREADS =   1
   WRF NUMBER OF TILES X FROM ENV WRF_NUM_TILES_X =   1
   WRF NUMBER OF TILES Y FROM ENV WRF_NUM_TILES_Y =   1
   WRF NUMBER OF TILES =   1
```

### Tipo de compilación

Binarios: `/home/pgich/Build_WRF/WRF/main/real.exe` (mtime 2023-10-24 12:54:43) y `wrf.exe` (2023-10-24 13:11:34). En `test/em_real/` hay enlaces a ellos.

- `ldd` de ambos: enlazan `libgomp.so.1` (OpenMP). **No enlazan ninguna biblioteca MPI.**
- `nm wrf.exe`: tiene `U GOMP_parallel@GOMP_4.0` y `U omp_get_max_threads_@OMP_1.0`. Los símbolos "mpi_" que aparecen son variables internas de `module_dm`/`module_wrf_quilt`, no la biblioteca MPI.
- `/home/pgich/Build_WRF/WRF/configure.wrf` (mtime 2023-10-24 12:11:16):
  - l.126: `# Settings for    Linux x86_64 ppc64le, gfortran compiler with gcc   (smpar)`
  - `FC = $(SFC)` = `gfortran` (no mpif90)
  - `-DDM_PARALLEL -DSTUBMPI` (l.181-182)
  - `OMP = -fopenmp`

**Conclusión literal:** la compilación es **smpar** (memoria compartida, OpenMP), con MPI de stub. `mpirun -np N` no reparte el dominio entre procesos.

### Límites del sistema (2026-11-04 ~12:45)

- `ulimit -a` (shell sin env.bash): `stack size 8192`, `max memory size unlimited`, `virtual memory unlimited`, `data seg size unlimited`. env.bash sube el stack a `unlimited`.
- `free -m`: Mem 41204 MiB total; swap ("Inter") 974 MiB total, 136 MiB usados después del intento 1.
- cgroup: `0::/user.slice/user-1000.slice/user@1000.service/app.slice/.../vte-spawn-....scope`.
  - En el scope, en `user-1000.slice` y en `user.slice`: `memory.max = max`, `memory.high = max`, `memory.swap.max = max`. **No hay límite de memoria por cgroup.**
- `vm.overcommit_memory = 0`, `overcommit_ratio = 50`. `systemd-oomd`: inactive. `/etc/security/limits.conf` no tiene líneas activas.
- Contadores de OOM:
  - `/proc/vmstat` → `oom_kill 1`.
  - `memory.events` del scope de la terminal, de `user@1000.service`, de `user-1000.slice` y de `user.slice` → `oom_kill 1`.
  - `memory.peak` del scope: 40144642048 bytes.
  - No pude leer `journalctl -k` ni `dmesg`: falta pertenecer al grupo `adm` o tener permisos de root.

## 2. GRIB2

`/home/pgich/wrf-modular-V1/wps_sanjuan/gfs_data/2026-09-23_12/` (mtime 2026-10-13 13:16:23) contiene `gfs.t12z.pgrb2.0p25.f000` … `f036`, de unos 480-537 MB cada uno, con mtime 2026-10-13 13:02-13:18. Con `link_grib.csh` se enlazaron solo **f000 y f003**.

## 3. WPS a 1 km (600×600): `wps/`

- Plantilla: `/home/pgich/wrf-operativo/datos/namelists/namelistTemp.wps` (mtime 2025-03-21 12:42:34), copiada como `wps/namelistTemp.wps.orig`.
- Binarios:
  - `/home/pgich/Build_WRF/WPS/geogrid/src/geogrid.exe` (2023-10-24 13:15:29)
  - `ungrib/src/ungrib.exe` (2023-10-24 13:13:54)
  - `metgrid/src/metgrid.exe` (2023-10-24 13:15:29)
- WPS_GEOG: `/home/pgich/wrf-operativo/datos/WPS_GEOG`, el mismo que la tesis.

`wps/namelist_wps.diff` (plantilla contra copia):
```
4,5c4,5
<  start_date = 'START_DATE','START_DATE' 
<  end_date   = 'END_DATE','END_DATE'
---
>  start_date = '2026-09-23_12:00:00','2026-09-23_12:00:00' 
>  end_date   = '2026-09-23_15:00:00','2026-09-23_15:00:00'
36,41c36,41
<  ref_lat   =  REF_LAT,
<  ref_lon   =  REF_LON,
<  truelat1  =  TRUELAT1,
<  truelat2  =  TRUELAT2,
<  stand_lon =  STAND_LON,
<  geog_data_path = 'RUTA_GEOG_DATA'
---
>  ref_lat   =  -31.53,
>  ref_lon   =  -68.53,
>  truelat1  =  -31.53,
>  truelat2  =  -31.53,
>  stand_lon =  -68.53,
>  geog_data_path = '/home/pgich/wrf-operativo/datos/WPS_GEOG'
```

Valores sin cambio respecto de la plantilla: `max_dom = 1`, `e_we = 600, 112,`, `e_sn = 600, 97,`, `dx = dy = 1000`, `map_proj = 'lambert'`, `geog_data_res = 'default','default'`, `interval_seconds = 10800`.

**Modificación de fechas en WPS.** El primer intento usó `end_date = 2026-09-23_13:00:00` y ungrib falló. Error exacto, de `wps/ungrib_intento1_fallido.log`:
```
2026-11-04 12:35:44.774 --- ERROR STOP IN READ_NAMELIST
2026-11-04 12:35:44.774 --- INTERVAL must fit evenly between start time and end time:
2026-11-04 12:35:44.775 --- Start time: 2026-09-23_12:00:00
2026-11-04 12:35:44.775 --- End time:   2026-09-23_13:00:00
2026-11-04 12:35:44.775 --- INTERVAL  : 10800 seconds,  3.000000 hours
2026-11-04 12:35:44.775 --- ERROR: Change your namelist, and resubmit
```
El usuario eligió la opción A: `end_date = 2026-09-23_15:00:00` en WPS (dos tiempos de GFS, 12Z y 15Z) y `interval_seconds = 10800` sin cambio.

- geogrid ya había corrido con `end_date` 13:00. Las fechas no afectan a geogrid, así que no se repitió.
- WPS de 600×600 corrió con el **lanzamiento de la tesis** (`env_tesis.sh`: OMP=1, tiles 1×1), porque fue antes del cambio de plan.

### Medición

`/usr/bin/time` no está instalado en la PC (`ls: no se puede acceder a '/usr/bin/time': No existe el fichero o el directorio`). Con la aprobación del usuario se usó `medir.py`, que registra con `os.wait4`:
- tiempo real (resolución aproximada de 1 s, por un sondeo cada 1 s),
- user y sys,
- `Maximum resident set size` (ru_maxrss, el mismo dato que da GNU time),
- exit status y señal.

| Etapa (600×600) | Real (s) | user (s) | sys (s) | Max RSS | Resultado |
|---|---|---|---|---|---|
| geogrid | 5,0 | 4,10 | 0,28 | 157 908 kB | OK. `geo_em.d01.nc` 43 MB. Sin WARNING ni ERROR |
| ungrib (2 tiempos) | 27,0 → **13,5 por tiempo** | 18,43 | 7,11 | 819 764 kB | OK. `GFS:2026-09-23_12` y `_15`, 781 MB cada uno |
| metgrid (2 tiempos) | 34,0 → **17,0 por tiempo** | 32,43 | 1,18 | 925 036 kB | OK. 2 `met_em` de 185 MB, `num_metgrid_levels = 34`. Sin WARNING ni ERROR |

Nota: la salida de metgrid dice `Note: The following floating-point exceptions are signalling: IEEE_OVERFLOW_FLAG IEEE_UNDERFLOW_FLAG IEEE_DENORMAL` después de `Successful completion of metgrid`.

## 4 y B. real.exe 600×600: `wrf/`

- Plantilla: `/home/pgich/wrf-operativo/datos/namelists/namelistTemp.input` (mtime 2025-03-21 12:42:55), copiada como `wrf/namelistTemp.input.orig`.
- En `wrf/` se enlazaron todos los archivos de `/home/pgich/Build_WRF/WRF/test/em_real/` (igual que `runWRF.bash:24`), menos su `namelist.input`, y los dos `met_em`.

`wrf/namelist_input.diff`:
```
3c3
<  run_hours                           = RUN_HOURS,
---
>  run_hours                           = 1,
6,17c6,17
<  start_year                          = START_YEAR, START_YEAR, 2000,
...
<  end_hour                            = END_HOUR, END_HOUR,   12,
...
---
>  start_year                          = 2026, 2026, 2000,
>  start_month                         = 09, 09,   01,
>  start_day                           = 23, 23,   24,
>  start_hour                          = 12, 12,   12,
>  start_minute                        = 00, 00,   00,
>  start_second                        = 00, 00,   00,
>  end_year                            = 2026, 2026, 2000,
>  end_month                           = 09, 09,   01,
>  end_day                             = 23, 23,   25,
>  end_hour                            = 13, 13,   12,
>  end_minute                          = 00, 00,   00,
>  end_second                          = 00, 00,   00,
29c29
<  history_outname                     = "HISTORY_OUTNAME"
---
>  history_outname                     = "wrfout_d<domain>_<date>"
```
(El diff completo está en el archivo.)

- La plantilla no tiene marcadores REF_*.
- `history_outname`: el marcador se reemplazó por el nombre por defecto de WRF, para escribir en el directorio de la prueba. El operativo usa `$WRF_WRFOUT/$anio_mes/wrfout_d<domain>_<date>`.
- El bloque `&fdda` está vacío, así que no hay nudging.
- Sin cambio: `max_dom = 1`, `time_step = 6`, `e_vert = 35`, `e_we = e_sn = 600`, física de la plantilla, `interval_seconds = 10800`.

### Intento 1: lanzamiento de la tesis (`env_tesis.sh`)

Archivos: `wrf/real_intento1_lanzamiento_tesis.log`, que tiene **0 bytes**, y su `.time`.
```
"inicio": "2026-11-04 12:38:58", "elapsed_wall_s": 42.11, "user_s": 4.46, "system_s": 37.18,
"maximum_resident_set_size_kbytes": 38553804, "exit_status": null, "terminado_por_senal": 9
```
No se generaron `wrfinput_d01`, `wrfbdy_d01` ni `rsl.*`. Los contadores `oom_kill 1` de la sección A corresponden a este intento: es el único OOM desde el arranque, que fue a las 10:10.

### Intento 2: lanzamiento del operativo (`env_operativo.sh` = `source env.bash`) con watchdog

Configuración del watchdog (`watchdog_mem.py`):
- Cada 2 s registra el RSS total de los procesos `real.exe` cuyo directorio de trabajo es `wrf/`, junto con MemAvailable y SwapFree.
- Manda SIGTERM si el RSS supera 34 GB o si MemAvailable baja de 3 GB.

`wrf/memoria_real.csv`:
```
fecha_hora,t_s,n_proc,rss_total_kB,memavailable_kB,swapfree_kB,accion
2026-11-04 12:49:39,0.0,0,0,38688572,858972,
2026-11-04 12:49:41,2.0,1,3758552,34937104,858972,
2026-11-04 12:49:43,4.0,1,11032452,27650460,858972,
2026-11-04 12:49:45,6.0,1,18015148,20655004,858972,
2026-11-04 12:49:47,8.0,1,25150272,13506456,858972,
2026-11-04 12:49:49,10.0,1,32101668,6543308,858972,
2026-11-04 12:49:51,12.0,1,35611140,3029016,858972,SIGTERM (MemAvailable<limite)
2026-11-04 12:49:53,14.0,0,0,38702764,858984,
```

- **Pico de RSS: 35 611 140 kB (33,96 GB).** Coinciden el watchdog y ru_maxrss: `maximum_resident_set_size_kbytes: 35611412`.
- **real.exe no terminó: lo cortó el watchdog** con SIGTERM a los 12 s (`terminado_por_senal: 15`), porque MemAvailable bajó a 3 029 016 kB (2,89 GB).
- `real.log` quedó con 0 bytes y no se generaron wrfinput ni wrfbdy. Cuando lo cortó, el RSS seguía creciendo a unos 3,5 GB cada 2 s.

## D. Dominio reducido 300×300 (1 km, mismo centro): `d300/`

Todo se lanzó con el entorno del operativo y el watchdog (`etapa.sh`). Única diferencia con la carpeta de 600×600: `e_we`/`e_sn` del dominio 1 (`d300/wps/namelist_wps.diff` y `d300/wrf/namelist_input.diff`):
```
<  e_we              =  600, 112,      >  e_we              =  300, 112,
<  e_sn              =  600,  97,      >  e_sn              =  300,  97,
<  e_we              = 600,    112,   94,    >  e_we          = 300,    112,   94,
<  e_sn              = 600,    97,    91,    >  e_sn          = 300,    97,    91,
```

| Etapa (300×300) | Real (s) | user (s) | sys (s) | Max RSS (ru_maxrss) | Pico RSS watchdog (muestreo cada 2 s) | Resultado |
|---|---|---|---|---|---|---|
| geogrid | 2,0 | 1,31 | 0,16 | 124 500 kB | 0,08 GB | OK. `geo_em` 11 MB |
| ungrib (2 tiempos) | 22,0 → 11,0 por tiempo | 18,40 | 2,21 | 819 628 kB | 0,78 GB | OK |
| metgrid (2 tiempos) | 16,0 → 8,0 por tiempo | 14,74 | 0,74 | 246 160 kB | 0,23 GB | OK. `met_em` 46 y 47 MB |
| real.exe | 3,0 | 1,55 | 1,42 | **10 345 388 kB (9,87 GB)** | 3,38 GB | **FATAL** (exit status 0) |

El muestreo del watchdog cada 2 s no capturó el pico real de real.exe en 300×300. El valor confiable es ru_maxrss.

`d300/wrf/real_stdout.log` (mtime 2026-11-04 12:51:30), completo:
```
 Ntasks in X            1 , ntasks in Y            1
Domain # 1: dx =  1000.000 m
REAL_EM V4.5 PREPROCESSOR
No git found or not a git repository, git commit version not available.
 *************************************
 Parent domain
 ids,ide,jds,jde            1         300           1         300
 ims,ime,jms,jme           -4         305          -4         305
 ips,ipe,jps,jpe            1         300           1         300
 *************************************
DYNAMICS OPTION: Eulerian Mass Coordinate
 alloc_space_field: domain            1 ,           10525263144  bytes allocated
Time period #   1 to process = 2026-09-23_12:00:00.
Total analysis times to input =    1.
 You might have set the end time in the namelist.input for the model
 Regional domains require more than one time-period to process, for BC generation
-------------- FATAL CALLED ---------------
FATAL CALLED FROM FILE:  <stdin>  LINE:     641
Make the end time at least one 'interval_seconds' beyond the start time
-------------------------------------------
```

La prueba se detuvo acá, según la regla "si algo falla, parate". No se corrió wrf.exe y no se probó 400×400.

- La misma condición de `end time` (13:00 con `interval_seconds = 10800`) estaba también en el `namelist.input` de 600×600. Ese real.exe no llegó a leerla porque murió antes, mientras reservaba memoria, sin escribir nada en el log.
- Para seguir hace falta una decisión del usuario sobre las fechas de real.exe frente a las de wrf.exe.

## Extrapolación a 600×600 (ESTIMACIÓN, no medición)

Supuesto: la memoria escala linealmente con el número de columnas. 600×600 son 360 000 columnas y 300×300 son 90 000, un factor de 4.

| Dato | 300×300 (medido) | × 4 | 600×600 (estimado) |
|---|---|---|---|
| `alloc_space_field` de real.exe | 10 525 263 144 bytes (9,80 GiB) | × 4 | ≈ 42 101 052 576 bytes ≈ **39,2 GiB** |
| Max RSS de real.exe | 10 345 388 kB (9,87 GB) | × 4 | ≈ 41 381 552 kB ≈ **39,5 GB** |

Datos de referencia de la PC: MemTotal es 42 193 036 kB (40,2 GiB) y MemAvailable antes de lanzar era unos 38,7 GB. En 600×600 se midieron directamente 38,55 GB (intento 1, OOM) y 33,96 GB (intento 2, cortado). Esos dos valores son mínimos, porque el proceso no terminó.

No hay medición de wrf.exe, así que no se puede dar segundos por paso, segundos por hora simulada ni la extrapolación a 36 h y 48 h.

## Pasos 5 y 6

No se ejecutaron porque wrf.exe no corrió. No hay líneas "Timing for main", wrfout, "SUCCESS COMPLETE WRF", NaN, SIGSEGV ni avisos de CFL.

## Archivos creados en `/home/pgich/wrf-modular-V1/outputs/prueba_costo_1km/`

Scripts y documentación:
- `prueba_costo_1km.md`: este archivo.
- `medir.py`: sustituto de `/usr/bin/time -v`.
- `watchdog_mem.py`
- `etapa.sh`: lanza el watchdog y `medir.py` con el entorno del operativo.
- `env_tesis.sh`: entorno de `wrf_runner.py`.
- `env_operativo.sh`: `source env.bash`.

`wps/` (600×600):
- `namelistTemp.wps.orig`, `namelist.wps`, `namelist_wps.diff`
- `geogrid.log`, `geogrid_stdout.log(.time)`
- `ungrib_intento1_fallido.log`, `ungrib_intento1_fallido_stdout.log(.time)`
- `ungrib.log`, `ungrib_stdout.log(.time)`
- `metgrid.log`, `metgrid_stdout.log(.time)`
- Datos pesados: `geo_em.d01.nc` (43 MB), `GFS:2026-09-23_12` y `_15` (781 MB cada uno), `met_em.d01.*` (2 × 185 MB)
- Enlaces: `GRIBFILE.AAA/AAB`, binarios, `geogrid/`, `metgrid/`, `Vtable`

`wrf/` (600×600):
- `namelistTemp.input.orig`, `namelist.input`, `namelist_input.diff`
- `namelist.output.intento1`
- `real_intento1_lanzamiento_tesis.log` (0 bytes) y su `.time`
- `real.log` (0 bytes), `real.log.time`
- `memoria_real.csv`, `memoria_real.csv.resumen.json`, `watchdog_real.out`
- Enlaces a `em_real/*` y a los `met_em`

`d300/wps/`:
- `namelistTemp.wps.orig`, `namelist.wps`, `namelist_wps.diff`
- `geogrid.log`, `ungrib.log`, `metgrid.log`, más `*_stdout.log(.time)`
- `memoria_{geogrid,ungrib,metgrid}.csv(.resumen.json)`, `watchdog_*.out`
- Datos pesados: `geo_em.d01.nc`, `GFS:*`, `met_em.*`

`d300/wrf/`:
- `namelistTemp.input.orig`, `namelist.input`, `namelist_input.diff`, `namelist.output`
- `real_stdout.log(.time)`
- `memoria_real.csv(.resumen.json)`, `watchdog_real.out`
- Enlaces

Tamaño total del directorio: 3,6 GB, casi todo en `GFS:*` y `met_em`.
