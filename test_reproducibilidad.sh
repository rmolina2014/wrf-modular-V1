#!/usr/bin/env bash
# Test de reproducibilidad (Seccion 5.6): repite los 4 casos completos (nudged y control)
# y compara campo por campo con la corrida original.
#
# Uso:   bash scripts/test_reproducibilidad.sh            # corre todo (~2 h)
#        bash scripts/test_reproducibilidad.sh --dry-run  # solo muestra los pasos
#        CASOS="1 3" bash scripts/test_reproducibilidad.sh
#
# Criterio de aceptacion FIJADO ANTES de correr: igualdad exacta (bit a bit) de T2, Q2,
# PSFC, U10 y V10 en todos los wrfout, en los dos brazos. Si hay diferencias, se informa
# la diferencia maxima y no se declara reproducible.
#
# Requisitos: ejecutar desde la raiz del repo, en la misma PC y con la misma cantidad
# de procesadores que las corridas originales (misma configuracion de MPI).
set -u
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
CASOS="${CASOS:-1 2 3 4}"
RUNS="outputs/runs"
declare -A DIRS=(
  [1]="2026-07-31_0000z/caso1_zonda"
  [2]="2026-01-01_0000z/caso2_calor"
  [3]="2026-05-16_0000z/caso3_frentefrio"
  [4]="2026-09-24_0000z/sanjuan_0924"
)
STAMP=$(date +%Y%m%d_%H%M)
OUT="outputs/reproducibilidad/$STAMP"
run() { echo "+ $*"; [ $DRY -eq 1 ] || "$@"; }

[ $DRY -eq 1 ] || mkdir -p "$OUT"
LOG="$OUT/resumen.txt"
say() { echo "$*"; [ $DRY -eq 1 ] || echo "$*" >> "$LOG"; }

say "== Test de reproducibilidad $STAMP =="
say "Equipo: $(uname -srm) | nproc=$(nproc) | git=$(git rev-parse --short HEAD)"
say "WRF run dir: ${LOCAL_WRF_DIR:-<no definido>}"
[ -n "${LOCAL_WRF_DIR:-}" ] && [ -f "$LOCAL_WRF_DIR/wrf.exe" ] && say "wrf.exe sha256: $(sha256sum "$LOCAL_WRF_DIR/wrf.exe" | cut -c1-16)"

RC=0
for N in $CASOS; do
  D="$RUNS/${DIRS[$N]}"
  say ""; say "--- Caso $N ($D) ---"
  for b in nudged control; do
    [ -d "$D/$b" ] || { say "FALTA $D/$b: no hay corrida original para comparar"; RC=1; continue 2; }
    run rm -rf "$D/${b}_orig"
    run cp -a "$D/$b" "$D/${b}_orig"
  done
  run cp -a "$D/control_manifest.json" "$D/control_manifest.json.orig"
  # forzar re-corrida del control: sin manifest no se reutiliza
  run rm -f "$D/control_manifest.json"
  T0=$(date +%s)
  run python -m src.casos.run_casos --solo "$N" --force
  say "Caso $N re-ejecutado en $(( $(date +%s) - T0 )) s"
  if [ $DRY -eq 0 ]; then
    # el manifest nuevo prueba que el control se re-corrio (su "creado" debe ser posterior al original)
    NUEVO=$(python -c "import json,sys;print(json.load(open(sys.argv[1])).get('creado',''))" "$D/control_manifest.json" 2>/dev/null)
    VIEJO=$(python -c "import json,sys;print(json.load(open(sys.argv[1])).get('creado',''))" "$D/control_manifest.json.orig" 2>/dev/null)
    if [ -z "$NUEVO" ] || [ "$NUEVO" = "$VIEJO" ]; then
      say "AVISO: el control NO se re-corrio (manifest sin cambios); el test del control no es valido"; RC=1
    else
      say "Control re-corrido (manifest creado $NUEVO)"
    fi
  fi
  for b in nudged control; do
    if [ $DRY -eq 1 ]; then echo "+ python scripts/comparar_wrfout.py $D/${b}_orig $D/$b"; continue; fi
    python scripts/comparar_wrfout.py "$D/${b}_orig" "$D/$b" | tee "$OUT/caso${N}_${b}.txt" | tail -8
    [ "${PIPESTATUS[0]}" -eq 0 ] && say "Caso $N $b: IDENTICO" || { say "Caso $N $b: HAY DIFERENCIAS"; RC=1; }
  done
  run python scripts/verifica_protocolo_temporal.py --case-dir "$D" --t0 "$(echo ${DIRS[$N]} | cut -d_ -f1)_00:00:00" \
      --wrfout-nudged "$D/nudged" --wrfout-control "$D/control"
done
say ""; [ $DRY -eq 1 ] && { echo "(dry-run: nada se ejecuto)"; exit 0; }
say "RESULTADO GLOBAL: $([ $RC -eq 0 ] && echo REPRODUCIBLE || echo 'NO CONFIRMADO')"
exit $RC
