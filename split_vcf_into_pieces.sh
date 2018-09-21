#!/bin/bash

# USAGE split_vcf_into_pieces.sh VCF_FILE.vcf OUTDIR 20000

file=$1
outdir=$2
lines=$3

if [ ! -d $outdir ]
then
	mkdir $outdir
fi

echo "Generating list of chromosomes"
cat $file | grep -v "^#" | cut -f 1 | sort | uniq > $outdir/chromosomes.txt

echo "Splitting file into pieces"
cat $file | tee >(grep "#" > $outdir/header.txt) | grep -v "#" | split -d -l $lines - "$outdir"piece-

for file in `ls "$outdir"piece*`
do
	echo "Finalizing file $file"
	mv $file $file.tmp
	cat $outdir/header.txt $file.tmp > $file
        rm $file.tmp
done
