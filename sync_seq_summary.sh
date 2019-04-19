## Sync Seq Summary files
rsync -rvm \
	--include="*/" --include="*sequencing_summary.txt" --exclude="*" \
	sherlock:/oak/stanford/groups/msalit/nspies/nanopore/raw/ \
	fastq/
