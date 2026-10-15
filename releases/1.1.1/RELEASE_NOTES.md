# MajorFoodProt release 1.1.1

Generated 2026-10-15 12:29 by `generate_release_notes.py`.

## UniProt data retrieval

- Download start: 2026-06-23
- Proteome downloads: 2026-06-23 to 2026-08-05 (43 days between first and last)
- UniProt data was retrieved incrementally, not as a single snapshot - proteome files dated 23 Jun (42), 2 Jul (10) and 5 Aug (49) 2026 by file date (proteome_downloads.log only covers 5 Aug); keyword searches 14-19 Aug 2026. This release was REPROCESSED on 13 Oct 2026 from those same files with the current pipeline (Steps 3-9, including a new OrthoFinder run); no new UniProt download was made. The comparison below is against the original build.
- Compared against previous release: 1.1.1 (original build, 21-22 Sep 2026)

## Summary

- Input file: `Food_peptide_database-input.tsv` (sha256 `fadf60441407a232724810fde0b9fc0b2909ef27327c96ac3b868d2f782ac694`)
- Deliverable: `output_tsvs/food_protein_DB_13Oct26.tsv`
- Species in input: 103
- Final candidates: 10137
- Step 8 CD-HIT identity threshold: 0.95
- Step 8: 15162 candidates -> 10137 after redundancy reduction

## Changes to the input since the previous release

Compared with `original_build/Food_peptide_database-input.tsv`:
- Species added: none
- Species removed: none
- Input file is byte-identical to the previous release's.

## Tool / data versions

- Pipeline code (majorfoodprot-code): v1.1.1 (commit `3a61cc0c2f`)
- OrthoFinder: 3.1.4 -- `orthofinder -f subproteomes -t 8 -a 4 -M msa -A mafft -s orthofinder_input_tree_rooted`
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

- `output_tsvs/food_protein_DB_13Oct26.tsv`: `5ad531894c642adb504eebd3fdb8d15fd4e6dcddbaf522c878cdff2fde24beec`

## Per-species: data acquisition (Steps 2-4)

| Species | Proteome DL date | Proteome seqs | Subproteome seqs |
|---|---|---|---|
| Bos taurus | — | — | 819 |
| Bubalus bubalis | — | — | 98 |
| Camelus dromedarius | — | — | 506 |
| Gallus gallus | — | — | 744 |
| Anas platyrhynchos platyrhynchos | — | — | 518 |
| Meleagris gallopavo | — | — | 549 |
| Capra hircus | — | — | 664 |
| Sus scrofa | — | — | 805 |
| Ovis aries | — | — | 739 |
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
| Ctenopharyngodon idella | 2026-08-05 | 1757 | 114 |
| Hypophthalmichthys molitrix | — | — | 29 |
| Oreochromis niloticus | — | — | 928 |
| Cyprinus carpio | — | — | 1094 |
| Labeo catla | 2026-08-05 | 133 | 14 |
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
| Magallana gigas | 2026-08-05 | 58641 | 400 |
| Crassostrea virginica | — | — | 468 |
| Magallana angulata | — | — | 6 |
| Ruditapes philippinarum | — | — | 29 |
| Mizuhopecten yessoensis | — | — | 338 |
| Placopecten magellanicus | — | — | 9 |
| Argopecten purpuratus | — | — | 0 |
| Mytilus edulis | — | — | 448 |
| Mytilus galloprovincialis | 2026-08-05 | 81997 | 498 |
| Perna canaliculus | 2026-08-05 | 39 | 1 |
| Mytilus chilensis | 2026-08-05 | 30 | 1 |
| Ensis directus | 2026-08-05 | 6 | 1 |
| Ensis arcuatus | 2026-08-05 | 0 | 0 |
| Ensis minor | 2026-08-05 | 4 | 0 |
| Siliqua patula | 2026-08-05 | 1 | 0 |
| Solen strictus | 2026-08-05 | 17 | 3 |
| Tegillarca granosa | 2026-08-05 | 24910 | 337 |
| Anadara broughtonii | 2026-08-05 | 72 | 9 |
| Mercenaria mercenaria | 2026-08-05 | 22 | 0 |
| Triticum aestivum | 2026-08-05 | 136850 | 4580 |
| Oryza sativa | 2026-08-05 | 148723 | 2824 |
| Zea mays | 2026-08-05 | 106164 | 3059 |
| Avena sativa | 2026-08-05 | 87080 | 3029 |
| Sorghum bicolor | 2026-08-05 | 42207 | 2067 |
| Cenchrus americanus | 2026-08-05 | 235 | 59 |
| Eleusine coracana | 2026-08-05 | 55412 | 2603 |
| Secale cereale | 2026-08-05 | 473 | 147 |
| Hordeum vulgare | 2026-08-05 | 60289 | 2441 |
| Prunus dulcis | 2026-08-05 | 45236 | 1821 |
| Juglans regia | 2026-08-05 | 38501 | 2024 |
| Anacardium occidentale | 2026-08-05 | 15 | 8 |
| Pistacia vera | 2026-08-05 | 10 | 6 |
| Corylus avellana | 2026-08-05 | 31408 | 1902 |
| Linum usitatissimum | 2026-08-05 | 479 | 110 |
| Salvia hispanica | 2026-08-05 | 32 | 8 |
| Cucurbita maxima | 2026-08-05 | 34610 | 1929 |
| Helianthus annuus | 2026-08-05 | 89523 | 2572 |
| Papaver somniferum | 2026-08-05 | 41630 | 1920 |
| Sesamum indicum | 2026-08-05 | 29842 | 1835 |
| Sinapis alba | 2026-08-05 | 155 | 34 |
| Arachis hypogaea | 2026-08-05 | 169708 | 2625 |
| Glycine max | — | — | 2821 |
| Pisum sativum | 2026-08-05 | 65713 | 2288 |
| Cicer arietinum | — | — | 1973 |
| Phaseolus vulgaris | 2026-08-05 | 32908 | 2034 |
| Lens culinaris | — | — | 56 |
| Vicia faba | 2026-08-05 | 36642 | 1969 |
| Phaseolus lunatus | 2026-08-05 | 75 | 36 |
| Vigna unguiculata | 2026-08-05 | 39856 | 1904 |
| Lupinus albus | 2026-08-05 | 38108 | 2014 |
| Vigna radiata | — | — | 2161 |
| Cajanus cajan | 2026-08-05 | 23053 | 1459 |
| Vigna subterranea | 2026-08-05 | 4 | 2 |
| Solanum tuberosum | 2026-08-05 | 92930 | 2708 |
| Ipomoea batatas | 2026-08-05 | 894 | 268 |
| Colocasia esculenta | 2026-08-05 | 56380 | 1679 |
| Manihot esculenta | — | — | 1969 |
| Dioscorea cayenensis | 2026-08-05 | 1 | 1 |
| Brassica oleracea | — | — | 2444 |
| Spinacia oleracea | — | — | 1815 |
| Brassica rapa | — | — | 1972 |
| Lactuca sativa | — | — | 1990 |
| Musa acuminata | — | — | 41 |
| Musa balbisiana | — | — | 22 |
| Musa paradisiaca | 2026-08-05 | 2 | 1 |
| Homo sapiens | — | — | 1046 |

## Per-species: orthology and final candidates (Steps 7-9)

| Species | Orthologue matches | Fallback rescued | Fallback declined | Final candidates | Signal peptides stripped |
|---|---|---|---|---|---|
| Bos taurus | 91 | 21 | 562 | 101 | 24 |
| Bubalus bubalis | 17 | 4 | 44 | 18 | 9 |
| Camelus dromedarius | 54 | 0 | 373 | 54 | 10 |
| Gallus gallus | 105 | 7 | 497 | 130 | 34 |
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

## Per-species diff vs. previous release (`original_build/food_protein_DB_22Sep26.tsv`)

| Species | Dropped | Gained | Unchanged |
|---|---|---|---|
| Bos taurus | 0 | 0 | 101 |
| Bubalus bubalis | 0 | 0 | 18 |
| Camelus dromedarius | 0 | 0 | 54 |
| Gallus gallus | 0 | 0 | 130 |
| Anas platyrhynchos platyrhynchos | 0 | 0 | 74 |
| Meleagris gallopavo | 0 | 0 | 63 |
| Capra hircus | 0 | 0 | 73 |
| Sus scrofa | 0 | 0 | 86 |
| Ovis aries | 0 | 0 | 102 |
| Engraulis ringens | 0 | 0 | 0 |
| Gadus chalcogrammus | 0 | 0 | 12 |
| Katsuwonus pelamis | 0 | 0 | 3 |
| Clupea harengus | 0 | 0 | 85 |
| Micromesistius poutassou | 0 | 0 | 0 |
| Sardina pilchardus | 0 | 0 | 2 |
| Scomber japonicus | 0 | 0 | 6 |
| Sardinops sagax | 0 | 0 | 0 |
| Thunnus albacares | 0 | 0 | 4 |
| Gadus morhua | 0 | 0 | 136 |
| Trichiurus lepturus | 0 | 0 | 0 |
| Scomber scombrus | 0 | 0 | 75 |
| Trachurus murphyi | 0 | 0 | 0 |
| Ctenopharyngodon idella | 0 | 0 | 13 |
| Hypophthalmichthys molitrix | 0 | 0 | 12 |
| Oreochromis niloticus | 0 | 0 | 144 |
| Cyprinus carpio | 0 | 0 | 173 |
| Labeo catla | 0 | 0 | 2 |
| Salmo salar | 0 | 0 | 90 |
| Ictalurus punctatus | 0 | 0 | 74 |
| Ictalurus furcatus | 0 | 0 | 8 |
| Clarias gariepinus | 0 | 0 | 0 |
| Pangasius bocourti | 0 | 0 | 0 |
| Chanos chanos | 0 | 0 | 85 |
| Oncorhynchus mykiss | 0 | 0 | 155 |
| Penaeus vannamei | 0 | 0 | 60 |
| Procambarus clarkii | 0 | 0 | 11 |
| Dosidicus gigas | 0 | 0 | 1 |
| Magallana gigas | 0 | 0 | 34 |
| Crassostrea virginica | 0 | 0 | 31 |
| Magallana angulata | 0 | 0 | 3 |
| Ruditapes philippinarum | 0 | 0 | 4 |
| Mizuhopecten yessoensis | 0 | 0 | 33 |
| Placopecten magellanicus | 0 | 0 | 6 |
| Argopecten purpuratus | 0 | 0 | 0 |
| Mytilus edulis | 0 | 0 | 29 |
| Mytilus galloprovincialis | 0 | 0 | 42 |
| Perna canaliculus | 0 | 0 | 1 |
| Mytilus chilensis | 0 | 0 | 0 |
| Ensis directus | 0 | 0 | 1 |
| Ensis arcuatus | 0 | 0 | 0 |
| Ensis minor | 0 | 0 | 0 |
| Siliqua patula | 0 | 0 | 0 |
| Solen strictus | 0 | 0 | 3 |
| Tegillarca granosa | 0 | 0 | 27 |
| Anadara broughtonii | 0 | 0 | 4 |
| Mercenaria mercenaria | 0 | 0 | 0 |
| Triticum aestivum | 0 | 0 | 1497 |
| Oryza sativa | 0 | 0 | 435 |
| Zea mays | 0 | 0 | 544 |
| Avena sativa | 0 | 0 | 454 |
| Sorghum bicolor | 0 | 0 | 258 |
| Cenchrus americanus | 0 | 0 | 8 |
| Eleusine coracana | 0 | 0 | 400 |
| Secale cereale | 0 | 0 | 39 |
| Hordeum vulgare | 0 | 0 | 324 |
| Prunus dulcis | 0 | 0 | 135 |
| Juglans regia | 0 | 0 | 114 |
| Anacardium occidentale | 0 | 0 | 5 |
| Pistacia vera | 0 | 0 | 5 |
| Corylus avellana | 0 | 0 | 105 |
| Linum usitatissimum | 0 | 0 | 6 |
| Salvia hispanica | 0 | 0 | 1 |
| Cucurbita maxima | 0 | 0 | 110 |
| Helianthus annuus | 0 | 0 | 300 |
| Papaver somniferum | 0 | 0 | 184 |
| Sesamum indicum | 0 | 0 | 152 |
| Sinapis alba | 0 | 0 | 6 |
| Arachis hypogaea | 0 | 0 | 285 |
| Glycine max | 0 | 0 | 297 |
| Pisum sativum | 0 | 0 | 194 |
| Cicer arietinum | 0 | 0 | 130 |
| Phaseolus vulgaris | 0 | 0 | 222 |
| Lens culinaris | 0 | 0 | 8 |
| Vicia faba | 0 | 0 | 162 |
| Phaseolus lunatus | 0 | 0 | 5 |
| Vigna unguiculata | 0 | 0 | 181 |
| Lupinus albus | 0 | 0 | 200 |
| Vigna radiata | 0 | 0 | 179 |
| Cajanus cajan | 0 | 0 | 77 |
| Vigna subterranea | 0 | 0 | 1 |
| Solanum tuberosum | 0 | 0 | 384 |
| Ipomoea batatas | 0 | 0 | 63 |
| Colocasia esculenta | 0 | 0 | 159 |
| Manihot esculenta | 0 | 0 | 187 |
| Dioscorea cayenensis | 0 | 0 | 1 |
| Brassica oleracea | 0 | 0 | 46 |
| Spinacia oleracea | 0 | 0 | 29 |
| Brassica rapa | 0 | 0 | 28 |
| Lactuca sativa | 0 | 0 | 42 |
| Musa acuminata | 0 | 0 | 36 |
| Musa balbisiana | 0 | 0 | 22 |
| Musa paradisiaca | 0 | 0 | 0 |
| Homo sapiens | 0 | 0 | 47 |

## Known issues / caveats

- **Mixed-date UniProt snapshot.** See "UniProt data retrieval" above: proteomes were fetched on three different dates (and the log covers only the last), so this is not a single UniProt snapshot. Release 1.1.2 is the first built from one fresh download.
- **Large repetitive proteins are incompletely represented.** Titin and nebulin gene models are fragmentary or mis-clustered in several non-human species, and the human reference is canonical isoforms only (e.g. TTN: 1 of 13 UniProt isoforms; NEB: 1 of 4). For MS/MS food authentication, search against all human isoforms and treat titin-derived matches with caution.
- **Reprocessed with the final pipeline (13 Oct 2026).** This release was built a second time from the same UniProt files and the same input (checksum identical) with pipeline commit `3a61cc0`, so that its step summaries exist in the same form as every later release, and so that release 1.1.2 can be compared with it like for like. Compared with the original build of 21-22 Sep 2026, the candidate set is identical (10,137 of 10,137 candidates, same order), as are the OrthoFinder statistics (88,189 genes, 87,192 in orthogroups, 972 orthogroups), the fallback counts (127 rescued; 784 / 50 / 50,811 declined) and the signal-peptide count (5,250). Two rows differ in which homologs they report: chicken ubiquitin B (`A0A1D5P546`) reports the same human homolog at the same 100% identity, but via the dense-family fallback instead of OrthoFinder orthology; and a rice lipid-transfer protein (`A0A0E0HY60`) lost one of 24 co-orthologous group members, a wheat paralog at 31.7% identity at the edge of DIAMOND's significance threshold. Both are the pipeline's known run-to-run variation in tree-based orthology and in borderline hits, not a change in the pipeline.
