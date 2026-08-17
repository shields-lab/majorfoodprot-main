#!/bin/bash

BASE_DIR="output_foodDB/orthofinder_runs"
OUT_DIR="blast_fasta_files"

# Create output directory if it doesn't exist
mkdir -p "$OUT_DIR"

# Loop through each subdirectory
for dir in "$BASE_DIR"/*/; do
    # Get folder name (species name)
    species=$(basename "$dir")

    # Loop through fasta files excluding Homo_sapiens.fa
    for fasta in "$dir"/*.fa; do
        filename=$(basename "$fasta")

        if [[ "$filename" != "Homo_sapiens.fa" ]]; then
            cp "$fasta" "$OUT_DIR/${species}_${filename}"
        fi
    done
done

echo "Done. Files copied to $OUT_DIR"
