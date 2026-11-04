#!/bin/bash
# Uso: etapa.sh <dir_trabajo> <ejecutable> <etiqueta> [rss_max_GB] [memavail_min_GB]
# Lanza el watchdog de memoria en segundo plano y mide el ejecutable con medir.py usando el entorno del operativo.
P=/home/pgich/wrf-modular-V1/outputs/prueba_costo_1km
D=$1; EXE=$2; ET=$3; RMAX=${4:-34}; AMIN=${5:-3}
cd "$D" || exit 1
python3 -I $P/watchdog_mem.py "$EXE" "$D" "$D/memoria_${ET}.csv" $RMAX $AMIN > "$D/watchdog_${ET}.out" 2>&1 &
WD=$!
sleep 1
python3 -I $P/medir.py "$ET" "$D/${ET}_stdout.log" 14400 -- bash -c "source $P/env_operativo.sh && exec ./$EXE"
wait $WD
cat "$D/watchdog_${ET}.out"
