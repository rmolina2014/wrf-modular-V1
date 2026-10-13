# Caso 3 - Ingreso de frente frio

**Fecha del evento:** 2026-05-16 | **Ciclo:** 00Z -> 24Z | **Informe generado:** 2026-10-12 21:18

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

- Registros válidos: **293** en el día, **293** en la ventana 00Z–24Z.
- Estaciones con datos en ventana: **6**

| Estación | Registros (00Z–24Z) |
|----------|--------------------|
| CARACOLES | 49 |
| CUESTA_Viento | 49 |
| ECOHUMUS | 49 |
| INTA_POCITO | 49 |
| PUNTA_NEGRA | 49 |
| VALLE_FERTIL | 48 |

## Desempeno del flujo (end-to-end)

Tiempos por etapa medidos en la ejecucion (artefacto `evaluacion_flujo.json`); cubre desde la llamada a la API EcoWitt hasta el informe de validacion.

| Etapa (orquestador) | Tiempo |
|---------------------|--------|
| Ingesta API EcoWitt + cobertura | 0.02 s |
| Parseo y QC -> obs_flat (Little_R) | 0.04 s |
| Descarga GFS 0.25 (AWS) | 5.35 s |
| WPS (geogrid+ungrib+metgrid) | 2.6 min |
| Propagacion met_em al run dir | 0.04 s |
| Pipeline WRF completo (preflight+real+nudged+control+validacion) | 12.3 min |

| Etapa (pipeline WRF) | Tiempo |
|----------------------|--------|
| Little_R -> OBS_DOMAIN101 | 0.05 s |
| Preflight (validacion obs/namelist) | 0.01 s |
| real.exe | 1.59 s |
| wrf.exe nudged (24 h) | 12.0 min |
| Validacion multi-temporal + informe de evolucion | 11.39 s |

**Tiempo total end-to-end:** 15.0 min.

## Resultados: Nudged vs Control

RMSE/Bias de la corrida nudgada (N) y de control (C) por tiempo de validación. dRMSE = RMSE(C) - RMSE(N) (positivo ⇒ mejora con nudging; negativo ⇒ degrada). 00Z: N≡C por construcción.

### T2 (K)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 6 | 2.61 | 2.61 | +0.00 | -0.67 | -0.67 | +0.136 | +0.136 |
| 06Z | 6 | 1.91 | 2.01 | +0.11 | -0.89 | -0.23 | +0.232 | +0.258 |
| 12Z | 6 | 3.65 | 3.61 | -0.04 | -1.81 | -1.29 | -0.600 | -0.602 |
| 18Z | 6 | 3.07 | 4.21 | +1.14 | +1.42 | +2.48 | -0.124 | -0.110 |
| 24Z | 6 | 2.81 | 2.70 | -0.11 | -0.84 | -0.05 | +0.160 | +0.113 |


### PSFC (hPa)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 6 | 47.16 | 47.16 | +0.00 | -36.44 | -36.44 | +0.861 | +0.861 |
| 06Z | 6 | 48.38 | 48.44 | +0.05 | -37.74 | -37.86 | +0.859 | +0.859 |
| 12Z | 6 | 49.73 | 49.78 | +0.05 | -39.51 | -39.60 | +0.862 | +0.862 |
| 18Z | 6 | 50.64 | 50.84 | +0.20 | -40.14 | -40.53 | +0.862 | +0.863 |
| 24Z | 6 | 50.48 | 50.78 | +0.30 | -39.59 | -40.07 | +0.863 | +0.863 |


### RH (%)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 6 | 12.12 | 12.12 | +0.00 | -11.73 | -11.73 | +0.965 | +0.965 |
| 06Z | 6 | 12.96 | 17.70 | +4.73 | -12.20 | -17.19 | +0.866 | +0.871 |
| 12Z | 6 | 12.44 | 14.47 | +2.03 | +0.44 | -4.57 | -0.208 | -0.262 |
| 18Z | 6 | 11.74 | 16.45 | +4.71 | -5.04 | -8.40 | +0.351 | +0.049 |
| 24Z | 6 | 8.93 | 8.44 | -0.49 | +4.29 | +3.74 | -0.572 | -0.561 |


### Wind (m/s)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 00Z | 6 | 3.05 | 3.05 | +0.00 | +0.94 | +0.94 | -0.271 | -0.271 |
| 06Z | 6 | 0.91 | 0.98 | +0.07 | +0.49 | +0.85 | +0.915 | +0.966 |
| 12Z | 6 | 1.16 | 1.06 | -0.10 | -0.31 | -0.19 | +0.783 | +0.836 |
| 18Z | 6 | 2.83 | 3.98 | +1.15 | +2.36 | +3.82 | +0.747 | +0.879 |
| 24Z | 6 | 2.29 | 3.45 | +1.16 | +1.97 | +3.16 | +0.725 | +0.682 |


### Ajuste vs. Generalización (hold-out espacial)

Las estaciones con `rol='evaluacion'` en `config/estaciones.json` nunca se asimilan (quedan fuera de `OBS_DOMAIN101`); sus métricas miden si el nudging **generaliza** a lugares sin datos, no solo si reproduce lo que ya se le dio (estaciones 'asimiladas').

#### T2 (K)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 1 | 1.86 | 1.86 | 4.87 | 4.87 |
| 06Z | 5 | 1 | 1.83 | 1.99 | 2.28 | 2.12 |
| 12Z | 5 | 1 | 2.23 | 2.26 | 7.41 | 7.24 |
| 18Z | 5 | 1 | 3.10 | 4.44 | 2.92 | 2.80 |
| 24Z | 5 | 1 | 1.33 | 1.60 | 6.20 | 5.55 |


#### PSFC (hPa)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 1 | 29.95 | 29.95 | 94.12 | 94.12 |
| 06Z | 5 | 1 | 30.95 | 31.02 | 96.21 | 96.27 |
| 12Z | 5 | 1 | 32.40 | 32.47 | 97.93 | 97.96 |
| 18Z | 5 | 1 | 32.90 | 33.24 | 99.86 | 99.93 |
| 24Z | 5 | 1 | 32.70 | 33.08 | 99.73 | 100.00 |


#### RH (%)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 1 | 12.83 | 12.83 | 7.64 | 7.64 |
| 06Z | 5 | 1 | 11.38 | 17.24 | 18.98 | 19.84 |
| 12Z | 5 | 1 | 10.58 | 13.94 | 19.21 | 16.88 |
| 18Z | 5 | 1 | 12.67 | 17.76 | 5.01 | 6.78 |
| 24Z | 5 | 1 | 4.86 | 4.64 | 18.98 | 17.88 |


#### Wind (m/s)

| Tiempo | N_asim | N_eval | RMSE N (asim) | RMSE C (asim) | RMSE N (eval) | RMSE C (eval) |
|--------|--------|--------|---------------|---------------|---------------|---------------|
| 00Z | 5 | 1 | 3.34 | 3.34 | 0.31 | 0.31 |
| 06Z | 5 | 1 | 0.84 | 0.85 | 1.21 | 1.45 |
| 12Z | 5 | 1 | 1.24 | 1.11 | 0.62 | 0.78 |
| 18Z | 5 | 1 | 2.26 | 3.60 | 4.74 | 5.47 |
| 24Z | 5 | 1 | 2.25 | 3.56 | 2.44 | 2.82 |


### Conclusiones del caso

Para la interpretación completa (series, gráficos y comparación con observaciones) ver `outputs/runs/2026-05-16_0000z/caso3_frentefrio/` (informe de evolución, tablas por horario y wrfouts).

---
*Informe generado automáticamente por `src/casos/run_casos.py`.*