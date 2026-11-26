# Binario usado en el Caso 4 prod4km — excepcion documentada

El protocolo indicaba `/home/pgich/Build_WRF/WRF/test/em_real/{wrf,real}.exe`,
que es el par usado por los casos 1 y 3 segun
`outputs/runs/2026-07-31_0000z/caso1_zonda__prod4km/BITACORA_PROD4KM.md`.
El 2026-11-26 esos archivos ya no existen:

```
ls: no se puede acceder a '/home/pgich/Build_WRF/WRF/test/em_real/wrf.exe': No existe el fichero o el directorio
ls: no se puede acceder a '/home/pgich/Build_WRF/WRF/test/em_real/real.exe': No existe el fichero o el directorio
```

No hay copia del par original en el filesystem ni en los backups del repo.
El usuario autorizo el 2026-11-26 usar el build disponible y documentar el desvio:

- `/home/pgich/Build_WRF/WRF_DEBUG_PHASE4_ETAPA3/main/wrf.exe`
  sha256 `91283460023d25d751ad7c6fc479624e126be0cc3308b23a284b2298084643b3`
- `/home/pgich/Build_WRF/WRF_DEBUG_PHASE4_ETAPA3/main/real.exe`
  sha256 `c7176b8843c052438a8fe1a0db64b5bfb43099320c716576bf4ed6f303511f7b`

Las tablas se enlazan desde `/home/pgich/Build_WRF/WRF_DEBUG_PHASE4_ETAPA3/test/em_real/`,
el directorio del mismo build. No se cambio ningun parametro del modelo: los
namelists se generaron solo con `scripts/prod4km/render_namelists.py` y las
unicas diferencias contra el Caso 1 son fechas y `history_outname` (ver diffs).
Esta es la unica excepcion a la regla 4 del protocolo.
