# Informe consolidado de casos de estudio — Fase 4

Generado el 2026-11-04 14:26 por `src/casos/run_casos.py`.

## Resumen de ejecución

| Caso | Fecha | Evento | Estado | Informe |
|------|-------|--------|--------|---------|
| Caso 1 - Viento Zonda | 2026-07-31 | viento_zonda | PENDIENTE | `outputs/informes/oficiales/variantes/op15km/informe_caso1_zonda_20260731.md` |
| Caso 2 - Calor de verano (Año Nuevo) | 2026-01-01 | calor_verano | PENDIENTE | `outputs/informes/oficiales/variantes/op15km/informe_caso2_calor_20260101.md` |
| Caso 3 - Ingreso de frente frio | 2026-05-16 | frente_frio | PENDIENTE | `outputs/informes/oficiales/variantes/op15km/informe_caso3_frentefrio_20260516.md` |
| Caso 4 - San Juan 2026-09-24 | 2026-09-24 | caso_sanjuan_0924 | FALLIDO | `outputs/informes/oficiales/variantes/op15km/informe_caso4_sanjuan_0924_20260924.md` |

## Métricas por caso (RMSE y r del nudging vs control)

Se reporta el RMSE y el coeficiente de correlación (r) de T2 (K) y RH (%) en cada tiempo de validación. En los casos con protocolo temporal, 'NNZ' significa horizonte de pronóstico en horas desde t0 (01Z = +1 h, 24Z = +24 h).

### Caso 1 - Viento Zonda (2026-07-31)

_No ejecutado: _

### Caso 2 - Calor de verano (Año Nuevo) (2026-01-01)

_No ejecutado: _

### Caso 3 - Ingreso de frente frio (2026-05-16)

_No ejecutado: _

### Caso 4 - San Juan 2026-09-24 (2026-09-24)

_No ejecutado: pipeline rc=1 (ver /home/pgich/wrf-modular-V1/results/casos_estudio/pipeline_caso4_sanjuan_0924__op15km.log)_

## Limitación del dominio y criterio de análisis

15 km, errores de terreno +201..+918 m. En todos los casos el análisis se apoya en la firma térmica (T2/RH); el viento se interpreta de forma cualitativa. Detalles en los informes por caso.

---
*Informe consolidado generado automáticamente.*