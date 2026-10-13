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
6. Check disk space. A full run keeps several GB per release (proteomes
   about 3 GB, OrthoFinder results about 2 GB, plus homologs and the UniProt
   record archive); delete old OrthoFinder `Results_*` directories you no
   longer need.
7. Run the long steps detached (`nohup`, `screen` or `tmux`), not in a
   terminal you will close, and keep the machine awake. Rehearsal timings on
   the 23-species example, for scale: downloads 1h26m, OrthoFinder 3h55m,
   Step 9 (UniProt record archive) 41 min, about 6 hours in all. The full
   94-species set will take longer; allow a day or two.

## Run it

One command does the whole run: it starts the release (creates
`releases/1.1.2/`, copies in the input and `query_fasta_files/`, pins the
input's checksum, stamps the UniProt download start, records the previous
release), runs Steps 0–9 inside it with the switch into the OrthoFinder
environment and back, and writes `RELEASE_NOTES.md`. From the root of this
repository, detached so closing the terminal does not stop it:

```bash
cd majorfoodprot-main
nohup bash $CODE/run_release.sh 1.1.2 /path/to/your_input.tsv > run_1.1.2.out 2>&1 &
```
Options: `--orthofinder-env NAME` and `--fooddb-env NAME` (your conda
environment names; defaults `orthofinder` and `fooddb`), `--query-dir DIR`
(reference FASTAs; default the previous release's, and required for the very
first release), `--identity`, `--threads`, `--skip-archive`. `--dry-run` prints
the plan, including the environment switches, and runs nothing — worth doing
first. Progress is in `releases/1.1.2/run_release.log`.

**If it stops** (a network error, a full disk), the message names the failed
step. Fix the cause and continue with the same version:
```bash
nohup bash $CODE/run_release.sh 1.1.2 --resume > run_1.1.2_resume.out 2>&1 &
```
Finished steps are skipped; a half-finished Step 3, 4 or 6 has its partial
output cleared first, so nothing stale is built on. The commands the script
runs, in order, are listed in the `majorfoodprot-code` README ("Step by
step"); what to check when a step misbehaves is in its Troubleshooting
section.

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
- [ ] `run_release.sh` started immediately after the input was prepared (dry run checked first)
- [ ] run completed (`DONE` in `run_release.log`); the download gap in the notes is acceptable
- [ ] `RELEASE_NOTES.md` generated, warnings resolved, caveats written
- [ ] committed; both repositories tagged and pushed
- [ ] GitHub Release created
- [ ] Zenodo version published; DOI added to `RELEASES.md` and README
- [ ] release directory kept until Zenodo upload verified
