#!/bin/bash

DATA_DIR="/home/flati/Downloads/peach/csv_pieces4/"
DIR="data/databases/graph.db"

echo "Stopping neo4j"
bin/neo4j stop

echo "About to remove the following files: $DIR/*"
rm -rI $DIR/*

echo "Loading data into neo4j"
bin/neo4j-import --into "$DIR" --id-type string --skip-duplicate-nodes \
	--nodes:Chromosome `ls "$DATA_DIR"Chromosome.csv.gz | tr '\n' ','` \
	--nodes:Genotype `ls "$DATA_DIR"Genotype.csv.gz | tr '\n' ','` \
	--nodes:Variant `ls "$DATA_DIR"/*/Variant.csv.gz | tr '\n' ','` \
	--nodes:VariantInfo `ls "$DATA_DIR"/*/VariantInfo.csv.gz | tr '\n' ','` \
	--nodes:GenotypeInfo `ls "$DATA_DIR"/*/GenotypeInfo.csv.gz | tr '\n' ','` \
        --relationships:Info `ls "$DATA_DIR"/*/Info.csv.gz | tr '\n' ','` \
        --relationships:HasVariant `ls "$DATA_DIR"/*/HasVariant.csv.gz | tr '\n' ','` \
        --relationships:GenoInfo `ls "$DATA_DIR"/*/GenoInfo.csv.gz | tr '\n' ','` \
        --relationships:HasInfo `ls "$DATA_DIR"/*/HasInfo.csv.gz | tr '\n' ','`

echo "Starting neo4j"
bin/neo4j start

echo "Getting neo4j status"
bin/neo4j status
