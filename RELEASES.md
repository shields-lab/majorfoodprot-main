# FoodDB Database Releases

The index of numbered database releases. This repository's ordinary commit
history is a working log, not a release history: only the releases below
(each a directory under `releases/`, a git tag, a GitHub Release and a
Zenodo version) are releases. How to produce one: [`UPDATING.md`](UPDATING.md).

## Versioning

- **`1.0`** — the pre-pipeline database (2025), used in Clíona Ní
  Chonnacháin's PhD thesis. Predates this repository and the current code.
- **`1.1.1`** — the first release made with the current pipeline
  ([`fooddb-code`](https://github.com/shields-lab/fooddb-code)). UniProt data
  was retrieved incrementally (23 Jun – 19 Aug 2026), so it is a mixed-date
  snapshot; its `RELEASE_INFO` and notes record this.
- **`1.1.2` and later** — each built from a single fresh UniProt download,
  started and recorded by `start_release.py`. The plain version is the
  identifier; the **UniProt download start date** is a separate, mandatory
  field carried on every key document (`RELEASE_INFO`, `RELEASE_NOTES.md`,
  the GitHub Release title, the Zenodo title and this table).
- Proposed numbering: bump the patch (1.1.2 → 1.1.3) for a re-run on updated
  UniProt data with the same species and method; bump the minor (1.2.0) when
  the species list or the method changes materially. Adjust here if the
  convention changes.

## Releases

| Version | UniProt download start | Download window | Directory | Tags | Zenodo DOI | Notes |
|---|---|---|---|---|---|---|
| 1.0 | 2025 | — | not in this repository | — | *TODO: locate the thesis files; ideally version 1 of the same Zenodo record* | Pre-pipeline; PhD thesis (Clíona Ní Chonnacháin) |
| 1.1.1 | 23 Jun 2026 | 23 Jun – 5 Aug (proteomes); keyword search 14–19 Aug | [`releases/1.1.1/`](releases/1.1.1/) | *to tag* `v1.1.1` | *pending* | Mixed-date snapshot; deliverable from the 21–22 Sep 2026 run |
| 1.1.2 | *pending* | *pending* | `releases/1.1.2/` | *pending* | *pending* | First release from a single fresh download |
