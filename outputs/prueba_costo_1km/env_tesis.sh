# Entorno idéntico al de WRFRunner.ejecutar_comando_seguro (src/modelo/wrf_runner.py:63-67)
export LD_LIBRARY_PATH=''
unset OMP_NUM_THREADS OMP_STACKSIZE KMP_STACKSIZE 2>/dev/null || true
source /home/pgich/wrf-operativo/ejecutables/env.bash
export OMP_NUM_THREADS=1 WRF_NUM_TILES_X=1 WRF_NUM_TILES_Y=1
