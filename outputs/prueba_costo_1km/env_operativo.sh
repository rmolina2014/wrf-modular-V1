# Lanzamiento del operativo: cron.bash hace `source env.bash` y runWRF.bash ejecuta `time $RUN_COMMAND ./real.exe` / `./wrf.exe`
# (RUN_COMMAND vacío => binario directo; env.bash fija OMP_NUM_THREADS=12, WRF_NUM_TILES_X=1, WRF_NUM_TILES_Y=8, KMP_*, ulimit -s unlimited)
source /home/pgich/wrf-operativo/ejecutables/env.bash
