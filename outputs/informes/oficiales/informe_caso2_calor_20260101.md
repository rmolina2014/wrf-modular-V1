# Caso 2 - Calor de verano (Año Nuevo)

**Fecha del evento:** 2026-01-01 | **Ciclo:** 00Z -> 24Z | **Informe generado:** 2026-10-12 21:03

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

- Registros válidos: **301** en el día, **301** en la ventana 00Z–24Z.
- Estaciones con datos en ventana: **7**

| Estación | Registros (00Z–24Z) |
|----------|--------------------|
| CARACOLES | 49 |
| CUESTA_Viento | 49 |
| ECOHUMUS | 49 |
| PUNTA_NEGRA | 49 |
| ULLUM_EMBALSE | 49 |
| VALLE_FERTIL | 49 |
| INTA_POCITO | 7 |

## Desempeno del flujo (end-to-end)

Tiempos por etapa medidos en la ejecucion (artefacto `evaluacion_flujo.json`); cubre desde la llamada a la API EcoWitt hasta el informe de validacion.

| Etapa (orquestador) | Tiempo |
|---------------------|--------|
| Ingesta API EcoWitt + cobertura | 0.02 s |
| Parseo y QC -> obs_flat (Little_R) | 0.04 s |
| Descarga GFS 0.25 (AWS) | 5.34 s |
| WPS (geogrid+ungrib+metgrid) | 2.6 min |
| Propagacion met_em al run dir | 0.06 s |
| Pipeline WRF completo (preflight+real+nudged+control+validacion) | 11.5 min |

| Etapa (pipeline WRF) | Tiempo |
|----------------------|--------|
| Little_R -> OBS_DOMAIN101 | 0.04 s |
| Preflight (validacion obs/namelist) | 0.01 s |
| real.exe | 1.58 s |
| wrf.exe nudged (24 h) | 11.2 min |
| Validacion multi-temporal + informe de evolucion | 11.99 s |

**Tiempo total end-to-end:** 14.2 min.

## Resultados: Nudged vs Control

RMSE/Bias de la corrida nudgada (N) y de control (C) por tiempo de validación. dRMSE = RMSE(C) - RMSE(N) (positivo ⇒ mejora con nudging; negativo ⇒ degrada). 00Z: N≡C por construcción.

### T2 (K)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 7 | 4.32 | 4.32 | +0.00 | -1.89 | -1.89 | +0.243 | +0.243 |
| 06Z | 6 | 3.19 | 3.35 | +0.17 | -0.88 | -0.16 | -0.324 | -0.307 |
| 12Z | 6 | 2.94 | 3.22 | +0.28 | -0.82 | -0.34 | +0.493 | +0.443 |
| 18Z | 6 | 3.11 | 3.04 | -0.07 | -1.45 | -1.12 | +0.812 | +0.811 |
| 24Z | 6 | 4.25 | 4.04 | -0.20 | -1.74 | -1.53 | +0.045 | +0.134 |


### PSFC (hPa)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 7 | 42.53 | 42.53 | +0.00 | -32.33 | -32.33 | +0.858 | +0.858 |
| 06Z | 6 | 45.75 | 45.81 | +0.06 | -35.06 | -35.17 | +0.839 | +0.840 |
| 12Z | 6 | 45.88 | 45.88 | +0.01 | -35.30 | -35.36 | +0.843 | +0.843 |
| 18Z | 6 | 45.11 | 45.07 | -0.04 | -34.90 | -34.89 | +0.845 | +0.845 |
| 24Z | 6 | 44.91 | 44.93 | +0.02 | -34.58 | -34.64 | +0.841 | +0.841 |


### RH (%)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 7 | 19.25 | 19.25 | +0.00 | -8.48 | -8.48 | +0.315 | +0.315 |
| 06Z | 6 | 18.83 | 24.84 | +6.01 | -11.87 | -18.58 | -0.177 | -0.371 |
| 12Z | 6 | 10.16 | 14.23 | +4.08 | -6.23 | -10.28 | -0.915 | -0.938 |
| 18Z | 6 | 3.33 | 5.87 | +2.54 | -1.48 | -4.96 | +0.789 | +0.700 |
| 24Z | 6 | 8.75 | 7.78 | -0.97 | +2.08 | -3.06 | -0.007 | +0.252 |


### Wind (m/s)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 7 | 4.10 | 4.10 | +0.00 | +3.76 | +3.76 | +0.162 | +0.162 |
| 06Z | 6 | 1.46 | 1.21 | -0.25 | +0.78 | +0.78 | +0.391 | +0.724 |
| 12Z | 6 | 1.16 | 1.36 | +0.19 | +0.52 | +0.88 | -0.240 | -0.250 |
| 18Z | 6 | 3.02 | 3.38 | +0.36 | +2.87 | +3.23 | +0.776 | +0.778 |
| 24Z | 6 | 1.28 | 1.70 | +0.42 | +1.10 | +1.44 | +0.881 | +0.800 |


### Ajuste vs. Generalización (hold-out espacial)

Las estaciones con `rol='evaluacion'` en `config/estaciones.json` nunca se asimilan (quedan fuera de `OBS_DOMAIN101`); sus métricas miden si el nudging **generaliza** a lugares sin datos, no solo si reproduce lo que ya se le dio (estaciones 'asimiladas').

#### T2 (K)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 2 | 3.55 | 3.55 | 5.81 | 5.81 |
| 06Z | 4 | 2 | 3.18 | 3.44 | 3.20 | 3.18 |
| 12Z | 4 | 2 | 2.48 | 2.84 | 3.70 | 3.88 |
| 18Z | 4 | 2 | 1.92 | 1.89 | 4.64 | 4.53 |
| 24Z | 4 | 2 | 3.37 | 3.14 | 5.60 | 5.42 |


#### PSFC (hPa)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 2 | 29.11 | 29.11 | 64.90 | 64.90 |
| 06Z | 4 | 2 | 31.66 | 31.77 | 65.39 | 65.41 |
| 12Z | 4 | 2 | 32.04 | 32.06 | 65.27 | 65.27 |
| 18Z | 4 | 2 | 31.47 | 31.44 | 64.22 | 64.16 |
| 24Z | 4 | 2 | 31.25 | 31.29 | 64.01 | 64.01 |


#### RH (%)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 2 | 20.96 | 20.96 | 14.08 | 14.08 |
| 06Z | 4 | 2 | 20.81 | 26.63 | 14.03 | 20.80 |
| 12Z | 4 | 2 | 10.38 | 14.31 | 9.70 | 14.07 |
| 18Z | 4 | 2 | 2.77 | 5.97 | 4.23 | 5.66 |
| 24Z | 4 | 2 | 8.36 | 9.05 | 9.50 | 4.21 |


#### Wind (m/s)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 2 | 3.80 | 3.80 | 4.78 | 4.78 |
| 06Z | 4 | 2 | 1.75 | 1.37 | 0.50 | 0.81 |
| 12Z | 4 | 2 | 1.26 | 1.50 | 0.93 | 1.01 |
| 18Z | 4 | 2 | 2.94 | 3.36 | 3.17 | 3.42 |
| 24Z | 4 | 2 | 1.26 | 1.94 | 1.31 | 1.06 |


### Conclusiones del caso

Para la interpretación completa (series, gráficos y comparación con observaciones) ver `outputs/runs/2026-01-01_0000z/caso2_calor/` (informe de evolución, tablas por horario y wrfouts).

---
*Informe generado automáticamente por `src/casos/run_casos.py`.*