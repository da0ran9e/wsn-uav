# Two-stage search: light signature (coarse filter) → full reference data (confirmation) — how accurate is each stage

Scope: (a) how accurate attribute/coarse filters are and how much they prune; (b) cascade / coarse-to-fine pipelines; (c) accuracy ceilings with full reference data for persons, vehicles and animals; (d) parameters for the simulation. Searched 2026-10-18. Many benchmark numbers come from secondary comparison tables inside later arXiv papers. Each such number is flagged.

## Q1. Coarse-filter (attribute / class) accuracy: pedestrian colour, vehicle colour/type/make, animal species

### Takeaway
A single colour attribute on a person is the weakest link. On re-ID footage, upper-body colour (9 classes) is correct only about 74 % of the time, even though *mean* attribute accuracy is reported at 86–93 %. Vehicle colour reaches about 95 % micro accuracy but only about 80 % macro accuracy on real surveillance footage, and fails badly at night/IR. Make/model reaches 93–97 % in-domain but collapses out of domain. Camera-trap species classification reaches about 94–97 % at trained sites but drops at new sites.

### Cited Findings
**Pedestrian attributes**
- On Market-1501 (attributes annotated by Lin et al.), APR's attribute recognition accuracy is: gender 88.9 %, upper-body colour 74.0 %, lower-body colour 73.8 %, average over all attributes 86.6 %. The ARN baseline gets 72.4 % / 71.7 % for the colours. On DukeMTMC-reID, APR gets upper colour 74.2 %, lower colour 69.9 %, average 83.4 % — [Lin et al., "Improving Person Re-ID by Attribute and Identity Learning" (Pattern Recognition 2019), arXiv 1703.07220](https://ar5iv.arxiv.org/html/1703.07220)
- In Market-1501-attribute, upper-body colour is a one-of-8 label (upblack, upwhite, upred, uppurple, upyellow, upgray, upblue, upgreen). Exactly one is "yes" per identity, and later work treats it as 9 classes including a catch-all — [Market-1501_Attribute GitHub](https://github.com/vana77/Market-1501_Attribute); [Lin et al.](https://arxiv.org/pdf/1703.07220)
- PA-100K has 26 attributes and **no colour labels**. The UPAR authors had to re-annotate upper- and lower-body colour themselves — [UPAR, Specker et al., arXiv 2209.02522](https://arxiv.org/pdf/2209.02522); [HydraPlus-Net, Liu et al. ICCV 2017](https://arxiv.org/pdf/1709.09930)
- A recent VLM-based PAR model reports PA-100K mean accuracy (mA) of 92.88 and F1 of 92.32, with no per-attribute breakdown — [VLM-PAR, arXiv 2512.22217](https://arxiv.org/html/2512.22217v1)
- One 2026 per-attribute table lists "upperBodyYellow" at 93.27 % in a PETA-family column. It is hard to tell which dataset and metric this is, and on rare attributes mA (the mean of positive and negative recall) inflates scores. Treat it as unverified — [ReSAGE-PAR, arXiv 2606.06020](https://arxiv.org/pdf/2606.06020)

**Vehicles**
- Vehicle colour on a real surveillance set (UFPR-VeSV): the best method reaches 94.6 % micro accuracy and 79.7 % macro accuracy. The previous best had 71.5 % macro accuracy. The "unknown" class mainly holds **infrared night-time images**, where colour cannot be recovered — [Revisiting Vehicle Color Recognition in Long-Tailed Surveillance Scenarios, arXiv 2606.13625](https://arxiv.org/pdf/2606.13625)
- On UFPR-VCR, 72 of the 222 misclassified images (32.4 %) were taken at night, although night images are under 10 % of the set. 44.4 % of night images were still wrong even within the top-2 predictions — [Lima et al. 2024, arXiv 2408.11589](https://arxiv.org/pdf/2408.11589); [dataset](https://github.com/lima001/ufpr-vcr-dataset)
- CompCars make/model: a survey reports model accuracy of 97.6 % and make accuracy of 99.3 %, mostly on web-nature images — [Two decades of VMMR, J. King Saud Univ. 2023](https://www.sciencedirect.com/science/article/pii/S1319157823004391). On the CompCars surveillance subset, one paper reports about 96.7 % rank-1 for 180 classes. Simulated night versions of CompCars give 93.7 % top-1 — reported in search snippets, original tables not opened; see [Revisiting CompCars, Sensors 2021](https://www.mdpi.com/1424-8220/21/2/596)
- Domain shift: a CompCars-trained model drops from 96.88 % to 36.10 % top-1 on VMMRdb-51 test images — [Tafazzoli et al., CVPRW 2017](https://openaccess.thecvf.com/content_cvpr_2017_workshops/w9/papers/Tafazzoli_A_Large_and_CVPR_2017_paper.pdf) (as summarised in search results)

**Animals (species, camera traps)**
- Snapshot Serengeti, 48 species, 3.2 M images: CNNs identify animals with >93.8 % accuracy. With confidence thresholding, they automate 99.3 % of images at 96.6 % accuracy, matching crowdsourced volunteers — [Norouzzadeh et al., PNAS 2018, 115(25):E5716](https://www.uber.com/blog/research/automatically-identifying-counting-and-describing-wild-animals-in-camera-trap-images-with-deep-learning)
- Camera-trap models perform well at trained locations, but "generalization to new locations is poor, especially for classification" — [Beery, Van Horn, Perona, Recognition in Terra Incognita, ECCV 2018](https://arxiv.org/abs/1807.04975) (exact numbers not extracted)

### Inferences
- If the light signature is a hard "upper colour = yellow" filter, roughly **P(target passes) ≈ 0.74 in daylight**, from the 9-class accuracy. A rarer colour may score higher per class, but no clean per-colour number was found. At **night/IR, P(pass) for any colour attribute should be treated as near random**: the colour is not observable, so the filter must be soft (skipped) there.
- Single-attribute errors compound: if a node checks k independent attributes at about 0.75–0.9 each, P(pass) falls geometrically (for example 0.74 × 0.89 ≈ 0.66 for colour + gender). This argues for scoring and ranking rather than hard AND-filters. *(extrapolation)*

### Gaps
- No per-colour accuracy for "yellow upper" was found on PETA/RAP v2 from a primary table. The Wang et al. 2022 PAR survey (Pattern Recognition) was not opened.
- MegaDetector + species classifier numbers on new sites (exact accuracy drops) were not extracted.

## Q2. How much a single attribute prunes, and recall loss under errors and lighting

### Takeaway
No source gave the share of pedestrians wearing yellow. Market-1501-attribute shows colour distributions only as pie charts. Pruning power therefore has to be estimated: a rare colour can cut a crowd to roughly 5–10 %, but at 74 % colour accuracy, about a quarter of true targets are lost per hard filter. In IR/night, colour pruning is unusable.

### Cited Findings
- Lin et al. show the upper/lower-colour distributions of Market-1501/Duke only as pie charts (Fig. 3), without numeric counts — [Lin et al.](https://ar5iv.arxiv.org/html/1703.07220)
- IR night frames form an "unknown" colour class in surveillance vehicle data — [arXiv 2606.13625](https://arxiv.org/pdf/2606.13625); night images are over-represented 3× among colour errors — [Lima et al. 2024](https://arxiv.org/pdf/2408.11589)

### Inferences
- Simulation proposal *(extrapolation, not sourced)*: shortlist fraction ≈ prior(attribute) / accuracy-adjusted. For a distinctive colour, use 0.05–0.15 of people (or nodes whose footage has a candidate). For a common class ("white sedan", "a dog"), use 0.2–0.4. False-positive rate from attribute error is about (1 − acc)/(n_classes − 1) per non-target, roughly 3 % for 9 colours at 74 % accuracy.

### Gaps
- Real per-colour prevalence in pedestrian/vehicle datasets, from a citable table. RAP v2 or UPAR statistics may have it, but were not reached (the UPAR PDF was not text-extractable via fetch).

## Q3. Cascade / coarse-to-fine pipelines vs single stage

### Takeaway
Attribute-assisted re-ID and attribute-filter-then-verify cascades help, but the coarse stage alone is far from conclusive. Text/attribute-only person search tops out at about 76–78 % Rank-1, while image-based re-ID reaches about 95 % Rank-1. The classic vehicle cascade (attributes → plate) shows the pattern clearly.

### Cited Findings
- APR (attributes + ID jointly) raises Market-1501 Rank-1 from 73.69 to 84.29 and mAP from 51.48 to 64.67, on a ResNet-50 baseline — [Lin et al., Table 1](https://arxiv.org/pdf/1703.07220)
- PROVID (Liu et al., ECCV 2016) uses appearance attributes for **coarse filtering**, then a Siamese network for **license-plate verification**, plus spatio-temporal re-ranking. It reported +9.28 % mAP and +10.94 % HIT@1 over the prior SOTA on VeRi-776. A third-party table lists mAP 53.42 and Rank-1 81.56 — [Liu et al., ECCV 2016](https://mlanthology.org/eccv/2016/liu2016eccv-deep/); [DOI](https://www.doi.org/10.1007/978-3-319-46475-6_53)
- Text-based person search (a description-only "light signature") on CUHK-PEDES: IRRA ≈ 73.4–73.7 %, RDE ≈ 75.9 %, CONQUER 77.13 %, and other 2025–26 methods about 76.7–77.9 % Rank-1 — [CONQUER, arXiv 2601.18625](https://arxiv.org/html/2601.18625); [Revisiting TBPR, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12987367/); [ROGLE, arXiv 2606.01825](https://arxiv.org/pdf/2606.01825). SA-Person adds scene-aware re-ranking on top of IRRA/RDE — [arXiv 2505.24466](https://arxiv.org/html/2505.24466)
- Image re-ID (full image data) on Market-1501: TransReID 95.0 Rank-1 / 88.2 mAP; NFormer 94.7 / 91.1. On MSMT17: TransReID 83.3 / 64.9 (table in [arXiv 2308.10717](https://arxiv.org/pdf/2308.10717), possibly reproduced numbers)

### Inferences
- The two-stage design is supported in principle: a cheap coarse stage (≈ 75 % Rank-1, or ≈ 74–90 % attribute accuracy) shortlists, and a rich stage (≈ 95 % Rank-1 for same-clothes person re-ID) confirms. The overall recall is the product P(pass coarse) × P(correct fine). With hard filters this product is ≤ 0.74 × 0.95 ≈ 0.70 for persons. The coarse filter should therefore keep top-k or score-ranked candidates, not prune hard. *(extrapolation)*

### Gaps
- No primary paper was found that reports end-to-end recall of "text/attribute shortlist → image re-ID re-rank" against image-only re-ID on the same protocol.

## Q4. Full-data accuracy ceilings — does "near-absolute" hold?

### Takeaway
"Near-absolute" holds **only for face verification on cooperative, good-quality images** (FNMR ≈ 0.06–0.2 % at FMR 1e-6), and fails for twins. It does **not** hold for full-body person re-ID (≈ 95 % Rank-1 same-clothes; ≈ 56–74 % Rank-1 when clothes change), wild faces (IJB-C TAR ≈ 81 % at FAR 1e-6 in 2018 reporting, ≈ 97 % at 1e-5 more recently), or animal individual re-ID (34–99 % depending on species). A vehicle becomes near-certain only if the **license plate is readable**.

### Cited Findings
**Faces**
- NIST FRTE 1:1 (Aug 2026 summary): best FNMR on Visa-Visa 0.06 % (Cloudwalk Moontime, Recognito), Visa-Border 0.14 %, Border-Border 0.16 %, Mugshot-Mugshot 0.20 %, Kiosk-Border 0.53 % (best) with others ≈ 3.7 %. NIST's headline operating point for these sets is FMR = 1e-6. The article does not restate it, so confirm in the NIST tables. Demographic worst cases reach tens of percent under the "FMR max" view — [Biometric Update, Aug 2026](https://www.biometricupdate.com/202608/nist-frte-11-shows-facial-verification-accuracy-converging); [NIST FRTE 1:1](https://pages.nist.gov/frvt/html/frvt11.html)
- ROC reports leading Western vendors on FNMR at FMR = 1-in-1,000,000 on Visa-Border and Border-Border — [ROC, Sep 2025](https://roc.ai/2025/09/10/roc-is-1-american-vendor-in-nist-frte-ranking-among-the-worlds-most-accurate-face-recognition-algorithms/)
- Unconstrained faces (IJB-C): TAR of 81.15 % at FAR 1e-6 and 71.37 % at 1e-7 (Crystal Loss, 2018). More recent methods report about 95–97 % at FAR 1e-5 (for example PartialFC R200 / WebFace42M 96.93 % at 1e-5), with 1e-6 rarely reported — [Ranjan et al., arXiv 1804.01159](https://arxiv.org/pdf/1804.01159); [EQFace, arXiv 2105.00634](https://arxiv.org/pdf/2105.00634); aggregator: [HyperAI IJB-C](https://hyper.ai/de/sota/tasks/face-verification/benchmark/face-verification-on-ijb-c) (non-authoritative)
- Twins: NIST IR 8439 (2022) found that algorithms still give high false-match rates on identical twins and on most same-sex fraternal twins (5,938 images, 698 twin pairs). The FRTE Twins track's goal is a twin FMR that is only a small multiple of the unrelated-person FMR — [NIST IR 8439](https://nvlpubs.nist.gov/nistpubs/ir/2022/NIST.IR.8439.pdf); [FRTE Twins](https://pages.nist.gov/frvt/html/frvt_twins_demonstration.html)

**Persons (body re-ID)**
- Same-clothes: Market-1501 about 95 % Rank-1 / 88–91 % mAP; MSMT17 about 77–83 % Rank-1 / 60–65 % mAP — [arXiv 2308.10717](https://arxiv.org/pdf/2308.10717)
- Clothes-changing: PRCC 74.4 % Rank-1 / 70.2 % mAP (Ortho-ReID 2026); LTCC best about 56–58 % Rank-1 (DIFFER 58.2 %); CCIL 66.4 % / 65.2 % on PRCC — [Ortho-ReID, arXiv 2606.11661](https://arxiv.org/html/2606.11661); [CCIL, arXiv 2305.06145](https://arxiv.org/pdf/2305.06145)

**Vehicles**
- VeRi-776: about 96.6 % Rank-1 / 85.2 mAP by 2019 (appearance-based) — [Ayala-Acevedo et al., CVPRW 2019](https://openaccess.thecvf.com/content_CVPRW_2019/html/AI_City/Ayala-Acevedo_Vehicle_Re-Identification_Pushing_the_limits_of_re-identification_CVPRW_2019_paper.html). Plate verification is the stage that resolves look-alikes of the same make/model/colour — [PROVID](https://mlanthology.org/eccv/2016/liu2016eccv-deep/)

**Animals (individual re-ID)**
- MegaDescriptor (Swin-L/384) outperforms ImageNet/CLIP/DINOv2 on all 29 datasets. Per-dataset accuracy varies widely, for example Cows2021 99.54, BelugaID 66.48, HappyWhale 34.30. The metric is described in the paper as top-1/accuracy, but confirm in its Table — [Čermák et al., WACV 2024 (best paper)](https://openaccess.thecvf.com/content/WACV2024/papers/Cermak_WildlifeDatasets_An_Open-Source_Toolkit_for_Animal_Re-Identification_WACV_2024_paper.pdf)
- MiewID: 80.6 % average top-1 over a multispecies benchmark — [arXiv 2412.05602](https://arxiv.org/html/2412.05602)

### Inferences
- "Near-certain" (≥ 99 %) is defensible only for: (i) faces with a frontal, well-lit enrolment and probe (FNMR ≤ 0.2 % at FMR 1e-6); (ii) vehicles with a readable plate. For full-body persons with the same clothes, ≈ 95 % top-1 is "very likely", not certain. With a clothes change or at night it is 56–74 %. For animals of distinctive-pattern species (cows, zebras, big cats) it can be 95–99 %. For others (whales, belugas) it is 34–66 %. *(synthesis)*
- Failure conditions to model: clothes change; look-alike vehicles without a plate (same make/model/colour); twins and relatives; low resolution / far camera (wild-face regime, IJB-C ~81 % at FAR 1e-6); night/IR (colour is lost; faces and plates degrade); new deployment sites (domain shift; CompCars→VMMRdb 97 %→36 %; Terra Incognita).

### Gaps
- Live NIST FRTE tables for "wild" or surveillance-quality 1:1 at FMR 1e-6 were not opened. Current IJB-C TAR at FAR 1e-6 (post-2022) was not verified from a primary paper.
- No benchmark was found for multi-shot / video-template person re-ID that isolates the gain from many reference images (MARS etc. not searched).

## Q5. Recommended simulation parameters (all marked as extrapolations from the above)

### Takeaway
Model the coarse stage as a soft filter, with P(pass) about 0.75–0.95 by day and much lower at night for colour cues. Model the fine stage per target class: face ≈ 0.99+, plate-vehicle ≈ 0.99, person body ≈ 0.95 (same clothes) / 0.65 (clothes changed), animal individual 0.6–0.99 by species. Do not assume 100 %.

### Cited Findings
- Basis numbers: colour attribute 74 % ([Lin](https://ar5iv.arxiv.org/html/1703.07220)); text search ≈ 76–78 % R1 ([CONQUER](https://arxiv.org/html/2601.18625)); vehicle colour 94.6 % micro / 79.7 % macro, IR unknown ([2606.13625](https://arxiv.org/pdf/2606.13625)); species ≈ 94–97 % ([Norouzzadeh](https://www.uber.com/blog/research/automatically-identifying-counting-and-describing-wild-animals-in-camera-trap-images-with-deep-learning)); face FNMR 0.06–0.2 % at FMR 1e-6 ([FRTE](https://www.biometricupdate.com/202608/nist-frte-11-shows-facial-verification-accuracy-converging)); re-ID 95 % / CC 56–74 % ([2308.10717](https://arxiv.org/pdf/2308.10717), [2606.11661](https://arxiv.org/html/2606.11661)); animals 34–99.5 % ([WACV 2024](https://openaccess.thecvf.com/content/WACV2024/papers/Cermak_WildlifeDatasets_An_Open-Source_Toolkit_for_Animal_Re-Identification_WACV_2024_paper.pdf))

### Inferences (proposed table — extrapolation)
| Target class | Light-signature cue | P(true target passes coarse) day / night | Shortlist fraction of candidates | P(correct final decision, full data) |
|---|---|---|---|---|
| Person (face visible, good image) | clothing colour + gender | 0.75–0.90 soft top-k / ≤0.5 at night if colour used | 0.05–0.15 (rare colour), 0.2–0.4 (common) | 0.99 (FRTE-grade) – 0.80 (wild/low-res, IJB-C-like) |
| Person (body only) | clothing colour/type | same as above | same | 0.95 same clothes; 0.6–0.75 clothes changed |
| Vehicle | colour + type/make | colour 0.80–0.95 day; IR night ≈ uninformative; make 0.93–0.97 in-domain, much lower cross-domain | 0.05–0.2 | ≈0.99 with readable plate; ≈0.85–0.95 appearance only (VeRi-like) |
| Animal (breed/species) | species/breed class | 0.90–0.96 trained sites; lower at new sites | species prior (often 0.1–0.5) | 0.95–0.99 patterned species; 0.35–0.7 hard species |
| Twins / look-alikes | — | — | — | face FMR among twins is high (NIST IR 8439): treat as unresolvable without context |

### Gaps
- The shortlist fractions are not sourced. They need dataset prevalence statistics (RAP v2, UPAR colour histograms; VeRi colour/type histograms).
