# Prueba de costo 1 km, dominio 300×300, segundo intento (`d300/wrf_v2/`), 04-11-2026

**Estado:** real.exe terminó bien. **wrf.exe terminó por SIGSEGV** a los 259 s reales, después de 39 pasos (hasta 12:03:54 simulado). No se generó la salida de las 13:00. Según la regla "si algo falla, parate", **no se corrió 400×400 (`d400/`)**.

- Directorio: `/home/pgich/wrf-modular-V1/outputs/prueba_costo_1km/d300/wrf_v2/`
- `d300/wrf/` no se tocó.
- Entrada:
  - `met_em` de `d300/wps/`: 12Z y 15Z, generados a las 12:51.
  - Binarios `/home/pgich/Build_WRF/WRF/main/real.exe` (mtime 2023-10-24 12:54:43) y `wrf.exe` (2023-10-24 13:11:34), enlazados vía `test/em_real/`.
- Lanzamiento del operativo: `env_operativo.sh` = `source /home/pgich/wrf-operativo/ejecutables/env.bash` (mtime 2026-09-10 09:25:10), es decir OMP_NUM_THREADS=12, WRF_NUM_TILES_X=1, WRF_NUM_TILES_Y=8, `ulimit -s unlimited` y binario directo.
- Medición: `medir.py` (os.wait4) y `watchdog_mem.py`, que muestrea cada 2 s y corta si el RSS pasa de 34 GB o MemAvailable baja de 3 GB.
- Mientras corrió wrf.exe no se ejecutó ningún otro trabajo de cómputo.

## Namelists

Base: `namelist_d300_base.input`, copia de `d300/wrf/namelist.input` (fin 13:00, `run_hours = 1`, `e_we = e_sn = 300`).

`namelist_real.input` (para real.exe). Diff contra la base (`namelist_real_vs_base.diff`):
```
3c3
<  run_hours                           = 1,
---
>  run_hours                           = 3,
15c15
<  end_hour                            = 13, 13,   12,
---
>  end_hour                            = 15, 15,   12,
```

`namelist_wrf.input` (para wrf.exe): idéntico a la base (`cmp`), con start 2026-09-23_12:00:00, end 2026-09-23_13:00:00 y `run_hours = 1`.

En los dos: `interval_seconds = 10800`, `time_step = 6`, `e_vert = 35`, física de la plantilla del operativo y `&fdda` vacío (sin nudging). Los diffs contra la plantilla del operativo están en `namelist_real.diff` y `namelist_wrf.diff`.

Antes de cada ejecución se copió el namelist correspondiente a `namelist.input`. El `namelist.output` de real.exe se guardó como `namelist_real.output`.

## 1. real.exe

| Dato | Valor |
|---|---|
| Inicio y fin | 2026-11-04 12:59:18 → 12:59:27 |
| Tiempo real | **8,13 s** (user 6,45; sys 1,67) |
| Max RSS (ru_maxrss) | **10 574 656 kB (10,08 GiB)** |
| Pico RSS del watchdog | 10 521 160 kB (10,03 GB); mínimo de MemAvailable 28 032 088 kB |
| Salida | `real_em: SUCCESS COMPLETE REAL_EM INIT`; `LBC valid between these times 2026-09-23_12:00:00 and 2026-09-23_15:00:00` |
| Archivos | `wrfinput_d01` 85 786 776 B; `wrfbdy_d01` 6 708 166 B |

## 2. wrf.exe

| Dato | Valor |
|---|---|
| Inicio y fin | 2026-11-04 12:59:37 → 13:03:56 |
| Tiempo real | **259,14 s** (user 614,85; sys 24,52) |
| Terminación | **señal 11 (SIGSEGV)**, `exit_status: null` |
| Max RSS (ru_maxrss) | **11 598 376 kB (11,06 GiB)** |
| Pico RSS del watchdog | 11 591 604 kB (11,05 GB); mínimo de MemAvailable 26 974 680 kB; no cortó |
| Pasos ("Timing for main") | 39, hasta `2026-09-23_12:03:54` (39 × 6 s = 234 s simulados) |
| Segundos por paso, los 39 | promedio **1,5454**; mínimo **1,1945**; máximo **11,3432** (el primer paso) |
| Segundos por paso sin el primero (38) | promedio **1,2876** |
| Suma de "Timing for main" | 60,27 s, contra 259,14 s de reloj total |
| wrfout | `wrfout_d01_2026-09-23_12:00:00`: **83 166 882 B** (79,3 MiB). Es el único; la salida total es esa |
| SUCCESS COMPLETE WRF | **No** |
| NaN | 0 líneas con "NaN" |
| CFL | 4 avisos, todos en los primeros 24 s simulados (ver abajo) |

Encabezado del log:
```
 Ntasks in X            1 , ntasks in Y            1
WRF V4.5 MODEL
WRF NUMBER OF TILES FROM OMP_GET_MAX_THREADS =  12
WRF NUMBER OF TILES X FROM ENV WRF_NUM_TILES_X =   1
WRF NUMBER OF TILES Y FROM ENV WRF_NUM_TILES_Y =   8
```

Avisos de CFL (`wrf_stdout.log`, líneas 493-501):
```
           7  points exceeded v_cfl = 2 in domain d01 at time 2026-09-23_12:00:18 hours
Max   W:     12     23      5 W:   -8.12  w-cfl:    2.42  dETA:    0.02
          14  points exceeded v_cfl = 2 in domain d01 at time 2026-09-23_12:00:18 hours
Max   W:     12     24      3 W:  -20.97  w-cfl:    3.82  dETA:    0.01
          52  points exceeded v_cfl = 2 in domain d01 at time 2026-09-23_12:00:24 hours
Max   W:     12     23      3 W: -205.96  w-cfl:   16.42  dETA:    0.01
         115  points exceeded v_cfl = 2 in domain d01 at time 2026-09-23_12:00:24 hours
Max   W:     12     22      3 W: -774.63  w-cfl:   27.58  dETA:    0.01
```

Error exacto, al final de `wrf_stdout.log` (mtime 2026-11-04 13:03:56). Hay 8 repeticiones de las dos primeras líneas:
```
 Flerchinger USEd in NEW version. Iterations=          10

Program received signal SIGSEGV: Segmentation fault - invalid memory reference.

Backtrace for this error:
...
#0  0x14dd48c21772 in ???
#1  0x14dd48c20905 in ???
#2  0x14dd48961fcf in ???
#3  0x56025741ba34 in ???
#4  0x56025743ec9d in ???
#5  0x56025744e5a5 in ???
#6  0x5602564ce9b7 in ???
#7  0x14dd48f7136d in ???
#8  0x14dd489af043 in ???
#9  0x14dd48a2f61b in ???
#10  0xffffffffffffffff in ???
```

Datos literales relacionados, que se registran sin interpretar:
- El último paso registrado fue 12:03:54. El siguiente es 12:04:00, y el namelist tiene `radt = 4` (minutos).
- `src/modelo/wrf_runner.py:56-62` (mtime 2026-10-11 21:10:25) dice: "este wrf.exe (WRF-Chem 4.5, build OpenMP/serial de pgich) aborta (SIGSEGV en RRTMG-MCICA con tiles 1x8, o 'Bad value during integer read' en wrf_fddaobs_in / geth_idts con OMP>1) salvo que se ejecute en modo un solo hilo y un solo tile."
- El log tiene 417 551 líneas `Flerchinger USEd in NEW version. Iterations= 10` y pesa 24 240 554 B. Por eso se sube solo un resumen y las últimas 200 líneas.
- `OMP_NUM_THREADS = 12`, mientras que la PC tiene 10 CPU (nproc).

## 3. 400×400

**No se ejecutó.** El pico de RSS de real.exe en 300×300 fue de 10,08 GiB, menor a 12 GB, así que correspondía hacerlo. Pero wrf.exe falló antes y la regla dice parar.

## 4. Extrapolación (ESTIMACIÓN, no medición)

Advertencias:
- Se basa solo en 38-39 pasos (los primeros 4 min simulados) de una corrida que terminó en SIGSEGV.
- Supone costo constante por paso y escala lineal con el número de columnas: 600×600 equivale a 4 veces 300×300.
- No incluye pasos con escritura de wrfout horaria ni la inicialización completa.
- Las dos bases dan resultados muy distintos: la suma de "Timing for main" (60 s) es mucho menor que el reloj total (259 s).

1 h simulada son 600 pasos (3600 s ÷ 6 s).

| Base | s/paso | s reales por h simulada | 36 h | 48 h |
|---|---|---|---|---|
| 300×300, "Timing for main" sin el 1.er paso | 1,2876 | 1,2876 × 600 = **772,6 s** (12,9 min) | 772,6 × 36 = 27 812 s = **7,73 h** | 772,6 × 48 = 37 083 s = **10,30 h** |
| 300×300, "Timing for main" con el 1.er paso | 1,5454 | 927,2 s (15,5 min) | 33 381 s = 9,27 h | 44 508 s = 12,36 h |
| 300×300, reloj total ÷ pasos (259,14 ÷ 39) | 6,6446 | 3986,8 s (66,4 min) | 143 524 s = 39,87 h | 191 365 s = 53,16 h |
| **600×600** (× 4), "Timing" sin el 1.er paso | 5,150 | 772,6 × 4 = **3090 s** (51,5 min) | 3090 × 36 = 111 247 s = **30,9 h** | 3090 × 48 = 148 330 s = **41,2 h** |
| 600×600 (× 4), "Timing" con el 1.er paso | 6,182 | 3709 s | 37,1 h | 49,5 h |
| 600×600 (× 4), reloj total | 26,58 | 15 947 s | 159,5 h | 212,6 h |

Memoria en 600×600 (× 4):
- real.exe: 10 574 656 kB × 4 = 42 298 624 kB ≈ **40,3 GiB**.
- wrf.exe: 11 598 376 kB × 4 = 46 393 504 kB ≈ **44,2 GiB**.
- La PC tiene MemTotal 42 193 036 kB (40,2 GiB) y swap de 974 MiB. Lo medido directamente en 600×600 (real.exe ≥ 38,55 GB, cortado o matado) está en el `prueba_costo_1km.md` general.

## Archivos nuevos en `d300/wrf_v2/`

Texto:
- `prueba_costo_d300_v2.md`: este archivo.
- `namelistTemp.input.orig`, `namelist_d300_base.input`, `namelist_real.input`, `namelist_wrf.input`, `namelist.input`.
- `namelist_real_vs_base.diff`, `namelist_real.diff`, `namelist_wrf.diff`.
- `namelist_real.output`, `namelist.output`.
- `real_stdout.log`, `real_stdout.log.time`.
- `wrf_stdout.log` (24 MB, no se sube), `wrf_stdout.log.time`, `wrf_stdout_ultimas200.txt`, `wrf_resumen_timing.txt`.
- `memoria_real.csv` y `memoria_wrf.csv`, cada uno con su `.resumen.json`; `watchdog_real.out`, `watchdog_wrf.out`, `etapa_wrf.out`.

Pesados, no se suben: `wrfinput_d01`, `wrfbdy_d01`, `wrfout_d01_2026-09-23_12:00:00`.

Enlaces: `em_real/*` y los `met_em`.
