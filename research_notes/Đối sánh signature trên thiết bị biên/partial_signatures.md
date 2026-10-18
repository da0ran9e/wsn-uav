# Partial signature sets: how accuracy drops when a node holds 4/5 or 3/5 reference files

Scope: a UAV delivers 3–5 signature files (about one 512-d fp16 embedding each; each a different view or condition of the target). A camera node matches its own crops against the files it holds and answers YES when the score passes a threshold. Question: what happens to recall at a fixed false-alarm rate when 1 or 2 files are missing, and does it matter which one is missing?

Research budget note: about 15 tool calls. Several primary PDFs (Market-1501 ICCV 2015, NIST reports) could not be parsed in this environment, so some numbers are second-hand from later papers that reprint them. This is flagged per line.

## Q1. Accuracy vs number of reference images/templates per identity (person re-ID, face, vehicle, animal)

### Takeaway
Going from 1 image to several images per identity is worth a lot: about +6 Rank-1 and +10 mAP on Market-1501, about +19 % verification score on IJB-A, and about half the verification error in FRVT 2002. Most of the gain comes in the first ~3–4 images, then it flattens. So 5→4→3 sits on the flat part of the curve, as long as the remaining files still cover the views the camera sees.

### Cited Findings
- **Market-1501, single query vs multiple query (ResNet-50, Zheng, Zheng & Yang, ACM TOMM 2017):** Rank-1 79.51 → 85.84 and mAP 59.87 → 70.33 when all query images of the person from the same camera are used instead of one. ResNet-50 baseline: 73.69 → 81.47 R1, 51.48 → 63.95 mAP. VGG16 baseline: 65.02 → 74.14 R1, 38.27 → 52.25 mAP. Measured. — [Zheng et al., arXiv 1611.05666, Table III](https://ar5iv.labs.arxiv.org/html/1611.05666)
- The multi-query protocol and its average vs max pooling variants (MultiQ_avg, MultiQ_max) come from the original Market-1501 paper. I could not extract its own pooling numbers here. — [Zheng et al., ICCV 2015](https://openaccess.thecvf.com/content_iccv_2015/papers/Zheng_Scalable_Person_Re-Identification_ICCV_2015_paper.pdf); pooling variants named in [Su et al., arXiv 1605.03259](https://arxiv.org/pdf/1605.03259)
- **IJB-A (face templates, Crosswhite et al., "Template Adaptation", FG 2017):** the verification score at FAR 1e-2 rises by about 19 % from 1 media per template to 64. The authors write that "performance saturates at about 3 media per template". Mated similarity rises with template size, but its variance stays about the same. Single-media templates show the largest uncertainty. Measured, but the per-bin values are only in Fig. 5. — [Crosswhite et al., arXiv 1603.03958](https://ar5iv.labs.arxiv.org/html/1603.03958)
- IJB-A templates range from 1 image up to about 190–202 media, averaging about 11.4 images and 4.2 videos per subject. Sources disagree on the maximum. — [search summary of IJB-A papers, e.g. arXiv 1603.03958 / 1607.01450](https://arxiv.org/pdf/1607.01450)
- **NIST FRVT 2002 (supplemental, NISTIR 7083):** "Fusion of four scores from five images per person cuts verification error rates by about half." Measured, but from an old algorithm generation. — [NISTIR 7083](https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7083.pdf)
- **NIST FRVT 1:N (2021):** the error reduction is larger for "recent" enrolments than for "lifetime consolidated" (multi-image) ones, so accuracy on recent images is now better. Fresh, relevant images matter more than more images. — [FRVT 1:N report 2021-03-04](https://pages.nist.gov/frvt/reports/1N/frvt_1N_report_2021_03_04.pdf)
- ICAO/NIST travel presentation: "Accuracy better with multiple images; single image is a lower bound on accuracy." — [ICAO TRIP 2021](https://www.icao.int:443/Meetings/TRIP-Symposium-2021/PublishingImages/Pages/Presentations/Face%20Recognition%20in%20Travel%20Contexts.pdf)
- **MARS video re-ID, frames per tracklet (WACV 2023 supplement, one CNN setup):** Rank-1 75.0 at 2 frames, 79.8 at 4 frames, 78.6 at 8 frames. Performance "does not differ significantly" beyond 4 frames. The average MARS tracklet has about 59 frames. — [Mekhazni et al., WACV 2023 supplemental](https://openaccess.thecvf.com/content/WACV2023/supplemental/Mekhazni_Camera_Alignment_and_WACV_2023_supplemental.pdf); [CVPR 2020 supplemental, MGRA](https://openaccess.thecvf.com/content_CVPR_2020/supplemental/Zhang_Multi-Granularity_Reference-Aided_Attentive_CVPR_2020_supplemental.pdf)
- **Animals:** WildlifeDatasets / MegaDescriptor (WACV 2024) evaluates with a reference (database) set vs a query set across 29 datasets. I found no per-identity reference-count ablation. — [Čermák et al., WACV 2024](https://openaccess.thecvf.com/content/WACV2024/html/Cermak_WildlifeDatasets_An_Open-Source_Toolkit_for_Animal_Re-Identification_WACV_2024_paper.html). Algasov et al. study training-set size (500/1000/2000 images per species, 5 species, 6 methods), not reference-set size. — [arXiv 2405.15976](https://arxiv.org/html/2405.15976v1)

### Inferences
- The 1 → many gain (6–10 points on person re-ID, about 19 % on face, about 2× lower error in FRVT 2002) is an **upper bound** on what 5 → 1 costs. Because the curve saturates at about 3–4 items (IJB-A: about 3 media; MARS: about 4 frames), 5 → 4 and 5 → 3 should cost only a small fraction of it **when the views are redundant**.
- Caveat: the Market multi-query and MARS frames are mostly same-camera, near-duplicate views. They measure noise averaging more than view coverage, which is the redundant-view case (i). They say nothing about case (ii).

### Gaps
- No source gives a clean curve over exactly 1, 2, 3, 4, 5 distinct-view references per identity for person, vehicle or animal re-ID.
- I could not extract the per-bin IJB-A TAR values (Fig. 5 only) or the Market-1501 ICCV 2015 MultiQ_avg/max numbers (PDF parsing failed).
- No IJB-B/C template-size or NIST FRTE (2023–2026) multi-enrolment numbers were retrieved.
- Animal re-ID (ATRW, chimpanzee, cattle) reference-count curves: none found.

## Q2. Viewpoint dependence: is the query view present in the reference set or not?

### Takeaway
Losing the reference whose view matches the camera costs much more than losing a redundant one. In-domain the drop is small: about 1–3 mAP points for persons and 2–6 for vehicles. Out-of-domain (vehicle types not seen in training) it is large: about 20–30 mAP points, or 30–45 % relative. Low resolution roughly doubles the person-re-ID penalty.

### Cited Findings
- **Sun & Zheng, "Dissecting Person Re-identification from the Viewpoint of Viewpoint", CVPR 2019 (PCB model):** removing the true matches within ±10/20/40° of the query viewpoint gives a "non-trivial performance drop" compared with removing the same number at random. Measured values:
  - **Market-1203 (real):** about 3.0 % lower mAP than the random-removal control when 3 or 5 similar-view true matches are removed.
  - **PersonX45 (synthetic):** removing 9 similar-view matches gives 96.6 % mAP, about 1.0 % below the control.
  - **PersonX46-lr (low resolution):** the drop is "almost twice" that on PersonX46.
  - Harder conditions (complex background, extreme light, low resolution) increase the effect.
  - [arXiv 1812.02162 / CVPR 2019](https://ar5iv.labs.arxiv.org/html/1812.02162)
- Same paper: Rank-1 peaks when the true match has the same viewpoint as the query. Side (left/right) queries do better than front/back: average Rank-1 is 93.8 % for due left and 91.7 % for due front (PersonX45). With one training orientation, left or right beats front or back by up to 6 % mAP. — [same](https://ar5iv.labs.arxiv.org/html/1812.02162)
- **Ben Mabrouk et al., "Generalization Limits in Vehicle Re-Identification", arXiv 2606.01981 (June 2026, preprint):** mAP with a Same-View gallery vs a Different-View gallery (front and rear swapped).

  | Model | VeRi-776, seen types: same → different view | VeRi-776, unseen types: same → different view |
  |---|---|---|
  | TransReID | 93.1 → 89.7 | 66.5 → 46.6 |
  | ClipReID | 93.8 → 91.6 | 69.4 → 44.9 |
  | RotTrans | 94.9 → 88.9 | 68.8 → 44.5 |

  On VeRI-Wild, unseen types drop from 80.4 / 79.6 / 84.2 to 50.2 / 51.8 / 56.6. The paper reports mAP only, because Rank-1 is saturated. — [arXiv 2606.01981](https://arxiv.org/html/2606.01981)
- The same paper argues that same-view matching relies on details (stickers, scratches, logos), while different-view matching must fall back on view-invariant cues such as colour, so it is "inherently ambiguous". — [same](https://arxiv.org/html/2606.01981)
- VeRi-776 viewpoint-aware work states that very different appearance across viewpoints makes matching the same vehicle fail, which motivates viewpoint-conditioned attention. — [Chen et al., CVPRW 2020](https://openaccess.thecvf.com/content_CVPRW_2020/html/w35/Chen_Viewpoint-Aware_Channel-Wise_Attentive_Network_for_Vehicle_Re-Identification_CVPRW_2020_paper.html)

### Inferences
- For our system the camera's viewpoint is fixed (a doorbell sees fronts, a street camera sees sides or backs). If the one file whose view matches that camera is lost, the node effectively changes from "same-view" to "different-view" matching. The vehicle numbers put that at −2 to −6 mAP in-domain and −20 to −25 mAP (about 30–35 % relative) when the target class is outside the training distribution. A lost-child or suspect query on generic IoT cameras is closer to the out-of-domain case.
- A night or clothing-change file is a "condition" rather than a view. No source here measures losing the condition-matching reference. I assume it behaves like the view case (large drop when it is the only match). This is unmeasured.
- Side views are the most informative single references for persons (Sun & Zheng). If a node can keep only some files, keep the side views.

### Gaps
- No person- or face-domain study measures "query view absent from a *multi-view reference set*" at the identity level beyond the ±10–40° removal experiment.
- No TAR@FAR (as opposed to mAP) numbers for the missing-view condition.
- Animal viewpoint dependence (e.g. left vs right flank for tigers or zebras, which are not mirror images) is known in practice, but I retrieved no numbers.

## Q3. Aggregation: max vs mean similarity, and the effect of removing one reference

### Takeaway
Feature averaging (mean template) is the standard and the best aggregation on IJB-A, with winner-take-all (max) a close second. For a view-diverse reference set, max-over-references is the natural rule. Under max, removing a file can only lower or keep both genuine and impostor scores, so at a fixed threshold false alarms do not rise; only recall falls.

### Cited Findings
- Crosswhite et al. average media encodings and then templates, followed by unit normalisation. Averaging margins instead "performed consistently worse than computing average feature encodings". In classifier fusion, average fusion was best and winner-take-all a close second. No numbers are given in the text. — [arXiv 1603.03958](https://ar5iv.labs.arxiv.org/html/1603.03958)
- Market-1501 defines multi-query by average or max pooling of query features (MultiQ_avg, MultiQ_max). — [Zheng et al., ICCV 2015](https://openaccess.thecvf.com/content_iccv_2015/papers/Zheng_Scalable_Person_Re-Identification_ICCV_2015_paper.pdf); [arXiv 1605.03259](https://arxiv.org/pdf/1605.03259)
- Learned set aggregators (NAN, GhostVLAD, dependency-aware attention) exist because plain averaging over-weights low-quality members. — [NAN, arXiv 1603.05474](https://arxiv.org/pdf/1603.05474); [GhostVLAD, arXiv 1810.09951](https://arxiv.org/pdf/1810.09951)

### Inferences (derived, not measured)
- **Max rule, s = max_k cos(q, r_k):**
  - Removing a file changes the score only if that file held the max. With redundant views that happens about 1/n of the time, and even then the next-best score is close, so the drop is small.
  - If the removed file is the only view-matching one, s falls to the cross-view score, which is the Q2 drop.
  - Since s cannot increase for impostors either, the FAR at a threshold calibrated on 5 files stays the same or goes down. The cost is all in recall.
- **Mean template, s = cos(q, mean_k r_k):**
  - Removing a non-matching view can *raise* the genuine score, because the template moves toward the remaining views.
  - Removing the matching view lowers it.
  - Impostor scores can move either way, so a threshold calibrated on 5 files is no longer guaranteed to hold its FAR on 4 or 3 files. For a fixed 70–90 % threshold on view-diverse files, max (or top-k mean) is the safer choice.
- A node can scale its threshold by the number of files it holds, using offline calibration per count n ∈ {3, 4, 5}. Under max, the impostor score distribution shifts down as n falls, so the threshold could be lowered slightly to recover recall at the same FAR.

### Gaps
- No published numbers for max vs mean when a single reference is removed from a multi-view set.

## Q4. Expected drop in recall at fixed false-alarm rate, 5 → 4 and 5 → 3 files

### Takeaway
Defensible planning numbers:
- **Redundant views:** about 0–2 points (5→4) and 1–4 points (5→3).
- **Missing the only view-matching file:** about 2–6 points in-domain and about 15–25 points out-of-domain or at low resolution, regardless of 4 or 3 remaining files.

So *which* file is missing matters more than *how many*.

### Cited Findings (the anchors for the table)
- 1 → many-image gain: about +6 R1 / +10 mAP on Market-1501 ([arXiv 1611.05666](https://ar5iv.labs.arxiv.org/html/1611.05666)), about +19 % verification at FAR 1e-2 on IJB-A, saturating at about 3 media ([arXiv 1603.03958](https://ar5iv.labs.arxiv.org/html/1603.03958)), and about 2× lower error with five images in FRVT 2002 ([NISTIR 7083](https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7083.pdf)).
- MARS plateau from 4 frames: 79.8 at 4 frames vs 75.0 at 2. — [WACV 2023 supp.](https://openaccess.thecvf.com/content/WACV2023/supplemental/Mekhazni_Camera_Alignment_and_WACV_2023_supplemental.pdf)
- Missing-view drop: persons −1 to −3 mAP, about 2× at low resolution ([Sun & Zheng CVPR 2019](https://ar5iv.labs.arxiv.org/html/1812.02162)); vehicles −2 to −6 mAP on seen types and −20 to −25 mAP on unseen types ([arXiv 2606.01981](https://arxiv.org/html/2606.01981)).

### Table (all rows EXTRAPOLATED from the measured anchors above; no paper measures exactly 5→4→3 distinct-view files)

| Case | Domain | 5 → 4 files: recall@fixed FAR | 5 → 3 files: recall@fixed FAR | Basis |
|---|---|---|---|---|
| (i) Missing files are redundant views (camera's view still present) | person, face, vehicle | −0 to −2 pts | −1 to −4 pts | Saturation at about 3–4 items (IJB-A, MARS); the full 1→multi gain is only 6–10 pts / 19 %, and 5→3 is on the flat part |
| (ii) Missing file is the only one matching the camera's view or condition, in-domain model, clear crops | person | −1 to −3 pts (mAP-measured) | same as 5→4 if the second loss is redundant; else add (i) | Sun & Zheng: −1 % (PersonX), −3 % (Market-1203) |
| (ii) same | vehicle | −2 to −6 pts | same | Ben Mabrouk 2026, seen types |
| (ii) Missing matching view, out-of-domain or low resolution | vehicle, person in the wild, animal | −15 to −25 pts (≈ 30–35 % relative) | same or worse | Ben Mabrouk 2026, unseen types (−20 to −25 mAP); Sun & Zheng low-res ×2 |
| (iii) Both missing files include the matching view and the next-closest view | any | n/a | ≈ case (ii) plus −2 to −5 pts | extrapolated |

Conversion caveat: the anchors are mostly **mAP or Rank-1, not TAR@FAR**. Treating a mAP-point drop as an equal recall@FAR drop is an assumption. At strict FAR (1e-3 or lower), the drop in TAR is usually larger than the drop in mAP, so these values are optimistic at the strict end.

### Inferences
- Model for the simulator, with p_view the probability that the lost file is the one matching this camera's view:
  - **For 5→4:** recall_4 ≈ recall_5 − [(1 − p_view)·δ_red + p_view·δ_view]
  - **For 5→3:** recall_3 ≈ recall_5 − [2·δ_red + P(view file lost)·δ_view], with P(view file lost) = 2/5 if losses are uniform.
  - **Values:** δ_red ≈ 1 pt and δ_view ≈ 4 pts in-domain or 20 pts out-of-domain.
  - **Which files get lost:** in our delivery model losses are not uniform. A file is lost when its packet run is broken, so later files in the broadcast order, or files sent near the River edge, are lost more often.
- Design implications:
  - Order the files so that the most view-general one (for persons, the side view) is broadcast where delivery is most reliable.
  - Use max aggregation, so that losing files never raises false alarms.
  - Treat "3 files with the camera's view" as better than "4 files without it". Nodes could report which views they hold, not just how many.

### Gaps
- No direct measurement of TAR@FAR vs number of *distinct-view* references (1–5) for any domain. This is the key experiment to run offline (for example on Market-1203 with viewpoint labels, VeRi-776 with viewpoint labels, or a WildlifeDatasets species with flank labels) before quoting these numbers in a paper.
- Animal-domain numbers are entirely extrapolated.
- Face NIST FRTE (2023–2026) multi-enrolment figures not retrieved.
