grep "#CHROM" "$@" | cut -f 10- | tr '\t' '\n'
