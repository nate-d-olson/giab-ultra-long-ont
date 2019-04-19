#!/usr/bin/bash

## Sync Stat files
rsync -rvm \
	--include="*/" --include="*stats.tsv.gz" --exclude="*" \
	sherlock:/scratch/groups/msalit/nanopore/raw/ \
	~/Projects/giab-ultra-long-ont/stats/
