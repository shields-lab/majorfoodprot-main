# MajorFoodProt
<p align="center">
  <img src="food protein database logo.png" alt="MajorFoodProt logo" width="320">
</p>
*Orthology-driven database of candidate major food proteins from species making a major contribution to human protein intake.*

The Shields Lab database of major food protein sequences: for each food
species, the proteins orthologous to a curated set of reference food
proteins (milk, egg, muscle, seed storage proteins and others), drawn from
UniProt and filtered with OrthoFinder. The pipeline that builds it is in
[`majorfoodprot-code`](https://github.com/shields-lab/majorfoodprot-code); this repository
holds the database itself, one directory per numbered release.

**To cite the database**, cite the Zenodo record (DOI to be added after the
first deposit — see `RELEASES.md`). The record has one version per release;
its concept DOI always resolves to the latest, and each version has its own
DOI for exact reproducibility.

## Releases

| Version | UniProt data retrieved | Directory |
|---|---|---|
| 1.0 | 2025 (pre-pipeline; Clíona Ní Chonnacháin's PhD thesis) | not in this repository |
| 1.1.1 | 23 Jun – 19 Aug 2026 (incremental, mixed-date) | [`releases/1.1.1/`](releases/1.1.1/) |
| v1.2.0| October 2026 (2nd release) | [`results_v1.2.0/`](results_v1.2.0/) |

`RELEASES.md` is the full index (tags, DOIs, notes). Every release is
described in its own `RELEASE_NOTES.md`: UniProt download dates, input
changes, species and sequence counts, OrthoFinder statistics, the
dense-family-fallback counts, and a per-species list of what changed since
the previous release.

## What a release directory contains

```
releases/1.1.1/
├── RELEASE_INFO                        # version, UniProt download start, pinned input checksum, previous release
├── RELEASE_NOTES.md                    # the release description (also the GitHub Release text)
├── Food_peptide_database-input.tsv     # the input species list this release was built from
├── query_fasta_files/                  # the curated reference proteins used
├── output_tsvs/
│   └── food_protein_DB_<date>.tsv      # THE DATABASE: one row per final candidate protein
├── orthologs/                          # audit trail: dense-family-fallback decisions, identity histograms
├── orthofinder_input_tree_rooted       # species tree used for OrthoFinder
└── *.log                               # per-step logs
```

The deliverable's columns are described in
[`majorfoodprot-code/docs/file_formats.md`](https://github.com/shields-lab/majorfoodprot-code/blob/master/docs/file_formats.md).

The large files are not in git: the full UniProt proteomes, the per-species
subproteome FASTAs (OrthoFinder's input), `fooddb.sqlite` and the
intermediate ortholog tables are in each release's Zenodo record, and the
smaller ones are also attached to its GitHub Release.

## Updating the database

Producing a new release is a documented, repeatable procedure:
[`UPDATING.md`](UPDATING.md).
