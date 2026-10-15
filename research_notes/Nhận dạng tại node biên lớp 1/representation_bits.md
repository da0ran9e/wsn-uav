# Transmitted unit and size of a recognition signature, and the bits needed to keep false alarms low

Scope: what a UAV should broadcast as the "query" (reference signatures for 1 to a few targets) over IEEE 802.15.4 (99 B usable payload per frame), and how many bits each signature needs so that the expected number of false reports per cluster stays at about 1 or below. Matching is done against 10^4 to 10^6 stored crops per node, across hundreds to thousands of nodes.

Note on method: about 17 tool calls were used. Several primary PDFs (Jégou et al. 2011 PQ, Daugman CSVT 2004, Drozdowski et al. ICIP 2018) could not be text-extracted in this environment, so some of their exact table values are listed under Gaps instead of being quoted. All byte counts below are plain arithmetic (dimension × bytes per element). The false-alarm arithmetic is derived here and shown in full.

## Q1. Representation options, bytes per signature, and how many fit in one 99-byte 802.15.4 frame

### Takeaway
A 512-bit binary code or a 64-byte PQ code fits one signature per frame. A 512-d int8 embedding needs 6 frames and a float32 ArcFace embedding needs 21. Raw crops and MPEG CDVS descriptors cost tens of frames or more. The downlink budget (about 10^3 to 10^4 frames, about 100 kB to 1 MB per cluster) is therefore not the binding constraint even for float32: it could carry hundreds of full-precision signatures. What actually sets the bit length is the false-alarm budget (Q3).

### Cited Findings
- MPEG CDVS (ISO/IEC 15938-13) defines six descriptor lengths: 512 B, 1 KB, 2 KB, 4 KB, 8 KB and 16 KB. They are built from a global Scalable Compressed Fisher Vector plus compressed SIFT-like local descriptors, so that matching performance can be traded against bandwidth. — [Duan et al., CDVA: the emerging MPEG standard (arXiv 1704.08141)](https://arxiv.org/pdf/1704.08141); [MPEG CDVS tag page](https://mpeg.chiariglione.org/tags/cdvs?page=1)
- Sending CDVS frame by frame for video costs about 1 Mbps (4 KB per frame at 30 fps). This is what motivated MPEG CDVA. — [Duan et al., Video Coding for Machines (arXiv 2001.03569)](https://arxiv.org/pdf/2001.03569)
- Casting 512-d FP32 face embeddings to INT8 (scale by 127, round) keeps relative distances and cuts storage by up to about 80 %. The accuracy loss depends on the model: FaceNet was robust, while TransFace dropped significantly. — [Experimental Evaluation of Quantization Methods in Facial Recognition (UFMS / SBAC-PAD ext.)](https://repositorio.ufms.br/retrieve/cf33dad8-c741-4948-b7aa-d4885c44a9f2/29545.pdf)
- The Part-based Deep Hashing (PDH) re-ID baseline compares a 4,096-d float IDE (FC7) feature against binary codes of 128 to 2,048 bits. PDH uses 2,048-bit Boolean codes. — [Zhang et al., Part-based Deep Hashing for Large-scale Person Re-ID (arXiv 1705.02145)](https://ar5iv.labs.arxiv.org/html/1705.02145)
- Matryoshka Representation Learning (MRL) trains nested prefixes of one embedding (ResNet50: 8, 16, 32, …, 2048 dims), so any prefix can be sent. It reports up to 14× smaller embedding at the same ImageNet-1K accuracy, and up to 14× real-world retrieval speed-up through coarse-to-fine (funnel) reranking. — [Kusupati et al., NeurIPS 2022](https://proceedings.neurips.cc/paper_files/paper/2022/hash/c32319f4868da7613d78af9993100e42-Abstract.html); [arXiv 2205.13147](https://arxiv.org/abs/2205.13147)
- In product quantization (PQ) with asymmetric distance computation (ADC), the query stays uncompressed and only database vectors are encoded. Distances are computed "between a vector and a code", which raises precision over symmetric coding. — [Jégou, Douze, Schmid, Product Quantization for NN Search, TPAMI 2011](https://paper-notes.zhjwpku.com/assets/pdfs/Product_Quantization_for_Nearest_Neighbor_Search.pdf)

### Size table (arithmetic; frame payload = 99 B)

| Representation | Typical dim / config | Bytes per signature | Frames per signature | Signatures per frame |
|---|---|---|---|---|
| Raw face crop, JPEG | 112×112×3 | ~3–6 kB (**unsourced estimate**, quality-dependent) | ~30–60 | 0 |
| Raw person crop, JPEG | 256×128×3 | ~5–15 kB (**unsourced estimate**) | ~50–150 | 0 |
| MPEG CDVS descriptor | 6 operating points | 512 B – 16 KB | 6 – 166 | 0 |
| Re-ID float32 | 2048-d (ResNet50) | 8,192 B | 83 | 0 |
| Re-ID / CLIP float32 | 768-d | 3,072 B | 32 | 0 |
| ArcFace / CLIP float32 | 512-d | 2,048 B | 21 | 0 |
| float16 | 512-d | 1,024 B | 11 | 0 |
| int8 scalar quantized | 512-d | 512 B | 6 | 0 |
| 4-bit scalar quantized | 512-d | 256 B | 3 | 0 |
| PQ / OPQ | m = 64 sub-quantizers × 8 bit | 64 B | 1 | 1 |
| PQ / OPQ | m = 32 × 8 bit | 32 B | 1 | 3 |
| PQ / OPQ | m = 16 × 8 bit | 16 B | 1 | 6 |
| PQ / OPQ | m = 8 × 8 bit | 8 B | 1 | 12 |
| Binary hash | 512 bit | 64 B | 1 | 1 |
| Binary hash | 256 bit | 32 B | 1 | 3 |
| Binary hash | 128 bit | 16 B | 1 | 6 |
| Binary hash | 64 bit | 8 B | 1 | 12 |
| Matryoshka prefix, int8 | 64-d | 64 B | 1 | 1 |
| Matryoshka prefix, int8 | 128-d | 128 B | 2 | 0 |

Total downlink cost of Q signatures with a 1 k to 10 k frame budget: 5 float32 ArcFace signatures need 105 frames, about 1–10 % of the budget. 50 such signatures (for example 10 views × 5 targets) need about 1,050 frames.

### Inferences
- The query is broadcast, but the gallery (the node's stored detections) never leaves the node. The node can keep its gallery as full-precision float embeddings and compare the received compressed query to them (the ADC idea, applied query-side). Only the *query* side is degraded, so the loss is smaller than the symmetric binary-vs-binary numbers quoted in the hashing literature. This is an inference from the ADC principle, not a measured result for face or re-ID.
- One caveat breaks the "send float32, it is cheap" conclusion. Under the project's own A2G results (chain-of-consecutive-packets model; files are useful only if every frame arrives), a 21-frame signature must survive 21 consecutive frames. A 1-frame signature survives as a unit. Self-contained 1-frame signatures, each carrying its own target ID and index, degrade gracefully under loss. Multi-frame float signatures need FEC or repetition. This follows from the project's own requirement, not from an external source.
- Matryoshka or other nested embeddings give a natural progressive query: frame 1 carries a coarse prefix usable on its own, and later frames refine it.

### Gaps
- No peer-reviewed source was found for the JPEG size of 112×112 face or 256×128 person crops. The figures above are rough estimates.
- The ISO/IEC 19794-5 and 39794-5 face record sizes were not retrieved. Those standards store images, not deep templates, so they give no template byte count to compare with.
- The exact MRL per-dimension accuracy table (e.g. top-1 at 8, 16, 32 dims) could not be extracted.

## Q2. Accuracy versus bits per signature (face, re-ID, PQ)

### Takeaway
Published evidence agrees on the direction but has few exact numbers for modern face models. int8 is close to lossless for most models (with model-dependent exceptions). Sign or ITQ binarization of deep face templates costs a "negligible" to small drop, but no TAR@FAR=1e-4 or 1e-6 table for binarized ArcFace on IJB-C was found. In re-ID hashing, mAP keeps rising up to about 512 bits and then saturates. Binary re-ID codes lag float features substantially.

### Cited Findings
- **Face, binarization:** binarization schemes for deep face templates reduce storage and computation "vastly" with "only a negligible drop in biometric performance" (Drozdowski, Struck, Rathgeb, Busch, ICIP 2018, pp. 191–195). — [NTNU Open record](https://ntnuopen.ntnu.no/ntnu-xmlui/handle/11250/2577914); [ResearchGate](https://www.researchgate.net/publication/327995347_Benchmarking_Binarisation_Schemes_for_Deep_Face_Templates)
- **Face, binarization is the main source of loss in template protection:** IronMask avoids binarization because it is "the main cause of performance loss" in protected deep face templates (evaluated on ArcFace and CosFace). — [IronMask (DeepAI listing)](https://deepai.org/publication/ironmask-modular-architecture-for-protecting-deep-face-template)
- **Face, int8:** up to about 80 % storage reduction "without much loss"; FaceNet stays stable, TransFace degrades significantly. — [UFMS quantization study](https://repositorio.ufms.br/retrieve/cf33dad8-c741-4948-b7aa-d4885c44a9f2/29545.pdf)
- **Face, short binary codes (PCA-ITQ at 32, 64, 128 bits):** per-identity bit drift grows with code length, at a median of 1.357 bits per decade of ageing for 64-bit and 2.571 for 128-bit templates. — [Ageing Drift in Binary Face Templates (arXiv 2510.21778, preprint)](https://arxiv.org/pdf/2510.21778)
- **Face, float reference point:** ArcFace on IJB-C is about 0.957 TAR at FAR=1e-3 and about 0.895 at FAR=1e-5 in one comparison table (real-valued). — [OGCTL, arXiv 1903.04752](https://arxiv.org/pdf/1903.04752). Another table lists ArcFace at 95.74 % TAR at FAR=1e-4 (column alignment unverified). — [search summary of IJB-C tables; flag as uncertain](https://www.sota2.com/research/sota/face-recognition-on-ijb-c)
- **Re-ID, hashing baseline (IDE + binarization), Market-1501 / Market+500K distractors:**

| Code length | M-1501 Rank-1 % | M-1501 mAP % | +500K Rank-1 % | +500K mAP % |
|---|---|---|---|---|
| 128 bit | 19.06 | 9.58 | 12.20 | 4.48 |
| 256 bit | 21.91 | 10.75 | 14.82 | 5.33 |
| 512 bit | 25.36 | 12.37 | 17.61 | 6.44 |
| 1024 bit | 25.24 | 11.95 | 16.63 | 5.91 |
| 2048 bit | 27.14 | 12.76 | 18.68 | 6.56 |

  The proposed PDH at 2048 bits reaches 47.89 % Rank-1 and 26.06 % mAP (single query). The 500K distractors cut mAP roughly in half, which is direct evidence that gallery size inflates false matches. Binary distance plus sorting took 1.81 ms against 101.4 ms for 4096-d float on Market-1501 (42.9 ms against 2,605 ms with +500K). — [Zhang et al., arXiv 1705.02145 (Tables II, X)](https://ar5iv.labs.arxiv.org/html/1705.02145). Caution: these are 2017-era features. Modern float re-ID reaches about 85–90 % mAP on Market-1501, and its absolute binary numbers would differ (modern float figures are from general knowledge, unverified here).
- **PQ recall vs bytes (SIFT1M, exhaustive ADC):** at 32 bits (4 B), PQ 4×8 gives R@100 = 0.594 and OPQ 4×8 gives 0.652. — [Derived Codebooks, arXiv 1905.06900](https://arxiv.org/pdf/1905.06900). At 64 bits (8 B), PQ gives R@1 ≈ 0.225, and at 128 bits (16 B) ≈ 0.444 (polysemous/PQ). — [Quicker ADC, arXiv 1812.09162](https://arxiv.org/pdf/1812.09162). These are recall of the exact nearest neighbour on SIFT descriptors, not identity verification, so they show how fast quantization error falls with bytes but do not give FMR directly.
- **Effective vs nominal bits (iris):** a 2,048-bit IrisCode has only about 249 statistical degrees of freedom. Impostor HD over 9,060,003 comparisons fits Binomial(N=249, p=0.5), with mean 0.499 and SD 0.0317. Fully independent 2,048 bits would give SD ≈ 0.011. — [Daugman, binomial data page](https://www.cl.cam.ac.uk/~jgd1000/binomdata.html); [Daugman, How Iris Recognition Works](https://www.cl.cam.ac.uk/~jgd1000/irisrecog.pdf). A replication with another algorithm fit N = 352. — [Uniqueness of Iris Pattern Based on AR Model (arXiv 2306.12572)](https://arxiv.org/pdf/2306.12572)

### Inferences
- Nominal bit length overstates discriminative capacity by roughly 8× for iris (2048 → 249). For deep binary face codes produced by PCA+ITQ, which decorrelates the bits, the ratio is plausibly closer to 1–2×. This is unverified, and the effective degrees of freedom should be measured on the project's own model by fitting impostor Hamming distances to a binomial.
- A conservative working position until measured: int8 or 4-bit query-side quantization of a 512-d face embedding against a float gallery is close to lossless. 512-bit binary is a small but non-negligible loss. 128 bits or fewer is too short for low-FMR regimes with large galleries (see Q3).

### Gaps
- No source found for binarized or 4-bit ArcFace TAR@FAR=1e-4 / 1e-6 on IJB-C, or for EER tables from Drozdowski et al. 2018 (full text not accessible).
- The original Jégou 2011 SIFT1M recall@100 table at 64 bits could not be extracted.
- No modern (2022+) re-ID hashing table with transformer features on MSMT17 was retrieved.

## Q3. False-alarm arithmetic, minimum bits, tracklet aggregation, and fewer high-precision versus more low-bit signatures

### Takeaway
A cluster runs about 10^7 to 10^10 comparisons per query. Expected false alarms ≤ 1 therefore needs per-comparison FMR ≈ 10^-8 to 10^-10. This is below the FMR that NIST-style face verification is usually quoted at (1e-6), so a per-crop threshold alone cannot do it. Two things are needed together:
- **Tracklet- or node-level aggregation**, which shrinks the comparison count by 10–100× and averages out noise.
- **About ≥ 128 to 360 effective independent bits** in a binary code, depending on how tight the genuine distribution is. The absolute information floor is about 25–36 bits.

Sending a few well-quantized signatures (int8 or PQ-64 B, compared asymmetrically against a float gallery) is preferable to many very short codes, because the number of query signatures multiplies the false-alarm count linearly.

### Cited Findings
- NIST FRTE 1:N report cards quote FNIR at a fixed FPIR = 0.003 on a gallery of about 1.6 M identities, and plot error-vs-threshold curves for galleries of 0.6 M, 1.6 M, 3 M, 6 M and 12 M. To hold FPIR fixed as the gallery grows, the threshold must rise. — [NIST FRTE 1:N report card, hik_3](https://face.nist.gov/frte/reportcards/1N/hik_3.pdf); [gorilla_006](https://face.nist.gov/frte/reportcards/1N/gorilla_006.pdf)
- Adding 500 K distractors to Market-1501 roughly halved the hashing mAP (e.g. 12.37 → 6.44 % at 512 bits). — [arXiv 1705.02145](https://ar5iv.labs.arxiv.org/html/1705.02145)
- Impostor Hamming distance for independent bits is Binomial(N, 0.5). Daugman's IrisCode fits this with N = 249 effective degrees of freedom. — [Daugman binomial data](https://www.cl.cam.ac.uk/~jgd1000/binomdata.html)
- IJB-C template-level matching uses the L2-normalized sum of all image and video features in a template (set or tracklet aggregation), scored by cosine. — [Towards Privacy-Preserving, Real-Time and Lossless Feature Matching (arXiv 2208.00214)](https://arxiv.org/pdf/2208.00214)
- Rate–accuracy trade-off for transmitted features is the explicit design goal of MPEG CDVS (six rate points, 512 B – 16 KB), CDVA, and Video Coding for Machines. — [arXiv 1704.08141](https://arxiv.org/pdf/1704.08141); [arXiv 2001.03569](https://arxiv.org/pdf/2001.03569)

### Arithmetic (derived here)

**1. Comparison count.** C = Q × G × n, where Q = query signatures, G = stored items per node, n = nodes per cluster.

| Scenario | Q | G (items per node) | n | C |
|---|---|---|---|---|
| Small | 1 | 10^4 crops | 100 | 10^6 |
| Base | 5 | 10^5 crops | 500 | 2.5 × 10^8 |
| Base, tracklet-level | 5 | 10^4 tracklets | 500 | 2.5 × 10^7 |
| Large | 10 | 10^6 crops | 1000 | 10^10 |

**2. Expected false alarms.** E[FA] ≈ C × FMR. For E[FA] ≤ 1, FMR ≤ 1/C:
- 10^6 comparisons → FMR ≤ 1e-6 (≥ log2 C = 19.9 bits of information)
- 2.5 × 10^7 → FMR ≤ 4e-8 (24.6 bits)
- 2.5 × 10^8 → FMR ≤ 4e-9 (27.9 bits)
- 10^9 → FMR ≤ 1e-9 (29.9 bits)
- 5 × 10^10 → FMR ≤ 2e-11 (35.5 bits)

log2(C) is an information-theoretic floor. It assumes every genuine pair matches exactly (zero genuine noise), so it is never achievable in practice.

If each node sends at most one report, the probability that a given node raises a false report is p_node = 1 − (1 − FMR)^(Q·G). E[false reports per cluster] = n · p_node, which is ≈ C · FMR when that product is ≪ 1.

**3. Feedback budget check.**
- LoRa at 1 % duty cycle: one 0.4 s slot per 40 s per cluster gives 90 uplink slots per hour.
- Satellite: a few hundred bytes per hour is about 50–100 reports of a few bytes each.

A false-alarm rate of 10 per cluster would therefore consume 10–20 % of an hour's satellite budget. Worse, each false alarm can trigger a UAV verification visit, so a target of E[FA] ≤ 1 per cluster (≲ 0.1 when there are many clusters) is reasonable.

**4. Bits needed for a binary code.** Model impostor Hamming distance as Binomial(N_eff, 0.5) and declare a match when the normalized HD is ≤ t. The value of t is set by the genuine distribution (lower t needs a tighter genuine spread, i.e. better quality crops). FMR = P[Bin(N_eff, 0.5) ≤ t·N_eff], computed exactly:

| N_eff | t = 0.25 | t = 0.30 | t = 0.35 | t = 0.40 |
|---|---|---|---|---|
| 32 | 3.5e-3 | 1.0e-2 | 5.5e-2 | 1.1e-1 |
| 64 | 3.9e-5 | 7.8e-4 | 8.4e-3 | 5.2e-2 |
| 128 | 6.4e-9 | 2.5e-6 | 2.6e-4 | 1.3e-2 |
| 249 | 4.7e-16 | 6.6e-11 | 1.2e-6 | 7.4e-4 |
| 512 | 5.0e-31 | 2.0e-20 | 4.8e-12 | 2.5e-6 |

Minimum N_eff (effective independent bits) to reach the target FMR:

| Target FMR (scenario) | t = 0.25 | t = 0.30 | t = 0.35 |
|---|---|---|---|
| 1e-6 (small) | 87 | 136 | 245 |
| 4e-8 (base, tracklet) | 111 | 173 | 311 |
| 4e-9 (base, crop-level) | 127 | 202 | 360 |

If the effective-to-nominal ratio is about 1 (decorrelated ITQ bits), a 256-bit code (32 B, 3 per frame) covers the tracklet-level base case at t ≤ 0.30. A 512-bit code (64 B, 1 per frame) covers crop-level matching at t ≈ 0.35. With an iris-like 8:1 redundancy, 2048 nominal bits would be needed. The governing variable is the genuine distance spread, which depends on crop quality (low-resolution CCTV is much worse than enrolment photos), so t must be measured on the project's own model and data.

**5. Tracklet or evidence aggregation.**
- Matching per track instead of per crop cuts G by the mean track length (for example 10–100 crops per track). This lowers C by the same factor.
- Averaging embeddings over a track, as in IJB-C template pooling, tightens the genuine distribution. That allows a lower t, which lowers FMR exponentially (see the table).
- Requiring k independent matching tracks (or multiple query views agreeing) before a node reports turns the false-alarm probability into roughly FMR^k under independence. This is optimistic, because impostor look-alikes are correlated across views.
- A two-stage node rule (cheap binary or MRL-prefix filter, then float or PQ rerank against all received query views) follows the MRL funnel idea.

**6. Fewer high-precision or more low-bit signatures?** E[FA] scales linearly with Q, so Q low-bit signatures each at FMR f give Q·f. More views of the same target help recall (pose and appearance coverage) but multiply false alarms unless they are fused into one decision per target, e.g. max or mean over views followed by one threshold calibrated for the fused score.

Recommended unit: per target, 1–5 views, each a 64-B code (PQ-64 or 512-bit binary, or a 64-d int8 MRL prefix), one per frame with a self-identifying header. Repeat it across many frames of the 10^3–10^4 frame budget for loss robustness. Optionally add an int8 512-B "full" version spread over 6 frames for nodes that receive it completely. The node compares asymmetrically against its float gallery and reports only on a fused, tracklet-level decision.

### Inferences
- Under these assumptions, false alarms are governed by C × FMR, and the downlink can afford ≥ 64 B per signature easily. The binding constraint is therefore crop-quality and genuine spread, not the bit budget.
- Per-crop matching over 10^5–10^6 crops per node is incompatible with a 1-report-per-cluster budget at any FMR currently quoted for face recognition in the wild (about 1e-4 to 1e-6). Tracklet aggregation plus a fused multi-view rule is mandatory, not optional.
- For person (body) re-ID, which is far less discriminative than face, the effective N_eff is likely much lower. Re-ID alone at gallery sizes of 10^5+ will likely produce many false alarms per cluster. Treat it as a pre-filter, combined with face, time, and location cues. This is an inference based on the low hashing mAP and the halving under distractors.

### Gaps
- No source measured the effective degrees of freedom of binarized ArcFace or re-ID codes. The binomial model above is an assumption to be calibrated.
- No sourced FMR-vs-bits curve for deep face templates at FMR ≤ 1e-6 was found. The NIST FRTE report cards' exact FNIR/FPIR values for the 12 M gallery were not extracted.
- No paper was found that directly optimizes "number of query views × bits per view" under a broadcast budget. The trade-off above is derived, not cited.
