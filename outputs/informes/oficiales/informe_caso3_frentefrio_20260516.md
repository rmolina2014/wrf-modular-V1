# Caso 3 - Ingreso de frente frio

**Fecha del evento:** 2026-05-16 | **Ciclo:** 00Z -> 24Z | **Informe generado:** 2026-10-12 00:02

## Descripción del evento

Evento de ingreso de frente frío sobre San Juan

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

El dominio de 15 km no resuelve la topografía profunda de la precordillera (errores de altura del modelo de entre +201 m y +918 m en las estaciones, con máximos en CARACOLES +918 m, PUNTA_NEGRA +420 m y CUESTA_Viento +378 m). Por eso el análisis de **Caso 3 - Ingreso de frente frio** se restringe a la **firma térmica** (salto de T2 y caída de RH), y el viento se interpreta solo de forma cualitativa. Ver también `documentacion_proyecto/informe_avances_fases_proyecto.md`.

## Observaciones disponibles

- Registros válidos: **287** en el día, **287** en la ventana 00Z–24Z.
- Estaciones con datos en ventana: **6**

| Estación | Registros (00Z–24Z) |
|----------|--------------------|
| CARACOLES | 48 |
| CUESTA_Viento | 48 |
| ECOHUMUS | 48 |
| INTA_POCITO | 48 |
| PUNTA_NEGRA | 48 |
| VALLE_FERTIL | 47 |

## Desempeno del flujo (end-to-end)

Tiempos por etapa medidos en la ejecucion (artefacto `evaluacion_flujo.json`); cubre desde la llamada a la API EcoWitt hasta el informe de validacion.

| Etapa (orquestador) | Tiempo |
|---------------------|--------|
| Ingesta API EcoWitt + cobertura | 55.16 s |
| Parseo y QC -> obs_flat (Little_R) | 0.02 s |
| Descarga GFS 0.25 (AWS) | 9.6 min |
| WPS (geogrid+ungrib+metgrid) | 2.2 min |
| Propagacion met_em al run dir | 0.02 s |
| Pipeline WRF completo (preflight+real+nudged+control+validacion) | 20.7 min |

| Etapa (pipeline WRF) | Tiempo |
|----------------------|--------|
| Little_R -> OBS_DOMAIN101 | 0.03 s |
| Preflight (validacion obs/namelist) | 0.00 s |
| real.exe | 1.34 s |
| wrf.exe nudged (24 h) | 10.3 min |
| wrf.exe control (24 h) | 10.2 min |
| Validacion multi-temporal + informe de evolucion | 9.60 s |

**Tiempo total end-to-end:** 33.4 min.

## Resultados: Nudged vs Control

RMSE/Bias de la corrida nudgada (N) y de control (C) por tiempo de validación. dRMSE = RMSE(C) - RMSE(N) (positivo ⇒ mejora con nudging; negativo ⇒ degrada). 00Z: N≡C por construcción.

### T2 (K)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 6 | 3.45 | 3.45 | +0.00 | +1.77 | +1.77 | -0.727 | -0.727 |
| 06Z | 6 | 2.79 | 2.90 | +0.11 | -0.65 | +0.03 | +0.391 | +0.331 |
| 12Z | 6 | 2.54 | 2.77 | +0.23 | -0.84 | -0.11 | +0.049 | -0.064 |
| 18Z | 6 | 3.57 | 4.99 | +1.42 | +2.25 | +3.54 | -0.229 | -0.244 |
| 24Z | 6 | 2.90 | 3.06 | +0.16 | -0.14 | +0.89 | -0.242 | -0.303 |


### PSFC (hPa)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 6 | 48.14 | 48.14 | +0.00 | -37.79 | -37.79 | +0.862 | +0.862 |
| 06Z | 6 | 48.85 | 48.92 | +0.07 | -38.39 | -38.52 | +0.860 | +0.860 |
| 12Z | 6 | 51.93 | 52.01 | +0.08 | -42.15 | -42.28 | +0.857 | +0.857 |
| 18Z | 6 | 51.94 | 52.22 | +0.28 | -41.66 | -42.17 | +0.861 | +0.863 |
| 24Z | 6 | 50.74 | 51.13 | +0.39 | -39.87 | -40.50 | +0.865 | +0.865 |


### RH (%)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 6 | 22.35 | 22.35 | +0.00 | -21.68 | -21.68 | +0.857 | +0.857 |
| 06Z | 6 | 14.33 | 19.45 | +5.12 | -13.21 | -18.74 | +0.823 | +0.843 |
| 12Z | 6 | 11.84 | 15.74 | +3.89 | -2.70 | -7.07 | -0.057 | -0.284 |
| 18Z | 6 | 13.98 | 17.83 | +3.85 | -8.15 | -10.40 | +0.047 | -0.169 |
| 24Z | 6 | 8.52 | 7.41 | -1.11 | +1.37 | +0.97 | -0.407 | -0.149 |


### Wind (m/s)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 6 | 2.90 | 2.90 | +0.00 | +1.32 | +1.32 | -0.334 | -0.334 |
| 06Z | 6 | 0.98 | 1.08 | +0.10 | +0.60 | +0.91 | +0.934 | +0.967 |
| 12Z | 6 | 1.68 | 1.37 | -0.30 | -0.84 | -0.71 | +0.774 | +0.859 |
| 18Z | 6 | 3.61 | 4.97 | +1.36 | +3.17 | +4.76 | +0.664 | +0.774 |
| 24Z | 6 | 2.59 | 3.83 | +1.24 | +2.34 | +3.59 | +0.593 | +0.647 |


### Ajuste vs. Generalización (hold-out espacial)

Las estaciones con `rol='evaluacion'` en `config/estaciones.json` nunca se asimilan (quedan fuera de `OBS_DOMAIN101`); sus métricas miden si el nudging **generaliza** a lugares sin datos, no solo si reproduce lo que ya se le dio (estaciones 'asimiladas').

#### T2 (K)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 1 | 3.67 | 3.67 | 1.98 | 1.98 |
| 06Z | 5 | 1 | 2.55 | 2.74 | 3.75 | 3.62 |
| 12Z | 5 | 1 | 1.87 | 2.35 | 4.63 | 4.31 |
| 18Z | 5 | 1 | 3.81 | 5.42 | 1.98 | 1.60 |
| 24Z | 5 | 1 | 2.12 | 2.68 | 5.31 | 4.49 |


#### PSFC (hPa)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 1 | 31.05 | 31.05 | 95.32 | 95.32 |
| 06Z | 5 | 1 | 31.51 | 31.61 | 96.71 | 96.77 |
| 12Z | 5 | 1 | 34.55 | 34.66 | 101.06 | 101.09 |
| 18Z | 5 | 1 | 34.29 | 34.73 | 101.52 | 101.63 |
| 24Z | 5 | 1 | 33.01 | 33.48 | 100.00 | 100.40 |


#### RH (%)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 1 | 23.08 | 23.08 | 18.31 | 18.31 |
| 06Z | 5 | 1 | 14.03 | 19.94 | 15.76 | 16.84 |
| 12Z | 5 | 1 | 11.71 | 16.25 | 12.49 | 12.88 |
| 18Z | 5 | 1 | 15.24 | 19.40 | 3.37 | 5.11 |
| 24Z | 5 | 1 | 8.18 | 7.09 | 10.06 | 8.88 |


#### Wind (m/s)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 1 | 3.15 | 3.15 | 1.01 | 1.01 |
| 06Z | 5 | 1 | 0.93 | 0.98 | 1.20 | 1.46 |
| 12Z | 5 | 1 | 1.78 | 1.42 | 1.00 | 1.13 |
| 18Z | 5 | 1 | 3.37 | 4.89 | 4.64 | 5.36 |
| 24Z | 5 | 1 | 2.63 | 3.99 | 2.41 | 2.89 |


### Conclusiones del caso

Para la interpretación completa (series, gráficos y comparación con observaciones) ver `outputs/runs/2026-05-16_0000z/caso3_frentefrio/` (informe de evolución, tablas por horario y wrfouts).

---
*Informe generado automáticamente por `src/casos/run_casos.py`.*