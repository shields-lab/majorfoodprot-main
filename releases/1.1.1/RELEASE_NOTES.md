# FoodDB database release 1.1.1

Generated 2026-10-05 16:09 by `generate_release_notes.py`.

## UniProt data retrieval

- Download start: 2026-06-23
- Proteome downloads: 2026-06-23 to 2026-08-05 (43 days between first and last)
- UniProt data was retrieved incrementally, not as a single snapshot - proteome files dated 23 Jun (42), 2 Jul (10) and 5 Aug (49) 2026 by file date (proteome_downloads.log only covers 5 Aug); keyword searches 14-19 Aug 2026; OrthoFinder and Steps 7-9 re-run 21-22 Sep 2026.

## Summary

- Input file: `Food_peptide_database-input.tsv` (sha256 `fadf60441407a232724810fde0b9fc0b2909ef27327c96ac3b868d2f782ac694`)
- Deliverable: `output_tsvs/food_protein_DB_22Sep26.tsv`
- Species in input: 103
- Final candidates: 10137
- Step 8 CD-HIT identity threshold: 0.95
- Step 8: 15162 candidates -> 10137 after redundancy reduction

## Changes to the input since the previous release

No previous input snapshot available to compare against.

## Tool / data versions

- OrthoFinder: 3.1.4
- DIAMOND: 2.1.24
- CD-HIT: 4.8.1

## OrthoFinder summary (this release's orthology run)

- Number of species: 94
- Number of genes: 88189
- Number of genes in orthogroups: 87192
- Percentage of genes in orthogroups: 98.9
- Number of orthogroups: 972
- Number of orthogroups with all species present: 0
- Number of single-copy orthogroups: 0

## Dense multigene family fallback (Step 7)

- rescued: 127
- declined_ambiguous_paralog: 784
- declined_out_of_scope: 50
- declined_below_reference_threshold: 50811

## Checksums (sha256)

- `output_tsvs/food_protein_DB_22Sep26.tsv`: `6c6dd4ad36a22110ae9c2d1056d9e562f8e1de4da11001c9f6dda65d26c12d07`

## Per-species: data acquisition (Steps 2-4)

| Species | Proteome DL date | Proteome seqs | Subproteome seqs |
|---|---|---|---|
| Bos taurus | — | — | 1638 |
| Bubalus bubalis | — | — | 196 |
| Camelus dromedarius | — | — | 1012 |
| Gallus gallus | — | — | 1488 |
| Anas platyrhynchos platyrhynchos | — | — | 1036 |
| Meleagris gallopavo | — | — | 549 |
| Capra hircus | — | — | 1328 |
| Sus scrofa | — | — | 805 |
| Ovis aries | — | — | 1478 |
| Engraulis ringens | — | — | 0 |
| Gadus chalcogrammus | — | — | 20 |
| Katsuwonus pelamis | — | — | 6 |
| Clupea harengus | — | — | 651 |
| Micromesistius poutassou | — | — | 0 |
| Sardina pilchardus | — | — | 3 |
| Scomber japonicus | — | — | 9 |
| Sardinops sagax | — | — | 1 |
| Thunnus albacares | — | — | 9 |
| Gadus morhua | — | — | 932 |
| Trichiurus lepturus | — | — | 1 |
| Scomber scombrus | — | — | 532 |
| Trachurus murphyi | — | — | 0 |
| Ctenopharyngodon idella | 2026-08-05T16:18:46+00:00 | 1757 sequences | 114 |
| Hypophthalmichthys molitrix | — | — | 29 |
| Oreochromis niloticus | — | — | 928 |
| Cyprinus carpio | — | — | 1094 |
| Labeo catla | 2026-08-05T16:18:48+00:00 | 133 sequences | 14 |
| Salmo salar | — | — | 802 |
| Ictalurus punctatus | — | — | 594 |
| Ictalurus furcatus | — | — | 37 |
| Clarias gariepinus | — | — | 14 |
| Pangasius bocourti | — | — | 0 |
| Chanos chanos | — | — | 614 |
| Oncorhynchus mykiss | — | — | 1069 |
| Penaeus vannamei | — | — | 385 |
| Procambarus clarkii | — | — | 64 |
| Dosidicus gigas | — | — | 1 |
| Magallana gigas | 2026-08-05T16:21:41+00:00 | 58641 sequences | 400 |
| Crassostrea virginica | — | — | 468 |
| Magallana angulata | — | — | 6 |
| Ruditapes philippinarum | — | — | 29 |
| Mizuhopecten yessoensis | — | — | 338 |
| Placopecten magellanicus | — | — | 9 |
| Argopecten purpuratus | — | — | 0 |
| Mytilus edulis | — | — | 896 |
| Mytilus galloprovincialis | 2026-08-05T13:02:00+00:00 | 81997 sequences | 498 |
| Perna canaliculus | 2026-08-05T09:15:24+00:00 | 39 sequences | 1 |
| Mytilus chilensis | 2026-08-05T09:15:26+00:00 | 30 sequences | 1 |
| Ensis directus | 2026-08-05T09:15:27+00:00 | 6 sequences | 1 |
| Ensis arcuatus | 2026-08-05T09:15:29+00:00 | 0 sequences | 0 |
| Ensis minor | 2026-08-05T09:15:31+00:00 | 4 sequences | 0 |
| Siliqua patula | 2026-08-05T09:15:32+00:00 | 1 sequences | 0 |
| Solen strictus | 2026-08-05T09:15:34+00:00 | 17 sequences | 3 |
| Tegillarca granosa | 2026-08-05T09:16:39+00:00 | 24910 sequences | 337 |
| Anadara broughtonii | 2026-08-05T09:16:41+00:00 | 72 sequences | 9 |
| Mercenaria mercenaria | 2026-08-05T09:16:42+00:00 | 22 sequences | 0 |
| Triticum aestivum | 2026-08-05T09:22:45+00:00 | 136850 sequences | 4580 |
| Oryza sativa | 2026-08-05T09:29:23+00:00 | 148723 sequences | 2824 |
| Zea mays | 2026-08-05T09:33:52+00:00 | 106164 sequences | 3059 |
| Avena sativa | 2026-08-05T09:37:27+00:00 | 87080 sequences | 3029 |
| Sorghum bicolor | 2026-08-05T09:39:15+00:00 | 42207 sequences | 2067 |
| Cenchrus americanus | 2026-08-05T09:39:17+00:00 | 235 sequences | 59 |
| Eleusine coracana | 2026-08-05T09:41:31+00:00 | 55412 sequences | 2603 |
| Secale cereale | 2026-08-05T09:41:34+00:00 | 473 sequences | 147 |
| Hordeum vulgare | 2026-08-05T09:44:05+00:00 | 60289 sequences | 2441 |
| Prunus dulcis | 2026-08-05T09:45:54+00:00 | 45236 sequences | 1821 |
| Juglans regia | 2026-08-05T09:47:23+00:00 | 38501 sequences | 2024 |
| Anacardium occidentale | 2026-08-05T09:47:24+00:00 | 15 sequences | 8 |
| Pistacia vera | 2026-08-05T09:47:26+00:00 | 10 sequences | 6 |
| Corylus avellana | 2026-08-05T09:48:38+00:00 | 31408 sequences | 1902 |
| Linum usitatissimum | 2026-08-05T09:48:41+00:00 | 479 sequences | 110 |
| Salvia hispanica | 2026-08-05T09:48:42+00:00 | 32 sequences | 8 |
| Cucurbita maxima | 2026-08-05T09:50:10+00:00 | 34610 sequences | 1929 |
| Helianthus annuus | 2026-08-05T09:53:57+00:00 | 89523 sequences | 2572 |
| Papaver somniferum | 2026-08-05T09:55:44+00:00 | 41630 sequences | 1920 |
| Sesamum indicum | 2026-08-05T09:56:59+00:00 | 29842 sequences | 1835 |
| Sinapis alba | 2026-08-05T09:57:01+00:00 | 155 sequences | 34 |
| Arachis hypogaea | 2026-08-05T10:03:51+00:00 | 169708 sequences | 2625 |
| Glycine max | — | — | 2821 |
| Pisum sativum | 2026-08-05T16:31:41+00:00 | 65713 sequences | 2288 |
| Cicer arietinum | — | — | 1973 |
| Phaseolus vulgaris | 2026-08-05T10:08:05+00:00 | 32908 sequences | 2034 |
| Lens culinaris | — | — | 56 |
| Vicia faba | 2026-08-05T10:09:35+00:00 | 36642 sequences | 1969 |
| Phaseolus lunatus | 2026-08-05T10:09:37+00:00 | 75 sequences | 36 |
| Vigna unguiculata | 2026-08-05T10:11:39+00:00 | 39856 sequences | 1904 |
| Lupinus albus | 2026-08-05T10:13:16+00:00 | 38108 sequences | 2014 |
| Vigna radiata | — | — | 2161 |
| Cajanus cajan | 2026-08-05T10:14:13+00:00 | 23053 sequences | 1459 |
| Vigna subterranea | 2026-08-05T10:14:15+00:00 | 4 sequences | 2 |
| Solanum tuberosum | 2026-08-05T10:17:56+00:00 | 92930 sequences | 2708 |
| Ipomoea batatas | 2026-08-05T10:17:59+00:00 | 894 sequences | 268 |
| Colocasia esculenta | 2026-08-05T12:02:16+00:00 | 56380 sequences | 1679 |
| Manihot esculenta | — | — | 3938 |
| Dioscorea cayenensis | 2026-08-05T12:02:17+00:00 | 1 sequences | 1 |
| Brassica oleracea | — | — | 2444 |
| Spinacia oleracea | — | — | 1815 |
| Brassica rapa | — | — | 1972 |
| Lactuca sativa | — | — | 1990 |
| Musa acuminata | — | — | 41 |
| Musa balbisiana | — | — | 22 |
| Musa paradisiaca | 2026-08-05T12:02:19+00:00 | 2 sequences | 1 |
| Homo sapiens | — | — | 1046 |

## Per-species: orthology and final candidates (Steps 7-9)

| Species | Orthologue matches | Fallback rescued | Fallback declined | Final candidates | Signal peptides stripped |
|---|---|---|---|---|---|
| Bos taurus | 91 | 21 | 562 | 101 | 24 |
| Bubalus bubalis | 17 | 4 | 44 | 18 | 9 |
| Camelus dromedarius | 54 | 0 | 373 | 54 | 10 |
| Gallus gallus | 106 | 7 | 497 | 130 | 34 |
| Anas platyrhynchos platyrhynchos | 71 | 2 | 337 | 74 | 18 |
| Meleagris gallopavo | 52 | 2 | 394 | 63 | 0 |
| Capra hircus | 71 | 3 | 430 | 73 | 14 |
| Sus scrofa | 85 | 1 | 573 | 86 | 8 |
| Ovis aries | 100 | 5 | 497 | 102 | 25 |
| Engraulis ringens | 0 | 0 | 0 | 0 | 0 |
| Gadus chalcogrammus | 9 | 2 | 6 | 12 | 0 |
| Katsuwonus pelamis | 3 | 0 | 0 | 3 | 0 |
| Clupea harengus | 72 | 1 | 469 | 85 | 13 |
| Micromesistius poutassou | 0 | 0 | 0 | 0 | 0 |
| Sardina pilchardus | 1 | 0 | 1 | 2 | 0 |
| Scomber japonicus | 5 | 0 | 2 | 6 | 0 |
| Sardinops sagax | 0 | 0 | 0 | 0 | 0 |
| Thunnus albacares | 4 | 0 | 4 | 4 | 0 |
| Gadus morhua | 127 | 5 | 603 | 136 | 27 |
| Trichiurus lepturus | 0 | 0 | 0 | 0 | 0 |
| Scomber scombrus | 68 | 2 | 383 | 75 | 5 |
| Trachurus murphyi | 0 | 0 | 0 | 0 | 0 |
| Ctenopharyngodon idella | 7 | 1 | 65 | 13 | 2 |
| Hypophthalmichthys molitrix | 8 | 0 | 9 | 12 | 2 |
| Oreochromis niloticus | 139 | 0 | 585 | 144 | 33 |
| Cyprinus carpio | 170 | 7 | 621 | 173 | 49 |
| Labeo catla | 2 | 0 | 12 | 2 | 0 |
| Salmo salar | 82 | 2 | 517 | 90 | 13 |
| Ictalurus punctatus | 69 | 0 | 439 | 74 | 6 |
| Ictalurus furcatus | 6 | 2 | 25 | 8 | 0 |
| Clarias gariepinus | 0 | 0 | 13 | 0 | 0 |
| Pangasius bocourti | 0 | 0 | 0 | 0 | 0 |
| Chanos chanos | 77 | 1 | 431 | 85 | 8 |
| Oncorhynchus mykiss | 149 | 4 | 653 | 155 | 34 |
| Penaeus vannamei | 46 | 0 | 233 | 60 | 1 |
| Procambarus clarkii | 6 | 0 | 38 | 11 | 0 |
| Dosidicus gigas | 1 | 0 | 0 | 1 | 0 |
| Magallana gigas | 23 | 0 | 264 | 34 | 3 |
| Crassostrea virginica | 24 | 0 | 288 | 31 | 3 |
| Magallana angulata | 2 | 0 | 3 | 3 | 0 |
| Ruditapes philippinarum | 3 | 0 | 14 | 4 | 0 |
| Mizuhopecten yessoensis | 19 | 0 | 222 | 33 | 2 |
| Placopecten magellanicus | 3 | 1 | 2 | 6 | 0 |
| Argopecten purpuratus | 0 | 0 | 0 | 0 | 0 |
| Mytilus edulis | 19 | 0 | 306 | 29 | 0 |
| Mytilus galloprovincialis | 22 | 2 | 368 | 42 | 3 |
| Perna canaliculus | 1 | 0 | 0 | 1 | 0 |
| Mytilus chilensis | 0 | 0 | 0 | 0 | 0 |
| Ensis directus | 0 | 0 | 0 | 1 | 0 |
| Ensis arcuatus | 0 | 0 | 0 | 0 | 0 |
| Ensis minor | 0 | 0 | 0 | 0 | 0 |
| Siliqua patula | 0 | 0 | 0 | 0 | 0 |
| Solen strictus | 2 | 0 | 0 | 3 | 0 |
| Tegillarca granosa | 18 | 0 | 226 | 27 | 1 |
| Anadara broughtonii | 2 | 0 | 2 | 4 | 0 |
| Mercenaria mercenaria | 0 | 0 | 0 | 0 | 0 |
| Triticum aestivum | 133 | 0 | 1776 | 1497 | 1072 |
| Oryza sativa | 78 | 8 | 1347 | 435 | 271 |
| Zea mays | 54 | 4 | 1378 | 544 | 373 |
| Avena sativa | 92 | 0 | 1636 | 454 | 275 |
| Sorghum bicolor | 44 | 1 | 1049 | 258 | 163 |
| Cenchrus americanus | 3 | 0 | 13 | 8 | 4 |
| Eleusine coracana | 129 | 0 | 1344 | 400 | 189 |
| Secale cereale | 7 | 1 | 82 | 39 | 30 |
| Hordeum vulgare | 47 | 1 | 1142 | 324 | 205 |
| Prunus dulcis | 12 | 0 | 1095 | 135 | 88 |
| Juglans regia | 12 | 0 | 1233 | 114 | 51 |
| Anacardium occidentale | 0 | 0 | 1 | 5 | 4 |
| Pistacia vera | 0 | 0 | 0 | 5 | 5 |
| Corylus avellana | 15 | 0 | 1118 | 105 | 73 |
| Linum usitatissimum | 0 | 0 | 79 | 6 | 2 |
| Salvia hispanica | 0 | 0 | 6 | 1 | 0 |
| Cucurbita maxima | 13 | 0 | 1141 | 110 | 82 |
| Helianthus annuus | 43 | 0 | 1616 | 300 | 192 |
| Papaver somniferum | 4 | 0 | 1089 | 184 | 125 |
| Sesamum indicum | 11 | 0 | 1070 | 152 | 111 |
| Sinapis alba | 0 | 0 | 20 | 6 | 3 |
| Arachis hypogaea | 30 | 1 | 1710 | 285 | 195 |
| Glycine max | 20 | 0 | 1753 | 297 | 218 |
| Pisum sativum | 13 | 0 | 1332 | 194 | 122 |
| Cicer arietinum | 12 | 0 | 1158 | 130 | 97 |
| Phaseolus vulgaris | 17 | 0 | 1123 | 222 | 157 |
| Lens culinaris | 0 | 0 | 34 | 8 | 5 |
| Vicia faba | 10 | 1 | 1169 | 162 | 128 |
| Phaseolus lunatus | 0 | 0 | 28 | 5 | 5 |
| Vigna unguiculata | 15 | 0 | 1066 | 181 | 124 |
| Lupinus albus | 21 | 0 | 1131 | 200 | 89 |
| Vigna radiata | 36 | 0 | 1270 | 179 | 111 |
| Cajanus cajan | 10 | 0 | 918 | 77 | 47 |
| Vigna subterranea | 0 | 0 | 0 | 1 | 0 |
| Solanum tuberosum | 111 | 5 | 1546 | 384 | 107 |
| Ipomoea batatas | 5 | 2 | 149 | 63 | 7 |
| Colocasia esculenta | 86 | 0 | 952 | 159 | 47 |
| Manihot esculenta | 89 | 0 | 1158 | 187 | 50 |
| Dioscorea cayenensis | 0 | 0 | 0 | 1 | 1 |
| Brassica oleracea | 7 | 0 | 1690 | 46 | 6 |
| Spinacia oleracea | 8 | 1 | 1210 | 29 | 8 |
| Brassica rapa | 1 | 0 | 1272 | 28 | 1 |
| Lactuca sativa | 9 | 0 | 1305 | 42 | 7 |
| Musa acuminata | 0 | 0 | 0 | 36 | 32 |
| Musa balbisiana | 0 | 0 | 0 | 22 | 15 |
| Musa paradisiaca | 0 | 0 | 1 | 0 | 0 |
| Homo sapiens | 0 | 27 | 924 | 47 | 7 |

## Per-species diff vs. previous release

No `--previous-deliverable` given — first release, or diff skipped.

## Known issues / caveats

- **Mixed-date UniProt snapshot.** See "UniProt data retrieval" above: proteomes were fetched on three different dates (and the log covers only the last), so this is not a single UniProt snapshot. Release 1.1.2 is the first built from one fresh download.
- **Large repetitive proteins are incompletely represented.** Titin and nebulin gene models are fragmentary or mis-clustered in several non-human species, and the human reference is canonical isoforms only (e.g. TTN: 1 of 13 UniProt isoforms; NEB: 1 of 4). For MS/MS food authentication, search against all human isoforms and treat titin-derived matches with caution.
