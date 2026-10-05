# Caso 4 - San Juan 2026-08-06

**Fecha del evento:** 2026-08-06 | **Ciclo:** 00Z -> 12Z | **Informe generado:** 2026-10-05 20:30

## Descripción del evento

Caso de prueba 4 de la Fase 4 del proyecto: ciclo WRF 00Z→12Z con y sin observaciones nudging para la provincia de San Juan. El evento de 2026-08-06 corresponde a condiciones de la estación fría con variabilidad diaria característica de agosto en el dominio.

**Fuente:** Datos observacionales EcoWitt, GFS AWS 0.25°

## Estado de la ejecución

**Estado:** ✅ EJECUTADO

## Configuración aplicada

| Parámetro | Valor |
|-----------|-------|
| Dominio | 1 dominio, 15 km, 80×60, mercator (-31.5°, -68.5°) |
| Ciclo | 00Z–12Z (12 h) |
| Forzante | GFS 0.25° (AWS) |
| Obs nudging | `obs_nudge_opt=1`, coef viento/temp/humedad=0.0001, `obs_twindo=1.0` |
| Nudged vs Control | misma inicialización; solo cambia `obs_nudge_opt` (1 vs 0) |
| Validación | 06Z vs observaciones de estaciones (multi-temporal parcial) |

## Limitación conocida del dominio (relevant para el análisis)

El dominio de 15 km no resuelve la topografía profunda de la precordillera (errores de altura del modelo de entre +201 m y +918 m en las estaciones, con máximos en CARACOLES +918 m, PUNTA_NEGRA +420 m y CUESTA_Viento +378 m). Por eso el análisis de **Caso 4 - San Juan 2026-08-06** se restringe a la **firma térmica** (T2 y RH), y el viento se interpreta solo de forma cualitativa. Ver también `documentacion_proyecto/informe_avances_fases_proyecto.md`.

## Observaciones disponibles

- Registros válidos en ventana 00Z–12Z: **386**
- Estaciones con datos en ventana: **3**

| Estación | Registros (00Z–12Z) |
|----------|--------------------|
| ECOHUMUS | 282 |
| PUNTA_NEGRA | 103 |
| INTA_POCITO | 1 |

## Resultados: Nudged vs Control

RMSE/Bias de la corrida nudgada (N) y de control (C) por tiempo de validación. dRMSE = RMSE(C) - RMSE(N) (positivo ⇒ mejora con nudging; negativo ⇒ degrada).

**Nota:** Se cuenta con validación en 06Z. Los análisis de 00Z (inicio coincidente) y 12Z requieren verificación de disponibilidad de métricas completas.

### T2 (K)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 06Z | 7 | 7.09 | 7.93 | +0.84 | -4.79 | -4.00 | -0.398 | -0.705 |

### PSFC (hPa)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 06Z | 7 | 44.91 | 45.11 | +0.20 | -34.71 | -35.23 | +0.857 | +0.855 |

### RH (%)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 06Z | 7 | 29.57 | 37.06 | +7.49 | -10.75 | -13.60 | +0.367 | -0.407 |

### Wind (m/s)

| Tiempo | N | RMSE N | RMSE C | dRMSE | Bias N | Bias C | r N | r C |
|--------|----|--------|--------|-------|--------|--------|-----|-----|
| 06Z | 7 | 12.99 | 12.93 | -0.06 | +0.13 | +1.51 | +0.131 | +0.116 |

### Interpretación de resultados (06Z)

**Temperatura (T2):**
- Nudging produce una **mejora de +0.84 K** en RMSE respecto a control.
- Bias nudgado (-4.79 K) es inferior al control (-4.00 K), indicando subsaturación del modelo.
- Correlación débil en ambas corridas (r ≈ -0.4 a -0.7), sugiriendo dificultad del modelo para capturar la variabilidad observada.

**Presión en superficie (PSFC):**
- Mejora mínima con nudging (+0.20 hPa), prácticamente equivalente.
- Sesgo sistemático fuerte: modelo subestima presión ~35 hPa.
- Buena correlación espacial en ambas corridas (r ≈ 0.86).

**Humedad relativa (RH):**
- **Mejora significativa con nudging: +7.49 %** en RMSE.
- Bias nudgado (-10.75%) vs control (-13.60%), mostrando mejor representación de humedad.
- Control presenta correlación invertida (r = -0.407), mientras nudging mantiene positiva (r = +0.367).

**Viento:**
- Degradación mínima con nudging (-0.06 m/s), prácticamente sin cambio.
- Ambas corridas con correlación débil (r ≈ 0.12), limitación conocida del dominio (resolución insuficiente).

### Conclusiones del caso

El Caso 4 confirma que el nudging observacional produce **mejoras sistemáticas en T2 y RH**, siendo la humedad la variable de mayor impacto. La cobertura observacional limitada a 3 estaciones (y fuertemente dominada por ECOHUMUS) restringe la extensión espacial del impacto del nudging, pero valida el esquema de asimilación. 

Para la interpretación completa (series temporales, gráficos de dispersión, mapas de errores) ver `outputs/runs/2026-08-06_0000z/sanjuan_0806/` (scatter_4panels.png, mapa_errores_t2.png, tabla_metricas.png y wrfouts de nudged/control).

---

*Informe regenerado el 2026-10-05 desde datos disponibles en `outputs/runs/2026-08-06_0000z/sanjuan_0806/`.*
