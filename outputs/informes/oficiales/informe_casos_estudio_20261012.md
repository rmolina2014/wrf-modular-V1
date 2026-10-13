# Informe consolidado de casos de estudio — Fase 4

Generado el 2026-10-12 21:51 por `src/casos/run_casos.py`.

## Resumen de ejecución

| Caso | Fecha | Evento | Estado | Informe |
|------|-------|--------|--------|---------|
| Caso 1 - Viento Zonda | 2026-07-31 | viento_zonda | EJECUTADO | `outputs/informes/oficiales/informe_caso1_zonda_20260731.md` |
| Caso 2 - Calor de verano (Año Nuevo) | 2026-01-01 | calor_verano | EJECUTADO | `outputs/informes/oficiales/informe_caso2_calor_20260101.md` |
| Caso 3 - Ingreso de frente frio | 2026-05-16 | frente_frio | EJECUTADO | `outputs/informes/oficiales/informe_caso3_frentefrio_20260516.md` |
| Caso 4 - San Juan 2026-09-24 | 2026-09-24 | caso_sanjuan_0924 | EJECUTADO | `outputs/informes/oficiales/informe_caso4_sanjuan_0924_20260924.md` |

## Métricas por caso (RMSE y r del nudging vs control)

Se reporta el RMSE y el coeficiente de correlación (r) de T2 (K) y RH (%) en la ventana de mayor divergencia (06Z, 12Z y 18Z).

### Caso 1 - Viento Zonda (2026-07-31)

| Tiempo | RMSE T2 N | RMSE T2 C | r T2 N | r T2 C | RMSE RH N | RMSE RH C | r RH N | r RH C |
|--------|-----------|-----------|--------|--------|-----------|-----------|--------|--------|
| 00Z | 2.56 | 2.56 | -0.192 | -0.192 | 22.25 | 22.25 | +0.837 | +0.837 |
| 06Z | 3.31 | 4.18 | -0.213 | -0.502 | 32.81 | 36.49 | +0.545 | +0.487 |
| 12Z | 7.13 | 7.55 | -0.287 | -0.537 | 22.32 | 24.37 | +0.825 | +0.774 |
| 18Z | 3.00 | 3.13 | +0.854 | +0.839 | 7.85 | 8.68 | +0.084 | +0.016 |
| 24Z | 2.69 | 2.57 | +0.950 | +0.934 | 2.13 | 2.27 | +0.712 | +0.633 |

### Caso 2 - Calor de verano (Año Nuevo) (2026-01-01)

| Tiempo | RMSE T2 N | RMSE T2 C | r T2 N | r T2 C | RMSE RH N | RMSE RH C | r RH N | r RH C |
|--------|-----------|-----------|--------|--------|-----------|-----------|--------|--------|
| 00Z | 4.32 | 4.32 | +0.243 | +0.243 | 19.25 | 19.25 | +0.315 | +0.315 |
| 06Z | 3.19 | 3.35 | -0.324 | -0.307 | 18.83 | 24.84 | -0.177 | -0.371 |
| 12Z | 2.94 | 3.22 | +0.493 | +0.443 | 10.16 | 14.23 | -0.915 | -0.938 |
| 18Z | 3.11 | 3.04 | +0.812 | +0.811 | 3.33 | 5.87 | +0.789 | +0.700 |
| 24Z | 4.25 | 4.04 | +0.045 | +0.134 | 8.75 | 7.78 | -0.007 | +0.252 |

### Caso 3 - Ingreso de frente frio (2026-05-16)

| Tiempo | RMSE T2 N | RMSE T2 C | r T2 N | r T2 C | RMSE RH N | RMSE RH C | r RH N | r RH C |
|--------|-----------|-----------|--------|--------|-----------|-----------|--------|--------|
| 00Z | 2.61 | 2.61 | +0.136 | +0.136 | 12.12 | 12.12 | +0.965 | +0.965 |
| 06Z | 1.91 | 2.01 | +0.232 | +0.258 | 12.96 | 17.70 | +0.866 | +0.871 |
| 12Z | 3.65 | 3.61 | -0.600 | -0.602 | 12.44 | 14.47 | -0.208 | -0.262 |
| 18Z | 3.07 | 4.21 | -0.124 | -0.110 | 11.74 | 16.45 | +0.351 | +0.049 |
| 24Z | 2.81 | 2.70 | +0.160 | +0.113 | 8.93 | 8.44 | -0.572 | -0.561 |

### Caso 4 - San Juan 2026-09-24 (2026-09-24)

| Tiempo | RMSE T2 N | RMSE T2 C | r T2 N | r T2 C | RMSE RH N | RMSE RH C | r RH N | r RH C |
|--------|-----------|-----------|--------|--------|-----------|-----------|--------|--------|
| 00Z | 5.23 | 5.23 | -0.129 | -0.129 | 8.29 | 8.29 | +0.902 | +0.902 |
| 06Z | 5.65 | 6.03 | -0.774 | -0.858 | 14.64 | 18.97 | +0.899 | +0.807 |
| 12Z | 5.44 | 5.67 | +0.326 | +0.153 | 10.29 | 12.67 | +0.822 | +0.720 |
| 18Z | 4.09 | 4.57 | +0.685 | +0.618 | 3.78 | 4.46 | +0.823 | +0.758 |
| 24Z | 5.24 | 5.27 | +0.663 | +0.695 | 3.81 | 4.83 | +0.921 | +0.946 |

## Limitación del dominio y criterio de análisis

15 km, errores de terreno +201..+918 m. En todos los casos el análisis se apoya en la firma térmica (T2/RH); el viento se interpreta de forma cualitativa. Detalles en los informes por caso.

---
*Informe consolidado generado automáticamente.*