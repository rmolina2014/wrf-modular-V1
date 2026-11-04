# Bitácora de experimentos

Las entradas se agregan al final y no se editan.

---

## 04-11-2026: Prueba de costo WRF 1 km, configuración operativa (Caso 4, ciclo GFS 2026-09-23 12Z)

**Commit:** `9d5b1ad` (rama `verif_idynin`)

**Qué se hizo**
- Plan: correr la configuración del operativo (`namelistTemp.wps` y `namelistTemp.input`; 600×600, dx 1 km, lambert, `time_step=6`, `e_vert=35`) durante 1 h simulada, solo control y sin nudging. Se usaron los GRIB2 ya descargados en `wps_sanjuan/gfs_data/2026-09-23_12/`.
- WPS en 600×600 terminó bien. En WPS, `end_date` se movió a 15:00 porque `interval_seconds=10800` no admite un `end_date` a las 13:00.
- real.exe en 600×600:
  - Con el lanzamiento de la tesis (OMP=1, tiles 1×1) murió por señal 9 (`oom_kill 1`) con 38,55 GB.
  - Con el lanzamiento del operativo (`source env.bash`: OMP=12, tiles 1×8) lo cortó el watchdog con 33,96 GB (MemAvailable < 3 GB).
- Dominio reducido 300×300: WPS terminó bien. real.exe dio `FATAL: Make the end time at least one 'interval_seconds' beyond the start time` (namelist con fin a las 13:00 e intervalo de 3 h). No se corrió wrf.exe.
- Binarios WRF: compilación smpar (OpenMP; MPI de stub). No hay límites de memoria por cgroup. Swap: 974 MiB.

**Archivos subidos** (47; logs con `git add -f` porque `.gitignore` excluye `*.log`)
- `outputs/prueba_costo_1km/`: `prueba_costo_1km.md`, `medir.py`, `watchdog_mem.py`, `etapa.sh`, `env_tesis.sh`, `env_operativo.sh`.
- `outputs/prueba_costo_1km/wps/`, `wrf/`, `d300/wps/`, `d300/wrf/`: namelists, diffs, logs de geogrid/ungrib/metgrid/real, `*.time` y `memoria_*.csv`.
- No se subieron geo_em, met_em, GFS intermedios, GRIB2 ni wrfinput/wrfbdy (estos no existen).

**Resumen (punto 6, parcial)**
1. WPS 600×600: geogrid 5 s; ungrib 27 s (13,5 s por tiempo); metgrid 34 s (17 s por tiempo); RSS máx < 1 GB.
2. real.exe 600×600 no cabe en 40 GB de RAM. Medido: ≥ 38,5 GB. Estimado desde 300×300 (`alloc_space_field` 10,5 GB × 4): ≈ 39–42 GB.
3. wrf.exe no se ejecutó, así que no hay segundos por paso ni extrapolación a 36/48 h. Falta decidir cómo fechar real.exe frente a wrf.exe (fin a las 13:00 con intervalo de 3 h no es válido para real.exe).

## 04-11-2026: Evidencia geog_data_res, archivos livianos pendientes

**Commit:** `9d5b1ad` (mismo commit que la entrada anterior). `evidencia_geog.md` ya se había subido en `bba7b02`.

**Qué se hizo:** se subieron los archivos livianos de la comparación 'lowres' contra 'default' de geogrid (dominio de la tesis, 80×60, 15 km). Resultado: la diferencia default − lowres en HGT_M tiene un máximo absoluto de 175,7 m y un RMS de 20,0 m. La altura de grilla en las estaciones, comparada con la tabla de la tesis, no difiere más de 0,4 m.

**Archivos subidos:** `outputs/evidencia_geog/analisis_geog.py`, `tabla_estaciones.csv`, `resultados_geog.json`, `geogrid_lowres/namelist.wps`, `geogrid_default/namelist.wps`, `geogrid_lowres/geogrid.log`, `geogrid_default/geogrid.log`. No se subieron `geo_em.d01.nc` ni copias del operativo.
