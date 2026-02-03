#!/bin/bash
# set -e
PROGRAM_NAME="$(basename "$0")"

EXIT_SUCCESS=0
EXIT_FAILURE=1

# helper
slugify() {
  sed -E 's/[^A-Za-z0-9._-]+/_/g' <<<"$1"
}

# positional arguments
INPUT_GRAPH="$1"
OUTPUT_DIR="$2" #./output
WALK_LENGTH="$3"
BIAS="${4:-none}"
RADIUS="${5:-0}"

# config
EPS=0.1
DELTA=0.01
METRIC="cos"
N_EXP=250



if [ ! -d "$OUTPUT_DIR" ]; then
  mkdir -p "$OUTPUT_DIR"
fi

graph_base=$(basename "$INPUT_GRAPH")
graph_base="${graph_base%.*}"
graph_base=$(slugify "$graph_base")
bias=$(slugify "$BIAS")
time_stamp=$(date -u +%Y%m%d-%H%M%SZ)

OUTPUT_DIR="$2" #./output
run_dir="${graph_base}_bias-${bias}_radius-${RADIUS}_wl-${WALK_LENGTH}_nexp-${N_EXP}_${time_stamp}"
output_dir="${OUTPUT_DIR}${run_dir}"
if [ ! -d "$output_dir" ]; then
  mkdir -p "${output_dir}"
fi

output_vuln="impact_${run_dir}.csv"
output_vuln="${output_dir}/${output_vuln}"
SECONDS=0
python3 ./run_vuln.py \
  --input-graph "$INPUT_GRAPH" \
  --output "$output_vuln" \
  --bias "$BIAS" \
  --radius "$RADIUS" \
  --walk-length "$WALK_LENGTH" \
  --epsilon "$EPS" \
  --delta "$DELTA" \
  --n-exp "$N_EXP"
duration=$SECONDS


lcc="lcc_${run_dir}.csv"
output_lcc="${output_dir}/${lcc}"

scores="scores_${run_dir}.csv"
output_scores="$output_dir/${scores}"

params="params_${run_dir}.csv"
output_params="$output_dir/${params}"

python3 ./run_reach.py \
  --input-graph "$INPUT_GRAPH" \
  --input-data "$output_vuln" \
  --output-lcc $output_lcc \
  --output-scores $output_scores \
  --output-params $output_params
{
  echo "timestamp: $time_stamp"
  echo "input_graph: $INPUT_GRAPH"
  echo "bias: $BIAS"
  echo "radius: $RADIUS"
  echo "walk_length: $WALK_LENGTH"
  echo "epsilon: $EPS"
  echo "delta: $DELTA"
  echo "duration: $duration"
  echo "cmd: python3 ./run_vuln.py --input-graph \"$INPUT_GRAPH\" --output \"$run_dir\" --bias \"$BIAS\" --walk-length \"$WALK_LENGTH\" --epsilon \"$EPS\" --delta \"$DELTA\""
} > "${output_dir}/log.yaml"

exit $EXIT_SUCCESS
