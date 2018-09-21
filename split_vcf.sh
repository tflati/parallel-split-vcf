#!/bin/bash

# USAGE: split_vcf.sh VCF_FILE.vcf OUTDIR
# where OUTDIR is the directory which will contain the vcf split into pieces

OUT_DIR=$2
if [ -z "$OUT_DIR" ]
then
	echo "Provide an output directory"
	exit
fi

if [ ! -d "$OUT_DIR" ]
then
	echo "Creating directory $OUT_DIR"
	mkdir "$OUT_DIR"
fi

if [ ! -f $1.gz ]
then
	echo "Creating bgzip version of input file $1"
	bgzip -c $1 > $1.gz
fi

if [ ! -f $1.gz.tbi ]
then
	echo "Creating tabix index for bgzipped input file $1.gz"
	tabix -p vcf $1.gz
fi

echo "Splitting VCF into chromosome-based files into directory $OUT_DIR"
for chrom in `grep "##" $1 | grep -v "INFO" | grep -o "ID=[^,]*" | sed 's/ID=//g'`
do
	echo "Extracting vcf-$chrom"
	tabix -h $1.gz $chrom > "$OUT_DIR"/$chrom.vcf
done
