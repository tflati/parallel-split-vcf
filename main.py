from models import Variant, VariantInfo, Info, HasVariant, SampleInfo
import json
import csv
import gzip
import datetime
import sys
import os
from sortedcontainers import SortedSet

start_time = datetime.datetime.now()

# The input VCF file 
filename = sys.argv[1]

# The output directory where to store the CSV files
basedir = sys.argv[2]

simple_name = os.path.basename(filename)

print("[{}] STARTED ({})".format(simple_name, start_time))

if not os.path.exists(basedir):
	os.makedirs(basedir)

max_items = -1
items_loaded = 0
STEP = 10000

raw_files = {}
csv_files = {}

# "variants", "variant_infos", "genotypes", "genotype_infos", "chromosomes"
for element in [Variant, VariantInfo]:
	raw_file = gzip.open(basedir + str(element.__name__) + ".csv.gz", "w")
	csv_file = csv.writer(raw_file)
 	
	csv_files[element] = csv_file
	raw_files[element] = raw_file
	
for element in [Info, HasVariant, SampleInfo]:
	raw_file = gzip.open(basedir + str(element.__name__) + ".csv.gz", "w")
	csv_file = csv.writer(raw_file)
	node_types = [el for el in element.get_names()]
	node_types[0] = ":START_ID("+node_types[0]+")"
	node_types[1] = ":END_ID("+node_types[1]+")"
	
	csv_file.writerow(node_types)
	csv_files[element] = csv_file
	raw_files[element] = raw_file

statistics = {}
TOTAL_SNPS = "TOTAL_SNPS"
TOTAL_INDELS = "TOTAL_INDELS"
SNPS_PER_SAMPLE = "SNPS_PER_SAMPLE"
INDELS_PER_SAMPLE = "INDELS_PER_SAMPLE"
VARIANTS_PER_SAMPLE = "VARIANTS_PER_SAMPLE"
IDS = [TOTAL_SNPS, TOTAL_INDELS, SNPS_PER_SAMPLE, INDELS_PER_SAMPLE, VARIANTS_PER_SAMPLE]
for ID in IDS:
	statistics[ID] = {}

totalSampleInfoEdges = sampleInfoEdgesSkipped = 0

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
		format = fields[col_names.index("FORMAT")].split(":")
		samples = fields[9:]
		
		# Handling INFO information
		# e.g., AC=8;AF=1;AN=8;DP=130;ExcessHet=3.0103;FS=0;MLEAC=8;MLEAF=1;MQ=37.36;QD=25.82;SOR=0.743;NM=3;LM=VS_FB_GA;ANN=GA|intergenic_region|MODIFIER|Prupe.1G000100|Prupe.1G000100_v2.0.a1|intergenic_region|Prupe.1G000100_v2.0.a1|||n.1575_1576insA||||||
		info_dict = {}
		for subi in info.split(";"):
			if "=" in subi:
				key, value = subi.split("=")
				info_dict[key] = value
		
		# Detect type
		type = "SNP"
		if len(ref) > 1:
			type = "INDEL"
		for a in alt.split(","):
			if len(a) > 1:
				type = "INDEL"
		
		if "snps" not in statistics[TOTAL_SNPS]:
			statistics[TOTAL_SNPS]["snps"] = 0
		if "indels" not in statistics[TOTAL_INDELS]:
			statistics[TOTAL_INDELS]["indels"] = 0
			
		if type == "SNP":
			statistics[TOTAL_SNPS]["snps"] += 1
		elif type == "INDEL":
			statistics[TOTAL_INDELS]["indels"] += 1
		
		variant = Variant(ID="#".join([chrom, pos, ref, alt]), chrom=chrom, pos=pos, ref=ref, alt=alt, type=type)
		variant_info = VariantInfo(ID=chrom+"#"+pos+"#"+str(items_loaded), qual=qual, filter=filter, info=json.dumps(info_dict), format=":".join(format))
		
		# Nodes
		csv_files[Variant].writerow(variant.get_all())
		csv_files[VariantInfo].writerow(variant_info.get_all())
		
		# Edges
		csv_files[HasVariant].writerow([chrom, variant.ID])
		csv_files[Info].writerow([variant.ID, variant_info.ID])
		
		# Genotype handling
		for index, sample in enumerate(samples):
			
			# Build this sample's information
			sampleInfo = dict(zip(format, sample.split(":")))
			sampleID = sample_names[index]
			
			# Filtering edges
			if sampleInfo["GT"] == "0/0" or sampleInfo["GT"] == "./.":
				sampleInfoEdgesSkipped += 1
				continue
			
			csv_files[SampleInfo].writerow([variant_info.ID, sampleID, json.dumps(sampleInfo)])
			totalSampleInfoEdges += 1
			
			if type == "SNP":
				if sampleID not in statistics[SNPS_PER_SAMPLE]:
					statistics[SNPS_PER_SAMPLE][sampleID] = 0
				statistics[SNPS_PER_SAMPLE][sampleID] += 1
			elif type == "INDEL":
				if sampleID not in statistics[INDELS_PER_SAMPLE]:
					statistics[INDELS_PER_SAMPLE][sampleID] = 0
				statistics[INDELS_PER_SAMPLE][sampleID] += 1
			
			if sampleID not in statistics[VARIANTS_PER_SAMPLE]:
				statistics[VARIANTS_PER_SAMPLE][sampleID] = 0
			statistics[VARIANTS_PER_SAMPLE][sampleID] += 1
			
		items_loaded += 1
		
		if items_loaded % STEP == 0:
			print("[{}] Loaded {} items [time: {}]".format(simple_name, items_loaded, datetime.datetime.now()))

final_stat_filepath = basedir + "statistics.txt"
print("[{}] Opening statistics file in write mode: {}".format(simple_name, final_stat_filepath))
writer = open(final_stat_filepath, "w")
for ID in statistics:
	for key in statistics[ID]:
		writer.write(ID +"\t" + key + "\t" + str(statistics[ID][key]) + "\n")
writer.flush()
writer.close()
print("[{}] Statistics file {} closed.".format(simple_name, final_stat_filepath))

for element in raw_files:
	raw_files[element].close()

print("[{}] totalSampleInfoEdges={} sampleInfoEdgesSkipped={} ({})".format(simple_name, totalSampleInfoEdges, sampleInfoEdgesSkipped, float(sampleInfoEdgesSkipped)/(totalSampleInfoEdges+sampleInfoEdgesSkipped)))
	
end_time = datetime.datetime.now()
print("[{}] FINISHED ({})".format(simple_name, end_time))
print("[{}] STARTED ({})".format(simple_name, start_time))
print("================================================")
print("[{}] TOTAL TIME ({})".format(simple_name, end_time - start_time))

