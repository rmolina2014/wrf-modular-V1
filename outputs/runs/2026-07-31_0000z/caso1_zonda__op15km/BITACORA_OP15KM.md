
---

## CORRECCIONES AL REPORTE (2026-11-05 09:40 UTC)

**Error 1: Identificación de cu_physics**
- **Entrada anterior**: "cu_physics=6 (Grell-3D)"
- **CORRECCIÓN**: cu_physics=6 es **Tiedtke**, no Grell-3D

**Error 2: RMSE de velocidad del viento**
- **Entrada anterior**: "Wspd mostró ligera degradación (típico con BEP urbano)"
- **DATOS REALES**: 
  - Control promedio: 6.80 m/s
  - Nudging promedio: 6.69 m/s
  - ΔRMSE: +0.11 m/s (+1.7% de mejora)
- **CORRECCIÓN**: Nudging SÍ reduce el RMSE de wspd; no hubo degradación

**Error 3: Atribución a BEP**
- **ACLARACIÓN**: No se comparó BEP con/sin en esta corrida; no se pueden atribuir resultados específicos a BEP por separado

**Error 4: "Mejora durante asimilación"**
- **CORRECCIÓN**: Esta afirmación requiere métrica específica en el repo; se omite hasta verificación adicional
