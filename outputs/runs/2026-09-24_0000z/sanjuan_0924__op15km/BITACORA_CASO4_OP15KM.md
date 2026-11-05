# Bitácora Caso 4 (San Juan) op15km — 36 horas

**Estado**: ✅ COMPLETADO  
**Fecha inicio**: 2026-11-05 13:30 UTC  
**Configuración**: Physics explícita (cu=6 Tiedtke, sf_urban=2 BEP, ra_lw=4 RRTMG)  
**Namelists**: cu_physics=6, ra_lw=4, ra_sw=4, sf_urban=2, fdda_end=720, run_hours=36  
**geo_em**: MAP_PROJ=1, CEN_LAT=-31.53, CEN_LON=-68.53 ✓  

Archivos: pipeline.log, geogrid.log, ungrib.log, metgrid.log, real.log, wrf_control.log, wrf_nudged.log, geo_em_check.txt

## Validación (2026-11-05 14:18 UTC)

**Estado WRF**: ✅ Completado 13:34-14:01 UTC (SUCCESS en ambas ramas)  
**Validación**: ✅ Ejecutada con `--validate-only` post-WRF  
**Métricas**: ✅ Generadas: evaluacion_flujo.json, errores_largo.csv, metricas_por_horizonte.csv, metricas_por_tramo.csv  

Nota: El estado "COMPLETADO" en commit anterior refería solo a WRF. La validación (análisis de métricas, RMSE, comparación control/nudging) se corrió posteriormente con --validate-only tras verificar que los wrfout eran del Caso 4 (ciclo 2026-09-23_12:00:00).
