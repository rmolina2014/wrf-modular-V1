# Prueba de costo 1 km, dominio 300×300, tercer intento (`d300/wrf_v3/`): hilos OpenMP, 04-11-2026

**Resultado:** las tres corridas (1, 10 y 4 hilos) **terminaron por SIGSEGV (señal 11) después del mismo paso 39** (último registrado: `2026-09-23_12:03:54`). Ninguna completó los 20 minutos simulados, y ninguna llegó a `SUCCESS COMPLETE WRF`.

- Directorio: `/home/pgich/wrf-modular-V1/outputs/prueba_costo_1km/d300/wrf_v3/`
- `d300/wrf/` y `d300/wrf_v2/` no se tocaron.
- `wrfinput_d01` y `wrfbdy_d01` se copiaron de `wrf_v2/` con `cp -p` y son idénticos según `cmp`. Los generó real.exe el 2026-11-04 a las 12:59.
- Cada configuración corrió en su propia subcarpeta (`omp1/`, `omp10/`, `omp4/`) con enlaces a esos dos archivos y a `em_real/*`.
- Orden: omp1 → omp10 → omp4, una tras otra (`correr_las_tres.sh`). No había otros trabajos de cómputo en la PC.
- Medición: `medir.py` (os.wait4) con tope de 10 800 s (3 h) y `watchdog_mem.py` (límites: RSS 34 GB, MemAvailable 3 GB). El watchdog no cortó ninguna corrida.

## Namelist (20 min simulados)

`namelist_20min.input` es una copia de `namelist_wrf.input`. Diff (`namelist_20min_vs_wrf.diff`):
```
3,4c3,4
<  run_hours                           = 1,
<  run_minutes                         = 0,
---
>  run_hours                           = 0,
>  run_minutes                         = 20,
15,16c15,16
<  end_hour                            = 13, 13,   12,
<  end_minute                          = 00, 00,   00,
---
>  end_hour                            = 12, 12,   12,
>  end_minute                          = 20, 20,   00,
```

`end_hour` se pasó a 12 para que el fin sea 12:20, coherente con `run_minutes = 20`. Sin eso el fin quedaría en 13:20. Todo lo demás es igual: `time_step = 6`, `radt = 4`, e_we = e_sn = 300 y física del operativo. 20 minutos simulados son 200 pasos de 6 s.

## Lanzamientos

Todos parten del de la tesis, `env_tesis.sh` (`wrf_runner.py:63-67`):
```
export LD_LIBRARY_PATH=''
unset OMP_NUM_THREADS OMP_STACKSIZE KMP_STACKSIZE
source /home/pgich/wrf-operativo/ejecutables/env.bash
export OMP_NUM_THREADS=1 WRF_NUM_TILES_X=1 WRF_NUM_TILES_Y=1
```

`env_tesis_omp4.sh` y `env_tesis_omp10.sh` sobrescriben después `OMP_NUM_THREADS=4|10`, `WRF_NUM_TILES_Y=4|10` y `WRF_NUM_TILES_X=1`.

Verificación en el log: `WRF NUMBER OF TILES FROM OMP_GET_MAX_THREADS = 1 / 10 / 4` y `WRF NUMBER OF TILES = 1 / 10 / 4`.

## Resultados

| | omp1 (tiles 1×1) | omp10 (tiles 1×10) | omp4 (tiles 1×4) |
|---|---|---|---|
| Inicio y fin | 13:09:46 → 13:16:09 | 13:16:15 → 13:20:34 | 13:20:39 → 13:25:11 |
| Tiempo real total | 383,26 s | 259,17 s | 272,18 s |
| user / sys | 374,10 / 8,36 | 753,80 / 30,27 | 481,46 / 11,64 |
| Terminación | señal 11 | señal 11 | señal 11 |
| Líneas `Program received signal SIGSEGV` | 1 | 10 | 4 |
| Pasos completados | 39 / 200 | 39 / 200 | 39 / 200 |
| Último paso | 12:03:54 | 12:03:54 | 12:03:54 |
| s/paso con 1.er: prom / mín / máx | 4,5028 / 2,9581 / 61,1385 | 1,5530 / 1,2083 / 12,0168 | 1,8874 / 1,4118 / 18,6493 |
| s/paso sin 1.er: prom / mín / máx | **3,0124** / 2,9581 / 3,2016 | **1,2776** / 1,2083 / 1,4337 | **1,4463** / 1,4118 / 1,4925 |
| Suma de "Timing for main" (con / sin 1.er) | 175,61 / 114,47 | 60,57 / 48,55 | 73,61 / 54,96 |
| Max RSS (ru_maxrss) | 11 480 860 kB | 11 624 880 kB | 11 577 580 kB |
| Pico RSS del watchdog | 10,94 GB | 11,08 GB | 11,04 GB |
| Avisos CFL ("points exceeded") | 10 | 4 | 4 |
| NaN / SUCCESS COMPLETE WRF | 0 / 0 | 0 / 0 | 0 / 0 |
| wrfout | `wrfout_d01_2026-09-23_12:00:00`, 83 166 882 B | idem, 83 166 882 B | idem, 83 166 882 B |
| Tamaño de `wrf_stdout.log` (no se sube) | 24 239 930 B | 24 240 783 B | 24 240 323 B |

### Speed-up contra omp1

| Base | omp10 | omp4 |
|---|---|---|
| s/paso sin 1.er paso | 3,0124 / 1,2776 = **2,36** | 3,0124 / 1,4463 = **2,08** |
| s/paso con 1.er paso | 4,5028 / 1,5530 = 2,90 | 4,5028 / 1,8874 = 2,39 |
| Tiempo real total | 383,26 / 259,17 = 1,48 | 383,26 / 272,18 = 1,41 |

La PC tiene 10 CPU lógicas (`nproc` = 10).

### Avisos de CFL

omp1 tuvo 10 avisos (`omp1/wrf_resumen_timing.txt`):
```
           7  points exceeded v_cfl = 2 in domain d01 at time 2026-09-23_12:00:18 hours
Max   W:     12     23      5 W:   -8.12  w-cfl:    2.42  dETA:    0.02
          14  points exceeded v_cfl = 2 in domain d01 at time 2026-09-23_12:00:18 hours
Max   W:     12     24      3 W:  -20.97  w-cfl:    3.82  dETA:    0.01
          52  points exceeded v_cfl = 2 in domain d01 at time 2026-09-23_12:00:24 hours
Max   W:     12     23      3 W: -205.96  w-cfl:   16.42  dETA:    0.01
         115  points exceeded v_cfl = 2 in domain d01 at time 2026-09-23_12:00:24 hours
Max   W:     12     22      3 W: -774.63  w-cfl:   27.58  dETA:    0.01
          12  points exceeded v_cfl = 2 in domain d01 at time 2026-09-23_12:00:48 hours
Max   W:     18    289      3 W:   21.63  w-cfl:    4.03  dETA:    0.01
          17  points exceeded v_cfl = 2 in domain d01 at time 2026-09-23_12:00:48 hours
Max   W:     18    290      4 W:  -29.47  w-cfl:    5.21  dETA:    0.01
          20  points exceeded v_cfl = 2 in domain d01 at time 2026-09-23_12:00:48 hours
Max   W:     19    290      3 W:    3.67  w-cfl:    6.16  dETA:    0.01
          90  points exceeded v_cfl = 2 in domain d01 at time 2026-09-23_12:00:54 hours
Max   W:     17    290      3 W:  417.28  w-cfl:   31.58  dETA:    0.01
         251  points exceeded v_cfl = 2 in domain d01 at time 2026-09-23_12:00:54 hours
Max   W:     17    289     11 W: *******  w-cfl:  919.93  dETA:    0.04
          23  points exceeded v_cfl = 2 in domain d01 at time 2026-09-23_12:00:54 hours
Max   W:      2     98      3 W:   33.19  w-cfl:    3.75  dETA:    0.01
```

omp10 y omp4 tuvieron 4 avisos cada una. Según `diff`, son idénticos entre sí y coinciden con las 4 primeras líneas de omp1 (12:00:18 y 12:00:24). También coinciden con los 4 avisos de `wrf_v2` (OMP=12, tiles 1×8).

### Error

En las tres corridas, después del paso de 12:03:54, aparece `Program received signal SIGSEGV: Segmentation fault - invalid memory reference.` seguido de `Backtrace for this error:` y direcciones sin símbolos. Las primeras líneas de omp1:
```
#0  0x14a09c221772 in ???
#1  0x14a09c220905 in ???
#2  0x14a09be31fcf in ???
#3  0x55a88d6bea34 in ???
#4  0x55a88d6e1c9d in ???
#5  0x55a88d6f15a5 in ???
#6  0x55a88c7719b7 in ???
#7  0x14a09bfecaa5 in ???
...
```
Las 200 últimas líneas de cada log están en `ompN/wrf_stdout_ultimas200.txt`.

Datos literales, sin interpretar:
- El paso siguiente al último registrado es 12:04:00, y `radt = 4` (minutos).
- `wrf_v2`, con OMP=12 y tiles 1×8, también terminó por SIGSEGV después de 12:03:54.

## 3. Historial de git del comentario de `src/modelo/wrf_runner.py:56-62` y del commit 57afb94

La salida completa está en `git_historial_wrf_runner.txt`. Resumen literal:

**Commit que introdujo las líneas 56-62** (`git log -L56,62:src/modelo/wrf_runner.py`):
```
COMMIT 57afb944f654f2db912e032ada7d6c8c1d39a7e1
Autor: Roberto Molina
Fecha: 2026-10-12 10:49:00 -0300

feat: 4 casos de estudio 24h (nudging coef 0.0001) + evaluacion de flujo end-to-end

- Casos 1-3 (zonda 07-31, calor 01-01, frente frio 05-16) completados a 24h con/sin obs nudging
- Fix de estabilidad: time_step=45 fijo, adaptive_time_step off (evita segfault RRTMG)
- Instrumentacion de tiempos por etapa (API EcoWitt, QC, GFS, WPS, preflight, real, wrf, validacion)
- evaluacion_flujo.json por caso + seccion 'Desempeno del flujo' en informes
- informes oficiales con hold-out espacial (N_asim/N_eval)
```
Ese commit reemplazó la línea `# LD_LIBRARY_PATH vacío + unset de OMP: entorno operativo de esta PC`, que venía del commit anterior:
```
COMMIT f841bbd6c843af58024d112ee299350f2dc0f251
Autor: Dev
Fecha: 2026-10-04 23:14:04 -0300

Refactor estructura: CLI unificado, orquestador único, 4 casos oficiales, informes en español, legacy archivado, outputs centralizados
```

**Commit 57afb94** (`git show -s 57afb94`): es el mismo de arriba, `57afb944f654f2db912e032ada7d6c8c1d39a7e1`, del 2026-10-12 10:49:00 -0300, con el mensaje ya citado. `--stat`: 194 archivos, 60 646 inserciones y 28 135 eliminaciones. Incluye `src/modelo/wrf_runner.py | 12 +-` y `pipeline_wrf.py | 102 +-`.

## Archivos nuevos en `d300/wrf_v3/`

Texto:
- `prueba_costo_d300_v3.md`
- `namelist_20min.input`, `namelist_20min_vs_wrf.diff`
- `namelist_wrf.input`, `namelist_real.input`, `namelist_d300_base.input`, `namelistTemp.input.orig` (copias de `wrf_v2`)
- `correr_las_tres.sh`, `correr_las_tres.out`
- `git_historial_wrf_runner.txt`
- En cada `ompN/`:
  - `namelist.input`, `namelist.output`
  - `wrf_stdout.log.time`
  - `wrf_resumen_timing.txt`, `wrf_stdout_ultimas200.txt`
  - `memoria_wrf.csv(.resumen.json)`, `watchdog_wrf.out`

Pesados, no se suben:
- `wrfinput_d01` (86 MB) y `wrfbdy_d01` (6,7 MB)
- En cada `ompN/`: `wrfout_d01_2026-09-23_12:00:00` (83 MB) y `wrf_stdout.log` (24 MB)

Scripts nuevos en `outputs/prueba_costo_1km/`: `env_tesis_omp1.sh`, `env_tesis_omp4.sh`, `env_tesis_omp10.sh`, `etapa_env.sh`.
