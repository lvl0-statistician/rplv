#!/bin/bash


PROGRAM_NAME="$(basename "$0")"

EXIT_SUCCESS=0
EXIT_FAILURE=1

INPUT="./data/Spread_50.graphml"
OUTPUT="./output/"
WALK_LENGTH=5
BIASES=("low_density" "high_density")



# ./main.sh $INPUT $OUTPUT $WALK_LENGTH

wls=("3" "4" "5" "6" "7")
for wl in "${wls[@]}"; do
  ./main.sh $INPUT $OUTPUT $wl
done



# radiuses=(710 1000 1450 2130)
# for bias in "${BIASES[@]}"; do
#   for radius in "${radiuses[@]}"; do
#     echo "Running with bias ${bias} and radius ${radius}"
#     ./main.sh $INPUT $OUTPUT "${bias}" "${radius}"
#   done
# done



# biases=(low_degree high_degree none)
# for bias in "${biases[@]}"; do
#   echo "Running with bias=${bias}"
#   ./main.sh $INPUT $OUTPUT "$bias" 0
# done

exit $EXIT_SUCCESS
