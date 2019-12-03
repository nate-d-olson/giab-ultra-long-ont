## Pipeline for generating HG001, HG003, and HG004 specific homozygous SV callsets and genotyping UB flowcells

## URLs and snakemake modules for downloading input ref and vcfs
from snakemake.remote.FTP import RemoteProvider as FTPRemoteProvider
FTP = FTPRemoteProvider()

v06_url = "ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data/AshkenazimTrio/analysis/NIST_SVs_Integration_v0.6/HG002_SVs_Tier1_v0.6.vcf.gz"
HG001_pbsv_url = "ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data/NA12878/analysis/PacBio_pbsv_05212019/HG001_hs37d5.pbsv.vcf.gz"
hs37d5_url = "ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/phase2_reference_assembly_sequence/hs37d5.fa.gz"

## Start of pipeline
rule all:
    input: 
        "vcfs/HG003_HG004_giab_sv_v0.6_homvar.vcf", 
        "vcfs/HG003_HG004_giab_sv_v0.6_homvar/indels.0.pdf", 
        "vcfs/HG001_pbsv_homvar.vcf",
        "vcfs/HG001_pbsv_homvar/indels.0.pdf",
        "vcfs/HG001_HG003_HG004_homvar.clustered.vcf",
        "svviz_out_FAH59421"
#         "svviz_out_FAH71622"
        

rule get_hs37d5:
    input: FTP.remote(hs37d5_url)
    output: "resources/hs37d5.fna"
    shell: "gunzip -c {input} > {output}"

rule index_ref:
    input: "resources/hs37d5.fna"
    output: "resources/hs37d5.fna.fai"
    wrapper: "0.38.0/bio/samtools/faidx"

rule bwa_index:
    input:
        "resources/hs37d5.fna"
    output:
        "resources/hs37d5.fna.amb",
        "resources/hs37d5.fna.ann",
        "resources/hs37d5.fna.bwt",
        "resources/hs37d5.fna.pac",
        "resources/hs37d5.fna.sa"
    shell: "bwa index -a bwtsw {input}"

## Download vcfs and filter homozygouns reference variant calls 
rule get_HG001_vcf: 
    input: FTP.remote(HG001_pbsv_url)
    output: "vcfs/HG001_pbsv_homvar.vcf"
    shell: """
    gunzip -c {input} \
        | grep "^#\|1/1" \
        | grep "^#\|^[1..22]" > {output}
    """

rule get_HG003_HG004_vcf:
    input: FTP.remote(v06_url)
    output: "vcfs/HG003_HG004_giab_sv_v0.6_homvar.vcf"
    shell: """
    gunzip -c {input} \
        | grep '^#\|HG003_GT=1/1;HG004_GT=0/0\|HG003_GT=0/0;HG004_GT=1/1' \
        > {output}
    """

## VCF QC using bcftools stats and plot-vcfstats   
rule vcf_stats:
    input: "vcfs/{vcfid}.vcf"
    output: "vcfs/{vcfid}/indels.0.pdf"
    params: outdir="vcfs/{vcfid}"
    shell: """
    bcftools stats {input} > {params.outdir}/stats.txt
    plot-vcfstats -P -p {params.outdir} {params.outdir}/stats.txt
    """

## Combining HG001 and HG003/H004 homozygous variant SVs.
rule cluster_vcfs: 
    input: 
        hg001="vcfs/HG001_pbsv_homvar.vcf", 
        hg003_hg004="vcfs/HG003_HG004_giab_sv_v0.6_homvar.vcf",
        ref="resources/hs37d5.fna"
    output: "vcfs/HG001_HG003_HG004_homvar.clustered.vcf"
    shell: """
    ## Cluster SVs
    ls vcfs/*vcf > fof.lst
    SVmerge --ref {input.ref} --fof fof.lst --prefix "vcfs/HG001_HG003_HG004_homvar"
    rm fof.lst
    """

## Remove variants present in both files
rule make_specific:
    input: "vcfs/HG001_HG003_HG004_homvar.clustered.vcf"
    output: "vcfs/HG001_HG003_HG004_homvar_specific.clustered.vcf"
    shell: "grep '^#\|NumClusterSVs=1' {input} > {output}"

rule compress_vcf:
    input: "vcfs/HG001_HG003_HG004_homvar.clustered.vcf"
    output: "vcfs/HG001_HG003_HG004.clustered.vcf.gz"
    shell: "bgzip --stdout {input} > {output} && tabix -p vcf {output}"

## Genotyping with svviz
rule run_svviz:
    input: 
        bam = "bams/{flowcell}_hs37d5.bam",
        vcf = "vcfs/HG001_HG003_HG004_homvar.clustered.vcf.gz",
        ref = "resources/hs37d5.fna",
        refidx = "resources/hs37d5.fna.fai",
        refbwidx = "resources/hs37d5.fna.sa"
    output: 
        outdir=directory("svviz_results/{flowcell}"),
        flag="svviz_results/{flowcell}_complete"
    conda: "envs/svviz.yaml"
    shell: """
        svviz2 -o {output.outdir} --min-mapq 20 --ref {input.ref} --variants {input.vcf} {input.bam}
        touch {output.flag}
    """

    