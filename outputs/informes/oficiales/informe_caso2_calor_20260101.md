# Caso 2 - Calor de verano (Año Nuevo)

**Fecha del evento:** 2026-01-01 | **Ciclo:** 00Z -> 24Z | **Informe generado:** 2026-10-11 23:29

## Descripción del evento

Evento de calor en verano sobre San Juan

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

El dominio de 15 km no resuelve la topografía profunda de la precordillera (errores de altura del modelo de entre +201 m y +918 m en las estaciones, con máximos en CARACOLES +918 m, PUNTA_NEGRA +420 m y CUESTA_Viento +378 m). Por eso el análisis de **Caso 2 - Calor de verano (Año Nuevo)** se restringe a la **firma térmica** (salto de T2 y caída de RH), y el viento se interpreta solo de forma cualitativa. Ver también `documentacion_proyecto/informe_avances_fases_proyecto.md`.

## Observaciones disponibles

- Registros válidos: **290** en el día, **290** en la ventana 00Z–24Z.
- Estaciones con datos en ventana: **7**

| Estación | Registros (00Z–24Z) |
|----------|--------------------|
| CARACOLES | 48 |
| CUESTA_Viento | 48 |
| ECOHUMUS | 48 |
| PUNTA_NEGRA | 48 |
| ULLUM_EMBALSE | 48 |
| VALLE_FERTIL | 48 |
| INTA_POCITO | 2 |

## Desempeno del flujo (end-to-end)

Tiempos por etapa medidos en la ejecucion (artefacto `evaluacion_flujo.json`); cubre desde la llamada a la API EcoWitt hasta el informe de validacion.

| Etapa (orquestador) | Tiempo |
|---------------------|--------|
| Ingesta API EcoWitt + cobertura | 51.10 s |
| Parseo y QC -> obs_flat (Little_R) | 0.02 s |
| Descarga GFS 0.25 (AWS) | 9.8 min |
| WPS (geogrid+ungrib+metgrid) | 2.2 min |
| Propagacion met_em al run dir | 0.02 s |
| Pipeline WRF completo (preflight+real+nudged+control+validacion) | 19.4 min |

| Etapa (pipeline WRF) | Tiempo |
|----------------------|--------|
| Little_R -> OBS_DOMAIN101 | 0.04 s |
| Preflight (validacion obs/namelist) | 0.00 s |
| real.exe | 1.38 s |
| wrf.exe nudged (24 h) | 9.7 min |
| wrf.exe control (24 h) | 9.6 min |
| Validacion multi-temporal + informe de evolucion | 10.29 s |

**Tiempo total end-to-end:** 32.4 min.

## Resultados: Nudged vs Control

RMSE/Bias de la corrida nudgada (N) y de control (C) por tiempo de validación. dRMSE = RMSE(C) - RMSE(N) (positivo ⇒ mejora con nudging; negativo ⇒ degrada). 00Z: N≡C por construcción.

### T2 (K)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 7 | 3.66 | 3.66 | +0.00 | +1.14 | +1.14 | +0.350 | +0.350 |
| 06Z | 6 | 3.28 | 4.13 | +0.84 | +0.05 | +1.13 | -0.334 | -0.377 |
| 12Z | 6 | 5.10 | 5.46 | +0.36 | -4.55 | -4.95 | +0.830 | +0.853 |
| 18Z | 6 | 3.10 | 3.23 | +0.13 | -1.25 | -1.45 | +0.805 | +0.777 |
| 24Z | 6 | 4.32 | 4.73 | +0.41 | -0.82 | +1.54 | -0.178 | -0.038 |


### PSFC (hPa)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 7 | 44.55 | 44.55 | +0.00 | -34.97 | -34.97 | +0.859 | +0.859 |
| 06Z | 6 | 45.15 | 45.21 | +0.06 | -34.05 | -34.21 | +0.839 | +0.839 |
| 12Z | 6 | 44.97 | 44.91 | -0.06 | -34.18 | -34.08 | +0.842 | +0.841 |
| 18Z | 6 | 44.06 | 43.86 | -0.19 | -33.43 | -33.15 | +0.841 | +0.842 |
| 24Z | 6 | 45.69 | 46.07 | +0.39 | -35.31 | -36.07 | +0.841 | +0.842 |


### RH (%)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 7 | 19.77 | 19.77 | +0.00 | -16.24 | -16.24 | +0.443 | +0.443 |
| 06Z | 6 | 20.02 | 28.37 | +8.35 | -14.05 | -21.92 | -0.132 | -0.583 |
| 12Z | 6 | 6.17 | 6.85 | +0.68 | +3.16 | +1.50 | +0.477 | +0.311 |
| 18Z | 6 | 2.48 | 4.53 | +2.05 | -0.67 | -3.41 | +0.914 | +0.727 |
| 24Z | 6 | 9.83 | 14.12 | +4.29 | -0.96 | -11.51 | -0.035 | +0.300 |


### Wind (m/s)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 7 | 4.33 | 4.33 | +0.00 | +4.11 | +4.11 | +0.408 | +0.408 |
| 06Z | 6 | 1.86 | 1.96 | +0.10 | +1.31 | +0.97 | +0.115 | -0.250 |
| 12Z | 6 | 0.84 | 0.88 | +0.04 | +0.01 | +0.00 | +0.533 | +0.458 |
| 18Z | 6 | 2.80 | 3.13 | +0.33 | +2.37 | +2.73 | +0.664 | +0.654 |
| 24Z | 6 | 1.60 | 1.89 | +0.29 | +1.42 | +1.58 | +0.929 | +0.740 |


### Ajuste vs. Generalización (hold-out espacial)

Las estaciones con `rol='evaluacion'` en `config/estaciones.json` nunca se asimilan (quedan fuera de `OBS_DOMAIN101`); sus métricas miden si el nudging **generaliza** a lugares sin datos, no solo si reproduce lo que ya se le dio (estaciones 'asimiladas').

#### T2 (K)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 2 | 3.85 | 3.85 | 3.14 | 3.14 |
| 06Z | 4 | 2 | 3.70 | 4.74 | 2.21 | 2.48 |
| 12Z | 4 | 2 | 4.42 | 4.96 | 6.24 | 6.35 |
| 18Z | 4 | 2 | 1.84 | 1.87 | 4.70 | 4.93 |
| 24Z | 4 | 2 | 4.33 | 5.33 | 4.30 | 3.18 |


#### PSFC (hPa)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 2 | 31.40 | 31.40 | 66.94 | 66.94 |
| 06Z | 4 | 2 | 31.03 | 31.11 | 64.73 | 64.77 |
| 12Z | 4 | 2 | 30.96 | 30.85 | 64.42 | 64.39 |
| 18Z | 4 | 2 | 30.20 | 30.02 | 63.24 | 63.01 |
| 24Z | 4 | 2 | 32.06 | 32.59 | 64.86 | 65.14 |


#### RH (%)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 2 | 23.12 | 23.12 | 5.72 | 5.72 |
| 06Z | 4 | 2 | 21.33 | 29.66 | 17.09 | 25.60 |
| 12Z | 4 | 2 | 6.67 | 7.78 | 5.01 | 4.43 |
| 18Z | 4 | 2 | 2.31 | 5.07 | 2.80 | 3.19 |
| 24Z | 4 | 2 | 11.49 | 16.29 | 5.10 | 8.19 |


#### Wind (m/s)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 2 | 4.13 | 4.13 | 4.79 | 4.79 |
| 06Z | 4 | 2 | 2.26 | 2.19 | 0.39 | 1.38 |
| 12Z | 4 | 2 | 0.90 | 0.99 | 0.71 | 0.61 |
| 18Z | 4 | 2 | 2.65 | 2.94 | 3.10 | 3.48 |
| 24Z | 4 | 2 | 1.64 | 2.07 | 1.53 | 1.48 |


### Conclusiones del caso

Para la interpretación completa (series, gráficos y comparación con observaciones) ver `outputs/runs/2026-01-01_0000z/caso2_calor/` (informe de evolución, tablas por horario y wrfouts).

---
*Informe generado automáticamente por `src/casos/run_casos.py`.*