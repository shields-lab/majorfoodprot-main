# Updating the database: producing a new release

The procedure for producing a new numbered release of MajorFoodProt (e.g. 1.1.2),
step by step. Written to be followed by someone who has not done it before.
It is public deliberately: the process is as much part of the database as
the data.

> **Status:** the GitHub part of this procedure is in use (release 1.1.1 is
> published on GitHub). The **Zenodo step (Publish, step 4) has not been used
> yet**: it will be added only after releases 1.1.1 and 1.1.2 have been taken
> through GitHub and the process has settled, because a published Zenodo
> record is hard to retract. Until then, skip step 4 and keep each release
> directory, which holds the only copy of the large files (proteomes,
> subproteomes, `fooddb.sqlite`).

**What a release is.** A directory, `releases/<version>/`, in this
repository, holding the input used, the results, and a description
(`RELEASE_NOTES.md`) that includes how the new release differs from the
previous one. It is also published as a GitHub Release and as a new version
of the Zenodo record, which is the permanent, citable copy. The
`majorfoodprot-code` pipeline is run *inside* the release directory, so each release
starts from nothing and keeps its own copy of the input.

## Before you start

1. Install the software and the two conda environments (`fooddb`,
   `orthofinder`) as described in the `majorfoodprot-code` README (Prerequisites and
   Setup), and check `bash tests/run_fixture_tests.sh` passes there.
2. Clone both repositories side by side:
   ```bash
   git clone https://github.com/shields-lab/majorfoodprot-code.git
   git clone https://github.com/shields-lab/majorfoodprot-main.git
   export CODE=$PWD/majorfoodprot-code        # used in the commands below
   ```
3. Choose the version. Look at the table in `RELEASES.md`: the next patch
   number for a re-run on updated UniProt data with the same species and
   method (1.1.2 → 1.1.3), the next minor number when the species list or the
   method changes materially (1.1.x → 1.2.0).
4. Decide the input. Normally the previous release's input TSV, edited if you
   are adding or removing species or search terms (edit a copy outside
   `releases/`; do not edit a previous release's files). Reference FASTAs in
   the previous release's `query_fasta_files/` are carried over
   automatically; to change them, pass `--query-dir`.
5. Plan to run Steps 1–2 promptly: the date you start is recorded as the
   UniProt download start, and the first and last proteome download dates are
   recorded too. A long gap between them means the proteomes are not one
   UniProt snapshot, and the release notes will say so.

## Run it

```bash
cd majorfoodprot-main
conda activate fooddb
python $CODE/start_release.py start 1.1.2 /path/to/your_input.tsv
cd releases/1.1.2
```
`start` creates `releases/1.1.2/` (it refuses if it exists), copies in the
input and `query_fasta_files/`, pins the input's checksum, stamps the start
time, and records the previous release. Then, from inside `releases/1.1.2/`
(the input is now there under its own name; `IN` below):

```bash
IN=your_input.tsv
python $CODE/validate_input.py $IN
python $CODE/get_searchterm_proteins.py $IN
python $CODE/get_proteomes.py $IN
python $CODE/start_release.py record-downloads $IN      # check the span and coverage it reports
python $CODE/get_homologs.py $IN
python $CODE/get_subproteomes.py $IN
python $CODE/build_species_tree.py $IN --mode ortho
python $CODE/build_species_tree.py $IN --mode food

conda activate orthofinder
orthofinder -f subproteomes -t 8 -a 4 -M msa -A mafft -s orthofinder_input_tree_rooted > orthofinder_run_$(date +%d%b%y).log 2>&1
conda activate fooddb

python $CODE/red_orthologs.py $IN
python $CODE/nonred_orthologs.py $IN --identity 0.95
python $CODE/remove_signals.py
python $CODE/generate_release_notes.py $IN
```
OrthoFinder takes about three hours on the 94-species set. What to check
when a step misbehaves is in the `majorfoodprot-code` README (Troubleshooting).

## Review before publishing

- **`RELEASE_NOTES.md`**: read the *UniProt data retrieval* section first —
  any WARNING there (a long gap between downloads, a species with no fresh
  download, an input TSV edited after `start`) needs resolving or explaining.
  Then *Changes to the input* and the *per-species diff* against the previous
  release: large unexpected drops or gains for a species deserve a look.
  Fill in *Known issues / caveats* by hand.
- `orthologs/nonred_orthologs_identity_histograms.pdf` and
  `output_tsvs/query_species_hit_counts.tsv` (a high count in a species other
  than the reference's own suggests near-duplicates CD-HIT did not collapse).

## Publish

1. **Commit** the release directory. Large regenerable files are gitignored,
   so `git status` should show only small files plus the deliverable TSV:
   ```bash
   cd ../..
   git add releases/1.1.2 RELEASES.md README.md
   git status          # check nothing large or unexpected is staged
   git commit -m "Release 1.1.2 (UniProt download started DD Mon YYYY)"
   ```
2. **Tag both repositories** with the same string, so "database 1.1.2 was built
   by code 1.1.2" is a direct pairing:
   ```bash
   git tag v1.1.2 && git push origin master v1.1.2
   (cd $CODE && git tag v1.1.2 && git push origin v1.1.2)
   ```
   Tag `majorfoodprot-code` at the commit you actually ran.
3. **GitHub Release** on `majorfoodprot-main` for tag `v1.1.2`: title
   `MajorFoodProt 1.1.2 (UniProt download started DD Mon YYYY)`, body =
   `RELEASE_NOTES.md`, attached: the deliverable TSV and the input TSV.
   ```bash
   gh release create v1.1.2 --title "MajorFoodProt 1.1.2 (UniProt download started DD Mon YYYY)" \
     --notes-file releases/1.1.2/RELEASE_NOTES.md \
     releases/1.1.2/output_tsvs/food_protein_DB_*.tsv releases/1.1.2/<your_input>.tsv
   ```
4. **Zenodo**: add a new version to the MajorFoodProt record (the first release
   creates the record; its concept DOI is what papers cite). Upload:
   the deliverable TSV, the input TSV, `RELEASE_NOTES.md`, `fooddb.sqlite`,
   `red_orthologs.tsv`, `nonred_orthologs.tsv`, the `subproteomes/` FASTAs and
   the `proteomes/` FASTAs (as zip files), and a zip of `majorfoodprot-code` at the
   tag (so the code travels with the data). Set the version to `1.1.2`, put
   the UniProt download start date in the title and description, and add the
   two GitHub repositories as related identifiers. Check Zenodo's current
   per-record size limits before a large upload.
5. **Record it**: add the Zenodo DOI and tags to the `RELEASES.md` row and
   the README table, commit and push.
6. **Keep the release directory** until the Zenodo upload is verified: the
   proteomes and subproteomes exist only there until then.

## Checklist

- [ ] version chosen, previous release identified, input prepared
- [ ] `start_release.py start` run immediately before Step 1
- [ ] Steps 0–9 completed in `releases/<version>/`; `record-downloads` gap acceptable
- [ ] `RELEASE_NOTES.md` generated, warnings resolved, caveats written
- [ ] committed; both repositories tagged and pushed
- [ ] GitHub Release created
- [ ] Zenodo version published; DOI added to `RELEASES.md` and README
- [ ] release directory kept until Zenodo upload verified
