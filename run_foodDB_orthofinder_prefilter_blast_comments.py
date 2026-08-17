#!/usr/bin/env python3
"""
run_fooddb_orthofinder_prefilter_blast_adapted.py

Adapted from the earlier row-wise FoodDB pipeline, but with a simpler
OrthoFinder invocation modeled on the user's working notebook.

Main differences vs the previous script:
- Keeps the robust row-by-row logging / partial CSV writing.
- Keeps BLAST prefiltering to build shortlists.
- Creates one OrthoFinder run directory per row/species containing exactly
  two FASTA files directly inside that folder.
- Calls OrthoFinder simply as: orthofinder -f <run_dir> -t <threads>
  (optionally also -a and -S), which mirrors the notebook style more closely.
- Reuses an existing OrthoFinder results folder when present.

This version is intended to reduce errors related to nested run directories or
cwd handling while preserving the original logic.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
import requests


# ---------------------------
# FASTA helpers
# ---------------------------

FASTA_ID_RE = re.compile(r"^>(\S+)")
UNIPROT_SP_TR_RE = re.compile(r"^(sp|tr)\|([^|]+)\|([^ ]+)")


def log(msg: str) -> None:
    print(msg, flush=True)


def read_fasta(path: Path) -> Dict[str, Tuple[str, str]]:
    """Return dict: fasta_id -> (header_without_>, sequence)."""
    seqs: Dict[str, Tuple[str, str]] = {}
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        header = None
        parts: List[str] = []
        fid = None
        for line in f:
            line = line.rstrip("\n")
            if line.startswith(">"):
                if header is not None and fid is not None:
                    seqs[fid] = (header, "".join(parts).replace(" ", "").replace("\r", ""))
                header = line[1:].strip()
                m = FASTA_ID_RE.match(line)
                fid = m.group(1) if m else header.split()[0]
                parts = []
            else:
                if header is None:
                    continue
                parts.append(line.strip())
        if header is not None and fid is not None:
            seqs[fid] = (header, "".join(parts).replace(" ", "").replace("\r", ""))
    return seqs


def fasta_identifiers_as_uniprot_ids(fasta_records: Dict[str, Tuple[str, str]]) -> Set[str]:
    """Extract UniProt-ish accessions from headers best-effort."""
    ids: Set[str] = set()
    for fid, (header, _seq) in fasta_records.items():
        m = UNIPROT_SP_TR_RE.match(header)
        if m:
            ids.add(m.group(2))
            continue
        if "|" in fid:
            parts = fid.split("|")
            if len(parts) >= 2 and parts[1]:
                ids.add(parts[1])
            ids.add(parts[0])
            ids.add(parts[-1])
        else:
            ids.add(fid)
    return ids


def safe_species_filename(name: str) -> str:
    name = name.strip().replace(" ", "_")
    name = re.sub(r"[^A-Za-z0-9_]", "", name)
    return name or "Unknown_species"


# ---------------------------
# UniProt downloads / metadata
# ---------------------------


def get_species_name_from_taxid(taxid: str, cache: Dict[str, str]) -> str:
    taxid = str(taxid).strip()
    if taxid in cache:
        return cache[taxid]
    url = f"https://rest.uniprot.org/taxonomy/{taxid}"
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Could not fetch taxonomy for taxid {taxid}: HTTP {r.status_code}")
    data = r.json()
    sci = data.get("scientificName")
    if not sci:
        raise RuntimeError(f"No scientificName returned for taxid {taxid}")
    val = safe_species_filename(sci)
    cache[taxid] = val
    return val


def download_uniprot_proteome_fasta_by_taxid(taxid: str, out_fasta: Path) -> None:
    taxid = str(taxid).strip()
    url = "https://rest.uniprot.org/uniprotkb/stream"
    params = {"query": f"(organism_id:{taxid})", "format": "fasta", "compressed": "false"}
    with requests.get(url, params=params, stream=True, timeout=120) as r:
        if r.status_code != 200:
            raise RuntimeError(f"Failed downloading UniProt FASTA for taxid {taxid}: HTTP {r.status_code}")
        out_fasta.parent.mkdir(parents=True, exist_ok=True)
        with out_fasta.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                if chunk:
                    f.write(chunk)
    if out_fasta.stat().st_size < 10:
        raise RuntimeError(f"Downloaded FASTA too small for taxid {taxid}: {out_fasta}")


# ---------------------------
# BLAST helpers (prefilter step)
# ---------------------------


def run_cmd(cmd: List[str], cwd: Optional[Path] = None) -> None:
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, stdout=sys.stdout, stderr=sys.stderr)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed (exit {p.returncode}): {' '.join(cmd)}")


def ensure_blast_db(fasta: Path, db_prefix: Path) -> None:
    """Create BLAST protein DB if missing."""
    expected = db_prefix.with_suffix(".pin")
    if expected.exists():
        return
    db_prefix.parent.mkdir(parents=True, exist_ok=True)
    run_cmd(["makeblastdb", "-in", str(fasta), "-dbtype", "prot", "-out", str(db_prefix)])


def blastp_hits(
    query_fa: Path,
    db_prefix: Path,
    out_tsv: Path,
    threads: int,
    evalue: float,
    max_target_seqs: int,
    min_pident: float,
) -> Set[str]:
    """Run blastp and return set of subject IDs passing thresholds."""
    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    run_cmd([
        "blastp",
        "-query", str(query_fa),
        "-db", str(db_prefix),
        "-outfmt", "6 qseqid sseqid pident evalue bitscore",
        "-evalue", str(evalue),
        "-max_target_seqs", str(max_target_seqs),
        "-num_threads", str(threads),
        "-out", str(out_tsv),
    ])

    hits: Set[str] = set()
    if not out_tsv.exists() or out_tsv.stat().st_size == 0:
        return hits

    with out_tsv.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5:
                continue
            _q, s, pident_s, evalue_s, _bits = parts
            try:
                pident_v = float(pident_s)
                evalue_v = float(evalue_s)
            except Exception:
                continue
            if pident_v >= min_pident and evalue_v <= evalue:
                hits.add(s.strip())
    return hits


def normalize_fasta_id_for_lookup(raw_id: str) -> List[str]:
    """Generate possible identifier variants for matching BLAST and FASTA IDs."""
    cands = [raw_id]
    if "|" in raw_id:
        parts = raw_id.split("|")
        cands.extend([parts[-1], parts[0]])
        if len(parts) >= 2:
            cands.append(parts[1])
    seen = set()
    out = []
    for c in cands:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def write_subset_fasta(
    all_records: Dict[str, Tuple[str, str]],
    ids_to_keep: Set[str],
    out_fa: Path,
) -> Set[str]:
    """Write FASTA containing only records matching ids_to_keep."""
    out_fa.parent.mkdir(parents=True, exist_ok=True)
    written: Set[str] = set()

    key_map: Dict[str, str] = {}
    for k in all_records.keys():
        key_map[k] = k
        if "|" in k:
            parts = k.split("|")
            key_map.setdefault(parts[-1], k)
            key_map.setdefault(parts[0], k)
            if len(parts) >= 2:
                key_map.setdefault(parts[1], k)

    with out_fa.open("w", encoding="utf-8") as f:
        for rid in ids_to_keep:
            for cand in normalize_fasta_id_for_lookup(rid):
                real = key_map.get(cand)
                if real and real in all_records and real not in written:
                    hdr, seq = all_records[real]
                    f.write(f">{real} {hdr}\n")
                    for i in range(0, len(seq), 60):
                        f.write(seq[i:i + 60] + "\n")
                    written.add(real)
                    break
    return written


# ---------------------------
# OrthoFinder helpers
# ---------------------------


def newest_results_dir(orthofinder_root: Path) -> Path:
    candidates = [p for p in orthofinder_root.iterdir() if p.is_dir() and p.name.startswith("Results_")]
    if not candidates:
        raise FileNotFoundError(f"No Results_* directory found in {orthofinder_root}")
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def find_pairwise_orthologues_tsv(results_dir: Path, species_a: str, species_b: str) -> Path:
    for root, _dirs, files in os.walk(results_dir):
        for fn in files:
            if fn == f"Orthologues_{species_a}__v__{species_b}.tsv":
                return Path(root) / fn
            if fn == f"Orthologues_{species_b}__v__{species_a}.tsv":
                return Path(root) / fn
    raise FileNotFoundError(
        f"Could not find pairwise orthologues TSV for {species_a} vs {species_b} under {results_dir}"
    )


def parse_pairwise_orthologues_tsv(tsv_path: Path) -> Tuple[str, str, List[Tuple[List[str], List[str]]]]:
    """Return (speciesA, speciesB, rows) where each row is (A_genes_list, B_genes_list)."""
    rows: List[Tuple[List[str], List[str]]] = []
    with tsv_path.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        if not header or len(header) < 3:
            raise RuntimeError(f"Unexpected orthologues TSV header: {header}")
        a_name = header[1]
        b_name = header[2]
        for parts in reader:
            if len(parts) < 3:
                continue
            a_cell = parts[1].strip()
            b_cell = parts[2].strip()
            a_genes = [x.strip() for x in re.split(r",\s*|\s+", a_cell) if x.strip()] if a_cell else []
            b_genes = [x.strip() for x in re.split(r",\s*|\s+", b_cell) if x.strip()] if b_cell else []
            rows.append((a_genes, b_genes))
    return a_name, b_name, rows


def build_human_to_species_map(
    a_name: str,
    b_name: str,
    rows: List[Tuple[List[str], List[str]]],
    human_species: str,
    other_species: str,
) -> Dict[str, Set[str]]:
    mapping: Dict[str, Set[str]] = {}
    for a_genes, b_genes in rows:
        if a_name == human_species and b_name == other_species:
            for h in a_genes:
                mapping.setdefault(h, set()).update(b_genes)
        elif b_name == human_species and a_name == other_species:
            for h in b_genes:
                mapping.setdefault(h, set()).update(a_genes)
    return mapping


def run_orthofinder_simple(
    run_dir: Path,
    threads: int,
    search_program: Optional[str] = None,
    use_alignment_threads: bool = True,
) -> Path:
    """
    Run OrthoFinder in the simple style that worked in the notebook:
      orthofinder -f <run_dir> -t <threads>
    with optional -a and -S.

    Returns the OrthoFinder output directory under run_dir.
    """
    orthofinder_dir = run_dir / "OrthoFinder"
    if orthofinder_dir.exists():
        return orthofinder_dir

    cmd = ["orthofinder", "-f", str(run_dir), "-t", str(threads)]
    if use_alignment_threads:
        cmd += ["-a", str(threads)]
    if search_program:
        cmd += ["-S", search_program]

    run_cmd(cmd)

    if not orthofinder_dir.exists():
        raise RuntimeError(f"OrthoFinder finished but output folder not found: {orthofinder_dir}")
    return orthofinder_dir


# ---------------------------
# Input column detection
# ---------------------------


def pick_col(cols: List[str], candidates: List[str]) -> Optional[str]:
    lc = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in lc:
            return lc[cand.lower()]
    for c in cols:
        for cand in candidates:
            if cand.lower() in c.lower():
                return c
    return None


@dataclass
class InputColumns:
    taxid: str
    keywords: Optional[str]
    query_fasta: Optional[str]



def detect_input_columns(df: pd.DataFrame) -> InputColumns:
    cols = list(df.columns)
    taxid_col = pick_col(cols, ["Taxonomy ID", "TaxID", "taxid", "NCBI Taxonomy ID", "Organism ID"])
    if not taxid_col:
        raise ValueError("Could not find a Taxonomy ID column.")
    keywords_col = pick_col(cols, ["Uniprot Keywords", "UniProt Keywords", "Keywords", "keyword"])
    query_col = pick_col(cols, ["Query fasta file", "Query FASTA file", "query_fasta", "Query file", "Query FASTA"])
    return InputColumns(taxid=taxid_col, keywords=keywords_col, query_fasta=query_col)


# ---------------------------
# Keyword mode helpers
# ---------------------------


def normalize_keywords(s: str) -> List[str]:
    return [p.strip().lower() for p in re.split(r"[;,|]+", s) if p.strip()]


def header_matches_keywords(header: str, keywords: List[str]) -> bool:
    h = header.lower()
    return any(k in h for k in keywords)


def parse_uniprot_from_header(header: str) -> Dict[str, str]:
    out = {"uniprot_accession": "", "entry_name": "", "gene_name": "", "protein_name": ""}
    m = UNIPROT_SP_TR_RE.match(header)
    if m:
        out["uniprot_accession"] = m.group(2)
        out["entry_name"] = m.group(3)
    if m and " " in header:
        after = header.split(" ", 1)[1]
        out["protein_name"] = after.split(" OS=", 1)[0].split(" GN=", 1)[0].strip()
        gn_match = re.search(r"\bGN=([^ ]+)", after)
        if gn_match:
            out["gene_name"] = gn_match.group(1).strip()
    return out


# ---------------------------
# Output writer
# ---------------------------


def write_partial_csv(output_rows: List[Dict[str, str]], df: pd.DataFrame, out_csv: Path) -> None:
    base_cols = list(df.columns)
    extra_cols = [
        "Species", "Taxonomy ID", "Human_Ortholog_GeneID",
        "K. Protein Name", "L. UniProt ID", "M. Gene Name",
        "N.Fasta Identifier", "O.Uniprot entry name",
        "P.Protein sequence", "Q.Sequence length",
    ]
    out_cols = base_cols + [c for c in extra_cols if c not in base_cols]

    if not output_rows:
        pd.DataFrame(columns=out_cols).to_csv(out_csv, index=False)
        return

    out_df = pd.DataFrame(output_rows)
    for c in extra_cols:
        if c not in out_df.columns:
            out_df[c] = ""
    rest = [c for c in out_df.columns if c not in out_cols]
    out_df = out_df[out_cols + rest]
    out_df.to_csv(out_csv, index=False)


# ---------------------------
# Main
# ---------------------------


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)



def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Input CSV file")
    ap.add_argument("--human-proteome", required=True, help="Human proteome FASTA file")
    ap.add_argument("--query-dir", required=True, help="Directory containing query FASTA files")
    ap.add_argument("--out", required=True, help="Output CSV file (relative path goes under output_root)")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument(
        "--search-program",
        choices=["diamond", "blast", "mmseqs"],
        default="diamond",
        help="OrthoFinder -S search program.",
    )
    ap.add_argument("--blast-evalue", type=float, default=1e-5)
    ap.add_argument("--blast-max-target-seqs", type=int, default=200)
    ap.add_argument("--blast-min-pident", type=float, default=25.0)
    ap.add_argument(
        "--min-shortlist",
        type=int,
        default=20,
        help="If shortlist smaller than this, fall back to using query sequences for human shortlist.",
    )
    ap.add_argument("--output-root", default="output_foodDB", help="Root folder for all outputs")
    ap.add_argument(
        "--orthofinder-simple-only",
        action="store_true",
        help="Call OrthoFinder in minimal style (-f run_dir -t threads) without -a or -S.",
    )
    args = ap.parse_args()

    output_root = Path(args.output_root).resolve()
    ensure_dir(output_root)

    input_csv = Path(args.input).resolve()
    query_dir = Path(args.query_dir).resolve()

    out_csv = Path(args.out)
    if not out_csv.is_absolute():
        out_csv = (output_root / out_csv).resolve()

    proteomes_cache = output_root / "proteomes_cache"
    runs_dir = output_root / "orthofinder_runs"
    blast_dir = output_root / "blast"
    ensure_dir(proteomes_cache)
    ensure_dir(runs_dir)
    ensure_dir(blast_dir)

    tax_cache_path = output_root / "taxonomy_cache.json"
    if tax_cache_path.exists():
        try:
            tax_cache = json.loads(tax_cache_path.read_text(encoding="utf-8"))
        except Exception:
            tax_cache = {}
    else:
        tax_cache = {}

    df = pd.read_csv(input_csv)
    cols = detect_input_columns(df)

    human_species_name = "Homo_sapiens"
    human_proteome_path = Path(args.human_proteome).resolve()
    human_records = read_fasta(human_proteome_path)

    human_db_prefix = blast_dir / "db" / human_species_name
    ensure_blast_db(human_proteome_path, human_db_prefix)

    output_rows: List[Dict[str, str]] = []

    log(f"Loaded {len(df)} rows from: {input_csv}")
    log(f"Detected columns: taxid='{cols.taxid}', keywords='{cols.keywords}', query_fasta='{cols.query_fasta}'")
    log(f"Output CSV will be: {out_csv}")
    write_partial_csv(output_rows, df, out_csv)

    for idx, row in df.iterrows():
        try:
            taxid = str(row[cols.taxid]).strip()
            log(f"\n=== ROW {idx} taxid={taxid} ===")

            if not taxid or taxid.lower() == "nan":
                log(f"[row {idx}] Missing/NaN taxid -> SKIP")
                write_partial_csv(output_rows, df, out_csv)
                continue

            species_name = get_species_name_from_taxid(taxid, tax_cache)
            log(f"[{taxid} {species_name}] Start")

            if idx % 10 == 0:
                tax_cache_path.write_text(json.dumps(tax_cache, indent=2), encoding="utf-8")

            species_fa = proteomes_cache / f"{species_name}.fa"
            if not species_fa.exists():
                log(f"[{taxid} {species_name}] Downloading UniProt FASTA ...")
                download_uniprot_proteome_fasta_by_taxid(taxid, species_fa)
            else:
                log(f"[{taxid} {species_name}] Using cached FASTA: {species_fa}")

            species_records = read_fasta(species_fa)
            log(f"[{taxid} {species_name}] Proteome records loaded: {len(species_records)}")

            keywords_val = ""
            query_val = ""
            if cols.keywords and pd.notna(row.get(cols.keywords, "")):
                keywords_val = str(row[cols.keywords]).strip()
            if cols.query_fasta and pd.notna(row.get(cols.query_fasta, "")):
                query_val = str(row[cols.query_fasta]).strip()

            log(f"[{taxid} {species_name}] keywords='{keywords_val}' query='{query_val}'")

            # --- Keyword mode ---
            if keywords_val and keywords_val.lower() not in ("nan", "none", "na", ""):
                kws = normalize_keywords(keywords_val)
                log(f"[{taxid} {species_name}] Keyword mode: {kws}")
                before = len(output_rows)

                for fid, (hdr, seq) in species_records.items():
                    if header_matches_keywords(hdr, kws):
                        meta = parse_uniprot_from_header(hdr)
                        out = {c: row[c] for c in df.columns}
                        out["Species"] = species_name
                        out["Taxonomy ID"] = taxid
                        out["K. Protein Name"] = meta["protein_name"]
                        out["L. UniProt ID"] = meta["uniprot_accession"]
                        out["M. Gene Name"] = meta["gene_name"]
                        out["N.Fasta Identifier"] = fid
                        out["O.Uniprot entry name"] = meta["entry_name"]
                        out["P.Protein sequence"] = seq
                        out["Q.Sequence length"] = str(len(seq))
                        output_rows.append(out)

                added = len(output_rows) - before
                log(f"[{taxid} {species_name}] Keyword matches added: {added}")
                write_partial_csv(output_rows, df, out_csv)
                continue

            # --- OrthoFinder mode ---
            if not query_val or query_val.lower() in ("nan", "none", "na", ""):
                log(f"[{taxid} {species_name}] No keywords and no query fasta -> SKIP")
                write_partial_csv(output_rows, df, out_csv)
                continue

            query_path = Path(query_val)
            if not query_path.is_absolute():
                query_path = query_dir / query_path
            query_path = query_path.resolve()
            if not query_path.exists():
                log(f"[{taxid} {species_name}] Query FASTA not found: {query_path} -> SKIP")
                write_partial_csv(output_rows, df, out_csv)
                continue

            query_records = read_fasta(query_path)
            query_human_ids = fasta_identifiers_as_uniprot_ids(query_records)
            log(f"[{taxid} {species_name}] OrthoFinder mode (prefilter). Query IDs: {len(query_human_ids)}")

            species_db_prefix = blast_dir / "db" / species_name
            ensure_blast_db(species_fa, species_db_prefix)

            tag = f"{species_name}__{taxid}"
            row_blast_dir = blast_dir / tag
            ensure_dir(row_blast_dir)

            animal_hits = blastp_hits(
                query_fa=query_path,
                db_prefix=species_db_prefix,
                out_tsv=row_blast_dir / "query_vs_species.tsv",
                threads=args.threads,
                evalue=args.blast_evalue,
                max_target_seqs=args.blast_max_target_seqs,
                min_pident=args.blast_min_pident,
            )
            human_hits = blastp_hits(
                query_fa=query_path,
                db_prefix=human_db_prefix,
                out_tsv=row_blast_dir / "query_vs_human.tsv",
                threads=args.threads,
                evalue=args.blast_evalue,
                max_target_seqs=args.blast_max_target_seqs,
                min_pident=args.blast_min_pident,
            )

            log(f"[{taxid} {species_name}] BLAST hits: species={len(animal_hits)} human={len(human_hits)}")

            if not animal_hits:
                log(f"[{taxid} {species_name}] No BLAST hits to species proteome -> SKIP")
                write_partial_csv(output_rows, df, out_csv)
                continue
            if not human_hits:
                log(f"[{taxid} {species_name}] No BLAST hits to human proteome; using query IDs only.")
                human_hits = set(query_records.keys())

            # Simpler OrthoFinder run layout: run_dir contains exactly the two FASTAs.
            run_dir = runs_dir / tag
            ensure_dir(run_dir)
            human_short_fa = run_dir / f"{human_species_name}.fa"
            species_short_fa = run_dir / f"{species_name}.fa"

            written_h = write_subset_fasta(human_records, human_hits, human_short_fa)
            written_s = write_subset_fasta(species_records, animal_hits, species_short_fa)

            if len(written_h) < args.min_shortlist:
                log(f"[{taxid} {species_name}] Human shortlist tiny ({len(written_h)}). Falling back to query FASTA.")
                with human_short_fa.open("w", encoding="utf-8") as f:
                    for fid, (hdr, seq) in query_records.items():
                        f.write(f">{fid} {hdr}\n")
                        for i in range(0, len(seq), 60):
                            f.write(seq[i:i + 60] + "\n")
                written_h = set(query_records.keys())

            if len(written_s) < args.min_shortlist:
                log(f"[{taxid} {species_name}] Warning: species shortlist small ({len(written_s)}).")

            log(f"[{taxid} {species_name}] Shortlists: human={len(written_h)} species={len(written_s)}")

            log(f"[{taxid} {species_name}] Running/using OrthoFinder in simple folder layout ...")
            if args.orthofinder_simple_only:
                orthofinder_dir = run_orthofinder_simple(
                    run_dir=run_dir,
                    threads=args.threads,
                    search_program=None,
                    use_alignment_threads=False,
                )
            else:
                orthofinder_dir = run_orthofinder_simple(
                    run_dir=run_dir,
                    threads=args.threads,
                    search_program=args.search_program,
                    use_alignment_threads=True,
                )

            results_dir = newest_results_dir(orthofinder_dir)
            tsv = find_pairwise_orthologues_tsv(results_dir, human_species_name, species_name)
            a_name, b_name, ortho_rows = parse_pairwise_orthologues_tsv(tsv)
            human_to_species = build_human_to_species_map(a_name, b_name, ortho_rows, human_species_name, species_name)

            kept_pairs: List[Tuple[str, str]] = []
            for h_gene, s_genes in human_to_species.items():
                if "|" in h_gene:
                    parts = h_gene.split("|")
                    h_acc = parts[1] if len(parts) >= 2 else parts[0]
                else:
                    h_acc = h_gene

                if (h_acc not in query_human_ids) and (h_gene not in query_human_ids) and (h_gene not in query_records):
                    continue

                for sg in s_genes:
                    kept_pairs.append((h_gene, sg))

            log(f"[{taxid} {species_name}] Kept ortholog pairs after query filter: {len(kept_pairs)}")

            before = len(output_rows)
            for h_gene, s_gene in kept_pairs:
                cand_ids = normalize_fasta_id_for_lookup(s_gene)
                found = None
                for cid in cand_ids:
                    if cid in species_records:
                        found = cid
                        break
                if not found:
                    continue

                hdr, seq = species_records[found]
                meta = parse_uniprot_from_header(hdr)

                out = {c: row[c] for c in df.columns}
                out["Species"] = species_name
                out["Taxonomy ID"] = taxid
                out["Human_Ortholog_GeneID"] = h_gene
                out["K. Protein Name"] = meta["protein_name"]
                out["L. UniProt ID"] = meta["uniprot_accession"]
                out["M. Gene Name"] = meta["gene_name"]
                out["N.Fasta Identifier"] = found
                out["O.Uniprot entry name"] = meta["entry_name"]
                out["P.Protein sequence"] = seq
                out["Q.Sequence length"] = str(len(seq))
                output_rows.append(out)

            added = len(output_rows) - before
            log(f"[{taxid} {species_name}] Output rows added: {added}")
            write_partial_csv(output_rows, df, out_csv)

        except Exception as e:
            log(f"[row {idx}] ERROR: {e}")
            traceback.print_exc()
            write_partial_csv(output_rows, df, out_csv)
            continue

    tax_cache_path.write_text(json.dumps(tax_cache, indent=2), encoding="utf-8")
    write_partial_csv(output_rows, df, out_csv)

    log(f"\nDONE. Wrote output CSV: {out_csv}")
    log(f"Total output rows: {len(output_rows)}")
    log(f"All outputs stored under: {output_root}")


if __name__ == "__main__":
    main()
