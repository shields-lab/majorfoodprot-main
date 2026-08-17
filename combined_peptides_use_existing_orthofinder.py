#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
combined_peptides_use_existing_orthofinder.py

Rebuild the food peptide database table using UniProt (TaxID + keywords),
and attach ortholog information from an EXISTING OrthoFinder run.

IMPORTANT:
- This script does *not* run OrthoFinder.
- It expects that OrthoFinder has already been run for each species/taxid.
- It reads *_QUERY.tsv files from the OrthoFinder "Orthologues" folders.

OrthoFinder folder layout assumed:

    <ORTHOFINDER_BASE>/
        <safe_species1>_<taxid1>/
            OrthoFinder/
                <some_run_dir_1>/
                    Orthologues/
                        something_QUERY.tsv
        <safe_species2>_<taxid2>/
            OrthoFinder/
                <some_run_dir_2>/
                    Orthologues/
                        something_QUERY.tsv
        ...

Where <safe_species> is created by removing non-alphanumeric characters
from the species name (same logic as in the original pipeline).

You can control the top-level OrthoFinder folder with the
    --orthofinder-base
argument (see parse_args() below).
"""

import os
import re
import math
import time
import argparse
from math import isnan

import requests
import pandas as pd


# ---------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        description="Rebuild UniProt-based food peptide DB and attach orthologs from EXISTING OrthoFinder results."
    )
    p.add_argument(
        "--input",
        required=True,
        help="Input CSV (e.g. Food_peptide_database-input.csv)"
    )
    p.add_argument(
        "--base-output",
        default="food_db_output",
        help="Base output folder (default: food_db_output)"
    )
    p.add_argument(
        "--orthofinder-base",
        default=None,
        help=(
            "Folder that contains all OrthoFinder run subfolders. "
            "If omitted, defaults to <base-output>/orthofinder_runs.\n\n"
            "This is the main place to change if your OrthoFinder results "
            "live somewhere else (e.g. a shared cluster directory)."
        )
    )
    return p.parse_args()


# ---------------------------------------------------------------------
# Helper functions (from original notebook / cluster script)
# ---------------------------------------------------------------------

def get_taxonomy_id_string(row):
    """Clean Taxonomy ID into a string like '4565'."""
    candidates = ["Taxonomy ID", "Taxonomy id", "Taxonomy Id"]
    tax_value = None
    for c in candidates:
        if c in row.index:
            tax_value = row[c]
            break

    if tax_value is None or (isinstance(tax_value, float) and math.isnan(tax_value)):
        return ""

    if isinstance(tax_value, (int, float)):
        return str(int(tax_value))

    s = str(tax_value).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s


def has_query_fasta(row):
    possible_cols = [
        "Query fasta",
        "Query Fasta",
        "Query fasta file",
        "Query FASTA",
        "Query fasta and Uniprot keywords",
        "Query fasta and  Uniprot keywords"
    ]
    for col in possible_cols:
        if col in row.index:
            val = row[col]
            if pd.notna(val) and str(val).strip():
                return True
    return False


def get_uniprot_keywords_list(row):
    possible_cols = [
        "Uniprot keywords",
        "Uniprot Keywords",
        "Uniprot Key",
        "Uniprot key",
        "Uniprot Keys",
        "Query fasta and Uniprot keywords",
        "Query fasta and  Uniprot keywords"
    ]

    text = ""
    for col in possible_cols:
        if col in row.index:
            val = row[col]
            if pd.notna(val) and str(val).strip():
                text = str(val).strip()
                break

    if not text:
        return []

    parts = re.split(r"[;,]", text)
    return [p.strip() for p in parts if p.strip()]


def get_species_name(row):
    for c in ["Species name", "Species Name"]:
        if c in row.index and pd.notna(row[c]):
            return str(row[c]).strip()
    return ""


def make_species_filename(species_name, tax_id):
    # Kept for completeness, though we don't use it in this script.
    if species_name:
        s = "".join(ch for ch in species_name if ch.isalnum())
        if s:
            return f"{s}.fasta"
    return f"tax{tax_id}.fasta"


def clean_taxid(val):
    if val is None:
        return ""
    if isinstance(val, (int, float)):
        if isinstance(val, float) and isnan(val):
            return ""
        return str(int(val))
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s


def safe_species_name(species, tax_id):
    # This MUST match the naming used when creating OrthoFinder run directories
    s = "".join(ch for ch in species if ch.isalnum()) or f"tax{tax_id}"
    return s


# ---------------------------------------------------------------------
# UniProt helpers
# ---------------------------------------------------------------------

UNIPROT_STREAM_URL = "https://rest.uniprot.org/uniprotkb/stream"
UNIPROT_JSON_URL = "https://rest.uniprot.org/uniprotkb/stream"


def fetch_proteins_for_keyword(tax_id, keyword, max_results=200):
    """
    Get UniProt entries for:
        (organism_id:tax_id) AND ("keyword")
    Returns list of dicts.
    """
    if not tax_id or not keyword:
        return []

    query = f'(organism_id:{tax_id}) AND ("{keyword}")'

    params = {
        "query": query,
        "format": "json",
        "fields": "accession,id,protein_name,gene_names,sequence,length,organism_name"
    }

    try:
        r = requests.get(UNIPROT_JSON_URL, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[UniProt] Request failed for query: {query}")
        print("Error:", e)
        return []

    results = []

    for i, res in enumerate(data.get("results", [])):
        if i >= max_results:
            break

        acc = res.get("primaryAccession")
        entry_name = res.get("uniProtkbId")

        # Protein name
        protein_name = None
        desc = res.get("proteinDescription", {})
        rec = desc.get("recommendedName", {})
        full = rec.get("fullName")
        if isinstance(full, dict):
            protein_name = full.get("value")
        elif isinstance(full, str):
            protein_name = full

        # Gene name (first gene)
        gene_name = None
        for g in res.get("genes", []):
            gname = g.get("geneName")
            if isinstance(gname, dict) and gname.get("value"):
                gene_name = gname["value"]
                break

        # Sequence + length
        seq_info = res.get("sequence", {})
        seq = seq_info.get("value", "")
        length = seq_info.get("length", len(seq) if seq else None)

        # Organism
        org_name = ""
        org = res.get("organism", {})
        if isinstance(org, dict):
            org_name = org.get("scientificName", "") or org.get("commonName", "")

        # Build "FASTA identifier"-like header (not actual FASTA writing here)
        fasta_id = None
        if acc and entry_name:
            parts = []
            if protein_name:
                parts.append(protein_name)
            if org_name:
                parts.append(f"[{org_name}]")
            desc_text = " ".join(parts)
            fasta_id = f">{acc}|{entry_name} {desc_text}".strip()

        results.append({
            "UniProt ID": acc,
            "Uniprot entry name": entry_name,
            "Protein Name": protein_name,
            "Gene Name": gene_name,
            "Protein sequence": seq,
            "Sequence length": length,
            "Fasta Identifier": fasta_id
        })

    return results


# ---------------------------------------------------------------------
# STEP: UniProt keyword-based table
# ---------------------------------------------------------------------

def build_uniprot_result_df(df):
    """
    For each row in the input df:
    - if it has both Taxonomy ID and UniProt keywords:
        -> query UniProt and expand into multiple rows (one per protein).
    - else:
        -> keep a single row with NaNs for the UniProt columns.

    Returns: result_df (expanded table).
    """
    all_rows = []
    rows_with_keywords = 0
    rows_searched = 0

    for idx, row in df.iterrows():
        base = row.to_dict()

        tax_id = get_taxonomy_id_string(row)
        keywords = get_uniprot_keywords_list(row)
        has_kw = len(keywords) > 0
        has_tax = bool(tax_id)

        if has_kw:
            rows_with_keywords += 1

        if has_kw and has_tax:
            rows_searched += 1

            proteins_for_row = []
            seen = set()

            for kw in keywords:
                print(f"[UniProt] Row {idx}: TaxID {tax_id}, keyword '{kw}'")
                hits = fetch_proteins_for_keyword(tax_id, kw, max_results=200)
                print(f"   -> {len(hits)} proteins found")

                for p in hits:
                    acc = p.get("UniProt ID")
                    if acc and acc not in seen:
                        seen.add(acc)
                        proteins_for_row.append(p)

                time.sleep(0.2)  # small pause to be polite to UniProt

            if proteins_for_row:
                for p in proteins_for_row:
                    new_row = {**base, **p}
                    all_rows.append(new_row)
            else:
                # TaxID + keywords but no hits -> keep row with empty UniProt fields
                new_row = {
                    **base,
                    "Protein Name": None,
                    "UniProt ID": None,
                    "Gene Name": None,
                    "Fasta Identifier": None,
                    "Uniprot entry name": None,
                    "Protein sequence": None,
                    "Sequence length": None
                }
                all_rows.append(new_row)
        else:
            # No usable keywords/TaxID -> keep row with empty UniProt fields
            new_row = {
                **base,
                "Protein Name": None,
                "UniProt ID": None,
                "Gene Name": None,
                "Fasta Identifier": None,
                "Uniprot entry name": None,
                "Protein sequence": None,
                "Sequence length": None
            }
            all_rows.append(new_row)

    print("[UniProt] Keyword-based search finished.")
    print("  Rows with keywords:", rows_with_keywords)
    print("  Rows searched (keywords + TaxID):", rows_searched)

    result_df = pd.DataFrame(all_rows)
    print("  result_df shape:", result_df.shape)
    return result_df


# ---------------------------------------------------------------------
# STEP: Attach OrthoFinder orthologs to result_df (existing runs)
# ---------------------------------------------------------------------

def collect_orthofinder_orthologs(orthofinder_base):
    """
    Scan orthofinder_base for run folders and collect aggregated orthologs
    from *_QUERY.tsv in the latest OrthoFinder result folder.

    Returns:
        dict mapping (safe_species, tax_id) -> "orth1;orth2;..."
    """
    ortholog_map = {}

    if not os.path.isdir(orthofinder_base):
        print(f"[OrthoFinder orthologs] No orthofinder_runs folder at {orthofinder_base}")
        return ortholog_map

    for run_name in os.listdir(orthofinder_base):
        run_dir = os.path.join(orthofinder_base, run_name)
        if not os.path.isdir(run_dir):
            continue

        # run_name is like "<safe_species>_<taxid>"
        if "_" not in run_name:
            continue

        # Locate OrthoFinder main folder
        of_root = os.path.join(run_dir, "OrthoFinder")
        if not os.path.isdir(of_root):
            print(f"[OrthoFinder orthologs] No 'OrthoFinder' subfolder in {run_dir}")
            continue

        # Find latest result folder inside OrthoFinder
        subdirs = [
            os.path.join(of_root, d)
            for d in os.listdir(of_root)
            if os.path.isdir(os.path.join(of_root, d))
        ]
        if not subdirs:
            print(f"[OrthoFinder orthologs] No result folders in {of_root}")
            continue

        latest_dir = max(subdirs, key=os.path.getmtime)
        orthologues_dir = os.path.join(latest_dir, "Orthologues")
        if not os.path.isdir(orthologues_dir):
            print(f"[OrthoFinder orthologs] No 'Orthologues' folder in {latest_dir}")
            continue

        # Find *_QUERY.tsv
        query_tsvs = [f for f in os.listdir(orthologues_dir) if f.endswith("_QUERY.tsv")]
        if not query_tsvs:
            print(f"[OrthoFinder orthologs] No *_QUERY.tsv in {orthologues_dir}")
            continue

        query_tsv = os.path.join(orthologues_dir, query_tsvs[0])
        try:
            df_q = pd.read_csv(query_tsv, sep="\t")
        except Exception as e:
            print(f"[OrthoFinder orthologs] Failed to read {query_tsv}: {e}")
            continue

        if "Orthologs" not in df_q.columns:
            print(f"[OrthoFinder orthologs] Column 'Orthologs' not found in {query_tsv}")
            continue

        orths = df_q["Orthologs"].dropna().astype(str).tolist()
        if not orths:
            print(f"[OrthoFinder orthologs] No non-empty 'Orthologs' in {query_tsv}")
            continue

        # Aggregate unique orthologs as a semicolon-separated string
        unique_orths = sorted(set(orths))
        agg_orths = ";".join(unique_orths)

        # Key: (safe_species, tax_id) from run_name
        safe_species = "_".join(run_name.split("_")[:-1])
        tax_id = run_name.split("_")[-1]

        ortholog_map[(safe_species, tax_id)] = agg_orths
        print(f"[OrthoFinder orthologs] {run_name}: {len(unique_orths)} unique ortholog entries.")

    return ortholog_map


def add_orthologs_to_result_df(result_df, orthofinder_base):
    """
    Add 'OrthoFinder_orthologs' column to result_df by mapping
    species + Taxonomy ID (and presence of Query fasta) to the
    aggregated orthologs from collect_orthofinder_orthologs().
    """
    ortholog_map = collect_orthofinder_orthologs(orthofinder_base)
    if not ortholog_map:
        print("[OrthoFinder orthologs] No orthologs collected; column will be empty.")
        result_df["OrthoFinder_orthologs"] = ""
        return result_df

    # Resolve species and taxonomy columns, and Query fasta column
    def find_col(candidates):
        for c in candidates:
            if c in result_df.columns:
                return c
        return None

    species_col = find_col(["Species name", "Species Name"])
    tax_col = find_col(["Taxonomy ID", "Taxonomy id", "Taxonomy Id"])
    query_fasta_col = find_col([
        "Query fasta",
        "Query Fasta",
        "Query fasta file",
        "Query FASTA",
        "Query fasta and Uniprot keywords",
        "Query fasta and  Uniprot keywords"
    ])

    # Column may not exist in result_df if original df didn't have it
    has_query_col = query_fasta_col is not None and query_fasta_col in result_df.columns

    orthologs_col = []

    for _, row in result_df.iterrows():
        if species_col is None or tax_col is None:
            orthologs_col.append("")
            continue

        species = str(row.get(species_col, "")).strip()
        tax_id = clean_taxid(row.get(tax_col, ""))

        if not species or not tax_id:
            orthologs_col.append("")
            continue

        # Only assign orthologs for rows that were associated with a Query fasta
        if has_query_col:
            qval = row.get(query_fasta_col, "")
            if pd.isna(qval) or not str(qval).strip():
                orthologs_col.append("")
                continue

        safe_sp = safe_species_name(species, tax_id)
        key = (safe_sp, tax_id)
        orths = ortholog_map.get(key, "")
        orthologs_col.append(orths)

    result_df["OrthoFinder_orthologs"] = orthologs_col
    print("[OrthoFinder orthologs] Added 'OrthoFinder_orthologs' column to result_df.")
    return result_df


def normalize_taxonomy_column(result_df):
    tax_col = None
    for c in ["Taxonomy ID", "Taxonomy id", "Taxonomy Id"]:
        if c in result_df.columns:
            tax_col = c
            break

    if tax_col is not None:
        def clean_tax(x):
            if pd.isna(x):
                return ""
            if isinstance(x, (int, float)):
                return str(int(x))
            s = str(x).strip()
            if s.endswith(".0"):
                s = s[:-2]
            return s

        result_df[tax_col] = result_df[tax_col].apply(clean_tax)
    return result_df


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():
    args = parse_args()

    base_output_folder = args.base_output
    os.makedirs(base_output_folder, exist_ok=True)

    # OrthoFinder base folder (THIS is the path you will usually debug/change)
    if args.orthofinder_base:
        orthofinder_base = args.orthofinder_base
    else:
        orthofinder_base = os.path.join(base_output_folder, "orthofinder_runs")

    print("[Main] Input CSV:", args.input)
    print("[Main] Base output folder:", base_output_folder)
    print("[Main] OrthoFinder base folder (existing runs):", orthofinder_base)

    # 1) Load the original input sheet
    df = pd.read_csv(args.input)
    print("[Main] Loaded input rows:", len(df))

    # 2) UniProt keyword search & table expansion
    print("[Main] Building UniProt result table...")
    result_df = build_uniprot_result_df(df)

    # 3) Attach OrthoFinder orthologs from EXISTING runs
    print("[Main] Adding OrthoFinder orthologs (no OrthoFinder run is performed)...")
    result_df = add_orthologs_to_result_df(result_df, orthofinder_base)

    # 4) Normalize Taxonomy ID and save final table
    result_df = normalize_taxonomy_column(result_df)

    output_path = os.path.join(
        base_output_folder,
        "Food_peptide_database-with_uniprot_results_with_orthologs.csv"
    )
    result_df.to_csv(output_path, index=False)
    print("[Main] Saved final table:", output_path)
    print("[Main] Final result_df shape:", result_df.shape)


if __name__ == "__main__":
    main()
