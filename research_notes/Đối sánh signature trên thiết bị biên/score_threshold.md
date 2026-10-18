# What a "70–90 % match score" means, and how a fixed YES/NO threshold behaves (persons, vehicles, animals)

Scope note: 19 tool calls were used. Several primary PDFs (ArcFace full paper, the 2507.12107 threshold table, GOM PDF) could not be text-extracted in this environment; numbers below come only from pages actually read. Everything I fitted or derived myself is labelled **[EXTRAPOLATION]**.

## 1. What raw cosine values do genuine and impostor pairs give, and what does a vendor "percent" mean?

### Takeaway
A raw cosine similarity is not a percentage and not a probability. For modern face embeddings (ArcFace family) the operating threshold at FMR 1e-4 to 1e-5 is a cosine of about **0.30–0.45**, which is far below "70 %". For re-ID (person or vehicle) the best thresholds on normalised distance sit around **0.16–0.49**, depending on the model. Vendor percentages, such as the AWS Rekognition default of 80 % and the recommended 99 %, or the Azure default of 0.5, are each vendor's own monotone mapping, so a "70–90 %" threshold only means something once it is tied to an FAR or a calibrated posterior.

### Cited Findings
- **Face (InsightFace / ArcFace packs):** typical 1:1 cosine thresholds are **0.30–0.45 at FMR = 1e-4 to 1e-5**. The exact value depends on backbone, training data and population and must be recomputed for every model version. The threshold is the (1 − target FMR) quantile of the impostor distribution on a validation split, using at least 10/FMR non-mate pairs (about 10^7 for FMR 1e-6). A threshold reported without its FMR operating point is "meaningless". — [InsightFace guide](https://insightface.ai/guides/choose-face-recognition-model-and-evaluate)
- **Face accuracy at that operating point (IJB-C, TAR @ FAR 1e-4):** about 90–93 % for mobile MBF, 95–96 % for R50, and 96–97.5 % for R100 / w600k_r50 / glintr100. LFW 99.50–99.85 % is saturated. — [InsightFace guide](https://insightface.ai/guides/choose-face-recognition-model-and-evaluate)
- Low-quality / hard subsets (masked, large pose, low resolution): FNMR at FMR ≤ 1e-6 is about **5–8 %** for the strongest open-source pack, against a claimed 1–2 % for commercial models. These are vendor-internal numbers and are not independently verified. — [InsightFace guide](https://insightface.ai/guides/choose-face-recognition-model-and-evaluate)
- Open-source face models usually sit near a cosine threshold of about 0.2 at FAR 0.1 %, and one prototype sat around 0.3–0.4. I saw this only as a search snippet; the table was not read. ArcFace-WebFace600K on LFW: threshold about 0.2125 at FAR 0.1 %. — [arXiv 2507.12107](https://arxiv.org/pdf/2507.12107), [arXiv 2308.02065](https://arxiv.org/pdf/2308.02065) (snippets only)
- One source reports ArcFace thresholds ranging from about 0.33 to 0.82 across FAR settings on IJB-B. This is a snippet only, and the metric definition (similarity or distance) was not verified. — [AdvFaces, arXiv 1908.05008](https://arxiv.org/pdf/1908.05008)
- **Person re-ID (GOM paper, distance normalised to [0,1]):** the threshold τ at which mReP peaks is MobileNetV2 0.27/0.27 (Market/Duke), BagTricks 0.16/0.20, AGW 0.47/0.49 and SpCL 0.37/0.36. Peak mReP is 61.6 / 77.8 / 81.4 / 66.0 % on Market-1501. Thresholds must be chosen per method. — [Wang et al., "Re-identification = Retrieval + Verification", arXiv 2011.11506](https://ar5iv.labs.arxiv.org/html/2011.11506)
- **Vehicle re-ID (VeRi-776, same paper):** τmax is ResNet-50 0.32, VOC-ReID 0.43 and BagTricks 0.35, with peak mReP of 58.1 / 68.8 / 68.9 %. — [arXiv 2011.11506](https://ar5iv.labs.arxiv.org/html/2011.11506)
- **Animals (MegaDescriptor / WildlifeDatasets):** I found no published fixed cosine threshold. WildFusion states that raw global cosine scores "can't be fused with local matches without calibration", and calibration improved accuracy across 17 datasets. In the AnimalCLEF 2026 open-set clustering baseline (MegaDescriptor + MiewID, DBSCAN), ARI is about **0.20**. Participants use per-species thresholds. — [WildFusion, arXiv 2408.12934](https://arxiv.org/pdf/2408.12934v1); [CEUR Vol-4283 paper368](https://ceur-ws.org/Vol-4283/paper368.pdf) (snippets)
- **AWS Rekognition:** `FaceMatchThreshold` is "the minimum confidence in the face match to return… The default value is **80%**". — [AWS API SearchFacesByImage](https://docs.aws.amazon.com/rekognition/latest/APIReference/API_SearchFacesByImage.html). For public safety AWS recommends "**99%** or higher" plus human review. For finding missing persons it says to "use a similarity threshold lower than 99%" to get a larger candidate set, and to index multiple images of the person to reduce false positives. — [AWS public-safety guidance](https://docs.aws.amazon.com/rekognition/latest/dg/considerations-public-safety-use-cases.html)
- **Azure Face Verify:** `isIdentical` is true when confidence is ≥ **0.5** by default. The confidence field exists so that advanced users can override it and "fine-tune on their own data". Microsoft Entra Face Check uses a separate default and recommended threshold of **70 %**. — [Azure VerificationResultOutput](https://learn.microsoft.com/en-us/javascript/api/@azure-rest/ai-vision-face/verificationresultoutput); [Campus Technology on Face Check](https://campustechnology.com/articles/2024/08/16/microsoft-releases-face-check-identity-verification-for-enterprise-use.aspx)

### Inferences
- The same identity produces different "percentages" in different systems: Azure YES at 0.5, AWS default 80 %, Entra 70 %. A "70–90 %" range in our simulation should therefore be defined as a **calibrated score** (see §2), not as raw cosine. A raw-cosine threshold of 0.7–0.9 on ArcFace would reject most genuine pairs, because operating thresholds are about 0.3–0.45.
- The AWS guidance matches our use case: missing-person search is a "lower than 99 %" scenario, and holding several reference images (our 3–5 signature files) is the recommended way to cut false positives.

### Gaps
- The exact ArcFace cosine values at FAR 1e-3 / 1e-4 / 1e-6 on IJB-C, and the means and SDs of the genuine and impostor histograms, were not extractable (PDF limits).
- I found no published genuine and impostor cosine histograms for OSNet, TransReID, CLIP or MegaDescriptor. I also found no official vendor document that explains how AWS maps its similarity to a percentage; the mapping is not disclosed.
- CLIP image–image similarity: I found no sourced threshold.

## 2. How do you turn a score into P(same identity)?

### Takeaway
Use a monotone post-hoc map fitted on labelled genuine and impostor pairs. Logistic (Platt) scaling, beta calibration (recommended for bounded scores such as cosine), isotonic regression or histogram binning all work. Report the result as a likelihood ratio, or as a posterior under a stated prior. Image quality and subgroup can enter the calibration as covariates (categorical / quality-aware or cluster-wise calibration).

### Cited Findings
- FairCal (Salvador et al., ICLR 2022) calibrates face cosine scores with **beta calibration**. This is a 3-parameter monotone map fitted by log-loss, which the authors call "the recommended method when dealing with bounded scores". The paper also uses histogram binning (equal-mass bins, confidence = fraction of genuine pairs, not guaranteed monotone) and isotonic regression. It states that raw scores and prior bias-mitigation outputs "do not result in calibrated probabilities", and that any score-based classifier can be converted post hoc. — [FairCal, arXiv 2106.03761](https://ar5iv.arxiv.org/html/2106.03761)
- FairCal calibrates per unsupervised cluster (K = 100). At a global FPR of 5 %, the baseline false-match ratio between Black and White subjects is about **15×**; FairCal brings it to about **1.2×**. The evaluation operating points are global FPR 0.1 % and 1 %. — [FairCal](https://ar5iv.arxiv.org/html/2106.03761); [Mila summary](https://mila.quebec/en/article/faircal-fairness-calibration-for-face-verification)
- Terhörst et al., Fair Score Normalization (2020), is a post-comparison score normalisation; later work notes that it needs re-tuning for each FPR. — [arXiv 2002.03592](https://arxiv.org/abs/2002.03592v3)
- Mandasari et al., "Score Calibration in Face Recognition" (IET Biometrics 2014), uses linear (logistic) calibration to likelihood ratios, evaluated with **Cllr**. *Categorical* calibration that adds image information, such as quality condition, improved both calibration and verification on MOBIO and SCface. SCface is a surveillance-camera dataset. — [EPFL Infoscience](https://infoscience.epfl.ch/record/198437?ln=en)
- InsightFace recommends z-norm or t-norm if gallery score distributions shift between deployments. — [InsightFace guide](https://insightface.ai/guides/choose-face-recognition-model-and-evaluate)
- Platt (1999), "Probabilistic outputs for SVMs", and Guo et al. (ICML 2017), "On calibration of modern neural networks" (temperature scaling), are standard references. FairCal cites them; I did not fetch them separately in this session. — [Guo et al. 2017](https://arxiv.org/abs/1706.04599)

### Inferences
- Recipe **[EXTRAPOLATION, standard practice]**:
  1. Fit `P(same | s, q) = σ(a·s + b + c·q)` on validation pairs, where q is a quality bin. This gives logistic / categorical calibration.
  2. The log-likelihood ratio is `logit P − logit π_train`, where π_train is the share of genuine pairs in the calibration set.
  3. For the deployment prior π (the chance that a given crop is the target, which is tiny), the posterior is `σ(LLR + logit π)`.
- A "displayed 80 %" in our model can therefore be defined either way:
  - (A) a calibrated posterior at a balanced prior (π = 0.5), which is equivalent to LR = 4; or
  - (B) a vendor-style monotone map anchored so that, for example, 70 % ↔ FAR 1e-3, 80 % ↔ FAR 1e-4 and 90 % ↔ FAR 1e-5.

  Option B is closer to how AWS and Azure behave in practice, where a higher threshold means fewer false matches.

### Gaps
- I found no source for a specific "Beyond cosine: calibrated similarity" paper, and no peer-reviewed quality-aware calibration with published coefficients for re-ID or animals.

## 3. TPR/FPR at a fixed threshold: clear video vs surveillance; clothes change; viewpoint

### Takeaway
At a fixed FAR, face TPR is about 96 % on good data with strong models. It drops by several points on hard or low-quality subsets, and much more for mobile backbones on hard cohorts. For persons recognised by body appearance, a clothes change is catastrophic: rank-1 falls from about 99.8 % to 42–65 % on PRCC. Vehicle viewpoint change is the dominant documented failure mode, but I found no view-stratified numbers.

### Cited Findings
- **Face, good quality:** IJB-C TAR is 96–97.5 % at FAR 1e-4 for R100-class models and 90–93 % for mobile. On demographic cohorts, R100 stays within a few points, R50 shows mid-single-digit gaps, and MBF can show **double-digit** gaps on the hardest cohort. — [InsightFace guide](https://insightface.ai/guides/choose-face-recognition-model-and-evaluate)
- **Face, hard or low-quality:** FNMR is about 5–8 % at FMR ≤ 1e-6 for the best open-source pack. — [InsightFace guide](https://insightface.ai/guides/choose-face-recognition-model-and-evaluate). NIST FIVE 2024 (face in video) lists range to subject, legacy cameras, compression, motion blur and subjects who never face the camera as challenges. Its goals include threshold calibration to a target FPIR. A single track may produce K ≈ 3 templates because tracks break. — [NIST IFPC 2025 slides](https://pages.nist.gov/ifpc/2025/presentations/03.pdf). NIST FRTE 1:N reports FNIR at fixed FPIR, for example 0.001 or 0.003. — [NIST report card example](https://face.nist.gov/frte/reportcards/1N/psl_002.pdf). I did not extract FIVE FNIR values.
- **Person, clothes change (PRCC):** PCB scores rank-1 **99.8 %** with the same clothes but **41.8 %** with changed clothes. The clothes-change-specific IFD reaches 99.0 % vs **65.3 %**. GI-ReID reaches 85.97 % vs 37.55 %. "All models experience a significant drop." — [IFD, arXiv 2501.05851](https://arxiv.org/pdf/2501.05851); [arXiv 2103.15537](https://arxiv.org/pdf/2103.15537) (table extraction was garbled; column order should be checked)
- **Person / vehicle open-set at the best threshold:** peak mReP (a joint retrieval-and-verification precision) is only **58–81 %** on Market, Duke and VeRi even at the best τ. — [arXiv 2011.11506](https://ar5iv.labs.arxiv.org/html/2011.11506)
- **Vehicle viewpoint:** "existing deep metric learning baselines struggle to separate positive pairs from different viewpoints from negative pairs observed from similar viewpoints". The same vehicle looks different across angles, and different vehicles look alike. — [VANet summary](https://liner.com/review/vehicle-reidentification-with-viewpointaware-metric-learning); [Vehicle re-ID review, arXiv 2102.09744](https://arxiv.org/pdf/2102.09744). A cross-domain drop of about 15 % mAP (VeRi-Wild → VeRi-776) is reported. — [arXiv 2606.01981](https://arxiv.org/pdf/2606.01981)
- **Animals:** open-set wildlife re-ID is still weak. The ARI of about 0.20 for the AnimalCLEF 2026 baseline is reported above. — [CEUR Vol-4283](https://ceur-ws.org/Vol-4283/paper368.pdf)

### Inferences
- In our scenario, if the target changes clothes after the reference images were taken, a body-appearance signature should not be trusted. For that case, model a TPR around 0.4–0.65 relative to rank-1. **[EXTRAPOLATION: rank-1 ≠ TPR at a fixed FAR, but it is the best available proxy.]**

### Gaps
- I found no paper reporting TPR at fixed FAR for person re-ID or vehicle re-ID across quality levels, no view-stratified VeRi-776 numbers (VANet reports similar-view vs different-view results, but I did not read them), and no quality-stratified animal re-ID results.

## 4. Should the threshold differ by class and by gallery size? Multiple testing

### Takeaway
Yes on both counts. Thresholds are model-, dataset- and population-specific: re-ID τ ranges from 0.16 to 0.49 across models, AnimalCLEF uses per-species thresholds, and FairCal shows subgroup FPR gaps of up to 15× at a single global threshold. With N independent candidate crops, the per-camera false-YES probability is 1 − (1 − FPR)^N, so the per-comparison FAR has to shrink about as 1/N to hold the camera-level false-YES rate constant.

### Cited Findings
- Each method reaches its best mReP at a different threshold, so the threshold must be chosen per method and per application. — [arXiv 2011.11506](https://ar5iv.labs.arxiv.org/html/2011.11506)
- One global threshold produces unequal FPR across subgroups (15× in the FairCal example). — [FairCal](https://ar5iv.arxiv.org/html/2106.03761)
- Per-species thresholds are used in animal re-ID. — [CEUR Vol-4283](https://ceur-ws.org/Vol-4283/paper332.pdf) (snippet)
- NIST 1:N evaluations fix FPIR, a per-search false-positive rate over the whole gallery, rather than a per-comparison FMR, because false positives grow with gallery size. — [NIST FRTE report card](https://face.nist.gov/frte/reportcards/1N/psl_002.pdf); [Innovatrics glossary on FPIR](https://innovatrics.com/glossary/false-positive-identification-rate-fpir) (vendor glossary)

### Inferences
- **[EXTRAPOLATION — probability, assumes independence]:**
  - The camera-level false-YES rate is `P_FY(N) = 1 − (1 − f)^N ≈ N·f`.
  - At f = 1e-4 and N = 1 000 crops, P_FY ≈ 9.5 %. At f = 1e-6, P_FY ≈ 0.1 %.
  - Comparing each crop against k signature files and taking the maximum score multiplies the comparisons to N·k.
  - Crops from the same track are correlated, so the true rate lies between f·(number of tracks) and f·N.
- Recommendation: fix the class-specific threshold from a target **per-camera** false-YES rate, for example the LoRa report budget. Set `f = 1 − (1 − FY_target)^(1/(N·k))`. This is a Šidák-style correction.

### Gaps
- I found no source that measures max-over-gallery false positives for re-ID embeddings at the camera level.

---

## Simulation model (sourced anchors + fitted parameters)

**[EXTRAPOLATION]** The Gaussian score model is my own fit to the sourced operating points. Treat the parameters as placeholders until they can be measured.

Score s is the max cosine over k held signature files. The model draws impostor scores from N(μ_I, σ_I) and genuine scores from N(μ_G(q), σ_G).

| Class | Anchor (source) | μ_I, σ_I | μ_G (clear) | μ_G (surveillance) | τ at "70/80/90 %" ↔ f = 1e-3 / 1e-4 / 1e-5 |
|---|---|---|---|---|---|
| Face (ArcFace R100) | τ ≈ 0.30–0.45 at FMR 1e-4–1e-5; TAR ≈ 96 % at 1e-4 ([InsightFace](https://insightface.ai/guides/choose-face-recognition-model-and-evaluate)) | 0.00, 0.10 | 0.58 (σ 0.12) → TPR ≈ 0.96 at τ = 0.37 | ≈ 0.48 → TPR ≈ 0.82 at 1e-4 (matches the FNMR 5–8 % at 1e-6 on hard subsets only loosely) | 0.31 / 0.37 / 0.43 |
| Person body re-ID | τ 0.16–0.49, peak mReP 58–81 % ([GOM](https://ar5iv.labs.arxiv.org/html/2011.11506)); clothes change rank-1 ×0.42–0.66 ([IFD](https://arxiv.org/pdf/2501.05851)) | wider overlap: d′ ≈ 2.5–3 | TPR ≈ 0.7–0.85 at f = 1e-3 | clothes change: TPR × 0.4–0.65 | per model, calibrate |
| Vehicle re-ID | τ 0.32–0.43, peak mReP 58–69 % on VeRi ([GOM](https://ar5iv.labs.arxiv.org/html/2011.11506)) | d′ ≈ 2.5 | TPR ≈ 0.7–0.8 at f = 1e-3 (same view) | cross-view: lower, no source | per model |
| Animal (MegaDescriptor) | open-set ARI ≈ 0.20 ([AnimalCLEF](https://ceur-ws.org/Vol-4283/paper368.pdf)); per-species thresholds | d′ ≈ 1.5–2 (weakest) | TPR ≈ 0.4–0.6 at f = 1e-3 | lower | per species |

Equations **[EXTRAPOLATION]**:
- **True target present.** The camera holds k files and m usable crops of the target. Then `P(YES | target) = 1 − Π_j (1 − TPR_j(q, k))`, where `TPR(q,k) = Φ((μ_G(q) + δ·ln k − τ)/σ_G)`, with δ ≈ 0.02–0.05 per doubling of k. Multiple references raise the max score, as AWS recommends multiple images; the size of the gain is not sourced.
- **Non-target only.** With N candidate crops, `P(YES | non-target) = 1 − (1 − f)^(N·k)`, where `f = 1 − Φ((τ − μ_I)/σ_I)`. Correlated crops within one track should be counted once (N → number of tracks).
- **Mapping to displayed percent.** Let `p_disp = σ(a·(s − τ_80) + logit 0.8)`, with a chosen so that p_disp = 0.7 at τ_70 and 0.9 at τ_90 (option B in §2). Alternatively, report a calibrated posterior with a prior π from the expected number of target crops.
