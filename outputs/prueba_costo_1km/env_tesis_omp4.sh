# Lanzamiento de la tesis (env_tesis.sh) con OMP_NUM_THREADS=4 y tiles 1x4
source /home/pgich/wrf-modular-V1/outputs/prueba_costo_1km/env_tesis.sh
export OMP_NUM_THREADS=4 WRF_NUM_TILES_X=1 WRF_NUM_TILES_Y=4
