from mpi4py import MPI
import glob
import sys
import os
import subprocess
from models import Sample, Chromosome, VariantInfo, Variant, Info, HasVariant, SampleInfo
import csv
import gzip
import datetime

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

FREE = 0
DO = 1
FINISHED = 2

# The directory containing the pieces of the VCF file
# This directory must also contain other 2 files: header.txt and chromosome.txt
INPUTDIR = sys.argv[1]
# The output directory
BASEDIR = sys.argv[2]
# The phenodata file
PHENODATA = sys.argv[3] if len(sys.argv) > 3 else None

if rank == 0:
    
    start_time = datetime.datetime.now()
    sys.stderr.write("[MASTER] STARTED ({})\n".format(start_time))

    files = []
#     files_original = []
    for file in sorted(glob.glob(INPUTDIR + "/*/piece*")):
        #if os.path.basename(file) == "header.txt": continue
        #if os.path.basename(file) == "chromosomes.txt": continue
        
        files.append(file)
#         files_original.append(file)
        
    if not os.path.exists(BASEDIR):
        sys.stderr.write("[MASTER] Creating output directory {}\n".format(BASEDIR))
        os.makedirs(BASEDIR)
    
#     raw_files = {}
    csv_files = {}

    # Read PHENODATA file (if available)
    phenodata_map = {}
    if PHENODATA is not None:
        with open(PHENODATA, "r") as f:
            for line in f:
                sample_id, tag = line.strip().split("\t")
                phenodata_map[sample_id] = tag

    for element in [Sample, Chromosome, VariantInfo, Variant]:
        raw_file = gzip.open(BASEDIR + str(element.__name__) + ".csv.gz", "w")
        csv_file = csv.writer(raw_file)
    
        names = [name for name in element.get_names()]
        names[0] = "#" + names[0]
        
#         names[0] = names[0] + ":ID("+str(element.__name__)+")"
#         if element is Variant: names[2] += ":INT"
#         elif element is VariantInfo: names[1] += ":FLOAT"
        
        csv_file.writerow(names)
        csv_files[element] = csv_file
#         raw_files[element] = raw_file

    for element in [Info, HasVariant, SampleInfo]:
        raw_file = gzip.open(BASEDIR + str(element.__name__) + ".csv.gz", "w")
        csv_file = csv.writer(raw_file)
        node_types = [el for el in element.get_names()]
        node_types[0] = ":START_ID("+node_types[0]+")"
        node_types[1] = ":END_ID("+node_types[1]+")"
        
        csv_file.writerow(node_types)
        csv_files[element] = csv_file
                
    print("Loaded {} total phenodata".format(len(phenodata_map)))
    
    # Produce file-specific information
    print("=== Creating genotype CSV ===")
    samples_ids = set()
    sample_list = []
    for header_file in sorted(glob.glob(INPUTDIR + "/*/header.txt")):
        with open(header_file, "r") as file:
            for line in file:
                
                line = line.rstrip()
                
                if line.startswith("##"): continue
                if line.startswith("#"):
                    line = line[1:]
                    cols = line.split("\t")
                    col_names = cols[0:9]
                    sample_names = cols[9:]
                    
                    for sample_name in sample_names:
                        if sample_name in phenodata_map:
                            genotype = Sample(ID=sample_name, tag=phenodata_map[sample_name])
                        else:
                            genotype = Sample(ID=sample_name)
                        
                        if sample_name not in samples_ids:
                            samples_ids.add(sample_name)
                            sample_list.append(genotype)
    
    for sample in sample_list:                    
        csv_files[Sample].writerow(sample.get_all())
                    
    #print("[MASTER] Generating chromosome CSV...")
    with open(INPUTDIR + "chromosomes.txt", "r") as file:
        for line in file:
            chromosome = line.rstrip()
            chrom = Chromosome(ID=chromosome)
            csv_files[Chromosome].writerow(chrom.get_all())
    
#     for element in raw_files:
#         raw_files[element].close()
    
    # Process each file independently
    print("=== Converting into CSV ===")
    print("Files to analyze: {}".format(len(files)))
    finished = 0
    total = len(files)
    i = 0
    while len(files) > 0:
         
        input_file = files.pop(0)
        out_file = BASEDIR + "pieces/" + str(i) + "/"
        if not os.path.exists(out_file):
            os.makedirs(out_file)
         
        i += 1
         
        status = MPI.Status()
        data = comm.recv(tag=FREE, status=status)
         
        if data is not None:
            finished += 1
            percentage = int(100*float(finished)/total)
            sys.stderr.write("[{}{}] {}%\r".format("="*percentage, " "*(100-percentage), percentage))
         
        sender = status.Get_source()
        #print("[MASTER] SLAVE {} IS FREE TO DO WORK".format(sender))
        comm.send([input_file, out_file], dest=sender, tag=DO)
     
    for i in range(1, size):
        comm.recv(tag=FREE, source=i)
     
        finished += 1
        percentage = int(100*float(finished)/total)
        sys.stderr.write("[{}{}] {}%\r".format("="*percentage, " "*(100-percentage), percentage))
             
        #print("[MASTER] SENDING DIE SIGNAL TO SLAVE {}".format(i))
        comm.send(None, dest=i, tag=FINISHED)
        
    # Join all subfiles
    print("\n=== Merging files ===")
    all_dirs = glob.glob(BASEDIR + "pieces/*")
    n = len(all_dirs)
    i = 0
    for output_directory in all_dirs:
        
        i += 1
        percentage = int(100*float(i)/n)
        sys.stderr.write("[{}{}] {}%\r".format("="*percentage, " "*(100-percentage), percentage))
        
        for element in [Info, HasVariant, SampleInfo, VariantInfo, Variant]:
            piece = output_directory + "/" + str(element.__name__) + ".csv.gz"
            #print("Reading piece file="+piece)
            with gzip.open(piece, "r") as f:
                reader = csv.reader(f)
                for line in reader:
                    if line[0].startswith("#"): continue
                    csv_files[element].writerow(line)
    
    sys.stderr.flush()
    
    # Gather statistics
    print("\n=== Gathering statistics ===")
    stats = {}
    i = 0
    for outputdir in all_dirs:
        
        i += 1
        percentage = int(100*float(i)/n)
        sys.stderr.write("[{}{}] {}%\r".format("="*percentage, " "*(100-percentage), percentage))
        
        #print("Collecting statistics from file " + stat_filepath)
        with open(outputdir + "/statistics.txt", "r") as stat_file:
            for line in stat_file:
                pieces = line.split("\t")
                ID, key, value = pieces[0], pieces[1], pieces[2]
                if ID not in stats:
                    stats[ID] = {}
                if key not in stats[ID]:
                    stats[ID][key] = 0
                
                try:
                    v = int(value)
                except ValueError:
                    v = float(value)
                
                stats[ID][key] += v
    
    final_stat_filepath = BASEDIR + "statistics.txt"
    writer = open(final_stat_filepath, "w")
    for ID in stats:
        for key in stats[ID]:
            writer.write(ID +"\t" + key + "\t" + str(stats[ID][key]) + "\n")
    writer.close()
    sys.stderr.flush()
        
    end_time = datetime.datetime.now()
    sys.stderr.write("\n[MASTER] FINISHED ({})\n".format(end_time - start_time))
    
else:
    
    comm.send(None, dest=0, tag=FREE)
    
    die = False
    while True:
        status = MPI.Status()
        data = comm.recv(source=0, status=status)
        tag = status.Get_tag()
        
        if tag == FINISHED:
            #print("RANK={} IS GOING TO DIE".format(rank))
            break
        
        elif tag == DO:
            #print("RANK={} will process file={}".format(rank, data))
            
            # Process input data
#             outputdir = BASEDIR + str(os.path.basename(data)).replace(".vcf", "") + "/"
#             command = "python converter.py " + data + " " + outputdir
            command = "python converter.py " + " ".join(data)
            #print("RANK={} will execute commmand='{}'".format(rank, command))
            
            pid = subprocess.Popen(command, shell=True)
            pid.wait()
            
            # Communicate we're done
            comm.send(data, dest=0, tag=FREE)
