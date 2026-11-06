# Configuración Operativa San Juan - Valores de Plantillas

## 1. Búsqueda de Marcadores en Archivos

### Archivo: `/home/pgich/wrf-operativo/ejecutables/sanjuan/env.bash`

Marcadores encontrados (líneas 25-29):
```
25: export REF_LAT=-31.121
26: export REF_LON=-69.433
27: export TRUELAT1=-31.121
28: export TRUELAT2=-31.121
29: export STAND_LON=-69.433
22: export RUN_HOURS=48
```

### Archivo: `/home/pgich/wrf-operativo/ejecutables/runWPS.bash`

Reemplazos de marcadores (líneas 32-39):
```
32: sed -i "s/START_DATE/$start_date/g" $namlist_wps
33: sed -i "s/END_DATE/$end_date/g" $namlist_wps
34: sed -i "s|RUTA_GEOG_DATA|"$WPS_GEOG"|g" $namlist_wps
35: sed -i "s|REF_LAT|"$REF_LAT"|g" $namlist_wps
36: sed -i "s|REF_LON|"$REF_LON"|g" $namlist_wps
37: sed -i "s|TRUELAT1|"$TRUELAT1"|g" $namlist_wps
38: sed -i "s|TRUELAT2|"$TRUELAT2"|g" $namlist_wps
39: sed -i "s|STAND_LON|"$STAND_LON"|g" $namlist_wps
```

### Archivo: `/home/pgich/wrf-operativo/ejecutables/runWRF.bash`

Reemplazos de marcadores (líneas 62-75):
```
62: sed -i "s/RUN_HOURS/$RUN_HOURS/g" $namlist_input 
63: sed -i "s/START_YEAR/$year_start/g" $namlist_input
64: sed -i "s/START_MONTH/$month_start/g" $namlist_input
65: sed -i "s/START_DAY/$day_start/g" $namlist_input 
66: sed -i "s/START_HOUR/$hour_start/g" $namlist_input
67: sed -i "s/START_MINUTE/$minute_start/g" $namlist_input
68: sed -i "s/START_SECOND/$second_start/g" $namlist_input
69: sed -i "s/END_YEAR/$year_end/g" $namlist_input
70: sed -i "s/END_MONTH/$month_end/g" $namlist_input
71: sed -i "s/END_DAY/$day_end/g" $namlist_input
72: sed -i "s/END_HOUR/$hour_end/g" $namlist_input
73: sed -i "s/END_MINUTE/$minute_end/g" $namlist_input
74: sed -i "s/END_SECOND/$second_end/g" $namlist_input
75: sed -i "s|HISTORY_OUTNAME|"$history_outname"|g" $namlist_input
```

### Archivo: `/home/pgich/wrf-operativo/datos/namelists/sanjuan/namelistTemp.wps`

Plantilla con marcadores (líneas 36-41):
```
36: ref_lat   =  REF_LAT,
37: ref_lon   =  REF_LON,
38: truelat1  =  TRUELAT1,
39: truelat2  =  TRUELAT2,
40: stand_lon =  STAND_LON,
41: geog_data_path = 'RUTA_GEOG_DATA'
```

Otros parámetros fijos del dominio:
```
15: e_we              =  141, 141,
16: e_sn              =  200,  200,
33: dx = 4000,
34: dy = 4000,
```

### Archivo: `/home/pgich/wrf-operativo/datos/namelists/sanjuan/namelistTemp.input`

Plantilla con marcadores (líneas 3, 6-17, 29):
```
3: run_hours                           = RUN_HOURS,
6: start_year                          = START_YEAR, START_YEAR, 2000,
7: start_month                         = START_MONTH, START_MONTH,   01,
8: start_day                           = START_DAY, START_DAY,   24,
9: start_hour                          = START_HOUR, START_HOUR,   12,
10: start_minute                        = START_MINUTE, START_MINUTE,   00,
11: start_second                        = START_SECOND, START_SECOND,   00,
12: end_year                            = END_YEAR, END_YEAR, 2000,
13: end_month                           = END_MONTH, END_MONTH,   01,
14: end_day                             = END_DAY, END_DAY,   25,
15: end_hour                            = END_HOUR, END_HOUR,   12,
16: end_minute                          = END_MINUTE, END_MINUTE,   00,
17: end_second                          = END_SECOND, END_SECOND,   00,
29: history_outname                     = "HISTORY_OUTNAME"
```

Otros parámetros fijos del dominio:
```
33: time_step                           = 15,
37: e_we                                = 141,    112,   94,
38: e_sn                                = 200,    97,    91,
41: num_metgrid_levels                  = 32,
43: dx                                  = 4000, 10000,  3333.33,
44: dy                                  = 4000, 10000,  3333.33,
```

---

## 2. Valores Reales para el Dominio San Juan

### Valores de Configuración Extraídos del Script

| Parámetro | Valor | Fuente |
|-----------|-------|--------|
| **REF_LAT** | -31.121 | env.bash línea 25 |
| **REF_LON** | -69.433 | env.bash línea 26 |
| **TRUELAT1** | -31.121 | env.bash línea 27 |
| **TRUELAT2** | -31.121 | env.bash línea 28 |
| **STAND_LON** | -69.433 | env.bash línea 29 |
| **RUN_HOURS** | 48 | env.bash línea 22 |
| **e_we** | 141 | namelistTemp.wps línea 15, namelistTemp.input línea 37 |
| **e_sn** | 200 | namelistTemp.wps línea 16, namelistTemp.input línea 38 |
| **dx** | 4000 m | namelistTemp.wps línea 33, namelistTemp.input línea 43 |
| **dy** | 4000 m | namelistTemp.wps línea 34, namelistTemp.input línea 44 |
| **time_step** | 15 s | namelistTemp.input línea 33 |
| **num_metgrid_levels** | 32 | namelistTemp.input línea 41 |

### Inicialización

El script calcula automáticamente:
- **Hora UTC de inicialización**: Extraída del parámetro de fecha de entrada (formato: YYYYMMDDHHCC)
- **Horas de pronóstico**: 48 horas (RUN_HOURS=48)

Ejemplo de cálculo en `runWPS.bash` línea 18:
```bash
end_date=`date -d "${fecha:0:-2} ${fecha:8:10} $RUN_HOURS hours" +%Y-%m-%d_%H":00:00"`
```

---

## 3. Verificación Independiente: Namelists Renderizados

### Búsqueda Realizada
Se buscaron namelists.wps y namelist.input renderizados en:
- `/home/pgich/wrf-operativo/salidas/` - sin resultados
- `/home/pgich/wrf-operativo/ejecutables/WRF/` - encontrados varios .orig/.jan00/.4km/.global/.volc/.diags/.fire/.chem etc., pero ninguno etiquetado explícitamente como de San Juan con fecha reciente
- `/home/pgich/wrf-operativo/ejecutables/WPS/` - sin namelists renderizados guardados

### Nota sobre Archivos Temporales
Los scripts crean archivos temporales durante ejecución:
- `$WRF_EJECUTABLES/WPS/namelist.wps` (temporal, se sobrescribe por cada corrida)
- `$WRF_EJECUTABLES/WRF/namelist.input` (temporal, se sobrescribe por cada corrida)
- Copia de seguridad: `/home/pgich/namelist_ultimo.wps` y `/home/pgich/namelist_ultimo.input` (creadas en runWPS.bash línea 30 y runWRF.bash línea 32)

**Estado actual**: No hay archivos de backup con timestamp que permita verificar una corrida específica.

---

## 4. Última Corrida de San Juan

### Salida WRF Más Reciente

| Parámetro | Valor |
|-----------|-------|
| **Ruta** | `/home/pgich/wrf-operativo/salidas/wrfout/2025_09/wrfout_d01_2025-09-09_06:00:00.nc` |
| **Fecha de archivo** | 2025-09-09 |
| **Tamaño** | 18.3 GB |
| **Dominio** | d01 |
| **Hora inicial (UTC)** | 2025-09-09 06:00:00 |

**Nota**: Este archivo es el más reciente en la estructura de salidas. No se dispone de información de metadatos en los logs para confirmar explícitamente que es una corrida de San Juan (no Chaco/Paraguay u otro dominio).

---

## 5. Validación Cruzada

### Comparación: Valores del Script vs. Plantillas

No se encontraron discrepancias. Los valores son consistentes:

| Elemento | Valor |
|----------|-------|
| REF_LAT (env.bash) | -31.121 |
| REF_LAT (plantilla namelistTemp.wps) | Marcador: REF_LAT → sustituido por env value |
| REF_LON (env.bash) | -69.433 |
| REF_LON (plantilla namelistTemp.wps) | Marcador: REF_LON → sustituido por env value |
| TRUELAT1 (env.bash) | -31.121 |
| TRUELAT1 (plantilla namelistTemp.wps) | Marcador: TRUELAT1 → sustituido por env value |
| TRUELAT2 (env.bash) | -31.121 |
| TRUELAT2 (plantilla namelistTemp.wps) | Marcador: TRUELAT2 → sustituido por env value |
| STAND_LON (env.bash) | -69.433 |
| STAND_LON (plantilla namelistTemp.wps) | Marcador: STAND_LON → sustituido por env value |
| RUN_HOURS (env.bash) | 48 |
| RUN_HOURS (plantilla namelistTemp.input) | Marcador: RUN_HOURS → sustituido por env value |

**Conclusión**: Sin namelists renderizados guardados no se puede hacer una verificación con valores numéricos reales de una ejecución completada. Todos los marcadores en las plantillas son reemplazados por valores provenientes de env.bash y cálculos de fecha en los scripts.

---

## 6. Análisis de la Cadena Operativa

### Flujo de Configuración

```
env.bash (variables de entorno)
    ↓
runWPS.bash (rellena namelistTemp.wps → namelist.wps)
    ↓
Ejecuta: geogrid.exe, ungrib.exe, metgrid.exe
    ↓
runWRF.bash (rellena namelistTemp.input → namelist.input)
    ↓
Ejecuta: real.exe, wrf.exe
    ↓
Salida: wrfout_d<domain>_<date>.nc
```

### Rutas Clave

- **Base operativa**: `/home/pgich/wrf-operativo/`
- **Configuración dominio**: `/home/pgich/wrf-operativo/ejecutables/sanjuan/env.bash`
- **Plantillas**: `/home/pgich/wrf-operativo/datos/namelists/sanjuan/`
- **Datos GFS**: `$WRF_GFS` → `/home/pgich/wrf-operativo/datos/GFS025/`
- **Datos geográficos**: `$WPS_GEOG` → `/home/pgich/wrf-operativo/datos/WPS_GEOG`
- **Salidas WRF**: `$WRF_WRFOUT` → `/home/pgich/wrf-operativo/salidas/wrfout/`

---

## Conclusión

**Valores reales con que se rellena la cadena operativa de San Juan:**

- **Ubicación**: Lat -31.121°, Lon -69.433°
- **Proyección**: Lambert Conformal Conic
- **Resolución**: 4 km × 4 km
- **Dominio**: 141 × 200 puntos de grilla
- **Pronóstico**: 48 horas
- **Timestep**: 15 segundos
- **Niveles meteorológicos**: 32
- **Hora de inicialización**: Dinámica (parámetro de entrada al script)

No se encontraron discrepancias entre los valores definidos en `env.bash` y los utilizados en los scripts de relleno de plantillas.
