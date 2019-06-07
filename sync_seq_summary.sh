## Sync Seq Summary files
rsync -rvm \
	--include="*/" --include="*sequencing_summary.txt" --exclude="*" \
	sherlock:/scratch/groups/msalit/nanopore/raw/ \
	fastq/
