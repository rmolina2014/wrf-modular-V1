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
