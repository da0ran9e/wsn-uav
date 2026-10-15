# Recall/precision with a partial reference set, and how to set match thresholds at the edge node

Scope: Q10 (accuracy vs fraction of references received, by representation, and vs gallery size) and Q16 (threshold policy, normalisation, fusion, what a node should report). The evidence is split into **[MEASURED]** (published numbers, with source) and **[MODEL]** (my extrapolation, labelled).

Caveat on retrieval: several primary PDFs (MegaFace full text, NIST IR 8271, Template Adaptation) could not be parsed in this session because no PDF tools were available. Where an exact table value was not readable, I quote only what the text states and list the rest under Gaps. Items tagged *(prior knowledge, not re-fetched)* are standard references I did not re-open this session. The report writer should verify those before quoting exact page or figure numbers.

## Q10a — Accuracy as a function of the fraction of reference images/signatures received, per representation

### Takeaway
No study varies "fraction of the query set received" directly. The nearest analogues all show strongly diminishing returns. In set-based face recognition, verification gains about 19 % from 1 to 64 media per template and levels off at about 3 media. In video re-ID on MARS, rank-1 saturates at about 4 frames per tracklet. So a node that holds 20 % of a 10–20-image reference set (2–4 images) keeps most of the recall of a node with 100 %. Representation precision matters more at the low end. A Matryoshka 8-d prefix keeps about 62 % 1-NN accuracy, while naive truncation of an ordinary embedding (SVD/random) collapses. Binary hash codes lose about 10–20 mAP points going from 64 to 16 bits.

### Cited Findings
**Set/template size (raw images → pooled embeddings) [MEASURED]**
- IJB-A templates range from 1 image up to about 190–202 media. The verification protocol has 10 splits of about 11,748 template pairs each (1,756 genuine, 9,992 impostor), scored as TAR at FAR = 1e-2 and 1e-3 — [Template Adaptation, Crosswhite et al., arXiv 1603.03958](https://arxiv.org/abs/1603.03958); [Pooling Faces, arXiv 1607.01450](https://arxiv.org/pdf/1607.01450)
- Template-size study (IJB-A, template pairs binned by max size (1,2)…(32,64)): the verification score at FAR 1e-2 "increases by about 19%" from one media per template to sixty-four. Performance levels off at about **3 media per template**. The mean mated similarity rises with template size, but the score spread does not shrink, and uncertainty is largest when the max template size is 1 — [Crosswhite et al., ar5iv 1603.03958 §4.5](https://ar5iv.labs.arxiv.org/html/1603.03958)
- MARS video re-ID, frames-per-tracklet ablation (supervised model): Rank-1 is about **75.0 % at 2 frames, 79.8 % at 4, 78.6 % at 8, 79.3 % at 16**. The authors say temporal information "stabilizes at 4 frames". The average MARS tracklet has about 59 frames — [Mekhazni et al., WACV 2023 supplemental](https://openaccess.thecvf.com/content/WACV2023/supplemental/Mekhazni_Camera_Alignment_and_WACV_2023_supplemental.pdf); [arXiv 2211.03626](https://arxiv.org/pdf/2211.03626); [Zhang et al. CVPR 2020 supp. (59 frames)](https://openaccess.thecvf.com/content_CVPR_2020/supplemental/Zhang_Multi-Granularity_Reference-Aided_Attentive_CVPR_2020_supplemental.pdf)
- Learned set aggregation (quality-weighted pooling, as in NAN) is the standard way to combine a variable number of references — [Neural Aggregation Network, arXiv 1603.05474](https://arxiv.org/pdf/1603.05474)

**Truncated float embeddings (Matryoshka prefixes) [MEASURED]**
- ResNet-50, ImageNet-1K, 1-NN accuracy at 8 / 16 dims: **MRL 62.19 / 67.91 %**; fixed-feature model trained at that dimension 58.93 / 66.77 %; **SVD of a 2048-d feature 19.14 / 46.02 %**; random feature selection 2.36 / 12.06 %. Values are read from the supplementary table, which extracted ambiguously, so verify them. Per the paper, MRL beats all baselines significantly at d ≤ 128 — [Kusupati et al., NeurIPS 2022 supplemental](https://papers.neurips.cc/paper_files/paper/2022/file/c32319f4868da7613d78af9993100e42-Supplemental-Conference.pdf); [Google Research page](https://research.google/pubs/matryoshka-representation-learning/)

**Binary hash codes, accuracy vs code length [MEASURED, third-party re-runs]**
- HashNet on NUS-WIDE (mAP@5000) at 16 / 32 / 48 / 64 bits: **0.588 / 0.677 / 0.722 / 0.725** — [DualHash, arXiv 2510.18218](https://arxiv.org/pdf/2510.18218)
- HashNet on ImageNet-100 (mAP@1000) at 16 / 32 / 48 / 64 bits: **0.506 / 0.630 / 0.663 / 0.683** — [Hashing with Binary Matrix Pursuit, arXiv 1808.01990](https://arxiv.org/pdf/1808.01990). An AlexNet re-run gives 41.2 / 54.3 / 58.8 / 62.5 — [Householder Quantization, arXiv 2311.04207](https://arxiv.org/pdf/2311.04207). Setups differ, so compare only within one source.

### Inferences
- **[MODEL] Recall vs fraction of references.** Take the template-size curve (+19 % from 1→64, saturating at about 3) and the MARS curve (−4.8 points at 2 frames vs 4; flat beyond 4). For a reference set of K ≈ 10–20 views of one target, a usable rule is: recall(f) ≈ recall(100 %) · (1 − c·e^{−fK/k₀}), with k₀ ≈ 2–3 views and c ≈ 0.15–0.2 (the gap between 1 view and many). Implied: f = 20 % of K = 15 gives 3 views, about 95 % of full recall. f = 50 % or more is essentially saturated. The steep loss is only at **1 view** (f ≲ 7 % for K = 15). This is extrapolated from face/person benchmarks, not measured for UAV-broadcast queries.
- **[MODEL] Diversity matters more than count.** The saturation happens because extra views are correlated. A "fraction" made of near-duplicate frames from one video is worth less than the same fraction made of diverse views. So the distribution layer should prioritise diverse views first in broadcast order. This fits the template-size result that variance does not shrink with size: more near-identical media do not reduce uncertainty.
- **[MODEL] Truncation is safe only if the embedding was trained for it (Matryoshka).** Truncating an ordinary embedding loses most of its accuracy at low dimension: SVD reaches 19 % at 8-d, versus 62 % for MRL. Low-bit hashing costs about 10–15 mAP points per halving below 32 bits.

### Gaps
- No published "partial template / incomplete enrollment" study varies the fraction of a query set and reports TAR/FAR. IJB-S, YouTube Faces and IJB-C per-template-size tables were not retrieved.
- The exact per-bin TAR values in Crosswhite et al. Fig. 5 exist only as a plot.
- No source found for face-specific (rather than ImageNet) Matryoshka/hashing accuracy vs dimension at fixed FAR.

## Q10b — Error rates vs gallery size (number of stored crops each node compares)

### Takeaway
False positives grow about **linearly** with the number of comparisons (NIST: FPIR ≈ N·FMR at high thresholds). Rank-1 identification also degrades steadily with distractors: in MegaFace, top 2016 algorithms fall from >95 % (LFW-scale) to 35–75 % at 10⁶ distractors. A node comparing k references against G stored crops is effectively running k·G comparisons, so its threshold must rise with k·G to keep a fixed false-alarm rate.

### Cited Findings
- NIST defines FNIR(N, R, T) and FPIR(N, T) as functions of enrolled gallery size N, threshold T and candidate rank R — [NIST FRVT 1:N report 2020](https://pages.nist.gov/frvt/reports/1N/frvt_1N_report_2020_02_26.pdf); [NISTIR 8271](https://nvlpubs.nist.gov/nistpubs/ir/2019/NIST.IR.8271.pdf)
- NIST binomial model: **FPIR(τ) = 1 − (1 − FMR(τ))^N ≈ N·FMR(τ)** at high thresholds — [NIST, Implications for 1:N (demographics supplement)](https://pages.nist.gov/frvt/reports/demographics/implications_for_1N.pdf)
- MegaFace (gallery 10 → 10⁶ distractors, FaceScrub/FGNET probes): "rates drop for all algorithms as the gallery size gets larger". Algorithms above 95 % on LFW (equivalent to 10 distractors) reach **35–75 % rank-1 at 1M distractors**; Joint-Bayes and LBP baselines fall to **<10 %**. At low FAR, FaceScrub verification drops about 40 % on average (about 15 % for FaceNet/FaceN), and FGNET about 60 % for all but FaceNet. Only FAR of 1e-5 to 1e-6 is meaningful at that scale — [Kemelmacher-Shlizerman et al., CVPR 2016 (ar5iv)](https://ar5iv.labs.arxiv.org/html/1512.00596); [CVF open access](https://openaccess.thecvf.com/content_cvpr_2016/papers/Kemelmacher-Shlizerman_The_MegaFace_Benchmark_CVPR_2016_paper.pdf)
- Later MegaFace rank-1 at 1M distractors (secondary survey table): FaceNet v8 **70.49 %**, NTechLAB 73.30 %, ArcFace 77.06 %. The MF2 benchmark's best team (GRCC) reached **75.77 %** — [EURASIP JIVP survey table](https://jivp-eurasipjournals.springeropen.com/articles/10.1186/s13640-020-00510-w/tables/5); [MF2, arXiv 1705.00393](https://arxiv.org/pdf/1705.00393). The 70.49 % value is not confirmed in the primary paper.
- Large-gallery face search: [Wang, Otto, Jain, "Face Search at Scale: 80 Million Gallery", arXiv 1507.07242](https://arxiv.org/pdf/1507.07242)

### Inferences
- **[MODEL] Node false-alarm budget.** A node with G stored crops and k received references, using max-score over all pairs, makes M = k·G comparisons. Per-node FPIR ≈ 1 − (1 − FMR(τ))^M. Example: G = 10⁴ crops, k = 20 refs gives M = 2·10⁵. At FMR = 1e-5, FPIR = 1 − e^{−2} ≈ **86 %**, so nearly every node raises a false alarm. To hold FPIR at 2 %, FMR must be about **1e-7**. A node with k = 4 (20 % of the set) needs FMR about 5e-7 for the same 2 %. **Fewer references means fewer comparisons, which allows a slightly lower per-comparison threshold for the same node-level false-alarm rate.** The cost is recall (Q10a).
- **[MODEL] Gallery size dominates over reference fraction.** G varies by orders of magnitude across nodes (a doorbell vs a 24/7 shop camera), while k varies by at most about 5×. G·k is therefore the main driver of false alarms, and it should be reported.
- **[MODEL] Cluster level.** If a cluster has n nodes each at FPIR_node, the cluster false-alarm probability is about 1 − (1 − FPIR_node)^n. This is the reason for the multiple-comparison control in Q16.

### Gaps
- The NIST FNIR-vs-N slopes (640K → 12M) and the "lifetime consolidated vs most-recent image" enrolment comparison were not readable here; the PDFs exceed fetch limits. Both are in NISTIR 8271 and should be pulled for exact values.
- Exact MegaFace per-distractor curves (10, 100 … 100K) exist only as plots.

## Q16a — Fixed global threshold vs per-node adaptive threshold; normalisation, quality, FDR control

### Takeaway
Do not let each node apply its own fixed raw-score threshold. The literature supports normalising scores (cohort/S-norm, with adaptive cohorts giving about 20 % relative EER gains in speaker verification) and converting them to **calibrated likelihood ratios**, the ENFSI-endorsed reporting form. Thresholding should be done centrally, at a fixed false-alarm or FDR target, with Benjamini–Hochberg across clusters. If a node must decide locally, its threshold should rise with the number of comparisons k·G (Neyman–Pearson at fixed node FPIR), not simply because it holds fewer references.

### Cited Findings
- T-norm, Z-norm and cohort normalisation in speaker verification: Auckenthaler, Carey & Lloyd-Thomas, "Score normalization for text-independent speaker verification systems", *Digital Signal Processing* 10 (2000) — [DOI 10.1006/dspr.1999.0360](https://doi.org/10.1006/dspr.1999.0360) *(prior knowledge, not re-fetched)*
- Adaptive cohort selection applied to Z-, T-, ZT- and S-norm (AS-norm) — [Matějka et al., Interspeech 2017](https://fit.vut.cz/research/group/speech/public/publi/2017/matejka_interspeech2017_IS170803.pdf). In cross-lingual speaker verification, adaptive S-norm gave **21 % relative EER** and **19.9 % MinDCF** improvement over no normalisation; an in-domain cohort worked best — [arXiv 2007.07689](https://arxiv.org/pdf/2007.07689). A trainable AS-norm adds a further 4.11 % relative EER on VoxCeleb1-O — [arXiv 2504.04512](https://arxiv.org/html/2504.04512v1)
- MagFace: the pre-normalisation embedding magnitude is a quality measure that provably rises monotonically with recognisability, and comes out of the same forward pass (CVPR 2021) — [arXiv 2103.06627](https://arxiv.org/abs/2103.06627); [CVF](https://openaccess.thecvf.com/content/CVPR2021/html/Meng_MagFace_A_Universal_Representation_for_Face_Recognition_and_Quality_Assessment_CVPR_2021_paper.html). No threshold-on-magnitude rule was found in the retrieved material.
- ENFSI Guideline for Evaluative Reporting (2015): conclusions are expressed as a **likelihood ratio** and/or a verbal scale derived from the LR, never the reverse — [ENFSI Guideline PDF](https://roebuckforensics.com.au/wp-content/uploads/2024/07/ENFSI-Guideline.pdf); [NFI announcement](https://www.forensicinstitute.nl/news/news/2015/05/19/european-guideline-for-evaluative-reporting-in-forensic-science). Verbal scales are criticised for arbitrary ranges and cliff-edge effects — [Leiden repository](https://scholarlypublications.universiteitleiden.nl/access/item%3A2950587/view)
- Score-based LR methodology for biometrics (Morrison & Enzinger) — [NIST workshop slides 2016](https://www.nist.gov/document/04morrisonenzingernistworkshop20160430aoptimizedpdf)
- False-discovery-rate control: Benjamini & Hochberg, JRSS-B 57 (1995) — [DOI 10.1111/j.2517-6161.1995.tb02031.x](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x) *(prior knowledge, not re-fetched)*

### Inferences
- **[MODEL] Raise or lower the threshold for fewer references?** Two effects pull in opposite directions:
  - Fewer references means fewer comparisons, so a lower threshold holds the same FPIR (Q10b).
  - Fewer references also means a noisier max-score, because mated-score variance is largest at template size 1 (Crosswhite et al.).
  
  Applying a fixed raw threshold to every node therefore gives very different FPIRs across nodes, dominated by G. The principled fix is to set the per-comparison threshold so that FMR(τ) = α_node / (k·G) (Bonferroni/Šidák). Equivalently, report a p-value or LLR and decide centrally.
- **[MODEL] Central decision with BH.** The BS receives one score per cluster (or node), converts each to a p-value using the impostor score distribution and M = k·G, and applies BH at q = 5–10 %. Only clusters that pass are sent a verification UAV. This bounds the expected fraction of wasted visits rather than the per-node error rate, which fits a "few true, a few false" mission with a fixed verification budget.
- **[MODEL] Cohort normalisation at the node.** Each node can compute an S-norm using its own stored crops as the impostor cohort, since the target is almost always absent from most crops. This absorbs per-camera domain shift (lighting, resolution) for free. It is the edge analogue of per-camera calibration in re-ID.
- **[MODEL] Quality.** A MagFace-style magnitude (or another quality score) should down-weight low-quality stored crops before fusion and be reported, but no published threshold rule was found.

### Gaps
- No re-ID paper with per-camera threshold calibration numbers was retrieved.
- No conformal-prediction open-set face/re-ID paper with numbers was retrieved; conformal p-values are equivalent in form to the p-value conversion above.
- The exact EER gain of Matějka 2017 was not extracted.

## Q16b — Fusing scores across multiple references, and what a node should report in a few bytes

### Takeaway
For fusing per-reference scores, the sum (mean) of calibrated scores/LLRs is the most robust rule (Kittler et al. 1998). Max is the right detector when references are views of possibly different targets, or when only one stored crop is expected to match. A node should send about 6 bytes: a quantised calibrated LLR (or p-value), the top raw score, a count above threshold, the number of comparisons (log k·G), the reference fraction, and a quality value. The BS then ranks clusters with BH.

### Cited Findings
- Kittler, Hatef, Duin & Matas (IEEE TPAMI 1998): the **sum rule** outperforms other combination schemes and is less sensitive to estimation errors. The product rule is fragile, since one bad expert drives the result — [Kittler et al. (PDF mirror)](https://people.cs.pitt.edu/~chang/231/y14/combineclassifier.pdf)
- Kittler & Alkoot (2003): Sum beats Vote for Gaussian estimation errors, but Vote may win under heavy-tailed errors — [Kybernetika 1998/related](https://www.kybernetika.cz/content/1998/4/381/paper.pdf); [arXiv 1502.02191 review](https://arxiv.org/pdf/1502.02191)
- Template adaptation and pooling studies show that IJB-A methods using different set-fusion strategies end up at nearly the same top performance once adapted — [Crosswhite et al.](https://ar5iv.labs.arxiv.org/html/1603.03958)

### Inferences
- **[MODEL] Fusion rule per axis.**
  - *Across references of one target:* use the mean of normalised scores, or the sum of per-reference LLRs only if the references are near-independent. Correlated frames from one video over-count evidence if their LLRs are summed, so use the mean, or sum with an effective-count correction.
  - *Across stored crops:* use max, since the target appears in few crops. Correct it for the number of crops via the p-value or Šidák transform, p = 1 − (1 − p_single)^G.
  - *Across targets in a multi-target query:* report per target (by ID) or max.
- **[MODEL] Suggested report payload (about 6 B, fits a LoRa/802.15.4 frame with room to spare):**

| Field | Bytes | Meaning |
|---|---|---|
| `llr_q` | 1 | calibrated log-LR (or −log10 p), node-level, after crop-count correction; 0.25-nat steps |
| `top_s` | 1 | top raw cosine, quantised, for audit and recalibration at BS |
| `n_hit` | 1 | number of stored crops above a common moderate threshold (spatial/temporal corroboration) |
| `log2_M` | 1 | log2 of comparisons k·G, so the BS can apply its own multiplicity correction |
| `ref_frac` | 0.5 | fraction of reference set held (4 bits, 1/16 steps) |
| `q` | 0.5 | quality of the best-matching crop (4 bits, e.g. MagFace magnitude bin) |
| `target_id` | 1 | which target (multi-target queries) |

  The BS ranks clusters by `llr_q`, combined with prior coverage, and applies BH at a chosen q to choose verification visits. `ref_frac` and `log2_M` let it discount low-evidence reports instead of the node silently changing its threshold.
- **[MODEL] Policy summary.**
  1. The node normalises (S-norm against its own crops) and calibrates to an LLR.
  2. The node reports and does not decide, except for a minimal gate to save LoRa airtime. That gate is a Bonferroni-scaled threshold FMR(τ) = α/(k·G).
  3. The BS decides with FDR control.
  4. A node with less of the reference set does not need a stricter threshold: its comparison count is lower. Its LLR is less reliable, though, and the BS should know `ref_frac`.

### Gaps
- No peer-reviewed study of byte-budgeted biometric match reports (LoRa-scale) was found. The payload above is a design proposal, not a published standard.
- Calibration (score→LLR mapping) needs impostor and mated score distributions for the actual matcher. These must be measured in the project's own layer-1 experiments.
