# parallel-split-vcf

## This package is useful for parsing VCF files and convert them into CSV for subsequent database population. 

### Usage for a single VCF file:

> ./split\_vcf\_into\_pieces.sh <PIECES\_OUT\_DIR> 20000 <VCF\_FILE.vcf>
>
> ./launch.sh <PIECES\_OUT\_DIR> <CSV\_DIR>

###  Usage for multiple VCF files:

> ./split\_vcf\_into\_pieces.sh <PIECES\_OUT\_DIR> 20000 <VCF\_FILE> [<VCF\_FILE>]
>
> ./launch.sh <PIECES\_OUT\_DIR> <CSV\_DIR> <PHENODATA.TSV>

where *PHENODATA.TSV* is a two-column tab-delimited file which associates each sample with a breed/tag/species/tissue.
Some examples:

> Sample1	Peach
>
> Sample2	Cow
>
> Sample3	Poplar

or 

> Sample1	Populus_Nigra
>
> Sample2	Populus_Nigra
>
> Sample3	Populus_Nigra
>
> Sample4	Populus_Nigra
>
> Sample5	Populus_Trichocarpa
>
> Sample6	Populus_Euphratica

To tag samples, you can use the following scripts (*extract_samples.sh* and *tag_samples.sh*) on each sample group, to tag all the samples of a given group with the same tag automatically:

> ./extract\_samples.sh <VCF\_FILE.vcf> <VCF\_FILE.vcf> <VCF\_FILE.vcf> | ./tag\_samples.sh "MY_TAG" > phenodata.tsv

For example:

> ./extract\_samples.sh ../../trichocarpa/data/*/Combined\_indels\_filt.vcf | ./tag\_samples.sh "Trichocarpa" > trichocarpa\_phenodata.tsv
>
> ./extract\_samples.sh ../../morgante/data/*/Combined\_indels\_filt.vcf | ./tag\_samples.sh "Nigra\_M" > nigram\_phenodata.tsv
>
> ./extract\_samples.sh ../../euphratica/data/*/Combined\_indels\_filt.vcf | ./tag\_samples.sh "Euphratica" > euphratica\_phenodata.tsv

and then merge the three phenodata files into a single one:

> cat \*phenodata.\* > poplar\_phenodata\_all.tsv

