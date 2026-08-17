#!/bin/bash
#SBATCH --job-name=fooddb_orthofinder_turkey
#SBATCH --output=fooddb_orthofinder_turkey.out
#SBATCH --error=fooddb_orthofinder_turkey.err
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH -t 7-00:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=marina.villacampafernandez@ucd.ie

set -euo pipefail

# Optional: if your cluster uses modules, uncomment/adapt:
# module load blast+/2.14.1
# module load orthofinder
# module load diamond

python run_fooddb_orthofinder_prefilter_blast_adapted_single_species.py \
  --input Food_peptide_database-input.csv \
  --human-proteome query_fasta_files/Homo_sapiens.fasta \
  --query-dir query_fasta_files/ \
  --out Food_peptide_database-output_turkey_prefiltered.csv \
  --output-root output_foodDB_turkey \
  --threads 8 \
  --search-program blast \
  --only-taxid 9103
