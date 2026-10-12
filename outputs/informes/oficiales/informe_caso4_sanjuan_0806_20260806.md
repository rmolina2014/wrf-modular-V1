# Caso 4 - San Juan 2026-08-06

**Fecha del evento:** 2026-08-06 | **Ciclo:** 00Z -> 24Z | **Informe generado:** 2026-10-12 10:45

## Descripción del evento

Caso oficial San Juan 2026-08-06

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

El dominio de 15 km no resuelve la topografía profunda de la precordillera (errores de altura del modelo de entre +201 m y +918 m en las estaciones, con máximos en CARACOLES +918 m, PUNTA_NEGRA +420 m y CUESTA_Viento +378 m). Por eso el análisis de **Caso 4 - San Juan 2026-08-06** se restringe a la **firma térmica** (salto de T2 y caída de RH), y el viento se interpreta solo de forma cualitativa. Ver también `documentacion_proyecto/informe_avances_fases_proyecto.md`.

## Observaciones disponibles

- Registros válidos: **1234** en el día, **1234** en la ventana 00Z–24Z.
- Estaciones con datos en ventana: **6**

| Estación | Registros (00Z–24Z) |
|----------|--------------------|
| CARACOLES | 283 |
| VALLE_FERTIL | 283 |
| CUESTA_Viento | 282 |
| ECOHUMUS | 282 |
| PUNTA_NEGRA | 103 |
| INTA_POCITO | 1 |

## Desempeno del flujo (end-to-end)

Tiempos por etapa medidos en la ejecucion (artefacto `evaluacion_flujo.json`); cubre desde la llamada a la API EcoWitt hasta el informe de validacion.

| Etapa (orquestador) | Tiempo |
|---------------------|--------|
| Ingesta API EcoWitt + cobertura | 56.57 s |
| Parseo y QC -> obs_flat (Little_R) | 0.07 s |
| Descarga GFS 0.25 (AWS) | 0.00 s |
| WPS (geogrid+ungrib+metgrid) | 2.5 min |
| Propagacion met_em al run dir | 0.03 s |
| Pipeline WRF completo (preflight+real+nudged+control+validacion) | 23.4 min |

| Etapa (pipeline WRF) | Tiempo |
|----------------------|--------|
| Little_R -> OBS_DOMAIN101 | 0.17 s |
| real.exe | 1.79 s |
| wrf.exe nudged (24 h) | 11.9 min |
| wrf.exe control (24 h) | 11.2 min |
| Validacion multi-temporal + informe de evolucion | 12.02 s |

**Tiempo total end-to-end:** 26.9 min.

## Resultados: Nudged vs Control

RMSE/Bias de la corrida nudgada (N) y de control (C) por tiempo de validación. dRMSE = RMSE(C) - RMSE(N) (positivo ⇒ mejora con nudging; negativo ⇒ degrada). 00Z: N≡C por construcción.

### T2 (K)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 5 | 6.66 | 6.66 | +0.00 | -3.73 | -3.73 | -0.281 | -0.281 |
| 06Z | 5 | 6.26 | 6.36 | +0.10 | -4.97 | -4.53 | +0.018 | -0.323 |
| 12Z | 4 | 3.18 | 3.29 | +0.11 | -2.16 | -1.72 | +0.271 | +0.175 |
| 18Z | 4 | 3.95 | 5.12 | +1.17 | +3.22 | +4.41 | +0.747 | +0.658 |
| 24Z | 4 | 4.80 | 6.13 | +1.33 | +1.36 | +2.91 | -0.969 | -0.982 |


### PSFC (hPa)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 5 | 48.61 | 48.61 | +0.00 | -37.69 | -37.69 | +0.840 | +0.840 |
| 06Z | 5 | 51.26 | 51.42 | +0.16 | -41.13 | -41.21 | +0.834 | +0.832 |
| 12Z | 5 | 55.20 | 55.07 | -0.14 | -45.80 | -45.69 | +0.852 | +0.851 |
| 18Z | 5 | 52.67 | 52.94 | +0.27 | -42.38 | -42.86 | +0.854 | +0.856 |
| 24Z | 5 | 51.42 | 51.61 | +0.19 | -40.03 | -40.60 | +0.851 | +0.851 |


### RH (%)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 5 | 10.82 | 10.82 | +0.00 | -4.48 | -4.48 | +0.992 | +0.992 |
| 06Z | 5 | 23.63 | 31.21 | +7.59 | -1.84 | -2.35 | +0.603 | +0.307 |
| 12Z | 4 | 22.59 | 22.19 | -0.40 | -10.06 | -12.68 | -0.070 | +0.019 |
| 18Z | 4 | 20.84 | 24.21 | +3.37 | -17.40 | -20.24 | +0.774 | -0.025 |
| 24Z | 4 | 16.16 | 25.44 | +9.27 | -15.00 | -22.54 | +0.622 | +0.198 |


### Wind (m/s)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 5 | 1.41 | 1.41 | +0.00 | +0.61 | +0.61 | +0.800 | +0.800 |
| 06Z | 5 | 4.14 | 5.35 | +1.21 | +2.79 | +3.96 | +0.789 | +0.705 |
| 12Z | 4 | 6.41 | 8.18 | +1.77 | +1.90 | +2.68 | -0.439 | -0.457 |
| 18Z | 4 | 4.22 | 5.06 | +0.84 | +2.53 | +3.62 | -0.646 | -0.481 |
| 24Z | 4 | 1.80 | 3.06 | +1.26 | +1.52 | +2.94 | +0.934 | +0.967 |


### Ajuste vs. Generalización (hold-out espacial)

Las estaciones con `rol='evaluacion'` en `config/estaciones.json` nunca se asimilan (quedan fuera de `OBS_DOMAIN101`); sus métricas miden si el nudging **generaliza** a lugares sin datos, no solo si reproduce lo que ya se le dio (estaciones 'asimiladas').

#### T2 (K)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 4 | 1 | 5.26 | 5.26 | 10.54 | 10.54 |
| 06Z | 4 | 1 | 5.14 | 5.34 | 9.50 | 9.40 |
| 12Z | 3 | 1 | 3.47 | 3.57 | 2.08 | 2.23 |
| 18Z | 3 | 1 | 4.54 | 5.91 | 0.68 | 0.04 |
| 24Z | 3 | 1 | 4.85 | 6.66 | 4.65 | 4.14 |


#### PSFC (hPa)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 4 | 1 | 30.76 | 30.76 | 89.62 | 89.62 |
| 06Z | 4 | 1 | 33.08 | 33.16 | 93.60 | 93.92 |
| 12Z | 3 | 2 | 30.76 | 30.42 | 78.74 | 78.70 |
| 18Z | 3 | 2 | 28.53 | 29.04 | 75.60 | 75.77 |
| 24Z | 3 | 2 | 27.00 | 27.26 | 74.28 | 74.46 |


#### RH (%)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 4 | 1 | 12.09 | 12.09 | 1.05 | 1.05 |
| 06Z | 4 | 1 | 26.38 | 34.87 | 2.58 | 2.88 |
| 12Z | 3 | 1 | 12.64 | 12.36 | 39.53 | 38.88 |
| 18Z | 3 | 1 | 19.16 | 23.47 | 25.21 | 26.30 |
| 24Z | 3 | 1 | 17.80 | 28.38 | 9.70 | 13.13 |


#### Wind (m/s)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 4 | 1 | 1.50 | 1.50 | 0.99 | 0.99 |
| 06Z | 4 | 1 | 2.53 | 3.41 | 7.75 | 9.81 |
| 12Z | 3 | 1 | 7.40 | 9.45 | 0.47 | 0.44 |
| 18Z | 3 | 1 | 4.26 | 5.31 | 4.10 | 4.20 |
| 24Z | 3 | 1 | 1.73 | 3.41 | 2.00 | 1.62 |


### Conclusiones del caso

Para la interpretación completa (series, gráficos y comparación con observaciones) ver `outputs/runs/2026-08-06_0000z/sanjuan_0806/` (informe de evolución, tablas por horario y wrfouts).

---
*Informe generado automáticamente por `src/casos/run_casos.py`.*