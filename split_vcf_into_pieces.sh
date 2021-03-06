#!/bin/bash

# USAGE ./split_vcf_into_pieces.sh OUTDIR 20000 <VCF_FILE.vcf> [<VCF_FILE.vcf>]
# Splits the input file in multiple smaller files (each made of maximum XXX lines)

outdir=$1
lines=$2
shift
shift

if [ ! -d "$outdir" ]
then
	mkdir "$outdir"
fi


echo "Analyzing $# VCF files"

echo "Generating list of chromosomes"
for file in "$@"
do
	cat "$file" | cut -f 1 | grep -v "^#"
done | sort | uniq > $outdir/chromosomes.txt

echo "Splitting file into pieces"
for file in "$@"
do
	echo "Splitting file $file"
	simple=`basename "$file"`
	if [ ! -d "$outdir/$simple" ]
	then
		mkdir "$outdir/$simple"
	fi
	
	cat "$file" | tee >(grep "#" > "$outdir/$simple/header.txt") | grep -v "#" | split -d -l $lines - "$outdir/$simple/piece-"
done

find $outdir -name "header.txt" | xargs bash -c 'grep "#CHROM" | cut -f 10- | tr "\t" "\n"'

find "$outdir" -type f -name "piece*" -exec sh -c '
	file="$0"
	simple=`dirname "$file"`
	echo "Finalizing file $file (dir=$simple)"
	mv "$file" "$file.tmp"
	cat "$simple/header.txt" "$file.tmp" > "$file"
	rm "$file.tmp"
' {} ';'

# find "$outdir" -name "header.txt" -print0 | xargs -0 rm
