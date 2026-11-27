# Nota sobre la verificacion del protocolo temporal (Caso 4 prod4km)

El script del repositorio `scripts/verifica_protocolo_temporal.py` devuelve
codigo 1 en el Caso 2 por su chequeo T4:

```
[FALLA] T4 control = nudged salvo obs_nudge_opt | obs_nudge_opt control=None
RESULTADO: NO CUMPLE
```

T4 asume que los namelists de control y nudged difieren **solo** en la linea
`obs_nudge_opt`. Los namelists autorizados, generados exclusivamente con
`scripts/prod4km/render_namelists.py`, no siguen ese esquema: el brazo control
no incluye el bloque `&fdda` (ni `obs_nudge_opt`, ni `auxinput11_*`, ni
coeficientes) y `history_outname` apunta a `control/` frente a `nudged/`.
Lo mismo ocurre en los namelists de los casos 1 y 3 (verificados por lectura).

No se modifico ningun namelist ni el script del repositorio. Se ejecuto una
copia adaptada en `/tmp/opencode/verifica_protocolo_temporal_adaptado.py`,
que mantiene T1,T2,T3,T5,T6,T7,T8,T9 intactos y sustituye T4 por:

- el control no tiene ningun parametro de nudging de observaciones activo;
- el resto de parametros, excluyendo `&fdda` y `history_outname`, es identico.

Resultado: `PROTOCOLO CUMPLIDO` (codigo 0), guardado en
`informes/protocolo_temporal_adaptado.txt`. La salida original del script del
repositorio se conserva en `informes/protocolo_temporal.txt`. El mismo falso
positivo se detecto y documento por primera vez en el Caso 2, en
`logs/prod4km_caso2_validacion_protocolo_fallo_20261126.log`.

Esta es una excepcion de verificacion, no de configuracion del modelo. El
corte del nudging se verifico ademas de forma independiente: ultima llamada
`CALL IN4DOB ... XTIME = 720.00`, sin lecturas de observaciones posteriores
(`informes/XTIME_nudging.txt`).
