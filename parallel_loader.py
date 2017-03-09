from mpi4py import MPI
import glob
import sys
import os
import subprocess

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

FREE = 0
DO = 1
FINISHED = 2

INPUTDIR = sys.argv[1]
BASEDIR = sys.argv[2]

if rank == 0:
    files = glob.glob(INPUTDIR + "/*")
    
    if not os.path.exists(BASEDIR):
        print("Creating output directory {}".format(BASEDIR))
        os.makedirs(BASEDIR)
    
    while len(files) > 0:
        
        file = files.pop(0)
        
        status = MPI.Status()
        who = comm.recv(tag=FREE, status=status)
        sender = status.Get_source()
        print("[MASTER] SLAVE {} IS FREE TO DO WORK".format(sender))
        comm.send(file, dest=sender, tag=DO)
    
    for i in range(1, size):
        print("[MASTER] SENDING DIE SIGNAL TO SLAVE {}".format(i))
        comm.send(file, dest=i, tag=FINISHED)
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
