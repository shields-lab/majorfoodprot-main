# FoodDB Database Releases

This repository's ordinary commit history is a working log, not a release
history — most commits are intermediate re-runs, fixes, or in-progress work
and do **not** correspond to a numbered database release. The authoritative
list of actual releases is this file plus the matching [GitHub
Releases](../../releases) page (tags below link there once each release is
cut).

## Versioning scheme

- **`1.0`** — the pre-pipeline database (2025), used in Clíona Ní
  Chonnacháin's PhD thesis. Predates this repository and this codebase
  entirely; not derived from any commit here.
- **`1.1.1-ddMMMyy`** — first and subsequent production runs of the current
  pipeline ([`shields-lab/fooddb-code`](https://github.com/shields-lab/fooddb-code)).
  The date suffix is the date the UniProt source download (Steps 1–2)
  *started*, not the date the run finished or was committed — the download
  date is what actually determines the UniProt data snapshot a release is
  built from.
- Later production runs increment the version (`1.1.2-...`, `1.2.0-...`,
  etc.) once a numbering convention for what counts as a minor vs. patch
  change is needed — not yet decided, since only one production run exists
  so far.

## How to cut a release

1. Confirm the working tree is a clean, complete run (Steps 0–9 all
   finished, `output_tsvs/food_protein_DB_*.tsv` is the file you intend to
   ship) and commit it normally.
2. Tag the commit with the release version, on **both** repos:
   ```bash
   # in fooddb-main, at the commit representing this release
   git tag v1.1.1-ddMMMyy
   git push origin v1.1.1-ddMMMyy

   # in fooddb-code, at the commit whose code actually produced this run
   git tag v1.1.1-ddMMMyy
   git push origin v1.1.1-ddMMMyy
   ```
   Using the *same* tag string on both repos makes "database vX was built by
   code vX" a direct, queryable pairing instead of a prose footnote.
3. Generate the release document (`fooddb-code`'s `generate_release_notes.py`
   — see [its pseudocode doc](https://github.com/shields-lab/fooddb-code/blob/master/docs/pseudocode/generate_release_notes.md)
   for exactly what it pulls together and from where):
   ```bash
   python /path/to/fooddb-code/generate_release_notes.py \
       Food_peptide_database-input.tsv \
       --version 1.1.1-ddMMMyy \
       --previous-deliverable output_tsvs/food_protein_DB_<previous-date>.tsv
   ```
   Writes `docs/releases/v1.1.1-ddMMMyy.md`: UniProt download dates/counts,
   OrthoFinder's own gene/orthogroup stats, dense-family-fallback rescue
   counts, Step 8 redundancy-reduction counts, per-species signal-peptide
   counts, a deliverable checksum, and (given `--previous-deliverable`) a
   per-species diff of which final candidate accessions were dropped,
   gained, or unchanged since the last release. Fill in the "Known issues /
   caveats" section by hand, then add the Zenodo DOI once minted (see
   below).
4. Create a GitHub Release from the `fooddb-main` tag, using that document
   as the release body.
5. Attach the deliverable TSV (and `fooddb.sqlite` if it fits) as a release
   **asset**, not just left in git history — sidesteps GitHub's ~50MB
   per-file warning on ordinary tracked blobs.
6. Commit `docs/releases/v1.1.1-ddMMMyy.md` to `fooddb-main` and add a row
   to the table below.

## Large per-species data (proteomes/subproteomes)

The full per-species UniProt proteomes and post-reduction subproteomes are
not tracked in git (`.gitignore`) and are too large for GitHub Release
assets at the full multi-species scale. These are archived separately on
Zenodo, one dataset deposit per release, versioned with the same
`1.1.1-ddMMMyy`-style string as the matching database release. Link the
resulting DOI back into that release's GitHub Release notes and the table
below.

## Releases

| Version | Date | fooddb-code tag | fooddb-main tag | Data DOI (Zenodo) | Notes |
|---|---|---|---|---|---|
| `1.0` | 2025 | — (predates this codebase) | — | — | Pre-pipeline database, PhD thesis (Clíona Ní Chonnacháin). Files not yet archived here — TODO: locate and link, or mint a Zenodo record for it too so it's citable alongside later versions. |
| `1.1.1-ddMMMyy` | *pending* | *pending* | *pending* | *pending* | First production run of the current pipeline. Fill in once the run completes. |
