# Evidencia: geog_data_res ('lowres' vs 'default') y error de altura estación–grilla

- Fecha: 2026-11-04, entre las 11:15 y las 11:35 (-03). Usuario `pgich`.
- Lo único que se ejecutó fue `geogrid.exe`, dos veces. No se corrió ungrib, metgrid, real ni wrf. No se descargó nada. No se modificó ningún archivo existente: todo lo nuevo está en `outputs/evidencia_geog/`. No se hizo commit.
- Las fechas son mtime (`stat`), en hora -0300.

## 1. Rutas

| Elemento | Ruta absoluta | mtime |
|---|---|---|
| Catálogo de estaciones (lat, lon, elev) | /home/pgich/wrf-modular-V1/config/estaciones.json | 2026-10-12 18:39:53 |
| LOS_PIONEROS (no figura en estaciones.json) | /home/pgich/wrf-modular-V1/documentacion_proyecto/implementacion_arquitectura_27082026.md, línea 96 | 2026-10-11 19:24:04 |
| Interpolación IDW de 4 nodos | /home/pgich/wrf-modular-V1/src/validacion/spatial_interp.py (`SpatialInterpolator.interpolar_4_nodos`, l.34–79) | 2026-10-11 19:24:04 |
| Directorio WPS | /home/pgich/Build_WRF/WPS (README: "WRF Pre-Processing System Version 4.5") | — |
| geogrid.exe | /home/pgich/Build_WRF/WPS/geogrid.exe → geogrid/src/geogrid.exe | 2023-10-24 13:15:29 |
| GEOGRID.TBL de WPS | /home/pgich/Build_WRF/WPS/geogrid/GEOGRID.TBL → GEOGRID.TBL.ARW | 2023-04-21 17:49:32 |
| GEOGRID.TBL que usa la tesis | /home/pgich/wrf-modular-V1/wps_sanjuan/GEOGRID.TBL. Es un archivo regular, no un enlace; `namelist.wps` tiene `opt_geogrid_tbl_path = './'`. Es byte a byte idéntico a GEOGRID.TBL.ARW (`cmp`). | 2026-10-11 19:24:04 |
| Script WPS de la tesis | /home/pgich/wrf-modular-V1/wps_sanjuan/run_wps_sanjuan.sh | 2026-10-11 20:37 |
| WPS_GEOG que usa ese script | /home/pgich/wrf-operativo/datos/WPS_GEOG (`run_wps_sanjuan.sh:42`: `GEOG_DATA_PATH=${GEOG_DATA_PATH:-/home/pgich/wrf-operativo/datos/WPS_GEOG}`) | 2023-10-27 10:50:31 |
| namelist.wps de la tesis | /home/pgich/wrf-modular-V1/wps_sanjuan/namelist.wps | 2026-11-02 10:39:31 |

Estaciones:
- `config/estaciones.json` tiene **8** estaciones: INTA_POCITO, ULLUM_EMBALSE, ECOHUMUS, PUNTA_NEGRA, INTA_SANMARTIN, VALLE_FERTIL, CUESTA_Viento y CARACOLES.
- Para LOS_PIONEROS se usaron los valores de `implementacion_arquitectura_27082026.md:96`: `"lat": -32.1234, "lon": -67.1234, "elev": 890`. `documentacion_proyecto/CONFIG_WRF_SAN_JUAN.md:186` tiene los mismos valores.
- **El total es 9 estaciones, no 10.** No encontré una décima en el repo. `documentacion_proyecto/ejecucion_06082026.md:100` también dice "9 estaciones".

## 2. GEOGRID.TBL: bloques HGT_M y LANDUSEF (LU_INDEX)

Fuente: `/home/pgich/wrf-modular-V1/wps_sanjuan/GEOGRID.TBL`, líneas 3–23 y 23–83. En este archivo LU_INDEX no tiene un bloque propio: aparece como `dominant = LU_INDEX` dentro del bloque `LANDUSEF`.

```
===============================
name = HGT_M
        priority = 1
        dest_type = continuous
        smooth_option = smth-desmth_special; smooth_passes=1
        fill_missing=0.
        interp_option = gmted2010_30s:average_gcell(4.0)+four_pt+average_4pt
        interp_option =     gtopo_30s:average_gcell(4.0)+four_pt+average_4pt
        interp_option =      gtopo_2m:four_pt
        interp_option =      gtopo_5m:four_pt
        interp_option =     gtopo_10m:four_pt
        interp_option =        lowres:average_gcell(4.0)+four_pt
        interp_option =       default:average_gcell(4.0)+four_pt+average_4pt
        rel_path = gmted2010_30s:topo_gmted2010_30s/
        rel_path =     gtopo_30s:topo_30s/
        rel_path =      gtopo_2m:topo_2m/
        rel_path =      gtopo_5m:topo_5m/
        rel_path =     gtopo_10m:topo_10m/
        rel_path =        lowres:topo_gmted2010_5m/
        rel_path =       default:topo_gmted2010_30s/
===============================
```

```
===============================
name=LANDUSEF
        priority=1
        dest_type=categorical
        z_dim_name=land_cat
        dominant = LU_INDEX
        landmask_water =    nlcd2006_9s:17         # Calculate a landmask from this field
        landmask_water =   nlcd2006_30s:17         # Calculate a landmask from this field
        landmask_water =    nlcd2011_9s:17         # Calculate a landmask from this field
        landmask_water =       nlcd2006:17         # Calculate a landmask from this field
        landmask_water =       ssib_10m:16         # Calculate a landmask from this field
        landmask_water =        ssib_5m:16         # Calculate a landmask from this field
        landmask_water =      modis_15s:17         # Calculate a landmask from this field
        landmask_water = modis_15s_lake:17,21      # Calculate a landmask from this field
        landmask_water =      modis_30s:17         # Calculate a landmask from this field
        landmask_water = modis_30s_lake:17,21      # Calculate a landmask from this field
        landmask_water =       usgs_30s:16         # Calculate a landmask from this field
        landmask_water =     usgs_lakes:16,28      # Calculate a landmask from this field
        landmask_water =    modis_lakes:17,21      # Calculate a landmask from this field
        landmask_water =        usgs_2m:16         # Calculate a landmask from this field
        landmask_water =        usgs_5m:16         # Calculate a landmask from this field
        landmask_water =       usgs_10m:16         # Calculate a landmask from this field
        landmask_water =         lowres:17,21      # Calculate a landmask from this field
        landmask_water =        default:17,21      # Calculate a landmask from this field
        interp_option =    nlcd2006_9s:average_gcell(0.0)
        interp_option =   nlcd2006_30s:average_gcell(0.0)
        interp_option =    nlcd2011_9s:average_gcell(0.0)  
        interp_option =       nlcd2006:nearest_neighbor
        interp_option =       ssib_10m:four_pt
        interp_option =        ssib_5m:four_pt
        interp_option =      modis_15s:nearest_neighbor
        interp_option = modis_15s_lake:nearest_neighbor
        interp_option =      modis_30s:nearest_neighbor
        interp_option = modis_30s_lake:nearest_neighbor
        interp_option =       usgs_30s:nearest_neighbor
        interp_option =     usgs_lakes:nearest_neighbor
        interp_option =    modis_lakes:nearest_neighbor
        interp_option =        usgs_2m:four_pt
        interp_option =        usgs_5m:four_pt
        interp_option =       usgs_10m:four_pt
        interp_option =         lowres:average_gcell(4.0)+four_pt
        interp_option =        default:nearest_neighbor
        rel_path =    nlcd2006_9s:nlcd2006_ll_9s/
        rel_path =   nlcd2006_30s:nlcd2006_ll_30s/
        rel_path =    nlcd2011_9s:nlcd2011_ll_9s/
        rel_path =       nlcd2006:nlcd2006_ll_30s/
        rel_path =       ssib_10m:ssib_landuse_10m/
        rel_path =        ssib_5m:ssib_landuse_5m/
        rel_path =      modis_15s:modis_landuse_20class_15s/
        rel_path = modis_15s_lake:modis_landuse_20class_15s_with_lakes/
        rel_path =      modis_30s:modis_landuse_20class_30s/
        rel_path = modis_30s_lake:modis_landuse_20class_30s_with_lakes/
        rel_path =       usgs_30s:landuse_30s/
        rel_path =     usgs_lakes:landuse_30s_with_lakes/
        rel_path =    modis_lakes:modis_landuse_21class_30s/
        rel_path =        usgs_2m:landuse_2m/
        rel_path =        usgs_5m:landuse_5m/
        rel_path =       usgs_10m:landuse_10m/
        rel_path =         lowres:modis_landuse_20class_5m_with_lakes/
        rel_path =        default:modis_landuse_20class_30s_with_lakes/
===============================
```

Carpetas de topografía y uso de suelo en `/home/pgich/wrf-operativo/datos/WPS_GEOG/`:
- Topografía: `topo_gmted2010_30s` y `topo_gmted2010_5m`.
- Uso de suelo: `landuse_30s_with_lakes`, `modis_landuse_20class_30s_with_lakes` y `modis_landuse_20class_5m_with_lakes`.

| Campo | 'lowres' → | 'default' → | ¿Existe 'default' en la PC? |
|---|---|---|---|
| HGT_M | `topo_gmted2010_5m/` | `topo_gmted2010_30s/` | Sí: 649 archivos, tiene `index`, 1,8G |
| LANDUSEF / LU_INDEX | `modis_landuse_20class_5m_with_lakes/` | `modis_landuse_20class_30s_with_lakes/` | Sí: 649 archivos, tiene `index`, 894M |

Como el dataset de 'default' existe, no hizo falta frenar en este punto.

## 3. geogrid.exe con 'lowres' y con 'default'

Comandos:
```bash
E=/home/pgich/wrf-modular-V1/outputs/evidencia_geog
mkdir -p $E/geogrid_lowres $E/geogrid_default
for v in lowres default; do d=$E/geogrid_$v
  cp -p /home/pgich/wrf-modular-V1/wps_sanjuan/namelist.wps $d/namelist.wps
  cp -p /home/pgich/wrf-modular-V1/wps_sanjuan/GEOGRID.TBL  $d/GEOGRID.TBL   # opt_geogrid_tbl_path='./'
  ln -s /home/pgich/Build_WRF/WPS/geogrid.exe $d/geogrid.exe
done
sed -i "s/^ geog_data_res     = 'lowres',/ geog_data_res     = 'default',/" $E/geogrid_default/namelist.wps
for v in lowres default; do cd $E/geogrid_$v; ./geogrid.exe > geogrid_stdout.txt 2>&1; echo exit=$?; done
```

`diff geogrid_lowres/namelist.wps geogrid_default/namelist.wps` (es la única diferencia):
```
17c17
<  geog_data_res     = 'lowres',
---
>  geog_data_res     = 'default',
```
`geogrid_lowres/namelist.wps` es idéntico a `wps_sanjuan/namelist.wps` (`cmp`). Las dos carpetas comparten dominio (e_we=80, e_sn=60, dx=dy=15000), map_proj 'mercator', ref_lat -31.5, ref_lon -68.5 y las fechas 2026-09-23_12 a 2026-09-25_00.

| Corrida | exit | Log | mtime log | Última línea |
|---|---|---|---|---|
| lowres | 0 | /home/pgich/wrf-modular-V1/outputs/evidencia_geog/geogrid_lowres/geogrid.log | 2026-11-04 11:28:12 | `!  Successful completion of geogrid.        !` |
| default | 0 | /home/pgich/wrf-modular-V1/outputs/evidencia_geog/geogrid_default/geogrid.log | 2026-11-04 11:28:13 | `!  Successful completion of geogrid.        !` |

- Líneas WARNING o ERROR (`grep -E "WARNING|ERROR"` en geogrid.log y en geogrid_stdout.txt): **ninguna en las dos corridas.**
- Los logs sí tienen líneas `INFORM`. En las dos corridas son del tipo `Could not read 'index' file ... This field is optional and will not be processed.` y corresponden a LAKE_DEPTH, URB_PARAM, FRC_URB2D, IMPERV, CANFRA, EROD, CLAYFRAC, SANDFRAC, IRRIGATION, orogwd3_* (LS/SS) y BATHYMETRY.
- Para HGT_M y LANDUSEF los logs dicen `INFORM: Using lowres data source for HGT_M.` / `... for LANDUSEF.` en la corrida lowres, y `INFORM: Using default data source for HGT_M.` / `... for LANDUSEF.` en la corrida default.

Versión de WPS: el `geogrid.log` no imprime número de versión. El atributo global de ambos `geo_em.d01.nc` es `:TITLE = "OUTPUT FROM GEOGRID V4.5" ;`, y `/home/pgich/Build_WRF/WPS/README` dice "WRF Pre-Processing System Version 4.5".

## 4. Control: ¿se reproduce la grilla de la tesis?

Comparé HGT_M de `/home/pgich/wrf-modular-V1/outputs/evidencia_geog/geogrid_lowres/geo_em.d01.nc` (mtime 2026-11-04 11:28:12) con HGT en el primer tiempo (`2026-09-24_00:00:00`) de `/home/pgich/wrf-modular-V1/outputs/runs/2026-09-24_0000z/sanjuan_0924/control/wrfout_d01_2026-09-24_00:00:00` (mtime 2026-10-20 11:00:01).

- Forma: (59, 79) en ambos.
- **Diferencia máxima absoluta de HGT: 0.0 m.** XLAT y XLONG: 0.0.
- HGT_M nuevo contra `/home/pgich/wrf-modular-V1/wps_sanjuan/geo_em.d01.nc` (mtime 2026-11-02 10:39:31): 0.0.

Atributos de ambos geo_em: `MAP_PROJ = 3`, `DX = 15000.f`, `CEN_LAT = -31.50001f`, `CEN_LON = -68.5f`, `MMINLU = "MODIFIED_IGBP_MODIS_NOAH"`. Dominio: lat -35.329 a -27.508, lon -74.671 a -62.329.

## 5. HGT_M: estadísticas y diferencia default − lowres

| geo_em | mín (m) | máx (m) | media (m) |
|---|---|---|---|
| lowres | 0.0 | 5461.81 | 815.60 |
| default | 0.0 | 5446.88 | 815.93 |

Diferencia default − lowres sobre los 59×79 puntos de masa:

| Métrica | Valor (m) |
|---|---|
| Máximo absoluto | 175.73 |
| Media absoluta | 9.03 |
| RMS | 20.03 |
| Media con signo | +0.33 |

Punto de máxima diferencia:
- Índices (base 0): j=50 (sur-norte), i=43 (oeste-este).
- Coordenadas: XLAT_M = -28.6245, XLONG_M = -67.8671.
- HGT_M: lowres 3194.03, default 3018.31, diferencia −175.73.

## 6. Altura por estación (IDW de 4 nodos, `SpatialInterpolator.interpolar_4_nodos`)

- Se importó la función de `src/validacion/spatial_interp.py` sin modificarla.
- Para los geo_em se renombraron `XLAT_M→XLAT`, `XLONG_M→XLONG` y `HGT_M→HGT` en memoria, porque la función busca esos nombres. El algoritmo no cambió.
- Script: `outputs/evidencia_geog/analisis_geog.py`. Comando: `python3 -I outputs/evidencia_geog/analisis_geog.py`, con `/home/pgich/anaconda3/bin/python3`, xarray 2023.6.0 y numpy 1.24.3.
- La diferencia se calcula como grilla − real, en metros.

| Estación | lat | lon | real | grilla lowres | dif lowres | grilla default | dif default | Tesis real/grilla/dif | grilla lowres − grilla tesis | ¿> 5 m? |
|---|---|---|---|---|---|---|---|---|---|---|
| INTA_POCITO | -31.65 | -68.5833 | 615 | 808.9 | +193.9 | 815.6 | +200.6 | 615/809/+194 | -0.1 | no |
| ULLUM_EMBALSE | -31.4667 | -68.6667 | 768 | 917.1 | +149.1 | 895.6 | +127.6 | 768/917/+149 | +0.1 | no |
| ECOHUMUS | -31.65 | -68.3 | 600 | 599.1 | -0.9 | 599.0 | -1.0 | 600/599/-1 | +0.1 | no |
| PUNTA_NEGRA | -31.5192 | -68.8178 | 800 | 1306.9 | +506.9 | 1219.7 | +419.7 | 800/1307/+507 | -0.1 | no |
| INTA_SANMARTIN | -31.5 | -68.25 | 600 | 908.3 | +308.3 | 908.9 | +308.9 | 600/908/+308 | +0.3 | no |
| VALLE_FERTIL | -30.6335 | -67.4682 | 900 | 1034.7 | +134.7 | 1037.2 | +137.2 | 900/1035/+135 | -0.3 | no |
| CUESTA_Viento | -30.1833 | -69.0667 | 1530 | 1917.2 | +387.2 | 1908.1 | +378.1 | 1530/1917/+387 | +0.2 | no |
| CARACOLES | -31.5194 | -68.9851 | 942 | 1912.4 | +970.4 | 1860.5 | +918.5 | 942/1912/+970 | +0.4 | no |
| LOS_PIONEROS* | -32.1234 | -67.1234 | 890 | 618.3 | -271.7 | 621.5 | -268.5 | 890/618/-272 | +0.3 | no |

\* Las coordenadas y la elevación de LOS_PIONEROS salen de `documentacion_proyecto/implementacion_arquitectura_27082026.md:96`, no de `config/estaciones.json`.

Comparación con la tabla de la tesis:
- **Ninguna discrepancia mayor a 5 m.** La diferencia máxima entre la grilla lowres y la grilla de la tesis es 0.4 m (CARACOLES).
- La altura real coincide con la de la tesis en las 9 estaciones (diferencia 0).
- La IDW sobre HGT del wrfout de la tesis da los mismos valores que lowres (columna `grilla_wrfout_tesis` en el CSV).

## Archivos creados

Todos están en `/home/pgich/wrf-modular-V1/outputs/evidencia_geog/`:

| Archivo | mtime |
|---|---|
| evidencia_geog.md | (este archivo) |
| analisis_geog.py | 2026-11-04 11:28:58 |
| resultados_geog.json (puntos 4, 5 y 6 completos, con las mtime de los insumos) | 2026-11-04 11:29:08 |
| tabla_estaciones.csv | 2026-11-04 11:29:08 |
| geogrid_lowres/namelist.wps (copia con `cp -p`, conserva mtime) | 2026-11-02 10:39:31 |
| geogrid_lowres/GEOGRID.TBL (copia con `cp -p`) | 2026-10-11 19:24:04 |
| geogrid_lowres/geogrid.exe (enlace → /home/pgich/Build_WRF/WPS/geogrid.exe) | 2026-11-04 11:28:08 |
| geogrid_lowres/geogrid.log | 2026-11-04 11:28:12 |
| geogrid_lowres/geogrid_stdout.txt | 2026-11-04 11:28:12 |
| geogrid_lowres/geo_em.d01.nc | 2026-11-04 11:28:12 |
| geogrid_default/namelist.wps (copia + sed en geog_data_res) | 2026-11-04 11:28:08 |
| geogrid_default/GEOGRID.TBL (copia con `cp -p`) | 2026-10-11 19:24:04 |
| geogrid_default/geogrid.exe (enlace → /home/pgich/Build_WRF/WPS/geogrid.exe) | 2026-11-04 11:28:08 |
| geogrid_default/geogrid.log | 2026-11-04 11:28:13 |
| geogrid_default/geogrid_stdout.txt | 2026-11-04 11:28:13 |
| geogrid_default/geo_em.d01.nc | 2026-11-04 11:28:13 |
