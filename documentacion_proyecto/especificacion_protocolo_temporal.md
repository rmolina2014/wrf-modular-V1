# Especificación: protocolo de separación temporal (asimilación previa a t0 + pronóstico libre 24 h)

Repo base: `wrf-modular-V1`, commit `d3b5f25` (corrección de huso horario).
Objetivo: medir **cuánto mejora la asimilación el pronóstico**. Se asimila hasta `t0`, se pronostica libre `t0 → t0+24 h` y se compara contra las observaciones de las ocho estaciones, con un control sin nudging.

Convención de este documento: **[hecho]** = lo vi en el repo; **[a verificar]** = no lo confirmé en la fuente original; **[propuesta]** = decisión de diseño mía, tuya para aceptar o cambiar.

---

## 0. Decisiones previas (necesito tu confirmación antes de tocar código)

| # | Decisión | Propuesta | Alternativa |
|---|---|---|---|
| D1 | Ventana de asimilación previa | **12 h** (inicio = t0 − 12 h) | 6 h (más barata, menos spin-up) / 24 h |
| D2 | Emisión t0 por caso | Elegir t0 **antes** del evento (ej. Zonda: 12 h antes de la hora de inicio observada) para que las +24 h lo cubran | t0 fijo 00 UTC |
| D3 | Observaciones | Las 8 estaciones, todas asimilan (sin roles) | Mantener roles (descartado: ya no hay hold-out) |
| D4 | Línea base extra | **Persistencia** (último valor observado en t0 sostenido) | Sin persistencia |
| D5 | Tramos de horizonte | +1–6, +7–12, +13–18, +19–24 h además de cada hora | Solo horario |
| D6 | Obs. desde `start − obs_twindo` | No (solo `[start, t0]`) | Sí, si la guía lo recomienda [a verificar] |

---

## 1. Esquema temporal

```
start = t0 − 12 h      t0                      t0 + 24 h
  |==== nudging ====|------- pronóstico libre -------|
  GFS ciclo 12Z (D−1), f000…f036 cada 3 h
  Brazo N (nudging): obs_nudge_opt=1, fdda_end = 720 min
  Brazo C (control): obs_nudge_opt=0, todo lo demás idéntico
  Evaluación: horas t0+1 … t0+24 (24 instantes) vs observaciones
```

- `run_hours = asim_h + horizonte_h = 36` **[hecho: hoy el código usa run_hours = 24 y fdda_end = run_hours*60 en `pipeline_wrf.py: preparar_namelist`]**.
- Archivos `wrfout`: 37 (hora 0 a 36), `history_interval = 60`.
- Paso de tiempo fijo 45 s (commit 57afb94, se mantiene).

## 2. Configuración por caso (`config/casos_oficiales.json`)

Agregar por caso (campos nuevos, los viejos de fecha se conservan para compatibilidad):

```json
{
  "id": "caso1_zonda",
  "t0": "2026-07-31T12:00:00Z",
  "ventana_asimilacion_h": 12,
  "horizonte_h": 24,
  "asimilar_todas_las_estaciones": true
}
```

Derivados (calcular en código, no duplicar en JSON):
- `start = t0 − ventana_asimilacion_h`
- `run_hours = ventana_asimilacion_h + horizonte_h`
- `fdda_end_min = ventana_asimilacion_h * 60`
- `valid_times = [t0 + k h, k = 1..horizonte_h]`
- ciclo GFS = el de las 12Z del día de `start` (con start = D−1 12Z, ciclo 12), `f000..f036` cada 3 h.

## 3. Cambios por archivo

### 3.1 `src/casos/run_casos.py`
1. `ejecutar_caso`: leer `t0`, `ventana_asimilacion_h`, `horizonte_h`; calcular `start`, `run_hours`; pasarlos a todas las etapas.
2. `descargar_gfs(fecha_ini, ciclo, horas)`: pedir `horas = run_hours` (36) desde el ciclo de `start`. Verificar disponibilidad de f036 en el bucket.
3. `ejecutar_wps`: exportar `START_DATE=<start>` y `RUN_HOURS=36` (el script `wps_sanjuan/run_wps_sanjuan.sh` ya lee ambas por entorno **[hecho]**). Confirmar que `met_em` cubre 36 h.
4. `propagar_metem` y `_valid_times_iso`: generar desde `start` con `run_hours` (hoy asumen 24 h).
5. `descargar_obs_historico` / `cobertura_obs`: la ventana UTC a descargar y verificar pasa a ser `[start, t0]` para asimilar, y `[t0+1h, t0+24h]` para validar. Se requieren **ambos** CSV (D−1 y D) fusionados, como ya se hace con `_ventana.csv`. Cobertura mínima aceptable: reportarla por estación y por ventana; no abortar, pero marcar estación sin datos en validación como excluida.
6. `ejecutar_pipeline`: invocar `pipeline_wrf.py --date <D−1> --hour 12:00 --run-hours 36 --asim-hours 12`.
7. Reporte final: tabla por horizonte (ver 3.5).

### 3.2 `pipeline_wrf.py`
1. `preparar_namelist(...)`: **reemplazar** `fdda_end = run_hours*60` por un argumento `fdda_end_min` (default = `asim_hours*60`). En el control, `obs_nudge_opt=0` y mismo resto.
2. Nuevo argumento CLI `--asim-hours` (default 12). Validar `0 < asim_hours < run_hours`.
3. `generar_littler_desde_json`: hoy filtra `[start, start+run_hours)`. Cambiar a `[start, t0]` con `t0 = start + asim_hours`. Ninguna observación con tiempo `> t0` puede entrar a `OBS_DOMAIN101` (esto es el corazón del protocolo).
4. `ESTACIONES_JSON`: permitir ruta por argumento; con `asimilar_todas_las_estaciones` todas las estaciones activas entran como asimiladas.
5. Manifiesto de la corrida: agregar `t0`, `asim_hours`, `horizonte_h`, `fdda_end_min`, `sha256(OBS_DOMAIN101)` y estaciones asimiladas. La reutilización del control (manifiesto de control) debe invalidarse si cambian `start`, `run_hours` o la namelist base.
6. `run_valida_wrf`: pasar `--t0` y `--horizon-h` en lugar de `--valid-times` sueltos.

### 3.3 `src/modelo/namelist_manager.py` (`configurar_fdda`)
Agregar los parámetros de fin de nudging. Por la guía de WRF, para inicialización dinámica: `obs_idynin = 1`, y rampa de salida `obs_dtramp` **[a verificar en el PDF original y en WRF 4.5]**. Hasta verificar, dejar configurable y por defecto `obs_idynin = 0`, `obs_dtramp` ausente, y que el pipeline imprima el valor efectivo. Dejar `fdda_end = asim_hours*60`.
Revisar también **[a verificar]**:
- `obs_twindo` es la **semi**ventana (1.0 h → pesos 2 h en total).
- `obs_rinxy × obs_sfcfacr` (50 km × 2.0 = 100 km efectivos?). Si se confirma, la tesis debe decir 100 km o bajar `obs_sfcfacr` a 1.0.

### 3.4 `src/asimilacion/obsnud_writer.py`
- Líneas ~174-198: filtro por rol. Agregar parámetro `usar_roles=False` (por defecto no filtra).
- Defensa: parámetro `t_max` (= t0); descartar con aviso cualquier registro `> t_max`.
- Mantener 5 líneas por registro y orden cronológico.

### 3.5 `src/validacion/valida_wrf_cli.py` y `metrics.py`
1. Entrada: `--t0`, `--horizon-h 24`, y los `wrfout` de N y C.
2. Para cada estación `s` y cada horizonte `h = 1..24`: interpolar modelo al punto de la estación (corrigiendo T por diferencia de altura **solo si se declara**; por defecto sin corrección y se reporta el sesgo) y comparar con la observación de `t0+h` (promedio horario centrado, regla fija y documentada).
3. Salidas:
   - `errores_largo.csv`: `caso, estacion, variable, lead_h, valid_time, obs, mod_N, mod_C` (una fila por combinación; permite recalcular todo).
   - `metricas_por_horizonte.csv`: `variable, lead_h, n, RMSE_C, RMSE_N, dRMSE = RMSE_C − RMSE_N, mejora_pct = dRMSE/RMSE_C*100, sesgo_C, sesgo_N`.
   - `metricas_por_tramo.csv` (D5).
   - Persistencia (D4): `RMSE_P` por horizonte con el último valor observado `≤ t0`.
4. Eliminar la separación ajuste / hold-out de la tabla principal (dejar la lógica detrás de un flag `--holdout` para trabajo futuro).
5. Intervalos de confianza de ΔRMSE: **[propuesta]** bootstrap por bloques (bloques de ~6 h) remuestreando tiempos, no observaciones individuales, porque los errores consecutivos están autocorrelacionados. Un bootstrap simple subestimaría la incertidumbre.
6. Estaciones sin dato en un horizonte: se omiten en ese par y se reporta `n`. INTA_SANMARTIN solo tiene presión → entra solo en presión.

### 3.6 `src/preflight/preflight.py` y `config/preflight_config.json`
- `gfs.run_hours_max`: 12 → **36**.
- Nuevo check **2.2.8 Separación temporal** (bloqueante): `fdda_end_min == asim_hours*60`, `run_hours == asim+horizonte`, ninguna obs `> t0` en el archivo Little-R, `start == t0 − asim`.
- Check de cobertura por ventana (asimilación y validación) por estación.
- Mantener 2.2.7 (huso horario `fecha_hora == hora_unix`).

### 3.7 Pruebas (`tests/`)
- `test_separacion_temporal`: obs sintéticas en `t0+1 min` no aparecen en OBS_DOMAIN101.
- `test_fdda_end`: namelist con `fdda_end = 720` para asim 12 h.
- `test_control_identico`: diff de namelists N vs C solo en `obs_nudge_opt`.
- `test_valid_times`: 24 instantes `t0+1…t0+24`.
- `test_metricas`: ΔRMSE y mejora % con un caso calculado a mano.

## 4. Verificación automática

Script entregado: `scripts/verifica_protocolo_temporal.py`.

```bash
python scripts/verifica_protocolo_temporal.py \
  --case-dir outputs/runs/<run>/caso1_zonda \
  --t0 2026-07-31_12:00:00 --asim-hours 12 --horizon 24 \
  --coef 0.0001 --wrfout-nudged <dir_N> --wrfout-control <dir_C>
```

Chequea: T1 inicio = t0 − asim; T2 run_hours = asim + horizonte; T3 fdda_end y obs_nudge_opt; T4 control idéntico salvo obs_nudge_opt; T5 coeficientes; T6 formato y orden de OBS_DOMAIN101; T7 sin obs después de t0; T8 sin obs antes de start; T9 número de wrfout = 37. Sale con código 1 si algo falla. Sobre una corrida actual (24 h continuas) correctamente da NO CUMPLE (T1, T2, T3, T7).

## 5. Procedimiento de corrida

1. Confirmar D1–D6 y `t0` por caso.
2. Archivar corridas actuales en `outputs/runs/_previas_nudging_continuo/` (no borrarlas; se citan solo como exploratorias).
3. Implementar cambios 3.1–3.6 y correr tests.
4. `--dry-run` / solo preparación (sin WRF): ejecutar el verificador sobre los directorios preparados. **No lanzar WRF si T1–T8 no pasan.**
5. **Piloto: caso 1 Zonda** completo (~15–17 min por brazo en tus corridas previas; 2 brazos). Verificar con el script y revisar `errores_largo.csv` a mano en 2–3 filas.
6. Casos 2 y 3, luego caso 4 (2026-09-24) **después** de verificar cobertura UTC de las 8 estaciones en ambas ventanas.
7. Repetir un caso (misma entrada) para el test de reproducibilidad (5.6 de la tesis): comparar `sha256` de OBS_DOMAIN101 y diferencia máxima de wrfout.
8. Enviarme: `metricas_por_horizonte.csv`, `errores_largo.csv`, manifiestos y logs de verificación; yo completo 5.4–5.9.

## 6. Criterios de aceptación
- [ ] Verificador T1–T9 sin fallas en los 4 casos y ambos brazos.
- [ ] N y C difieren solo en `obs_nudge_opt`.
- [ ] Cero observaciones posteriores a t0 en el archivo asimilado.
- [ ] 24 horizontes por variable y estación, con `n` reportado.
- [ ] Reproducibilidad demostrada en al menos un caso.
- [ ] Reporte de cobertura por estación y ventana.

## 7. Riesgos y puntos abiertos
1. **Semántica de `obs_idynin`, `obs_dtramp`, `obs_twindo`, `obs_sfcfacr`**: sé lo que dice un resumen de la guía; falta que lo leas en el PDF original y en `README.namelist` de WRF 4.5.
2. **Obs cerca de t0**: con `obs_twindo = 1 h` los pesos se extienden ±1 h; la última observación aún influye parte del pronóstico libre inicial si no hay rampa de salida. Define si se usa `obs_dtramp` o se acepta como parte del método (y se documenta).
3. **GFS 12Z f036** disponible en el bucket (verificar antes de cada caso).
4. **Sesgo topográfico** (errores de altitud de 135 a 970 m): ΔRMSE de T2 no es comparable entre estaciones sin corrección; reportar por estación y no solo agregado.
5. **Representatividad**: 4 casos, 8 estaciones: los resultados describen esos eventos, no una climatología de mejora. Redactar la conclusión con ese alcance.
6. **Mejora en ubicaciones sin estación** no queda demostrada por este diseño (queda como trabajo futuro con hold-out).
7. Verifica en fuente original cualquier cita antes de pasar a la tesis.
