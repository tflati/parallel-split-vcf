#!/bin/bash

DATA_DIR="/home/flati/data/cirilli/peach/csv_pieces_all/"
NEO4J_HOME="/home/flati/peach_project/neo4j-community-3.1.3"
DIR=$NEO4J_HOME"/data/databases/graph.db"

echo "Stopping neo4j"
$NEO4J_HOME/bin/neo4j stop

echo "About to remove the following files: $DIR/*"
rm -rI $DIR/*

echo "Loading data into neo4j"
$NEO4J_HOME/bin/neo4j-import --into "$DIR" --id-type string --skip-duplicate-nodes \
	--nodes:Chromosome `ls "$DATA_DIR"Chromosome.csv.gz | tr '\n' ','` \
	--nodes:Sample `ls "$DATA_DIR"Sample.csv.gz | tr '\n' ','` \
	--nodes:Variant `ls "$DATA_DIR"/*/Variant.csv.gz | tr '\n' ','` \
	--nodes:VariantInfo `ls "$DATA_DIR"/*/VariantInfo.csv.gz | tr '\n' ','` \
        --relationships:Info `ls "$DATA_DIR"/*/Info.csv.gz | tr '\n' ','` \
        --relationships:HasVariant `ls "$DATA_DIR"/*/HasVariant.csv.gz | tr '\n' ','` \
        --relationships:SampleInfo `ls "$DATA_DIR"/*/SampleInfo.csv.gz | tr '\n' ','`

echo "Starting neo4j"
$NEO4J_HOME/bin/neo4j start

echo "Getting neo4j status"
$NEO4J_HOME/bin/neo4j status
