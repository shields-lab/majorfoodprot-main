#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Download the full human proteome (TaxID 9606) from UniProt
and save it as a FASTA file for OrthoFinder.

Output:
  query_fasta_files/Homo_sapiens.fasta
"""

import os
import argparse
import requests
import sys

UNIPROT_STREAM_URL = "https://rest.uniprot.org/uniprotkb/stream"
HUMAN_TAXID = "9606"


def parse_args():
    p = argparse.ArgumentParser(
        description="Download full human proteome FASTA from UniProt"
    )
    p.add_argument(
        "--output-dir",
        default="query_fasta_files",
        help="Directory to save the human FASTA (default: query_fasta_files)"
    )
    p.add_argument(
        "--filename",
        default="Homo_sapiens.fasta",
        help="Output FASTA filename (default: Homo_sapiens.fasta)"
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if FASTA already exists"
    )
    return p.parse_args()


def download_human_proteome(output_path):
    query = f"organism_id:{HUMAN_TAXID}"

    params = {
        "query": query,
        "format": "fasta"
    }

    print("[Human proteome] Downloading from UniProt...")
    print("  Query:", query)

    try:
        with requests.get(UNIPROT_STREAM_URL, params=params, stream=True, timeout=120) as r:
            r.raise_for_status()

            bytes_written = 0
            with open(output_path, "w") as out:
                for chunk in r.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    text = chunk.decode("utf-8")
                    out.write(text)
                    bytes_written += len(text)

    except Exception as e:
        print("[ERROR] Failed to download human proteome:", e)
        sys.exit(1)

    if bytes_written == 0:
        print("[ERROR] Downloaded file is empty!")
        sys.exit(1)

    print(f"[Human proteome] Saved to: {output_path}")
    print(f"[Human proteome] Size: {bytes_written / 1e6:.2f} MB")


def main():
    args = parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    output_path = os.path.join(args.output_dir, args.filename)

    if os.path.exists(output_path) and not args.force:
        print("[Human proteome] File already exists:")
        print(" ", output_path)
        print("  Use --force to re-download.")
        return

    download_human_proteome(output_path)


if __name__ == "__main__":
    main()
