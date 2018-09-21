from mpi4py import MPI
import glob
import sys
import os
import subprocess
from models import Sample, Chromosome, VariantInfo, Variant
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

if rank == 0:
    
    start_time = datetime.datetime.now()
    print("[MASTER] STARTED ({})".format(start_time))

    files = []
    files_original = []
    for file in sorted(glob.glob(INPUTDIR + "/*")):
        if os.path.basename(file) == "header.txt": continue
        if os.path.basename(file) == "chromosomes.txt": continue
        
        files.append(file)
        files_original.append(file)
        
    if not os.path.exists(BASEDIR):
        print("[MASTER] Creating output directory {}".format(BASEDIR))
        os.makedirs(BASEDIR)
    
    raw_files = {}
    csv_files = {}

    for element in [Sample, Chromosome, VariantInfo, Variant]:
        raw_file = gzip.open(BASEDIR + str(element.__name__) + ".csv.gz", "w")
        csv_file = csv.writer(raw_file)
    
        names = [name for name in element.get_names()]
        names[0] = names[0] + ":ID("+str(element.__name__)+")"
        
        if element is Variant: names[2] += ":INT"
        elif element is VariantInfo: names[1] += ":FLOAT"
        
        csv_file.writerow(names)
        
        csv_files[element] = csv_file
        raw_files[element] = raw_file
    
    # Produce file-specific information
    print("[MASTER] Generating genotype CSV...")
    with open(INPUTDIR + "header.txt", "r") as file:
        for line in file:
            
            line = line.rstrip()
            
            if line.startswith("##"): continue
            if line.startswith("#"):
                line = line[1:]
                cols = line.split("\t")
                col_names = cols[0:9]
                sample_names = cols[9:]
                
                for sample_name in sample_names:
                    genotype = Sample(ID=sample_name)
                    csv_files[Sample].writerow(genotype.get_all())
                    
    print("[MASTER] Generating chromosome CSV...")
    with open(INPUTDIR + "chromosomes.txt", "r") as file:
        for line in file:
            chromosome = line.rstrip()
            chrom = Chromosome(ID=chromosome)
            csv_files[Chromosome].writerow(chrom.get_all())
    
    for element in raw_files:
        raw_files[element].close()
    
    # Process each file independently
    while len(files) > 0:
        
        file = files.pop(0)
        
        status = MPI.Status()
        who = comm.recv(tag=FREE, status=status)
        sender = status.Get_source()
        print("[MASTER] SLAVE {} IS FREE TO DO WORK".format(sender))
        comm.send(file, dest=sender, tag=DO)
    
    for i in range(1, size):
        comm.recv(tag=FREE, source=i)
        print("[MASTER] SENDING DIE SIGNAL TO SLAVE {}".format(i))
        comm.send(file, dest=i, tag=FINISHED)
        
    # Gather statistics
    stats = {}
    for file in files_original:
        outputdir = BASEDIR + str(os.path.basename(file)).replace(".vcf", "") + "/"
        stat_filepath = outputdir + "statistics.txt"
        print("Collecting statistics from file " + stat_filepath)
        with open(stat_filepath, "r") as stat_file:
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
        
        
    end_time = datetime.datetime.now()
    print("[MASTER] FINISHED ({})".format(end_time - start_time))
    
else:
    
    comm.send(0, dest=0, tag=FREE)
    
    die = False
    while True:
        status = MPI.Status()
        data = comm.recv(source=0, status=status)
        tag = status.Get_tag()
        
        if tag == FINISHED:
            print("RANK={} IS GOING TO DIE".format(rank))
            break
        
        elif tag == DO:
            print("RANK={} will process file={}".format(rank, data))
            
            # Process input data
            outputdir = BASEDIR + str(os.path.basename(data)).replace(".vcf", "") + "/"
            command = "python main.py " + data + " " + outputdir
            print("RANK={} will execute commmand='{}'".format(rank, command))
            
            pid = subprocess.Popen(command, shell=True)
            pid.wait()
            
            # Communicate we're done
            comm.send(0, dest=0, tag=FREE)
