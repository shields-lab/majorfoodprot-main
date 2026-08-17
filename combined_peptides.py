#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cluster-friendly version of combined_peptide.py

Main additions compared to the original Colab notebook:
- No Google Drive / Colab / widgets
- No "!" shell magics; uses subprocess instead
- Can be run from the command line with argparse
- Reads OrthoFinder QUERY ortholog tables and adds an
  'OrthoFinder_orthologs' column to the main output CSV.

Usage example (on cluster):

    python combined_peptide_cluster.py \
        --input Food_peptide_database-input.csv \
        --base-output food_db_output \
        --query-fasta-dir query_fasta_files \
        --run-orthofinder \
        --orthofinder-exe /path/to/orthofinder \
        --threads 8
"""

import os
import re
import math
import os, re, shutil
import time
import glob
import argparse
import subprocess
from math import isnan

import requests
import pandas as pd

# ---------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        description="Build food peptide DB, run OrthoFinder and add orthologs column."
    )
    p.add_argument(
        "--input",
        required=True,
        help="Input CSV (Food_peptide_database-input.csv)"
    )
    p.add_argument(
        "--base-output",
        default="food_db_output",
        help="Base output folder (default: food_db_output)"
    )
    p.add_argument(
        "--query-fasta-dir",
        default="query_fasta_files",
        help="Folder containing user query FASTA files (default: query_fasta_files)"
    )
    p.add_argument(
        "--orthofinder-exe",
        default="orthofinder",
        help="Path to OrthoFinder executable (default: 'orthofinder' on PATH)"
    )
    p.add_argument(
        "--threads",
        type=int,
        default=4,
        help="Number of threads for OrthoFinder and BLAST where used (default: 4)"
    )
    p.add_argument(
        "--run-orthofinder",
        action="store_true",
        help="If given, run OrthoFinder for each prepared run folder."
    )
    p.add_argument(
        "--human-proteome-fasta",
        required=True,
        help="Full human proteome FASTA (one sequence per human protein)."
    )
    p.add_argument(
        "--human-species-label",
        default="Homo_sapiens",
        help="Filename label OrthoFinder will use for human species (default: Homo_sapiens)"
    )
    p.add_argument(
        "--keep-only-orthologs",
        action="store_true",
        help="After OrthoFinder finishes, keep only Orthologues TSVs (and optionally Log.txt) to save disk."
    )
    return p.parse_args()

# ---------------------------------------------------------------------
# Helper functions (from original notebook)
# ---------------------------------------------------------------------

def get_taxonomy_id_string(row):
    """Clean Taxonomy ID into string like '4565'."""
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
    s = "".join(ch for ch in species if ch.isalnum()) or f"tax{tax_id}"
    return s

def keep_only_orthologs(run_dir, human_species_label="Homo_sapiens"):
    """
    Keep only pairwise ortholog TSV files from the latest OrthoFinder results.
    Deletes other large result folders to save disk.
    """
    of_root = os.path.join(run_dir, "OrthoFinder")
    if not os.path.isdir(of_root):
        print(f"[cleanup] No OrthoFinder folder in {run_dir}")
        return

    subdirs = [os.path.join(of_root, d) for d in os.listdir(of_root)
               if os.path.isdir(os.path.join(of_root, d)) and d.startswith("Results_")]
    if not subdirs:
        print(f"[cleanup] No Results_* folders in {of_root}")
        return

    latest_dir = max(subdirs, key=os.path.getmtime)
    orth_dir = os.path.join(latest_dir, "Orthologues")
    if not os.path.isdir(orth_dir):
        print(f"[cleanup] No Orthologues folder in {latest_dir}")
        return

    # Make a compact destination inside run_dir
    dest = os.path.join(run_dir, "orthologs_only")
    os.makedirs(dest, exist_ok=True)

    # Copy all TSVs from Orthologues (pairwise and summary)
    for root, _, files in os.walk(orth_dir):
        for fn in files:
            if fn.endswith(".tsv"):
                src = os.path.join(root, fn)
                shutil.copy(src, os.path.join(dest, fn))

    # Optionally keep Log.txt
    log_src = os.path.join(latest_dir, "Log.txt")
    if os.path.exists(log_src):
        shutil.copy(log_src, os.path.join(dest, "Log.txt"))

    # Now delete the full Results folder (big!)
    # If you want to be extra cautious, delete everything EXCEPT Orthologues, but simplest is remove entire results.
    shutil.rmtree(latest_dir)

    print(f"[cleanup] Kept TSVs in {dest} and removed {latest_dir}")

# ---------------------------------------------------------------------
# UNIPROT helpers
# ---------------------------------------------------------------------

UNIPROT_STREAM_URL = "https://rest.uniprot.org/uniprotkb/stream"
UNIPROT_JSON_URL   = "https://rest.uniprot.org/uniprotkb/stream"


def fetch_proteins_for_keyword(tax_id, keyword, max_results=200):
    """
    Get UniProt entries for:
        organism_id:tax_id AND "keyword"
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

        protein_name = None
        desc = res.get("proteinDescription", {})
        rec = desc.get("recommendedName", {})
        full = rec.get("fullName")
        if isinstance(full, dict):
            protein_name = full.get("value")
        elif isinstance(full, str):
            protein_name = full

        gene_name = None
        for g in res.get("genes", []):
            gname = g.get("geneName")
            if isinstance(gname, dict) and gname.get("value"):
                gene_name = gname["value"]
                break

        seq_info = res.get("sequence", {})
        seq = seq_info.get("value", "")
        length = seq_info.get("length", len(seq) if seq else None)

        org_name = ""
        org = res.get("organism", {})
        if isinstance(org, dict):
            org_name = org.get("scientificName", "") or org.get("commonName", "")

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
# STEP 1: Download target FASTAs for species with Query fasta + TaxID
# ---------------------------------------------------------------------

def download_target_fastas(df, target_seq_folder):
    os.makedirs(target_seq_folder, exist_ok=True)

    species_tax_pairs = set()
    for _, row in df.iterrows():
        if not has_query_fasta(row):
            continue
        tax_id = get_taxonomy_id_string(row)
        if not tax_id:
            continue
        species = get_species_name(row)
        if not species:
            continue
        species_tax_pairs.add((species, tax_id))

    print(f"[Target FASTA] Species needing target FASTA:", len(species_tax_pairs))

    for species, tax_id in species_tax_pairs:
        fasta_filename = make_species_filename(species, tax_id)
        fasta_path = os.path.join(target_seq_folder, fasta_filename)

        if os.path.exists(fasta_path):
            print(f"  [skip] {species} (TaxID {tax_id}) already downloaded.")
            continue

        query = f"organism_id:{tax_id}"
        print(f"  [download] UniProt sequences for {species} (TaxID {tax_id})...")

        try:
            resp = requests.get(
                UNIPROT_STREAM_URL,
                params={"query": query, "format": "fasta"},
                timeout=60
            )
            resp.raise_for_status()
            fasta_text = resp.text

            if fasta_text.strip():
                with open(fasta_path, "w") as f:
                    f.write(fasta_text)
                print(f"    -> Saved {fasta_filename}")
            else:
                print(f"    [warn] No sequences returned for {species} (TaxID {tax_id}).")
        except Exception as e:
            print(f"    [error] Failed for {species} (TaxID {tax_id}): {e}")

        time.sleep(0.5) # be polite to UniProt

# ---------------------------------------------------------------------
# STEP 2: Prepare OrthoFinder run folders (Query vs Target)
# ---------------------------------------------------------------------

def parse_query_ids_from_fasta(fasta_path):
    """
    Extract IDs/accessions from FASTA headers.
    Supports:
      >sp|P12345|...
      >tr|Q9XYZ1|...
      >P12345 ...
    Returns set of IDs like P12345, Q9XYZ1.
    """
    ids = set()
    with open(fasta_path, "r") as f:
        for line in f:
            if not line.startswith(">"):
                continue
            h = line[1:].strip()
            m = re.match(r"^(sp|tr)\|([^|]+)\|", h)
            if m:
                ids.add(m.group(2))
            else:
                ids.add(h.split()[0])
    return ids


def prepare_orthofinder_runs(
    df,
    query_base_dir,
    target_seq_folder,
    orthofinder_base,
    human_proteome_fasta,
    human_species_label="Homo_sapiens"
):
    """
    For each (species, tax_id) create ONE run directory containing:
      - FULL human proteome FASTA (human_proteome_fasta) copied as {human_species_label}.fasta
      - FULL target proteome FASTA copied as {safe_species}.fasta

    Then create a filter list of HUMAN protein IDs that correspond to the QUERY FASTA(s),
    by matching QUERY SEQUENCES to sequences in the HUMAN proteome FASTA.

    This produces in each run_dir:
      - query_human_ids.ids   (IDs exactly as they appear in the human proteome FASTA; matches OrthoFinder output)
      - query_unmatched.ids   (query headers that didn't match any human sequence; for debugging)

    IMPORTANT:
      - OrthoFinder is NOT run on query FASTAs. Query FASTAs are only used for filtering.
      - This avoids failures when query FASTA headers use different identifier styles (Pxxxx vs Dxxxx etc.).
    """
    import os
    import shutil
    import hashlib
    import pandas as pd

    os.makedirs(orthofinder_base, exist_ok=True)

    def find_col(candidates):
        for c in candidates:
            if c in df.columns:
                return c
        return None

    species_col = find_col(["Species name", "Species Name"])
    tax_col_raw = find_col(["Taxonomy ID", "Taxonomy id", "Taxonomy Id"])
    query_fasta_col = find_col([
        "Query fasta", "Query Fasta", "Query fasta file", "Query FASTA",
        "Query fasta and Uniprot keywords", "Query fasta and  Uniprot keywords"
    ])

    if species_col is None or tax_col_raw is None or query_fasta_col is None:
        print("[OrthoFinder prep] Missing Species/Taxonomy/Query fasta column(s).")
        return []

    if not os.path.exists(human_proteome_fasta):
        raise FileNotFoundError(f"Human proteome FASTA not found: {human_proteome_fasta}")

    # -------- FASTA iterators --------
    def fasta_iter(path):
        """Yield (header_token, sequence, full_header) for each FASTA record."""
        header = None
        seq_chunks = []
        with open(path, "r") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line:
                    continue
                if line.startswith(">"):
                    if header is not None:
                        seq = "".join(seq_chunks).replace(" ", "").replace("\r", "").upper()
                        yield header.split()[0], seq, header
                    header = line[1:].strip()
                    seq_chunks = []
                else:
                    seq_chunks.append(line.strip())
            if header is not None:
                seq = "".join(seq_chunks).replace(" ", "").replace("\r", "").upper()
                yield header.split()[0], seq, header

    def md5_seq(seq: str) -> str:
        return hashlib.md5(seq.encode("utf-8")).hexdigest()

    def map_query_sequences_to_human_ids(query_fasta_paths, human_fasta_path):
        """
        Returns:
          matched_human_ids: set of human IDs (first token in human FASTA header) whose sequences match query sequences
          unmatched_query_headers: list of query header tokens that did not match any human sequence
        """
        # Collect query sequence hashes
        qhash_to_qheaders = {}  # md5 -> set(query_header_tokens)
        all_query_headers = set()

        for qpath in query_fasta_paths:
            for qid, qseq, qfull in fasta_iter(qpath):
                if not qseq:
                    continue
                all_query_headers.add(qid)
                h = md5_seq(qseq)
                qhash_to_qheaders.setdefault(h, set()).add(qid)

        if not qhash_to_qheaders:
            return set(), sorted(all_query_headers)

        # Stream human proteome and match by sequence hash
        matched_human_ids = set()
        matched_query_headers = set()

        for hid, hseq, hfull in fasta_iter(human_fasta_path):
            if not hseq:
                continue
            hh = md5_seq(hseq)
            if hh in qhash_to_qheaders:
                matched_human_ids.add(hid)  # ID exactly as OrthoFinder will use
                matched_query_headers.update(qhash_to_qheaders[hh])

        unmatched = sorted(all_query_headers - matched_query_headers)
        return matched_human_ids, unmatched

    # -------- Build per-species run definitions --------
    query_fastas_by_key = {}     # key=(safe_species, tax_id) -> set(query fasta paths)
    species_name_by_key = {}     # key -> original species string
    run_dirs_by_key = {}         # key -> run_dir

    for idx, row in df.iterrows():
        qval = row.get(query_fasta_col, "")
        if pd.isna(qval) or not str(qval).strip():
            continue

        tax_id = clean_taxid(row.get(tax_col_raw, ""))
        species = str(row.get(species_col, "")).strip()
        if not tax_id or not species:
            continue

        qname = str(qval).strip()
        query_src = qname if os.path.isabs(qname) else os.path.join(query_base_dir, qname)
        if not os.path.exists(query_src):
            print(f"[OrthoFinder prep] Row {idx}: Query FASTA not found: {query_src}")
            continue

        safe_species = safe_species_name(species, tax_id)
        key = (safe_species, tax_id)

        species_name_by_key[key] = species
        query_fastas_by_key.setdefault(key, set()).add(query_src)

        if key not in run_dirs_by_key:
            run_dir = os.path.join(orthofinder_base, f"{safe_species}_{tax_id}")
            os.makedirs(run_dir, exist_ok=True)
            run_dirs_by_key[key] = run_dir

    if not run_dirs_by_key:
        print("[OrthoFinder prep] No valid Query+Target pairs found.")
        return []

    # -------- Create run dirs, copy full proteomes, write query_human_ids.ids --------
    run_dirs = []

    for key, run_dir in run_dirs_by_key.items():
        safe_species, tax_id = key
        orig_species = species_name_by_key[key]

        target_src = os.path.join(target_seq_folder, make_species_filename(orig_species, tax_id))
        if not os.path.exists(target_src):
            print(f"[OrthoFinder prep] Target FASTA not found for {orig_species} (TaxID {tax_id}): {target_src}")
            continue

        human_dest = os.path.join(run_dir, f"{human_species_label}.fasta")
        target_dest = os.path.join(run_dir, f"{safe_species}.fasta")

        shutil.copy(human_proteome_fasta, human_dest)
        shutil.copy(target_src, target_dest)

        # Map query sequences -> human IDs that exist in the human proteome FASTA (and thus in OrthoFinder output)
        qpaths = sorted(query_fastas_by_key.get(key, set()))
        matched_human_ids, unmatched_query_headers = map_query_sequences_to_human_ids(qpaths, human_proteome_fasta)

        # Write filter file used later by collect_orthofinder_orthologs()
        qids_path = os.path.join(run_dir, "query_human_ids.ids")
        with open(qids_path, "w") as out:
            for hid in sorted(matched_human_ids):
                out.write(hid + "\n")

        # Debug file: query headers that didn't match the human proteome by sequence
        um_path = os.path.join(run_dir, "query_unmatched.ids")
        with open(um_path, "w") as out:
            for qh in unmatched_query_headers:
                out.write(qh + "\n")

        print(f"[OrthoFinder prep] {safe_species}_{tax_id}: "
              f"{len(matched_human_ids)} query sequences matched to human proteome; "
              f"{len(unmatched_query_headers)} unmatched (see query_unmatched.ids).")

        run_dirs.append(run_dir)

    run_dirs = sorted(set(run_dirs))
    print("[OrthoFinder prep] Prepared run folders:")
    for rd in run_dirs:
        print("  -", rd)

    return run_dirs

# ---------------------------------------------------------------------
# STEP 3: Run OrthoFinder (optional)
# ---------------------------------------------------------------------

def run_orthofinder_on_runs(run_dirs, orthofinder_exe, threads=4, keep_only_orthologs_flag=False, human_species_label="Homo_sapiens"):
    if not run_dirs:
        print("[OrthoFinder] No run directories to process.")
        return

    for rd in run_dirs:
        print(f"[OrthoFinder] Running in: {rd}")
        cmd = [orthofinder_exe, "-f", rd, "-t", str(threads)]
        try:
            subprocess.run(cmd, check=True)
            print(f"  -> Completed {os.path.basename(rd)}")
            if keep_only_orthologs_flag:
                keep_only_orthologs(rd, human_species_label=human_species_label)
        except subprocess.CalledProcessError as e:
            print(f"  [error] OrthoFinder failed in {rd}: {e}")

# ---------------------------------------------------------------------
# STEP 4: UniProt keyword-based search to build result_df
# ---------------------------------------------------------------------

def build_uniprot_result_df(df):
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

                time.sleep(0.2)

            if proteins_for_row:
                for p in proteins_for_row:
                    new_row = {**base, **p}
                    all_rows.append(new_row)
            else:
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
# STEP 5: Attach OrthoFinder orthologs to result_df
# ---------------------------------------------------------------------

import glob

def normalize_of_id(x: str) -> str:
    """
    Normalize OrthoFinder protein IDs to match query IDs.
    Works with: sp|P12345|..., tr|Q9XYZ1|..., P12345
    """
    x = str(x).strip()
    m = re.match(r"^(sp|tr)\|([^|]+)\|", x)
    if m:
        return m.group(2)
    return x.split()[0]


def collect_orthofinder_orthologs(orthofinder_base, human_species_label="Homo_sapiens"):
    """
    Returns dict mapping (safe_species, tax_id) -> semicolon-separated target ortholog IDs
    but ONLY for human proteins listed in query_ids.txt.
    """
    ortholog_map = {}

    if not os.path.isdir(orthofinder_base):
        return ortholog_map

    for run_name in os.listdir(orthofinder_base):
        run_dir = os.path.join(orthofinder_base, run_name)
        if not os.path.isdir(run_dir) or "_" not in run_name:
            continue

        safe_species = "_".join(run_name.split("_")[:-1])
        tax_id = run_name.split("_")[-1]

        qids_path = os.path.join(run_dir, "query_human_ids.ids")
        if not os.path.exists(qids_path):
            print(f"[OrthoFinder orthologs] Missing query_human_ids.ids in {run_dir}")
            continue

        with open(qids_path) as f:
            query_ids = set(x.strip() for x in f if x.strip())

        of_root = os.path.join(run_dir, "OrthoFinder")
        if not os.path.isdir(of_root):
            print(f"[OrthoFinder orthologs] No 'OrthoFinder' folder in {run_dir}")
            continue

        subdirs = [os.path.join(of_root, d) for d in os.listdir(of_root)
                   if os.path.isdir(os.path.join(of_root, d))]
        if not subdirs:
            continue
        latest_dir = max(subdirs, key=os.path.getmtime)

        orth_dir = os.path.join(latest_dir, "Orthologues")
        if not os.path.isdir(orth_dir):
            continue

        # Look for pairwise TSV in either direction
        candidates = []
        candidates += glob.glob(os.path.join(orth_dir, f"Orthologues_{human_species_label}",
                                             f"{human_species_label}__v__{safe_species}.tsv"))
        candidates += glob.glob(os.path.join(orth_dir, f"Orthologues_{safe_species}",
                                             f"{safe_species}__v__{human_species_label}.tsv"))

        if not candidates:
            print(f"[OrthoFinder orthologs] No pairwise TSV found for {human_species_label} vs {safe_species}")
            continue

        pair_tsv = candidates[0]
        dfp = pd.read_csv(pair_tsv, sep="\t")

        if dfp.shape[1] < 2:
            print(f"[OrthoFinder orthologs] Unexpected format: {pair_tsv}")
            continue

        colA, colB = dfp.columns[0], dfp.columns[1]

        dfp["_A_norm"] = dfp[colA].apply(normalize_of_id)

        # Decide which side is human based on filename direction:
        # If file is Homo_sapiens__v__Target, then colA is human and colB is target
        # If file is Target__v__Homo_sapiens, then colA is target and colB is human
        file_is_human_to_target = os.path.basename(pair_tsv).startswith(f"{human_species_label}__v__")

        orths = set()

        if file_is_human_to_target:
            df_sub = dfp[dfp["_A_norm"].isin(query_ids)]
            target_col = colB
        else:
            # colB is human in this direction; normalize it too
            dfp["_B_norm"] = dfp[colB].apply(normalize_of_id)
            df_sub = dfp[dfp["_B_norm"].isin(query_ids)]
            target_col = colA

        for v in df_sub[target_col].dropna().astype(str):
            parts = re.split(r"[,\s]+", v.strip())
            for p in parts:
                if p:
                    orths.add(p)

        ortholog_map[(safe_species, tax_id)] = ";".join(sorted(orths))
        print(f"[OrthoFinder orthologs] {run_name}: kept {len(orths)} target ortholog IDs after filtering.")

    return ortholog_map


def add_orthologs_to_result_df(result_df, orthofinder_base, human_species_label="Homo_sapiens"):
    ortholog_map = collect_orthofinder_orthologs(orthofinder_base, human_species_label=human_species_label)

    """
    Add 'OrthoFinder_orthologs' column to result_df by mapping
    species + Taxonomy ID (and presence of Query fasta) to the
    aggregated orthologs from collect_orthofinder_orthologs().
    """
    #ortholog_map = collect_orthofinder_orthologs(orthofinder_base)
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
    # (e.g., if we expanded rows). We handle that gracefully.
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

# ---------------------------------------------------------------------
# STEP 6: Clean Taxonomy ID formatting and save result_df
# ---------------------------------------------------------------------

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

    print('in main, NUMBER 1')

    target_seq_folder = os.path.join(base_output_folder, "target-sequences")
    orthofinder_base = os.path.join(base_output_folder, "orthofinder_runs")

    print("[Main] Loading input:", args.input)
    df = pd.read_csv(args.input)
    print("  Rows:", len(df))

    # 1) Download target proteomes for Query + TaxID rows
    download_target_fastas(df, target_seq_folder)

    print('in main, NUMBER 2')

    # 2) Prepare OrthoFinder run folders

    run_dirs = prepare_orthofinder_runs(
        df,
        query_base_dir=args.query_fasta_dir,
        target_seq_folder=target_seq_folder,
        orthofinder_base=orthofinder_base,
        human_proteome_fasta=args.human_proteome_fasta,
        human_species_label=args.human_species_label
    )

    print('in main, NUMBER 3')

    # 3) Run OrthoFinder
    if args.run_orthofinder:
        print("[Main] Running OrthoFinder on all prepared run folders...")
        run_orthofinder_on_runs(
            run_dirs,
            args.orthofinder_exe,
            threads=args.threads,
            keep_only_orthologs_flag=args.keep_only_orthologs,
            human_species_label=args.human_species_label
        )
    else:
        print("[Main] --run-orthofinder not set, assuming OrthoFinder has already been run.")

    print('in main, NUMBER 4')

    # 4) UniProt keyword search -> result_df
    print("[Main] Building UniProt result table...")
    result_df = build_uniprot_result_df(df)

    # 5) Attach OrthoFinder orthologs
    print("[Main] Adding OrthoFinder orthologs...")
    result_df = add_orthologs_to_result_df(result_df, orthofinder_base, human_species_label=args.human_species_label)

    # 6) Normalize Taxonomy ID column and save
    result_df = normalize_taxonomy_column(result_df)

    output_path = os.path.join(base_output_folder, "Food_peptide_database-with_uniprot_results_with_orthologs.csv")
    result_df.to_csv(output_path, index=False)
    print("[Main] Saved:", output_path)
    print("[Main] Final result_df shape:", result_df.shape)


if __name__ == "__main__":
    main()
