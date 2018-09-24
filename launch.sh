#!/bin/bash

# USAGE: launch.sh PIECES_DIR CSV_DIR
# Given the directory with the VCF pieces, this script creates the corresponding CSV files.

#INPUT_DIR="~/Downloads/peach/out/"
#OUTPUT_DIR="~/Downloads/peach/csv/"
INPUT_DIR=$1
OUTPUT_DIR=$2
PHENODATA_FILE=$3
CORES="4"

time mpirun -np $CORES python ./parallel_converter.py "$INPUT_DIR" "$OUTPUT_DIR" "$PHENODATA_FILE"
