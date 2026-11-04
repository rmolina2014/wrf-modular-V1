#!/bin/bash
# Corre secuencialmente omp1, omp10 y omp4 (20 min simulados, tope 3 h reales cada una)
P=/home/pgich/wrf-modular-V1/outputs/prueba_costo_1km; V=$P/d300/wrf_v3
for t in 1 10 4; do
  echo "== omp$t inicio $(date '+%F %T')"
  $P/etapa_env.sh $V/omp$t wrf.exe wrf $P/env_tesis_omp$t.sh 10800 34 3
  echo "== omp$t fin $(date '+%F %T')"
done
