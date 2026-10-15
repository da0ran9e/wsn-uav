# Signatures per target and coarse-to-fine query organisation (Q5 and Q9)

Context: a UAV broadcasts the query over IEEE 802.15.4 with 99 B payload per frame. A file is usable only when it arrives complete. This note collects evidence on (Q5) how many reference images or templates one target needs, and (Q9) whether the query can be layered so that partial reception is still useful.

How the sources were checked: the NAN (CVPR 2017), Matryoshka (NeurIPS 2022) and NIST IR 8381 numbers were read from the full PDF text. Items marked "(snippet)" come from search-result summaries of the cited paper. Verify those against the paper before putting them in the paper.

## Q5a — Recognition accuracy vs number of reference images or frames per subject

### Takeaway
Going from one reference image to a set of several images gives a clear but modest gain. NIST measured about a 10x error reduction for the best algorithm. Video re-ID saturates at about 4 frames. Gait recognition loses about 1 point of normal-walking accuracy going from 20 frames down to 10. The algorithm and aggregation method matter more than raw image count. Several views/images, not dozens, appears sufficient. No source gives a clean "N images → accuracy" saturation curve for faces.

### Cited Findings

**Face, NIST 1:N (official evaluation)**

| Setting | Single image enrolled | About 6 images enrolled (average, variable) | Source |
|---|---|---|---|
| NEC-3, gallery N = 420 (border EXIT vs ENTRY) | 98.7 % correctly identified | 99.0 % | [NIST IR 8381 draft suppl.](https://pages.nist.gov/frvt/reports/travel/frvt_travel_report.pdf) |
| Visionlabs-10 (most accurate) | 99.9 % | 100 % ("about a factor of 10 fewer errors than NEC-3") | same |
| Flights boarded with zero false negatives (567 simulated flights of 420 passengers) | up to 428 / 567 | 545 / 567 (best algorithm) | same |
| Algorithms reaching > 99.5 % of travellers | 7 algorithms | at least 18 developers' algorithms | same |

- NIST's own summary: the algorithm effect "dominates two other main effects": first, that more enrolment images per person improves accuracy, and second, that a 100-fold gallery increase (420 → 42 000) degrades accuracy "only modestly". At 42 000 identities, errors are often about 3x those at 420. — [NIST IR 8381](https://nvlpubs.nist.gov/nistpubs/ir/2021/NIST.IR.8381.pdf), [travel report](https://pages.nist.gov/frvt/reports/travel/frvt_travel_report.pdf)
- The NIST ongoing 1:N API allows K ≥ 1 images per enrolled identity. It notes that multiple images raise accuracy over a single image. — [FRVT 1:N API](https://pages.nist.gov/frvt/api/FRVT_IREX_ongoing_1N_api.pdf)

**Face, set-to-set (IJB-A / YTF), from NAN (Yang et al., CVPR 2017; full text read)**
- IJB-A has 500 subjects, 5 397 images and 2 042 videos, with on average 11.4 images and 4.2 videos per subject. It has full pose variation. — [NAN, arXiv 1603.05474](https://arxiv.org/abs/1603.05474)
- YTF has 3 425 videos of 1 595 people, with 48–6 070 frames per video (mean 181.3). — same

| Aggregation of a template (IJB-A) | TAR@FAR=1e-3 | TAR@FAR=1e-2 | TPIR@FPIR=1e-2 | Rank-1 |
|---|---|---|---|---|
| CNN + MaxPool | 0.202 | 0.345 | 0.079 | 0.757 |
| CNN + Min L2 (best single pair) | 0.038 | 0.144 | 0.026 | 0.853 |
| CNN + Mean L2 (all pairs) | 0.688 | 0.895 | 0.514 | 0.916 |
| CNN + AvePool (one averaged embedding) | 0.771 | 0.913 | 0.634 | 0.931 |
| CNN + AvePool†, two-level: average within each media item, then across items | 0.856 | 0.935 | 0.793 | 0.951 |
| NAN (learned attention weights) | 0.860 | 0.933 | 0.804 | 0.954 |
| NAN† | 0.881 | 0.941 | 0.817 | 0.958 |
— [NAN Table 2](https://arxiv.org/abs/1603.05474)

- On YTF (low variation within a video): AvePool 95.20 %, Mean L2 95.30 %, NAN 95.72 %, MaxPool 88.36 %. The authors say gains are smaller because "face variations in this dataset are relatively small", so few frames carry new information. — [NAN Table 3](https://arxiv.org/abs/1603.05474)
- NAN's aggregated vector "is of the same dimension as a single feature", whatever the number of inputs. — same

**Person re-ID (body appearance)**
- Market-1501: multi-query (several images of the same person from the same camera, average or max pooled) beats single-query. HA-CNN goes from 91.2 % R1 / 75.7 % mAP to 93.8 % / 82.8 %, and Gated S-CNN from 65.88 % / 39.55 % to 76.04 % / 48.45 %. — [MGN paper table, arXiv 1804.01438](https://arxiv.org/pdf/1804.01438); [DML, arXiv 1706.00384](https://arxiv.org/pdf/1706.00384) (snippet)
- MARS video re-ID, frames per tracklet (snippet; verify):

| Frames | R1 | mAP |
|---|---|---|
| 2 | 75.0 | 81.8 |
| 4 | 79.8 | 84.9 |
| 8 | 78.6 | 84.6 |

  The authors say accuracy "is stable from 4 frames per tracklet". — [Mekhazni et al., WACV 2023 supplementary](https://openaccess.thecvf.com/content/WACV2023/supplemental/Mekhazni_Camera_Alignment_and_WACV_2023_supplemental.pdf)
- MARS tracklets are 2–920 frames long (mean about 59.5). — [arXiv 2009.04181](https://arxiv.org/pdf/2009.04181) (snippet)

**Gait**
- GaitSet reaches 82.5 % on CASIA-B with only 7 frames (AAAI 2019 version) and 85.0 % with 7 frames (TPAMI version). Full sequences give 95.0 % / 96.1 % on normal walking. — [GaitSet AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/4821); [TPAMI arXiv 2102.03247](https://arxiv.org/abs/2102.03247v1) (snippet)
- Another study with GaitSet at 10 vs 20 input frames (snippet):

| Frames | NM (normal) | BG (bag) | CL (clothing change) |
|---|---|---|---|
| 10 | 94.0 % | 86.9 % | 62.7 % |
| 20 | 94.7 % | 87.9 % | 68.3 % |

  The clothing-change condition is the hardest and the most sensitive to frame count. — [PMC7959613 Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC7959613/table/table-1)

### Inferences
- Diminishing returns are reached early. Video re-ID saturates at about 4 frames. NIST's average of about 6 enrolment images already removes about 90 % of single-image errors for top algorithms. NAN shows a well-aggregated set of about 11 images plus 4 videos (IJB-A) is near ceiling. A reasonable working assumption for the simulation is 3–6 diverse reference views per target. This is our extrapolation, not a measured curve.
- Diversity matters more than count. On YTF (redundant frames) the set gain is tiny, while on IJB-A (pose variation) it is large. Pick views that differ (frontal, profile or ¾ view, full body, other clothing or other illumination) rather than consecutive frames.
- Aggregation choice is critical. MaxPool or "best single pair" can be catastrophically worse than averaging at low FAR (0.04–0.20 vs 0.77 TAR@1e-3). If several references are sent, the node should average them, or average within condition and then across conditions (the AvePool† pattern), rather than taking the max similarity.
- Byte budget (our arithmetic, 99 B frames): one 512-d float32 embedding is 2 048 B ≈ 21 frames, fp16 is 1 024 B ≈ 11 frames, int8 is 512 B ≈ 6 frames. Because NAN/average pooling yields one vector the size of a single feature, a pre-aggregated template costs the same as one image's embedding. Several prototypes (for example one per condition) cost k times that.

### Gaps
- No explicit published curve of face accuracy vs exactly 1/3/5/10/20 enrolment images was retrieved. The IJB-B (Whitelam 2017) and IJB-C (Maze 2018) papers and the NIST FRTE 1:N main report (IR 8271) were not read. IJB-C has 138k face images and 11k videos, with 3 531 subjects per the [NIST readme](https://www.nist.gov/document/readmepdf-1). One interface page lists 1 845, which is likely the IJB-B count, so the sources conflict.
- QAN, MagFace quality weighting and IJB-S (surveillance video) numbers were not retrieved.
- Day vs IR-night cross-spectral effects were not covered by retrieved sources. Clothing change is only covered through gait (CL condition 62.7–68.3 %, vs about 94 % normal walking).

## Q5b — Template aggregation: one averaged vector vs several prototypes

### Takeaway
A learned quality-weighted average (NAN) slightly beats plain averaging. Plain averaging already captures most of the gain. Two-level averaging (within each media item, then across items) closes most of the remaining gap. One aggregated vector is the byte-cheapest option and is near-best.

### Cited Findings
- NAN vs AvePool on IJB-A: TAR@1e-3 0.860 vs 0.771. With media-level two-stage pooling: 0.881 (NAN†) vs 0.856 (AvePool†). — [NAN](https://arxiv.org/abs/1603.05474)
- NAN with cascaded attention beats single attention: TAR@1e-3 0.860 vs 0.847, TPIR@1e-2 0.804 vs 0.778. — [NAN Table 1](https://arxiv.org/abs/1603.05474)
- NAN "favors high-quality" face images and down-weights blurred, occluded or extreme-pose ones. — same

### Inferences
- For the query, sending one quality-aggregated embedding per target (and per strongly different condition, if needed) is a defensible design. The node-side matching is a single dot product per stored crop.

### Gaps
- No numbers retrieved for MagFace, QAN or multi-prototype vs single-average comparisons under clothing or spectral change.

## Q9a — Can the query be layered coarse → fine? (attributes → short embedding → full embedding)

### Takeaway
Yes. Matryoshka Representation Learning shows that a prefix of one embedding is almost as accurate as the full vector: 16 of 2048 dims loses about 3 points of 1-NN accuracy, and 64 dims loses under 1 point. A funnel cascade 16 → … → 2048 matches full-dimension retrieval at about 128x less compute. Attributes alone are a weak identifier (Rank-1 about 47–49 %). They are useful as a cheap filter but not as the final decision.

### Cited Findings

**Matryoshka (Kusupati et al., NeurIPS 2022; full text read), ResNet-50 on ImageNet-1K**

| Dims (prefix) | MRL linear top-1 % | MRL 1-NN % | FF (separately trained) 1-NN % | Truncated plain FF-2048, first k dims ("Rand. FS"), 1-NN % |
|---|---|---|---|---|
| 8 | 66.63 | 62.19 | 58.93 | 2.36 |
| 16 | 73.53 | 67.91 | 66.77 | 12.06 |
| 32 | 75.03 | 69.46 | 68.84 | 32.91 |
| 64 | 75.82 | 70.17 | 69.41 | 49.91 |
| 128 | 76.30 | 70.52 | 69.35 | 60.91 |
| 256 | 76.47 | 70.62 | 69.72 | 65.75 |
| 512 | 76.65 | 70.82 | 70.18 | 68.77 |
| 2048 | 76.80 | 70.97 | 71.19 | 71.19 |
— [MRL, arXiv 2205.13147, Tables 1–2](https://arxiv.org/abs/2205.13147)

- Key caveat: an ordinary embedding cannot be truncated. Taking the first 16 dims of a non-MRL model gives 12 % vs 68 % for MRL. Layering must be designed in at training time, or done with SVD/PCA (SVD-16: 46.02 %). — same, Table 2
- Funnel retrieval: a shortlist cascade 200 → 100 → 50 → 25 → 10 with representation sizes 16 → 32 → 64 → 128 → 256 → 2048 "is as accurate as the single-shot 2048-dim retrieval while being ~128x more efficient theoretically". Adaptive retrieval gives about 14x wall-clock speed-up. — [MRL §4](https://arxiv.org/abs/2205.13147)
- Shortlist k = 200 with D_s = 8 dims, re-ranked with D_r = 128: top-1 70.34 %, about equal to full 2048-dim search (MRL-E 71.17 %). — MRL Table 11
- Up to 14x smaller embedding for the same classification accuracy (adaptive classification). — MRL abstract

**Coarse attributes (pedestrian attribute recognition, PAR)**

| Dataset | Size | Attributes | Example mA |
|---|---|---|---|
| PA-100K | 100k images | 26 | DAFL 83.54, VTB 83.72; a 2025 hypergraph method 87.95 |
| PETA | 19k images | 35 evaluated | DAFL 87.07, VTB 85.31; hypergraph 88.50 |
| RAP v1 | 41 585 images | 51 | — |
| RAPv2 | — | — | hypergraph 83.02 |

  Sources: [arXiv 2604.26873](https://arxiv.org/pdf/2604.26873), [arXiv 2509.22331](https://arxiv.org/pdf/2509.22331), [Rethinking PAR, arXiv 2005.11909](https://arxiv.org/pdf/2005.11909) (snippets; protocols differ across papers).
- PETA and RAPv1 have identity overlap between train and test, so PA-100K numbers are considered more reliable. — [Rethinking PAR](https://arxiv.org/html/2005.11909v2)

**Attribute-only search (query = attribute vector, gallery = images), SAL (ECCV 2020)**

| Dataset | Attributes | SAL R1 | R5 | R10 | mAP | Prior best |
|---|---|---|---|---|---|---|
| Market-1501 | 27 | 49.0 | 68.6 | 77.5 | 29.8 | AIHM R1 43.3 / mAP 24.3 |
| PETA | 65 | 47.0 | 66.5 | 74.0 | 41.2 | — |
— [SAL, arXiv 2007.09609](https://arxiv.org/html/2007.09609v2)

- Image-query search on Market-1501 reaches mAP 84.0 % vs 24.3 % for attribute queries. This is the cost of using attributes alone. — [SAL intro](https://arxiv.org/html/2007.09609v2)
- In the Market-1501 attribute test, about 26 training images on average share one attribute description. Identical attribute vectors cover many people, so attributes cannot discriminate individuals. — same

**Text-description search (richer than attributes, still no image)**
- IRRA (CVPR 2023) on CUHK-PEDES: R1 73.38, R5 89.93, R10 93.71, mAP 66.13. — [arXiv 2501.17586 table](https://arxiv.org/html/2501.17586); [CONQUER](https://arxiv.org/html/2601.18625)

**Compact codes (PQ / IVF-PQ) for the fine layer**
- Product quantization (Jégou et al., TPAMI 2011) splits the vector into sub-spaces and quantizes each. IVFADC adds a coarse inverted file, which is itself a two-stage coarse → fine search. — [PQ paper](https://paper-notes.zhjwpku.com/assets/pdfs/Product_Quantization_for_Nearest_Neighbor_Search.pdf)
- On SIFT1B, a Faiss IVF baseline with 2^18 cells gives Recall@100 ≈ 0.80 with 8-byte codes and ≈ 0.96 with 16-byte codes. — [arXiv 1901.00275](https://arxiv.org/pdf/1901.00275) (snippet)
- Quick ADC: Recall@100 0.94 with 128-bit codes on SIFT1B. — [arXiv 1704.07355](https://alphaxiv.org/abs/1704.07355) (snippet)

### Inferences
Proposed layered query per target, using our byte arithmetic for 99 B frames:

| Layer | Content | Size | Frames | Use when only this layer arrives |
|---|---|---|---|---|
| L0 | ID, timestamp window, attribute vector (about 26–65 bits: child/adult, gender, upper/lower colour, bag…) | ≤ 16 B | fits in 1 frame together with the header | Gallery pre-filter. Attribute-only R1 is only about 47–49 %, so flag candidates, never conclude |
| L1 | MRL prefix 64-d int8, or a 16 B PQ code | 16–64 B | 1 frame | Shortlist ranking. MRL-64 loses < 1 point of 1-NN vs full on ImageNet |
| L2 | Full aggregated embedding (512-d fp16) | about 1 KB | about 11 frames | Final match |
| L3 | Extra condition prototypes (profile, night, alternative clothing) | about 1 KB each | about 11 frames each | Robustness to view, illumination and clothing |

- With this layering, any complete prefix is usable. That matches the "file usable only if complete" rule: L0 and L1 are single-frame files with very high survival probability, while L2 and L3 are multi-frame files.
- Risk of dropping the true target with an attribute filter: PAR mA is about 84–88 %, so per-attribute error is about 12–16 %. A hard conjunction over many attributes would drop the true target often. Use soft scoring (rank by attribute agreement, keep the top-x %), or filter only on 2–3 high-confidence attributes (for example child/adult, clothing colour). This is our inference; no source gives the miss-rate of a hard attribute filter.
- MRL evidence comes from ImageNet classification and retrieval, not face or re-ID. MRL on face or person embeddings would need verification.

### Gaps
- No retrieved source quantifies what fraction of a surveillance gallery an attribute filter prunes, together with the resulting true-target miss rate.
- Residual VQ / progressive PQ accuracy-vs-stage tables were not retrieved. Only flat PQ figures are available.
- Matryoshka results on face recognition (IJB-C) or re-ID were not found.
- Scalable feature coding (MPEG CDVS/CDVA-type layered descriptors) was not covered.

## Q9b — Fountain vs layered vs independent files (brief)

### Takeaway
No source was retrieved that compares these schemes for query data. The comparison below is reasoning only.

### Cited Findings
- None retrieved in this session.

### Inferences
- **Independent files** (one view or embedding per file): each complete file is useful on its own. The loss of one file degrades gracefully, consistent with the set-aggregation results above. Fits the current "file = contiguous complete packets" rule best.
- **Layered (MRL prefix / attributes → embedding)**: gives a usable coarse result from the first complete layer. Small layers survive with high probability, but higher layers depend on lower ones only for meaning, not for decoding.
- **Fountain / rateless coding**: removes the "contiguous run" requirement. Any K(1+ε) packets recover the file, but you get nothing below the threshold, so it is all-or-nothing. It suits large fine layers (L2–L3), while L0–L1 are too small to need it. A hybrid is reasonable: L0/L1 sent uncoded and repeated, L2/L3 fountain-coded.

### Gaps
- No measured numbers on LT/Raptor overhead (ε) for small K over 802.15.4 were retrieved. They are needed before choosing a scheme.
