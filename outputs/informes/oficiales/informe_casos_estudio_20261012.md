# Informe consolidado de casos de estudio — Fase 4

Generado el 2026-10-12 10:45 por `src/casos/run_casos.py`.

## Resumen de ejecución

| Caso | Fecha | Evento | Estado | Informe |
|------|-------|--------|--------|---------|
| Caso 1 - Viento Zonda | 2026-07-31 | viento_zonda | EJECUTADO | `outputs/informes/oficiales/informe_caso1_zonda_20260731.md` |
| Caso 2 - Calor de verano (Año Nuevo) | 2026-01-01 | calor_verano | EJECUTADO | `outputs/informes/oficiales/informe_caso2_calor_20260101.md` |
| Caso 3 - Ingreso de frente frio | 2026-05-16 | frente_frio | EJECUTADO | `outputs/informes/oficiales/informe_caso3_frentefrio_20260516.md` |
| Caso 4 - San Juan 2026-08-06 | 2026-08-06 | caso_sanjuan_0806 | EJECUTADO | `outputs/informes/oficiales/informe_caso4_sanjuan_0806_20260806.md` |

## Métricas por caso (RMSE y r del nudging vs control)

Se reporta el RMSE y el coeficiente de correlación (r) de T2 (K) y RH (%) en la ventana de mayor divergencia (06Z, 12Z y 18Z).

### Caso 1 - Viento Zonda (2026-07-31)

| Tiempo | RMSE T2 N | RMSE T2 C | r T2 N | r T2 C | RMSE RH N | RMSE RH C | r RH N | r RH C |
|--------|-----------|-----------|--------|--------|-----------|-----------|--------|--------|
| 00Z | 4.43 | 4.43 | -0.610 | -0.610 | 27.96 | 27.96 | +0.818 | +0.818 |
| 06Z | 3.37 | 4.43 | -0.600 | -0.863 | 32.95 | 36.22 | +0.654 | +0.607 |
| 12Z | 10.55 | 10.52 | +0.768 | +0.791 | 23.15 | 23.51 | +0.737 | +0.751 |
| 18Z | 2.32 | 2.50 | +0.951 | +0.937 | 6.07 | 6.54 | +0.637 | +0.558 |
| 24Z | 2.72 | 3.54 | +0.584 | +0.427 | 5.43 | 6.40 | -0.355 | -0.491 |

### Caso 2 - Calor de verano (Año Nuevo) (2026-01-01)

| Tiempo | RMSE T2 N | RMSE T2 C | r T2 N | r T2 C | RMSE RH N | RMSE RH C | r RH N | r RH C |
|--------|-----------|-----------|--------|--------|-----------|-----------|--------|--------|
| 00Z | 3.66 | 3.66 | +0.350 | +0.350 | 19.77 | 19.77 | +0.443 | +0.443 |
| 06Z | 3.28 | 4.13 | -0.334 | -0.377 | 20.02 | 28.37 | -0.132 | -0.583 |
| 12Z | 5.10 | 5.46 | +0.830 | +0.853 | 6.17 | 6.85 | +0.477 | +0.311 |
| 18Z | 3.10 | 3.23 | +0.805 | +0.777 | 2.48 | 4.53 | +0.914 | +0.727 |
| 24Z | 4.32 | 4.73 | -0.178 | -0.038 | 9.83 | 14.12 | -0.035 | +0.300 |

### Caso 3 - Ingreso de frente frio (2026-05-16)

| Tiempo | RMSE T2 N | RMSE T2 C | r T2 N | r T2 C | RMSE RH N | RMSE RH C | r RH N | r RH C |
|--------|-----------|-----------|--------|--------|-----------|-----------|--------|--------|
| 00Z | 3.45 | 3.45 | -0.727 | -0.727 | 22.35 | 22.35 | +0.857 | +0.857 |
| 06Z | 2.79 | 2.90 | +0.391 | +0.331 | 14.33 | 19.45 | +0.823 | +0.843 |
| 12Z | 2.54 | 2.77 | +0.049 | -0.064 | 11.84 | 15.74 | -0.057 | -0.284 |
| 18Z | 3.57 | 4.99 | -0.229 | -0.244 | 13.98 | 17.83 | +0.047 | -0.169 |
| 24Z | 2.90 | 3.06 | -0.242 | -0.303 | 8.52 | 7.41 | -0.407 | -0.149 |

### Caso 4 - San Juan 2026-08-06 (2026-08-06)

| Tiempo | RMSE T2 N | RMSE T2 C | r T2 N | r T2 C | RMSE RH N | RMSE RH C | r RH N | r RH C |
|--------|-----------|-----------|--------|--------|-----------|-----------|--------|--------|
| 00Z | 6.66 | 6.66 | -0.281 | -0.281 | 10.82 | 10.82 | +0.992 | +0.992 |
| 06Z | 6.26 | 6.36 | +0.018 | -0.323 | 23.63 | 31.21 | +0.603 | +0.307 |
| 12Z | 3.18 | 3.29 | +0.271 | +0.175 | 22.59 | 22.19 | -0.070 | +0.019 |
| 18Z | 3.95 | 5.12 | +0.747 | +0.658 | 20.84 | 24.21 | +0.774 | -0.025 |
| 24Z | 4.80 | 6.13 | -0.969 | -0.982 | 16.16 | 25.44 | +0.622 | +0.198 |

## Limitación del dominio y criterio de análisis

15 km, errores de terreno +201..+918 m. En todos los casos el análisis se apoya en la firma térmica (T2/RH); el viento se interpreta de forma cualitativa. Detalles en los informes por caso.

---
*Informe consolidado generado automáticamente.*