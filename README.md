# parallel-split-vcf

## This package is useful for parsing VCF files and convert them into CSV for subsequent database population. 

### Usage for a single VCF file:

> ./split\_vcf\_into_pieces.sh <VCF\_FILE.vcf> <PIECES\_OUT\_DIR> 20000
>
> ./launch.sh <PIECES\_OUT\_DIR> <CSV\_DIR>

###  Usage for multiple VCF files:

> ./split_vcf_into_pieces.sh <VCF\_FILE> [<VCF\_FILE>] <PIECES\_OUT\_DIR> 20000
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