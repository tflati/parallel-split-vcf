#!/bin/bash

#INPUT_DIR="~/Downloads/peach/out/"
#OUTPUT_DIR="~/Downloads/peach/csv/"
INPUT_DIR=$1
OUTPUT_DIR=$2
CORES="4"

time mpirun -np $CORES python parallel_loader.py "$INPUT_DIR" "$OUTPUT_DIR"
