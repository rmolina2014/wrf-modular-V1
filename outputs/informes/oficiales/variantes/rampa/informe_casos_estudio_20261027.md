# Informe consolidado de casos de estudio — Fase 4

Generado el 2026-10-27 12:49 por `src/casos/run_casos.py`.

## Resumen de ejecución

| Caso | Fecha | Evento | Estado | Informe |
|------|-------|--------|--------|---------|
| Caso 1 - Viento Zonda | 2026-07-31 | viento_zonda | PENDIENTE | `outputs/informes/oficiales/variantes/rampa/informe_caso1_zonda_20260731.md` |
| Caso 2 - Calor de verano (Año Nuevo) | 2026-01-01 | calor_verano | PENDIENTE | `outputs/informes/oficiales/variantes/rampa/informe_caso2_calor_20260101.md` |
| Caso 3 - Ingreso de frente frio | 2026-05-16 | frente_frio | EJECUTADO | `outputs/informes/oficiales/variantes/rampa/informe_caso3_frentefrio_20260516.md` |
| Caso 4 - San Juan 2026-09-24 | 2026-09-24 | caso_sanjuan_0924 | PENDIENTE | `outputs/informes/oficiales/variantes/rampa/informe_caso4_sanjuan_0924_20260924.md` |

## Métricas por caso (RMSE y r del nudging vs control)

Se reporta el RMSE y el coeficiente de correlación (r) de T2 (K) y RH (%) en cada tiempo de validación. En los casos con protocolo temporal, 'NNZ' significa horizonte de pronóstico en horas desde t0 (01Z = +1 h, 24Z = +24 h).

### Caso 1 - Viento Zonda (2026-07-31)

_No ejecutado: _

### Caso 2 - Calor de verano (Año Nuevo) (2026-01-01)

_No ejecutado: _

### Caso 3 - Ingreso de frente frio (2026-05-16)

| Tiempo | RMSE T2 N | RMSE T2 C | r T2 N | r T2 C | RMSE RH N | RMSE RH C | r RH N | r RH C |
|--------|-----------|-----------|--------|--------|-----------|-----------|--------|--------|
| 01Z | 2.15 | 2.60 | +0.265 | +0.280 | 12.15 | 15.18 | +0.789 | +0.921 |
| 02Z | 2.10 | 2.69 | -0.182 | -0.154 | 14.96 | 18.33 | +0.789 | +0.918 |
| 03Z | 2.39 | 3.02 | -0.666 | -0.662 | 18.07 | 21.66 | +0.815 | +0.888 |
| 04Z | 2.59 | 2.97 | -0.742 | -0.716 | 19.67 | 22.61 | +0.849 | +0.898 |
| 05Z | 2.10 | 2.39 | -0.202 | -0.161 | 18.75 | 21.63 | +0.834 | +0.873 |
| 06Z | 1.63 | 1.76 | +0.280 | +0.314 | 17.72 | 20.26 | +0.861 | +0.912 |
| 07Z | 2.18 | 2.14 | +0.231 | +0.277 | 16.39 | 18.34 | +0.793 | +0.851 |
| 08Z | 2.82 | 2.76 | +0.062 | +0.104 | 15.28 | 17.20 | +0.715 | +0.756 |
| 09Z | 3.47 | 3.44 | -0.072 | -0.061 | 14.52 | 16.28 | +0.569 | +0.590 |
| 10Z | 3.54 | 3.49 | -0.093 | -0.070 | 12.51 | 14.06 | +0.464 | +0.493 |
| 11Z | 3.78 | 3.76 | -0.238 | -0.225 | 9.94 | 11.26 | +0.300 | +0.351 |
| 12Z | 3.06 | 3.08 | -0.729 | -0.728 | 13.02 | 13.94 | +0.184 | +0.223 |
| 13Z | 2.50 | 2.52 | -0.631 | -0.638 | 18.57 | 19.25 | -0.029 | +0.019 |
| 14Z | 2.70 | 2.71 | +0.090 | +0.082 | 19.09 | 19.60 | -0.111 | -0.044 |
| 15Z | 3.79 | 3.80 | +0.340 | +0.336 | 22.71 | 23.08 | -0.282 | -0.224 |
| 16Z | 4.65 | 4.67 | +0.530 | +0.521 | 26.15 | 26.49 | -0.110 | -0.103 |
| 17Z | 5.01 | 5.15 | +0.301 | +0.277 | 23.19 | 24.08 | -0.010 | -0.064 |
| 18Z | 5.05 | 5.10 | +0.000 | -0.012 | 19.50 | 20.08 | +0.173 | +0.142 |
| 19Z | 4.82 | 4.85 | -0.305 | -0.317 | 18.12 | 18.51 | +0.125 | +0.108 |
| 20Z | 4.49 | 4.55 | -0.285 | -0.289 | 17.06 | 17.50 | -0.015 | -0.039 |
| 21Z | 4.04 | 4.21 | -0.124 | -0.116 | 15.20 | 16.21 | -0.143 | -0.161 |
| 22Z | 2.87 | 2.97 | +0.031 | +0.025 | 8.87 | 9.60 | -0.274 | -0.400 |
| 23Z | 2.87 | 2.86 | +0.055 | +0.045 | 9.71 | 9.66 | -0.648 | -0.608 |
| 24Z | 2.79 | 2.82 | +0.082 | +0.080 | 9.31 | 9.42 | -0.741 | -0.758 |

### Caso 4 - San Juan 2026-09-24 (2026-09-24)

_No ejecutado: _

## Limitación del dominio y criterio de análisis

15 km, errores de terreno +201..+918 m. En todos los casos el análisis se apoya en la firma térmica (T2/RH); el viento se interpreta de forma cualitativa. Detalles en los informes por caso.

---
*Informe consolidado generado automáticamente.*