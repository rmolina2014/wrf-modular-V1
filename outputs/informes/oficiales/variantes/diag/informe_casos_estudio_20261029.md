# Informe consolidado de casos de estudio — Fase 4

Generado el 2026-10-29 14:19 por `src/casos/run_casos.py`.

## Resumen de ejecución

| Caso | Fecha | Evento | Estado | Informe |
|------|-------|--------|--------|---------|
| Caso 1 - Viento Zonda | 2026-07-31 | viento_zonda | PENDIENTE | `outputs/informes/oficiales/variantes/diag/informe_caso1_zonda_20260731.md` |
| Caso 2 - Calor de verano (Año Nuevo) | 2026-01-01 | calor_verano | PENDIENTE | `outputs/informes/oficiales/variantes/diag/informe_caso2_calor_20260101.md` |
| Caso 3 - Ingreso de frente frio | 2026-05-16 | frente_frio | EJECUTADO | `outputs/informes/oficiales/variantes/diag/informe_caso3_frentefrio_20260516.md` |
| Caso 4 - San Juan 2026-09-24 | 2026-09-24 | caso_sanjuan_0924 | PENDIENTE | `outputs/informes/oficiales/variantes/diag/informe_caso4_sanjuan_0924_20260924.md` |

## Métricas por caso (RMSE y r del nudging vs control)

Se reporta el RMSE y el coeficiente de correlación (r) de T2 (K) y RH (%) en cada tiempo de validación. En los casos con protocolo temporal, 'NNZ' significa horizonte de pronóstico en horas desde t0 (01Z = +1 h, 24Z = +24 h).

### Caso 1 - Viento Zonda (2026-07-31)

_No ejecutado: _

### Caso 2 - Calor de verano (Año Nuevo) (2026-01-01)

_No ejecutado: _

### Caso 3 - Ingreso de frente frio (2026-05-16)

| Tiempo | RMSE T2 N | RMSE T2 C | r T2 N | r T2 C | RMSE RH N | RMSE RH C | r RH N | r RH C |
|--------|-----------|-----------|--------|--------|-----------|-----------|--------|--------|
| 01Z | 2.09 | 2.60 | +0.288 | +0.280 | 11.78 | 15.18 | +0.796 | +0.921 |
| 02Z | 2.07 | 2.69 | -0.161 | -0.154 | 14.91 | 18.33 | +0.777 | +0.918 |
| 03Z | 2.35 | 3.02 | -0.672 | -0.662 | 17.91 | 21.66 | +0.804 | +0.888 |
| 04Z | 2.55 | 2.97 | -0.730 | -0.716 | 19.52 | 22.61 | +0.845 | +0.898 |
| 05Z | 2.09 | 2.39 | -0.202 | -0.161 | 18.68 | 21.63 | +0.831 | +0.873 |
| 06Z | 1.63 | 1.76 | +0.276 | +0.314 | 17.70 | 20.26 | +0.858 | +0.912 |
| 07Z | 2.17 | 2.14 | +0.237 | +0.277 | 16.44 | 18.34 | +0.795 | +0.851 |
| 08Z | 2.82 | 2.76 | +0.061 | +0.104 | 15.30 | 17.20 | +0.713 | +0.756 |
| 09Z | 3.46 | 3.44 | -0.072 | -0.061 | 14.54 | 16.28 | +0.567 | +0.590 |
| 10Z | 3.55 | 3.49 | -0.100 | -0.070 | 12.51 | 14.06 | +0.456 | +0.493 |
| 11Z | 3.78 | 3.76 | -0.240 | -0.225 | 9.96 | 11.26 | +0.292 | +0.351 |
| 12Z | 3.06 | 3.08 | -0.730 | -0.728 | 13.00 | 13.94 | +0.185 | +0.223 |
| 13Z | 2.49 | 2.52 | -0.631 | -0.638 | 18.58 | 19.25 | -0.028 | +0.019 |
| 14Z | 2.70 | 2.71 | +0.090 | +0.082 | 19.11 | 19.60 | -0.119 | -0.044 |
| 15Z | 3.79 | 3.80 | +0.335 | +0.336 | 22.69 | 23.08 | -0.296 | -0.224 |
| 16Z | 4.64 | 4.67 | +0.526 | +0.521 | 26.13 | 26.49 | -0.123 | -0.103 |
| 17Z | 5.02 | 5.15 | +0.297 | +0.277 | 23.20 | 24.08 | -0.019 | -0.064 |
| 18Z | 5.04 | 5.10 | -0.003 | -0.012 | 19.47 | 20.08 | +0.169 | +0.142 |
| 19Z | 4.81 | 4.85 | -0.302 | -0.317 | 18.11 | 18.51 | +0.130 | +0.108 |
| 20Z | 4.50 | 4.55 | -0.286 | -0.289 | 17.08 | 17.50 | -0.023 | -0.039 |
| 21Z | 4.03 | 4.21 | -0.124 | -0.116 | 15.15 | 16.21 | -0.138 | -0.161 |
| 22Z | 2.94 | 2.97 | +0.019 | +0.025 | 9.48 | 9.60 | -0.409 | -0.400 |
| 23Z | 2.89 | 2.86 | +0.047 | +0.045 | 9.90 | 9.66 | -0.645 | -0.608 |
| 24Z | 2.79 | 2.82 | +0.077 | +0.080 | 9.29 | 9.42 | -0.730 | -0.758 |

### Caso 4 - San Juan 2026-09-24 (2026-09-24)

_No ejecutado: _

## Limitación del dominio y criterio de análisis

15 km, errores de terreno +201..+918 m. En todos los casos el análisis se apoya en la firma térmica (T2/RH); el viento se interpreta de forma cualitativa. Detalles en los informes por caso.

---
*Informe consolidado generado automáticamente.*