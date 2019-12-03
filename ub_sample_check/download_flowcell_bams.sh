#!/usr/bin/bash

# for i in FAH71622 FAH86841 FAH87405 FAJ04298 FAH86787 FAH86477 FAH87395 FAH86902 FAH59421; do
for i in FAH86841 FAH87405 FAJ04298 FAH86787 FAH86477 FAH87395 FAH86902; do
    bamroot=/scratch/groups/msalit/nanopore/processing/guppy-3.2.4-snakemake-pipe/bams/${i}_hs37d5.bam
    rsync sherlock:${bamroot}.bai bams/ &
    rsync -v --numeric-ids --progress \
        -e "ssh -T -c aes128-cbc -o Compression=yes -x" \
        sherlock:${bamroot} bams/
    done
    