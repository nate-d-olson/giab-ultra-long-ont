#!/usr/bin/bash

## Sync Stat files
rsync -rvm --delete \
	--include="*/" --include="*stats.tsv.gz" --exclude="*" \
	sherlock:/scratch/groups/msalit/nanopore/raw/ stats/
