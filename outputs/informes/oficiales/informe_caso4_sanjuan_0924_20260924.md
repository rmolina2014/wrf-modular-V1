# Caso 4 - San Juan 2026-09-24

**Fecha del evento:** 2026-09-24 | **Ciclo:** 00Z -> 24Z | **Informe generado:** 2026-10-12 21:51

## Descripción del evento

Caso oficial San Juan 2026-09-24 (todas las estaciones operativas con datos)

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

El dominio de 15 km no resuelve la topografía profunda de la precordillera (errores de altura del modelo de entre +201 m y +918 m en las estaciones, con máximos en CARACOLES +918 m, PUNTA_NEGRA +420 m y CUESTA_Viento +378 m). Por eso el análisis de **Caso 4 - San Juan 2026-09-24** se restringe a la **firma térmica** (salto de T2 y caída de RH), y el viento se interpreta solo de forma cualitativa. Ver también `documentacion_proyecto/informe_avances_fases_proyecto.md`.

## Observaciones disponibles

- Registros válidos: **2201** en el día, **2201** en la ventana 00Z–24Z.
- Estaciones con datos en ventana: **8**

| Estación | Registros (00Z–24Z) |
|----------|--------------------|
| CUESTA_Viento | 289 |
| ECOHUMUS | 289 |
| INTA_SANMARTIN | 289 |
| PUNTA_NEGRA | 289 |
| ULLUM_EMBALSE | 289 |
| VALLE_FERTIL | 289 |
| CARACOLES | 278 |
| INTA_POCITO | 189 |

## Desempeno del flujo (end-to-end)

Tiempos por etapa medidos en la ejecucion (artefacto `evaluacion_flujo.json`); cubre desde la llamada a la API EcoWitt hasta el informe de validacion.

| Etapa (orquestador) | Tiempo |
|---------------------|--------|
| Ingesta API EcoWitt + cobertura | 0.03 s |
| Parseo y QC -> obs_flat (Little_R) | 0.19 s |
| Descarga GFS 0.25 (AWS) | 6.4 min |
| WPS (geogrid+ungrib+metgrid) | 2.5 min |
| Propagacion met_em al run dir | 0.02 s |
| Pipeline WRF completo (preflight+real+nudged+control+validacion) | 24.6 min |

| Etapa (pipeline WRF) | Tiempo |
|----------------------|--------|
| Little_R -> OBS_DOMAIN101 | 0.22 s |
| Preflight (validacion obs/namelist) | 0.05 s |
| real.exe | 1.59 s |
| wrf.exe nudged (24 h) | 12.3 min |
| wrf.exe control (24 h) | 12.0 min |
| Validacion multi-temporal + informe de evolucion | 12.09 s |

**Tiempo total end-to-end:** 33.4 min.

## Resultados: Nudged vs Control

RMSE/Bias de la corrida nudgada (N) y de control (C) por tiempo de validación. dRMSE = RMSE(C) - RMSE(N) (positivo ⇒ mejora con nudging; negativo ⇒ degrada). 00Z: N≡C por construcción.

### T2 (K)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 8 | 5.23 | 5.23 | +0.00 | -3.03 | -3.03 | -0.129 | -0.129 |
| 06Z | 8 | 5.65 | 6.03 | +0.38 | -1.07 | -0.39 | -0.774 | -0.858 |
| 12Z | 7 | 5.44 | 5.67 | +0.23 | -1.49 | -0.80 | +0.326 | +0.153 |
| 18Z | 8 | 4.09 | 4.57 | +0.48 | -2.63 | -3.39 | +0.685 | +0.618 |
| 24Z | 8 | 5.24 | 5.27 | +0.04 | -4.42 | -4.50 | +0.663 | +0.695 |


### PSFC (hPa)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 8 | 41.48 | 41.48 | +0.00 | -32.30 | -32.30 | +0.866 | +0.866 |
| 06Z | 8 | 42.05 | 42.08 | +0.02 | -32.78 | -32.87 | +0.861 | +0.861 |
| 12Z | 7 | 44.40 | 44.47 | +0.07 | -34.69 | -34.84 | +0.847 | +0.848 |
| 18Z | 8 | 43.26 | 43.14 | -0.13 | -34.75 | -34.36 | +0.854 | +0.854 |
| 24Z | 8 | 42.18 | 42.18 | +0.00 | -33.44 | -33.42 | +0.860 | +0.860 |


### RH (%)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 8 | 8.29 | 8.29 | +0.00 | -5.49 | -5.49 | +0.902 | +0.902 |
| 06Z | 8 | 14.64 | 18.97 | +4.32 | -12.41 | -16.43 | +0.899 | +0.807 |
| 12Z | 7 | 10.29 | 12.67 | +2.38 | -7.39 | -9.61 | +0.822 | +0.720 |
| 18Z | 8 | 3.78 | 4.46 | +0.68 | -3.03 | -3.64 | +0.823 | +0.758 |
| 24Z | 8 | 3.81 | 4.83 | +1.02 | -2.18 | -3.58 | +0.921 | +0.946 |


### Wind (m/s)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 8 | 1.55 | 1.55 | +0.00 | +0.63 | +0.63 | +0.736 | +0.736 |
| 06Z | 8 | 2.93 | 3.00 | +0.07 | +1.61 | +2.03 | +0.162 | +0.394 |
| 12Z | 7 | 4.44 | 5.67 | +1.24 | +2.20 | +3.09 | +0.011 | -0.125 |
| 18Z | 8 | 7.17 | 7.38 | +0.21 | +3.82 | +2.67 | +0.088 | +0.087 |
| 24Z | 8 | 7.32 | 8.17 | +0.85 | +5.73 | +6.61 | +0.396 | +0.426 |


### Ajuste vs. Generalización (hold-out espacial)

Las estaciones con `rol='evaluacion'` en `config/estaciones.json` nunca se asimilan (quedan fuera de `OBS_DOMAIN101`); sus métricas miden si el nudging **generaliza** a lugares sin datos, no solo si reproduce lo que ya se le dio (estaciones 'asimiladas').

#### T2 (K)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 3 | 3.30 | 3.30 | 7.40 | 7.40 |
| 06Z | 5 | 3 | 2.73 | 3.30 | 8.53 | 8.88 |
| 12Z | 4 | 3 | 4.11 | 4.66 | 6.82 | 6.78 |
| 18Z | 5 | 3 | 3.16 | 3.76 | 5.29 | 5.67 |
| 24Z | 5 | 3 | 3.87 | 3.87 | 6.94 | 7.02 |


#### PSFC (hPa)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 3 | 29.04 | 29.04 | 56.42 | 56.42 |
| 06Z | 5 | 3 | 29.47 | 29.50 | 57.17 | 57.19 |
| 12Z | 4 | 3 | 32.03 | 32.19 | 56.85 | 56.85 |
| 18Z | 5 | 3 | 30.70 | 30.54 | 58.48 | 58.37 |
| 24Z | 5 | 3 | 29.97 | 29.91 | 56.98 | 57.03 |


#### RH (%)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 3 | 9.30 | 9.30 | 6.25 | 6.25 |
| 06Z | 5 | 3 | 14.63 | 19.52 | 14.66 | 18.02 |
| 12Z | 4 | 3 | 10.50 | 13.49 | 10.01 | 11.49 |
| 18Z | 5 | 3 | 3.08 | 4.16 | 4.73 | 4.92 |
| 24Z | 5 | 3 | 4.08 | 5.39 | 3.32 | 3.71 |


#### Wind (m/s)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 3 | 1.70 | 1.70 | 1.26 | 1.26 |
| 06Z | 5 | 3 | 2.58 | 2.93 | 3.44 | 3.13 |
| 12Z | 4 | 3 | 3.98 | 5.83 | 4.98 | 5.45 |
| 18Z | 5 | 3 | 8.06 | 7.82 | 5.37 | 6.58 |
| 24Z | 5 | 3 | 8.17 | 9.13 | 5.64 | 6.26 |


### Conclusiones del caso

Para la interpretación completa (series, gráficos y comparación con observaciones) ver `outputs/runs/2026-09-24_0000z/sanjuan_0924/` (informe de evolución, tablas por horario y wrfouts).

---
*Informe generado automáticamente por `src/casos/run_casos.py`.*