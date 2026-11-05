# Bitácora: Corrida op15km (15 km) — caso sanjuan_0924

**Fecha inicio**: 2026-11-04 14:33:55 UTC  
**Rama**: op15km  
**Brazo**: NUDGED solo (obs_nudge_opt=1)  
**Resolución**: 15 km (dx=15000, dy=15000)  
**Dominio**: 80x60 puntos, 35 niveles verticales

## Estado de Ejecución

### Preflight: ✅ OK
- 8 chequeos realizados, 0 bloqueantes, 1 advertencia (no se informó t0/asim_horas)
- 288 observaciones en ventana 2026-09-24 00:00:00 → 03:00:00 UTC
- Datos validados: `/outputs/runs/2026-09-24_0000z/sanjuan_0924__op15km/input/`

### real.exe: ✅ SUCCESS COMPLETE REAL_EM INIT (14:33:56)
- Duración: 0.7s
- wrfinput_d01 y wrfbdy_d01 generados
- LBC válido: 2026-09-24_00:00:00 → 2026-09-24_03:00:00

### wrf.exe (Nudged): ⚠️ EJECUTADO → GENERÓ SALIDA (14:33:56+)
**Hallazgo crucial**: 
- `wrf_nudged.log` **COMPLETA CON SUCCESS**: `wrf: SUCCESS COMPLETE WRF`
- Simulación llega hasta 2026-09-25_00:00:00 (24+ horas)
- Tres archivos wrfout generados en `/home/pgich/wrf-operativo/ejecutables/WRF_casos_24h/`:
  - wrfout_d01_2026-09-24_00:00:00 (mtime: 2026-11-04 14:33:57)
  - wrfout_d01_2026-09-24_01:00:00 (mtime: 2026-11-04 14:34:20)
  - wrfout_d01_2026-09-24_02:00:00 (mtime: 2026-11-04 14:34:44)

**Problema**: El pipeline.log se corta después de lanzar `./wrf.exe` (línea 54) → **LA SALIDA DEL PIPELINE NO FUE CAPTURADA** tras ese punto.

## Causa Probable

1. **wrf.exe se lanzó en background** → El script pipeline continuó (o terminó) sin esperar
2. **Redirección de logs no persistió** → El log del pipeline no capturó la ejecución completa de wrf.exe
3. **Salida de wrf.exe no se copió** → Los wrfout_d01 existen en `/home/pgich/wrf-operativo/` pero NO en el directorio de salida sanjuan_0924__op15km

## Archivos Generados

- **Inputs para WRF**:
  - namelist_nudged.input (obs_nudge_opt=1, run_hours=3, fdda_end=180)
  - OBS_DOMAIN101 (288 obs en formato correcto)
  - datos_validados_20260924_000000.csv
  - littler_20260924_000000.txt

- **Logs** (copiados en esta sesión):
  - pipeline.log (desde pipeline_caso4_sanjuan_0924__op15km.log)
  - wrf_nudged.log (desde /operativo/ejecutables/WRF_casos_24h/)
  - geo_em_check.txt (verificación de MAP_PROJ=1, CEN_LAT/LON)

- **Configuración**:
  - diff_config.md (diferencias vs caso original sanjuan_0924)

## Próximos Pasos (Recomendados)

1. **Investigar script de pipeline** → Verificar cómo se lanzan los subprocesos y la captura de logs
2. **Copiar wrfout pendientes** → Los 3 primeros wrfout_d01 existen pero no están en sanjuan_0924__op15km/
3. **Continuar o reintentar** → Decidir si:
   - Copiar los wrfout existentes y diagnosticar por qué se detuvieron en 02:00:00 (falta 22 horas)
   - Relanzar la corrida con captura de logs correcta
   - Investigar por qué se generaron solo 3 timesteps cuando run_hours=3 deberá ser 24

## Sistema

- **Host**: Linux 6.1.0-13-amd64
- **Procesos**: Sin OOM, KILLED, SEGFAULT detectados en dmesg/journalctl
- **Subdirectorio nudged en operativo**: Contiene wrfout anteriores (dic 31 2025 - ene 1 2026), NO los nuevos

---

## ⚠️ CORRECCIONES (2026-11-05 08:30 UTC)

### PROBLEMA 1: namelist_nudged.input tiene física incorrecta
**Entrada anterior**: Reportó que se usó namelist.input (CONUS, cu=-1, sf_urban=0).
**HECHO VERIFICADO**: 
- Pipeline cargó namelist.input de **raíz** (main), no el de rama op15km
- Rama op15km contiene: cu_physics=6, sf_urban_physics=2, fdda_end=720
- El archivo raíz (mtime 2026-11-04 14:32) tiene valores operativo (CONUS)
- NamelistManager usa "namelist.input" de raíz si "config/namelist.input.template" no existe

**Causa**: Branch op15km no fue seleccionada cuando se lanzó el pipeline.

---

### PROBLEMA 2: wrf_nudged.log subido es INCORRECTO
**Entrada anterior**: Subió archivo de `/operativo/ejecutables/WRF_casos_24h/wrf_nudged.log`
**HECHO VERIFICADO**:
- Archivo contiene datos del **caso 4 oficial** (arranca 2026-09-23_12:00:00)
- NO contiene datos de op15km (debería arrancar 2026-09-24_00:00:00)
- El archivo fue removido de la carpeta op15km.
- **El log real de op15km no existe** — solo hay 3 wrfout en operativo con no hay log correspondiente

---

### PROBLEMA 3: diff_config.md usaba fuentes imprecisas
**Entrada anterior**: Tabla con valores genéricos
**HECHO VERIFICADO y CORREGIDO**:
- **Operativo (sanjuan d01)**: Ahora sourced de `/home/pgich/wrf-operativo/datos/namelists/sanjuan/namelistTemp.input`
  - `e_we=141, e_sn=200, dx=4000, dy=4000, time_step=15, ra_lw=1, cu=0, sf_urban=0`
- **Control oficial**: Ahora sourced de `/home/pgich/wrf-modular-V1/outputs/runs/2026-09-24_0000z/sanjuan_0924/namelist_control.input`
  - `e_we=80, e_sn=60, dx=15000, dy=15000, time_step=45, ra_lw=-1, cu=-1, sf_urban=0, fdda_end=720`
- **op15km**: Rama op15km (`cu=6, ra_lw=4, ra_sw=4, sf_urban=2, fdda_end=720`)
- Tabla rehecha con fuentes explícitas.

---

### Resumen de lo que SÍ pasó:
1. real.exe ejecutó correctamente
2. wrf.exe **comenzó** a ejecutarse (14:33:56 +)
3. **Se generaron 3 wrfout** en `/operativo/ejecutables/WRF_casos_24h/` (mtime 14:33:57, 14:34:20, 14:34:44)
4. Pipeline log se cortó sin capturar la salida de wrf.exe
5. Los wrfout nunca se copiaron al directorio de salida esperado

### Resumen de lo que NO pasó:
1. op15km **NO usó la rama op15km** (usó main/raíz)
2. Las 24 horas de simulación **NO se completaron** (solo 3 timesteps generados)
3. No hay un log limpio de la corrida op15km — el log subido era de otro caso
