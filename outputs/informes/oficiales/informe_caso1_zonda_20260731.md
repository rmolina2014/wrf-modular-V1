# Caso 1 - Viento Zonda

**Fecha del evento:** 2026-07-31 | **Ciclo:** 00Z -> 24Z | **Informe generado:** 2026-10-12 20:48

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

- Registros válidos: **1923** en el día, **1923** en la ventana 00Z–24Z.
- Estaciones con datos en ventana: **7**

| Estación | Registros (00Z–24Z) |
|----------|--------------------|
| CUESTA_Viento | 289 |
| ECOHUMUS | 289 |
| PUNTA_NEGRA | 289 |
| VALLE_FERTIL | 286 |
| ULLUM_EMBALSE | 278 |
| INTA_POCITO | 269 |
| CARACOLES | 223 |

## Desempeno del flujo (end-to-end)

Tiempos por etapa medidos en la ejecucion (artefacto `evaluacion_flujo.json`); cubre desde la llamada a la API EcoWitt hasta el informe de validacion.

| Etapa (orquestador) | Tiempo |
|---------------------|--------|
| Ingesta API EcoWitt + cobertura | 0.03 s |
| Parseo y QC -> obs_flat (Little_R) | 0.20 s |
| Descarga GFS 0.25 (AWS) | 5.43 s |
| WPS (geogrid+ungrib+metgrid) | 2.4 min |
| Propagacion met_em al run dir | 0.06 s |
| Pipeline WRF completo (preflight+real+nudged+control+validacion) | 12.1 min |

| Etapa (pipeline WRF) | Tiempo |
|----------------------|--------|
| Little_R -> OBS_DOMAIN101 | 0.22 s |
| Preflight (validacion obs/namelist) | 0.05 s |
| real.exe | 1.63 s |
| wrf.exe nudged (24 h) | 11.9 min |
| Validacion multi-temporal + informe de evolucion | 12.18 s |

**Tiempo total end-to-end:** 14.6 min.

## Resultados: Nudged vs Control

RMSE/Bias de la corrida nudgada (N) y de control (C) por tiempo de validación. dRMSE = RMSE(C) - RMSE(N) (positivo ⇒ mejora con nudging; negativo ⇒ degrada). 00Z: N≡C por construcción.

### T2 (K)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 7 | 2.56 | 2.56 | +0.00 | +0.64 | +0.64 | -0.192 | -0.192 |
| 06Z | 7 | 3.31 | 4.18 | +0.87 | +1.11 | +2.02 | -0.213 | -0.502 |
| 12Z | 7 | 7.13 | 7.55 | +0.43 | -2.52 | -1.62 | -0.287 | -0.537 |
| 18Z | 7 | 3.00 | 3.13 | +0.14 | -1.47 | -1.65 | +0.854 | +0.839 |
| 24Z | 6 | 2.69 | 2.57 | -0.12 | -2.21 | -1.90 | +0.950 | +0.934 |


### PSFC (hPa)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 8 | 42.47 | 42.47 | +0.00 | -33.09 | -33.09 | +0.859 | +0.859 |
| 06Z | 8 | 43.01 | 43.10 | +0.09 | -33.66 | -33.82 | +0.864 | +0.864 |
| 12Z | 8 | 44.02 | 44.01 | -0.01 | -34.29 | -34.38 | +0.849 | +0.848 |
| 18Z | 8 | 43.11 | 43.17 | +0.06 | -33.75 | -33.63 | +0.853 | +0.853 |
| 24Z | 7 | 29.64 | 29.85 | +0.21 | -24.96 | -25.22 | +0.941 | +0.941 |


### RH (%)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 7 | 22.25 | 22.25 | +0.00 | -19.06 | -19.06 | +0.837 | +0.837 |
| 06Z | 7 | 32.81 | 36.49 | +3.68 | -26.20 | -30.34 | +0.545 | +0.487 |
| 12Z | 7 | 22.32 | 24.37 | +2.05 | -10.25 | -11.22 | +0.825 | +0.774 |
| 18Z | 7 | 7.85 | 8.68 | +0.82 | -6.00 | -6.60 | +0.084 | +0.016 |
| 24Z | 6 | 2.13 | 2.27 | +0.14 | +0.54 | -0.66 | +0.712 | +0.633 |


### Wind (m/s)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 7 | 2.25 | 2.25 | +0.00 | +1.89 | +1.89 | +0.055 | +0.055 |
| 06Z | 7 | 2.75 | 3.21 | +0.46 | +2.14 | +2.37 | -0.499 | -0.536 |
| 12Z | 7 | 2.66 | 1.99 | -0.67 | +2.16 | +1.54 | +0.826 | +0.834 |
| 18Z | 7 | 6.57 | 7.18 | +0.61 | +5.40 | +5.62 | -0.031 | -0.081 |
| 24Z | 6 | 7.74 | 9.30 | +1.56 | +6.15 | +7.31 | -0.007 | -0.070 |


### Ajuste vs. Generalización (hold-out espacial)

Las estaciones con `rol='evaluacion'` en `config/estaciones.json` nunca se asimilan (quedan fuera de `OBS_DOMAIN101`); sus métricas miden si el nudging **generaliza** a lugares sin datos, no solo si reproduce lo que ya se le dio (estaciones 'asimiladas').

#### T2 (K)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 2 | 2.97 | 2.97 | 0.90 | 0.90 |
| 06Z | 5 | 2 | 3.79 | 4.68 | 1.57 | 2.52 |
| 12Z | 5 | 2 | 6.34 | 7.06 | 8.79 | 8.66 |
| 18Z | 5 | 2 | 2.01 | 2.25 | 4.62 | 4.66 |
| 24Z | 5 | 1 | 2.84 | 2.76 | 1.72 | 1.23 |


#### PSFC (hPa)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 3 | 29.52 | 29.52 | 57.95 | 57.95 |
| 06Z | 5 | 3 | 30.40 | 30.51 | 58.24 | 58.33 |
| 12Z | 5 | 3 | 30.90 | 30.86 | 59.79 | 59.81 |
| 18Z | 5 | 3 | 30.32 | 30.36 | 58.52 | 58.60 |
| 24Z | 5 | 2 | 30.30 | 30.50 | 27.92 | 28.17 |


#### RH (%)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 2 | 18.77 | 18.77 | 29.20 | 29.20 |
| 06Z | 5 | 2 | 26.27 | 29.98 | 45.19 | 49.13 |
| 12Z | 5 | 2 | 26.35 | 28.76 | 2.88 | 3.11 |
| 18Z | 5 | 2 | 5.45 | 6.41 | 11.89 | 12.68 |
| 24Z | 5 | 1 | 2.25 | 2.22 | 1.35 | 2.54 |


#### Wind (m/s)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 2 | 2.53 | 2.53 | 1.33 | 1.33 |
| 06Z | 5 | 2 | 2.71 | 3.34 | 2.86 | 2.88 |
| 12Z | 5 | 2 | 2.18 | 1.50 | 3.58 | 2.87 |
| 18Z | 5 | 2 | 6.79 | 7.42 | 5.98 | 6.53 |
| 24Z | 5 | 1 | 7.91 | 9.15 | 6.81 | 10.01 |


### Conclusiones del caso

Para la interpretación completa (series, gráficos y comparación con observaciones) ver `outputs/runs/2026-07-31_0000z/caso1_zonda/` (informe de evolución, tablas por horario y wrfouts).

---
*Informe generado automáticamente por `src/casos/run_casos.py`.*