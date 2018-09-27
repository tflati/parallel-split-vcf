#!/bin/bash

# USAGE: load_into_database.sh DATA_DIR NEO4J_HOME
# where NEO4J_HOME is the main base directory of neo4j (containing bin, data, config, etc.)

if [ "$#" -lt 2 ]
then
	echo "USAGE: ./load_into_database.sh DATA_DIR NEO4J_HOME"
	exit
fi

#DATA_DIR="/home/flati/data/cirilli/peach/csv_pieces_101017/"
#NEO4J_HOME="/home/flati/peach_project/neo4j-community-3.1.3"
DATA_DIR=$1
NEO4J_HOME=$2
DIR=$NEO4J_HOME"/data/databases/graph.db"

echo "Stopping neo4j"
$NEO4J_HOME/bin/neo4j stop

echo "About to remove the following files: $DIR/*"
rm -rI $DIR/*

echo "Loading data into neo4j"
#$NEO4J_HOME/bin/neo4j-import --into "$DIR" --id-type string --skip-duplicate-nodes \
#	--nodes:Chromosome `ls "$DATA_DIR"Chromosome.csv.gz | tr '\n' ','` \
#	--nodes:Sample `ls "$DATA_DIR"Sample.csv.gz | tr '\n' ','` \
#	--nodes:Variant `ls "$DATA_DIR"Variant.csv.gz | tr '\n' ','; ls "$DATA_DIR"*/Variant.csv.gz | tr '\n' ','` \
#	--nodes:VariantInfo `ls "$DATA_DIR"VariantInfo.csv.gz | tr '\n' ','; ls "$DATA_DIR"*/VariantInfo.csv.gz | tr '\n' ','` \
#   --relationships:Info `ls "$DATA_DIR"*/Info.csv.gz | tr '\n' ','` \
#    --relationships:HasVariant `ls "$DATA_DIR"*/HasVariant.csv.gz | tr '\n' ','` \
#    --relationships:SampleInfo `ls "$DATA_DIR"*/SampleInfo.csv.gz | tr '\n' ','`

$NEO4J_HOME/bin/neo4j-admin import --id-type STRING \
	--nodes:Chromosome "$DATA_DIR"Chromosome.csv.gz \
	--nodes:Sample "$DATA_DIR"Sample.csv.gz \
	--nodes:Variant "$DATA_DIR"Variant.csv.gz \
	--nodes:VariantInfo "$DATA_DIR"VariantInfo.csv.gz \
    --relationships:Info "$DATA_DIR"/Info.csv.gz \
    --relationships:HasVariant "$DATA_DIR"/HasVariant.csv.gz \
    --relationships:SampleInfo "$DATA_DIR"/SampleInfo.csv.gz

echo "Starting neo4j"
sudo $NEO4J_HOME/bin/neo4j start

echo "Getting neo4j status"
sudo $NEO4J_HOME/bin/neo4j status
