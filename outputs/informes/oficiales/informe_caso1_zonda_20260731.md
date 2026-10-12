# Caso 1 - Viento Zonda

**Fecha del evento:** 2026-07-31 | **Ciclo:** 00Z -> 24Z | **Informe generado:** 2026-10-12 10:45

## Descripción del evento

Evento de viento zonda sobre San Juan

**Fuente:** gfs_aws

## Estado de la ejecución

**Estado:** ✅ EJECUTADO

## Configuración aplicada

| Parámetro | Valor |
|-----------|-------|
| Dominio | 1 dominio, 15 km, 80×60, mercator (-31.5°, -68.5°) |
| Ciclo | 00Z–24Z (24 h) |
| Forzante | GFS 0.25° (AWS) |
| Obs nudging | `obs_nudge_opt=1`, coef viento/temp/humedad=0.0001, `obs_twindo=1.0` |
| Nudged vs Control | misma inicialización; solo cambia `obs_nudge_opt` (1 vs 0) |
| Validación | multi-temporal 00Z 06Z 12Z 18Z 24Z vs observaciones de estaciones |

## Limitación conocida del dominio (relevant para el análisis)

El dominio de 15 km no resuelve la topografía profunda de la precordillera (errores de altura del modelo de entre +201 m y +918 m en las estaciones, con máximos en CARACOLES +918 m, PUNTA_NEGRA +420 m y CUESTA_Viento +378 m). Por eso el análisis de **Caso 1 - Viento Zonda** se restringe a la **firma térmica** (salto de T2 y caída de RH), y el viento se interpreta solo de forma cualitativa. Ver también `documentacion_proyecto/informe_avances_fases_proyecto.md`.

## Observaciones disponibles

- Registros válidos: **1880** en el día, **1880** en la ventana 00Z–24Z.
- Estaciones con datos en ventana: **7**

| Estación | Registros (00Z–24Z) |
|----------|--------------------|
| CUESTA_Viento | 288 |
| ECOHUMUS | 288 |
| PUNTA_NEGRA | 287 |
| VALLE_FERTIL | 285 |
| ULLUM_EMBALSE | 277 |
| INTA_POCITO | 268 |
| CARACOLES | 187 |

## Desempeno del flujo (end-to-end)

Tiempos por etapa medidos en la ejecucion (artefacto `evaluacion_flujo.json`); cubre desde la llamada a la API EcoWitt hasta el informe de validacion.

| Etapa (orquestador) | Tiempo |
|---------------------|--------|
| Ingesta API EcoWitt + cobertura | 1.0 min |
| Parseo y QC -> obs_flat (Little_R) | 0.10 s |
| Descarga GFS 0.25 (AWS) | 11.5 min |
| WPS (geogrid+ungrib+metgrid) | 3.2 min |
| Propagacion met_em al run dir | 0.07 s |
| Pipeline WRF completo (preflight+real+nudged+control+validacion) | 20.8 min |

| Etapa (pipeline WRF) | Tiempo |
|----------------------|--------|
| Little_R -> OBS_DOMAIN101 | 0.18 s |
| Preflight (validacion obs/namelist) | 0.03 s |
| real.exe | 1.39 s |
| wrf.exe nudged (24 h) | 10.4 min |
| wrf.exe control (24 h) | 10.2 min |
| Validacion multi-temporal + informe de evolucion | 10.16 s |

**Tiempo total end-to-end:** 36.5 min.

## Resultados: Nudged vs Control

RMSE/Bias de la corrida nudgada (N) y de control (C) por tiempo de validación. dRMSE = RMSE(C) - RMSE(N) (positivo ⇒ mejora con nudging; negativo ⇒ degrada). 00Z: N≡C por construcción.

### T2 (K)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 7 | 4.43 | 4.43 | +0.00 | +2.98 | +2.98 | -0.610 | -0.610 |
| 06Z | 7 | 3.37 | 4.43 | +1.06 | +1.48 | +2.60 | -0.600 | -0.863 |
| 12Z | 7 | 10.55 | 10.52 | -0.03 | -10.36 | -10.34 | +0.768 | +0.791 |
| 18Z | 6 | 2.32 | 2.50 | +0.18 | +1.75 | +1.85 | +0.951 | +0.937 |
| 24Z | 6 | 2.72 | 3.54 | +0.82 | -0.25 | +0.83 | +0.584 | +0.427 |


### PSFC (hPa)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 8 | 41.92 | 41.92 | +0.00 | -32.39 | -32.39 | +0.861 | +0.861 |
| 06Z | 8 | 42.90 | 43.02 | +0.12 | -33.41 | -33.61 | +0.860 | +0.860 |
| 12Z | 8 | 43.28 | 43.29 | +0.01 | -33.60 | -33.66 | +0.861 | +0.860 |
| 18Z | 7 | 32.22 | 32.41 | +0.19 | -28.28 | -28.46 | +0.942 | +0.942 |
| 24Z | 7 | 30.55 | 31.42 | +0.87 | -26.06 | -27.17 | +0.943 | +0.943 |


### RH (%)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 7 | 27.96 | 27.96 | +0.00 | -24.75 | -24.75 | +0.818 | +0.818 |
| 06Z | 7 | 32.95 | 36.22 | +3.27 | -27.79 | -31.21 | +0.654 | +0.607 |
| 12Z | 7 | 23.15 | 23.51 | +0.36 | +19.37 | +18.22 | +0.737 | +0.751 |
| 18Z | 6 | 6.07 | 6.54 | +0.48 | -4.41 | -4.67 | +0.637 | +0.558 |
| 24Z | 6 | 5.43 | 6.40 | +0.96 | -1.53 | -3.25 | -0.355 | -0.491 |


### Wind (m/s)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 7 | 2.32 | 2.32 | +0.00 | +1.65 | +1.65 | -0.192 | -0.192 |
| 06Z | 7 | 2.64 | 3.11 | +0.47 | +1.99 | +2.15 | -0.330 | -0.418 |
| 12Z | 7 | 4.48 | 4.71 | +0.23 | -1.47 | -1.24 | +0.379 | +0.230 |
| 18Z | 6 | 8.02 | 9.06 | +1.05 | +6.89 | +7.43 | -0.750 | -0.763 |
| 24Z | 6 | 7.30 | 9.78 | +2.49 | +6.84 | +8.54 | -0.028 | +0.277 |


### Ajuste vs. Generalización (hold-out espacial)

Las estaciones con `rol='evaluacion'` en `config/estaciones.json` nunca se asimilan (quedan fuera de `OBS_DOMAIN101`); sus métricas miden si el nudging **generaliza** a lugares sin datos, no solo si reproduce lo que ya se le dio (estaciones 'asimiladas').

#### T2 (K)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 2 | 4.83 | 4.83 | 3.22 | 3.22 |
| 06Z | 5 | 2 | 3.45 | 4.58 | 3.14 | 4.03 |
| 12Z | 5 | 2 | 9.63 | 9.72 | 12.56 | 12.29 |
| 18Z | 5 | 1 | 1.67 | 1.77 | 4.29 | 4.67 |
| 24Z | 5 | 1 | 2.94 | 3.75 | 1.01 | 2.14 |


#### PSFC (hPa)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 3 | 29.08 | 29.08 | 57.25 | 57.25 |
| 06Z | 5 | 3 | 30.06 | 30.22 | 58.32 | 58.42 |
| 12Z | 5 | 3 | 30.98 | 30.99 | 58.27 | 58.28 |
| 18Z | 5 | 2 | 32.56 | 32.81 | 31.35 | 31.40 |
| 24Z | 5 | 2 | 31.20 | 32.03 | 28.86 | 29.83 |


#### RH (%)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 2 | 24.79 | 24.79 | 34.64 | 34.64 |
| 06Z | 5 | 2 | 30.29 | 33.38 | 38.79 | 42.49 |
| 12Z | 5 | 2 | 23.42 | 25.15 | 22.45 | 18.80 |
| 18Z | 5 | 1 | 3.83 | 4.36 | 12.14 | 12.72 |
| 24Z | 5 | 1 | 3.67 | 4.33 | 10.48 | 12.33 |


#### Wind (m/s)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 2 | 2.62 | 2.62 | 1.30 | 1.30 |
| 06Z | 5 | 2 | 2.73 | 3.34 | 2.41 | 2.45 |
| 12Z | 5 | 2 | 0.81 | 0.82 | 8.28 | 8.72 |
| 18Z | 5 | 1 | 8.63 | 9.75 | 3.65 | 4.19 |
| 24Z | 5 | 1 | 7.60 | 9.60 | 5.54 | 10.67 |


### Conclusiones del caso

Para la interpretación completa (series, gráficos y comparación con observaciones) ver `outputs/runs/2026-07-31_0000z/caso1_zonda/` (informe de evolución, tablas por horario y wrfouts).

---
*Informe generado automáticamente por `src/casos/run_casos.py`.*