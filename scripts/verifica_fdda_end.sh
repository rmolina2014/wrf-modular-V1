#!/usr/bin/env bash
# Verificacion del fin del nudging (Seccion 5.3 / 5.10 de la tesis; guia de Reen, 2016).
# Pregunta: con el namelist oficial (fdda_end = 720 min, sin obs_idynin), el nudging deja de actuar
# en t0? Y cuanto cambian los resultados si se usa obs_idynin = 1 con rampa de desactivacion?
#
# Variantes (no tocan los resultados oficiales; van a <caso>__<variante>):
#   diag  : namelist oficial + obs_ipf_nudob (solo imprime en el log). El nudged debe ser IDENTICO
#           al oficial y el log muestra hasta que minuto actuo el nudging.
#   rampa : obs_idynin = 1, obs_dtramp = -60 (rampa 1->0 entre t0-60 y t0; se usan las
#           observaciones de la rampa), + obs_ipf_nudob. Se compara con el oficial.
#
# Uso:   bash scripts/verifica_fdda_end.sh --dry-run
#        CASOS="3" bash scripts/verifica_fdda_end.sh           # por defecto solo el caso 3 (~80 min)
#        CASOS="1 2 3 4" VARIANTES="rampa" bash scripts/verifica_fdda_end.sh
# Requisitos: raiz del repo, misma PC y mismo numero de procesos que las corridas oficiales.
set -u
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
CASOS="${CASOS:-3}"; VARIANTES="${VARIANTES:-diag rampa}"
RUNS="outputs/runs"
declare -A DIRS=(
  [1]="2026-07-31_0000z/caso1_zonda" [2]="2026-01-01_0000z/caso2_calor"
  [3]="2026-05-16_0000z/caso3_frentefrio" [4]="2026-09-24_0000z/sanjuan_0924" )
declare -A ARGS=(
  [diag]="--obs-ipf-nudob"
  [rampa]="--obs-idynin 1 --obs-dtramp -60 --obs-ipf-nudob" )
STAMP=$(date +%Y%m%d_%H%M); OUT="outputs/verificacion_fdda/$STAMP"
run() { echo "+ $*"; [ $DRY -eq 1 ] || "$@"; }
[ $DRY -eq 1 ] || mkdir -p "$OUT"
LOG="$OUT/resumen.txt"; say() { echo "$*"; [ $DRY -eq 1 ] || echo "$*" >> "$LOG"; }
say "== Verificacion del fin del nudging $STAMP =="
say "Equipo: $(uname -srm) | nproc=$(nproc) | git=$(git rev-parse --short HEAD)"
for N in $CASOS; do
  D="$RUNS/${DIRS[$N]}"
  for V in $VARIANTES; do
    say ""; say "--- Caso $N, variante $V (${ARGS[$V]}) ---"
    T0=$(date +%s)
    run python -m src.casos.run_casos --solo "$N" --force --variante "$V" "--pipeline-args=${ARGS[$V]}"
    say "Caso $N/$V ejecutado en $(( $(date +%s) - T0 )) s"
    [ $DRY -eq 1 ] && continue
    DV="${D}__$V"
    { python scripts/analisis/revisa_rsl_nudging.py "$DV"; } 2>&1 | tee -a "$LOG"
    { python scripts/analisis/compara_variante.py "$D" "$DV"; } 2>&1 | tee "$OUT/caso${N}_${V}_comparacion.txt" | tail -40 | tee -a "$LOG"
  done
done
say ""; say "Resultados en $OUT. Interpretacion:"
say " - diag: si 'lineas con XTIME > fdda_end' = 0, fdda_end corta el nudging en t0 aun sin obs_idynin."
say "         Si hay lineas posteriores, el nudging sigue actuando (como maximo hasta t0 + obs_twindo)."
say " - diag: el nudged debe ser identico al oficial (max |dif| = 0 en todos los horizontes)."
say " - rampa: las diferencias con el oficial muestran cuanto depende el resultado de la forma de cortar el nudging."
