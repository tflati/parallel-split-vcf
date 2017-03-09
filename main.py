from models import Variant, VariantInfo, Genotype, GenotypeInfo, Chromosome, Info, GenoInfo, HasInfo, HasVariant
import csv
import gzip
import datetime
import sys
import os
from sortedcontainers import SortedSet

start_time = datetime.datetime.now()
print("STARTED ({})".format(start_time))

filename = sys.argv[1]
basedir = sys.argv[2]

if not os.path.exists(basedir):
	os.makedirs(basedir)

max_items = -1
items_loaded = 0
STEP = 1000

raw_files = {}
csv_files = {}

# "variants", "variant_infos", "genotypes", "genotype_infos", "chromosomes"
for element in [Variant, VariantInfo, GenotypeInfo, Genotype, Chromosome]:
	raw_file = gzip.open(basedir + str(element.__name__) + ".csv.gz", "w")
	csv_file = csv.writer(raw_file)
# 	names = [name for name in element.get_names()]
# 	names[0] = "#" + names[0]
	names = element.get_names()
	csv_file.writerow(names);
	csv_files[element] = csv_file
	raw_files[element] = raw_file
	
for element in [Info, GenoInfo, HasInfo, HasVariant]:
	raw_file = gzip.open(basedir + str(element.__name__) + ".csv.gz", "w")
	csv_file = csv.writer(raw_file)
	node_types = element.get_names()
	csv_file.writerow([":START_ID("+node_types[0]+")", ":END_ID("+node_types[1]+")"]);
	csv_files[element] = csv_file
	raw_files[element] = raw_file

# chromosomes = SortedSet()

# vcf_reader = vcf.Reader(open(filename, 'r'))
# for record in vcf_reader:
sample_names = []
col_names = []
with open(filename, "r") as file:
	for line in file:
		
		line = line.rstrip()
		
		if line.startswith("##"): continue
		if line.startswith("#"):
			line = line[1:]
			cols = line.split("\t")
			col_names = cols[0:9]
			sample_names = cols[9:]
			
			for sample_name in sample_names:
				genotype = Genotype(id=sample_name)
				csv_files[Genotype].writerow(genotype.get_all())
			
			continue
		
		if max_items >= 0 and items_loaded > max_items:
			break
		
		fields = line.split("\t")
		chrom = fields[col_names.index("CHROM")]
		pos = fields[col_names.index("POS")]
		id = fields[col_names.index("ID")]
		ref = fields[col_names.index("REF")]
		alt = fields[col_names.index("ALT")]
		qual = fields[col_names.index("QUAL")]
		filter = fields[col_names.index("FILTER")]
		info = fields[col_names.index("INFO")]
		format = fields[col_names.index("FORMAT")]
		samples = fields[9:]
		
# 	 	chromosomes.add(chrom)

		variant = Variant(id="#".join([chrom, pos, ref, alt]), chrom=chrom, pos=pos, ref=ref, alt=alt)
		variant_info = VariantInfo(id=chrom+"#"+str(items_loaded), qual=qual, filter=filter, info=info, format=format)
		
		# Nodes
		csv_files[Variant].writerow(variant.get_all())
		csv_files[VariantInfo].writerow(variant_info.get_all())
		
		# Edges
		csv_files[HasVariant].writerow([chrom, variant.id])		
		csv_files[Info].writerow([variant.id, variant_info.id])
		
		# Genotype handling
		for index, sample in enumerate(samples):
			genotype_info = GenotypeInfo(id=sample)

			# Node
			csv_files[GenotypeInfo].writerow(genotype_info.get_all())
						
			# Edges
			csv_files[GenoInfo].writerow([variant_info.id, genotype_info.id])
			csv_files[HasInfo].writerow([genotype_info.id, sample_names[index]])

		items_loaded += 1
		
		if items_loaded % STEP == 0:
			print("Loaded {} items [time: {}]".format(items_loaded, datetime.datetime.now()))

# for chromosome in chromosomes:
# 	chrom = Chromosome(id=chromosome)
# 	csv_files[Chromosome].writerow(chrom.get_all())
	
for element in raw_files:
	raw_files[element].close()
	
end_time = datetime.datetime.now()
print("FINISHED ({})".format(end_time))
print("STARTED ({})".format(start_time))
print("================================================")
print("TOTAL TIME ({})".format(end_time - start_time))

