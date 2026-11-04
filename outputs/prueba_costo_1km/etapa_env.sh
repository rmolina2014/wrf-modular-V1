#!/bin/bash
# Uso: etapa_env.sh <dir_trabajo> <ejecutable> <etiqueta> <archivo_env> <timeout_s> [rss_max_GB] [memavail_min_GB]
# Igual que etapa.sh pero con entorno y tope de tiempo elegibles.
P=/home/pgich/wrf-modular-V1/outputs/prueba_costo_1km
D=$1; EXE=$2; ET=$3; ENVF=$4; TO=$5; RMAX=${6:-34}; AMIN=${7:-3}
cd "$D" || exit 1
python3 -I $P/watchdog_mem.py "$EXE" "$D" "$D/memoria_${ET}.csv" $RMAX $AMIN > "$D/watchdog_${ET}.out" 2>&1 &
WD=$!
sleep 1
python3 -I $P/medir.py "$ET" "$D/${ET}_stdout.log" "$TO" -- bash -c "source $ENVF && exec ./$EXE"
wait $WD
cat "$D/watchdog_${ET}.out"
