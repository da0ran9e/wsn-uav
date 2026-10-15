# Recognition task and target modality for an edge camera node receiving a compact query (Layer 1)

Scope: which recognition task (detection / attribute search / 1:1 / open-set 1:N / retrieval-re-ID) and which modality (face, whole-body re-ID, gait, vehicle re-ID, LPR, text/attribute person search) best fits: a UAV pushes a ~100 kB–1 MB query over 802.15.4 into heterogeneous urban cameras, each node scans hours to days of its own footage and returns a few-byte suspicion score over LoRa/satellite.

Labels used below:
- **[S]** means the figure came from a source retrieved in this session (link given).
- **[M]** means the figure comes from the researcher's own knowledge of the paper. The paper is named, but the number was NOT re-checked in this session. Verify it before quoting it in the paper.

---

## 1. Task types and how their metrics differ

### Takeaway
The deployment is **open-set retrieval with a reject option**. Most probes (people in a node's footage) are not the target, and each node must output a ranked score plus a decision threshold. That makes 1:N open-set metrics (FNIR@FPIR, or TPIR@FPIR) and retrieval metrics (Rank-k/mAP) the relevant ones. Closed-set Rank-1 and 1:1 verification accuracy overstate field performance.

### Cited Findings
- QMUL-SurvFace defines two protocols. **1:1 verification** is reported as TAR@FAR and ROC. **1:N open-set identification** uses a 3,000-ID gallery and 10,254 probe IDs, many of them non-mated distractors, and is reported as TPIR vs FPIR. — [Cheng et al., Surveillance Face Recognition Challenge, arXiv 1804.09691](https://arxiv.org/abs/1804.09691) [S]
- That paper argues open-set identification is harder but **required for surveillance** "due to the presence of a large number of non-target people (distractors) in public space". — [arXiv 1804.09691](https://arxiv.org/pdf/1804.09691) [S]
- NIST FRTE 1:N reports **FNIR at a threshold fixing FPIR = 0.003**. It ranks each developer's most accurate algorithm by mean rank across eight dataset columns (mugshot, visa/border, webcam, profile, etc.). — [NIST FRTE 1:N](https://pages.nist.gov/frvt/html/frvt1N.html) [S]
  - The latest report is dated 2026-03-30.
  - Vendor press releases claiming "#1" placements differ by column and are not NIST statements. — [Innovatrics](https://www.innovatrics.com/news/innovatrics-stands-out-in-latest-nist-frte-1n-benchmark/), [ROC](https://roc.ai/2025/09/10/roc-is-1-american-vendor-in-nist-frte-ranking-among-the-worlds-most-accurate-face-recognition-algorithms/) [S]
- Re-ID and text-based person search report **CMC Rank-k and mAP** over a gallery of crops. Every query is assumed to have a match in the gallery, so the setting is closed-set. — e.g. [CLIP-SCGI, arXiv 2410.09382](https://arxiv.org/pdf/2410.09382) [S]
- Detection and attribute recognition report AP/mAP for detection and mA (mean accuracy) or F1 for attributes. **[M]**: standard practice on PA-100K, PETA and RAP. Not re-checked this session.

### Metric summary table

| Task | Question answered at node | Typical metric | Open/closed set | Fit for this system |
|---|---|---|---|---|
| Detection | "Is there a person or child?" | AP@IoU | n/a | Pre-filter only; carries no identity |
| Attribute search | "Child-sized, red jacket?" | mA, F1; Rank-k for text queries | Retrieval | Good coarse filter; weak alone (many matches) |
| 1:1 verification | "Is this crop the target?" | TAR@FAR, FNMR@FMR | Pairwise | Building block; ignores the many-probe effect |
| Open-set 1:N | "Which watch-list target, or nobody?" | FNIR@FPIR (NIST), TPIR@FPIR | Open | **Matches deployment semantics** |
| Retrieval / re-ID | "Rank my stored crops by similarity" | Rank-1/5, mAP | Closed (benchmark) | **Matches node output** (top score becomes the suspicion score) |

### Inferences
- The node's job is to rank its own stored crops against the query and then threshold the top score. Benchmarks report this as closed-set Rank-k/mAP, but the deployment needs an FPIR-type operating point. A false alarm sends UAV team 2 to the wrong place.
- The paper should report the per-node false-alarm rate and the cluster-level miss rate. Rank-1 alone is not enough.

### Gaps
- No re-ID benchmark found that reports a standard open-set (FNIR@FPIR) protocol comparable to NIST. Re-ID open-set numbers are scattered.

---

## 2. Modalities: state-of-the-art accuracy on key benchmarks

### Takeaway
On clean benchmarks, face (IJB-C), whole-body re-ID (Market-1501) and vehicle re-ID (VeRi-776) all reach 85–97 % on their headline metrics. Gait is around 75–81 % Rank-1 in the wild, and text-to-person search around 65–77 % Rank-1. These numbers are not comparable across modalities. What matters is how far each one falls under surveillance conditions (Section 3).

### Cited Findings

**Face**
- AdaFace (CVPR 2022) reaches **IJB-C TAR@FAR=1e-4 ≈ 97.39 %** (WebFace4M training), about 97.09 % with MS1MV3. — [AdaFace arXiv 2204.00964](https://arxiv.org/pdf/2204.00964); leaderboard listing via [wizwand](https://www.wizwand.com/paper/68fa6e8c1e209131cea407e3) [S]
- LFW is saturated at about 99.8 % verification accuracy for modern margin losses (ArcFace, AdaFace). **[M]**
- **TinyFace (low-res, native surveillance-like) Rank-1** [S]:
  - AdaFace R100: ≈ 68.2 % (MS1MV2 training) and ≈ 72.0 % (WebFace4M training). — [AdaFace](https://arxiv.org/pdf/2204.00964), [github results table](https://github.com/wolfworld6/adaface)
  - A 2024 adapter method on top of AdaFace: 75.99 % Rank-1 and 79.13 % Rank-5. — [arXiv 2407.14972](https://arxiv.org/html/2407.14972v1)
- **QMUL-SurvFace (native surveillance faces)** [S]:
  - The original benchmark's best model (CentreFace) gets **29.9 % closed-set Rank-1**, compared with 65.2 % on MegaFace.
  - In **open-set 1:N** it gets **≈ 13.2–13.8 % TPIR at rank-20, FPIR = 10 %**. The two figures come from different versions of the paper. — [arXiv 1804.09691](https://arxiv.org/abs/1804.09691)
  - A cross-resolution paper reports about 55–61 % 1:1 verification accuracy, and an open-set AUC of 13.8 %, which falls to 9.9 % on super-resolved images. — [arXiv 1912.02851](https://arxiv.org/pdf/1912.02851)
  - An aggregator lists DiscFace at TAR@FAR=0.1 = 35.9. Unverified. — [hyper.ai](https://hyper.ai/en/sota/tasks/face-verification/benchmark/face-verification-on-qmul-survface)
- **NIST FRTE 1:N** [S]: metric is FNIR@FPIR=0.003, reported per column (mugshot, border, webcam, profile). — [NIST FRTE 1:N](https://pages.nist.gov/frvt/html/frvt1N.html)
  - The per-column table could not be extracted in this session; the page fetch was truncated.
  - **[M]**: leading algorithms reach FNIR well under 1 % on high-quality mugshots at gallery sizes around 1.6 M. FNIR is markedly higher on webcam and profile imagery.
- **NIST FIVE (face in video, non-cooperative subjects)** is NISTIR 8173 (Grother, Ngan, Quinn 2017). It is not part of the FRVT series. — [NIST](https://www.nist.gov/node/1190016) [S]
  - **[M]**: FIVE showed that error rates in non-cooperative video are much higher than for cooperative stills, and that they depend strongly on camera placement, with ceiling cameras worst.
  - A video-surveillance vendor argues that FRVT stills results do not transfer to surveillance. That is a vendor view. — [Oosto](https://oosto.com/5-limitations-of-nists-frvt-testing-for-video-surveillance/) [S]

**Person re-ID (whole body)**
- CLIP-ReID baseline: Market-1501 **94.7 % R1 / 88.1 % mAP**; MSMT17 **82.1 % R1 / 60.7 % mAP**. BoT baseline: Market 94.5 / 85.9. — table in [Sensors 2025, PMC11769178](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11769178/) [S]
- CLIP-SCGI (2024) claims MSMT17 **88.2 % R1 / 92.9 % mAP** (ViT). An aggregator lists different numbers, so this is inconsistent; check the paper. — [arXiv 2410.09382](https://arxiv.org/pdf/2410.09382) [S]
- Ye et al., "Deep Learning for Person Re-identification: A Survey and Outlook", TPAMI 2021, proposes the AGW baseline. **[M]**: AGW gets about 95.1 % R1 / 87.8 % mAP on Market-1501 and about 68 % R1 / 49 % mAP on MSMT17. The survey identifies open-world issues (domain shift, open-set, clothing change, low resolution) as the main gap.
- **Clothes-changing re-ID (CC protocol)**, all RGB-only [S]:
  - PRCC: CAL 55.2 R1 / 55.8 mAP; AIM 57.9 / 58.3; CCFA 61.2 / 58.4. One 2025 paper claims 70.6 / 69.1.
  - LTCC: CAL 40.1 / 18.0; AIM 40.6 / 19.1; CCFA 45.3 / 22.1; the 2025 paper claims 45.6 / 19.8.
  - Sources: [arXiv 2501.05851](https://arxiv.org/pdf/2501.05851), [arXiv 2305.06145](https://arxiv.org/pdf/2305.06145)
- **Cross-domain re-ID**: adding non-domain-specific data and random erasing gives on average +4.3 % mAP and +4.0 % R1 for CLIP re-ID. — [Sensors 2025](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11769178/) [S]
  - **[M]**: direct transfer (e.g. Market→Duke) typically drops mAP from about 80–90 % to roughly 20–40 % for older CNN baselines. Unverified this session.

**Gait**
- In-the-wild Rank-1 [S]:
  - DeepGaitV2: Gait3D 74.4 %, GREW 77.7 %.
  - CoD² (2025): Gait3D 78.3 %, GREW 81.2 %.
  - RRS-Gait-L: 76.7 % / 81.0 %.
  - Source: [arXiv 2511.06245](https://arxiv.org/pdf/2511.06245)
- **Cross-dataset** [S]: train GREW → test Gait3D gives **16.5 %** Rank-1; train Gait3D → test GREW gives 43.9 %. — [arXiv 2511.06245](https://arxiv.org/pdf/2511.06245)
- **[M]**: CASIA-B (lab) Rank-1 is above 90 % for normal walking in modern models, lower for coat-wearing. Gait needs a segmented silhouette sequence of ≥ ~30 frames.

**Vehicle re-ID**
- VeRi-776 [S]:
  - 2019: 85.2 % mAP / 96.6 % R1. — [CVPRW 2019](https://openaccess.thecvf.com/content_CVPRW_2019/html/AI_City/Ayala-Acevedo_Vehicle_Re-Identification_Pushing_the_limits_of_re-identification_CVPRW_2019_paper.html)
  - 2024 LKA-ReID: 84.5 % mAP / 97.6 % R1. — [arXiv 2409.17908](https://arxiv.org/pdf/2409.17908)
  - mAP rose from 12.76 % (2016) to 85.2 % (2020). — [review arXiv 2102.09744](https://arxiv.org/pdf/2102.09744)
- VehicleID: no figure retrieved this session.

**Licence-plate recognition**
- Laroca et al. layout-independent YOLO ALPR: about 96.8 % average end-to-end recognition over 8 public datasets, real time. — [arXiv 1909.01754](https://arxiv.org/abs/1909.01754v3) [S]
- On UFPR-ALPR, the original 2018 system scored 78.33 %, and commercial systems scored below 70 %. — [arXiv 1802.09567](https://arxiv.org/abs/1802.09567v2) [S]
- CCPD: no figure retrieved this session.

**Text / attribute-based person search (CLIP-style)**
- CUHK-PEDES / ICFG-PEDES / RSTPReid Rank-1 [S]:
  - ROGLE (2026): **76.93 / 66.97 / 65.20 %**. — [arXiv 2606.01825](https://arxiv.org/pdf/2606.01825)
  - PLOT: 75.28 / 65.76 / 61.80 %. — [arXiv 2409.13475](https://arxiv.org/pdf/2409.13475)
  - IRRA (CVPR 2023) on ICFG-PEDES: 63.46 %.
- **[M]**: IRRA CUHK 73.38 %, RSTPReid 60.20 %. RDE (CVPR 2024) about 75.9 / 67.7 / 65.4 %.
- CUHK-PEDES has 11,003 IDs, 34,054 images and 68,108 descriptions. — [arXiv 2501.17586](https://arxiv.org/pdf/2501.17586) [S]

### Comparison table (task × modality)

| Modality | Natural task | Clean-benchmark SOTA | Surveillance / hard-condition figure | Query size (approx.) | Biometric (GDPR Art. 4(14))? |
|---|---|---|---|---|---|
| Face | 1:1, open-set 1:N | IJB-C TAR@1e-4 ≈ 97.4 % [S]; LFW ≈ 99.8 % [M] | TinyFace R1 ≈ 68–76 % [S]; SurvFace R1 29.9 %, open-set TPIR ≈ 13 % @ FPIR 10 % [S] | 512-d template ≈ 1–2 kB per image | **Yes**, special category when used to identify |
| Whole-body re-ID | Retrieval | Market R1 ≈ 95 % / mAP 88 % [S]; MSMT17 R1 82–88 % [S] | Clothes-change PRCC R1 55–71 %, LTCC R1 40–46 %, mAP ≈ 20 % [S]; cross-domain large drop [M] | 512–2048-d embedding ≈ 1–8 kB per image | Arguably (physical characteristics allowing unique identification); contested |
| Gait | Retrieval | GREW R1 ≈ 78–81 %, Gait3D ≈ 74–78 % [S] | Cross-dataset R1 16.5–43.9 % [S] | Sequence template, small | Yes (behavioural biometric) |
| Vehicle re-ID | Retrieval | VeRi-776 mAP ≈ 85 %, R1 ≈ 97 % [S] | n/a this session | ~kB | No (unless linked to a person) |
| LPR / ANPR | Exact string match | ≈ 96.8 % end-to-end over 8 datasets [S] | UFPR-ALPR legacy 78 %, commercial < 70 % [S] | A few bytes | No, but personal data |
| Text / attribute search | Retrieval | CUHK-PEDES R1 ≈ 75–77 % [S] | RSTPReid R1 ≈ 60–65 % [S] | A few hundred bytes | Generally not biometric (no unique template) |

### Inferences
- Every option fits the link budget. A face or re-ID query of a few reference images, with embeddings and/or thumbnails, is roughly 5–50 kB, well within a 100 kB–1 MB cluster delivery. A text or attribute query is under 1 kB.
  - The binding constraint is therefore recognition robustness, not transport.
  - A raw-image query (e.g. 10–20 JPEG crops ≈ 200–600 kB) is also feasible. This lets each node compute embeddings with whatever model it runs, which solves model heterogeneity across vendors. That is a design point for the paper.
- Face open-set accuracy drops sharply in native surveillance imagery: from about 97 % TAR on IJB-C to about 13 % open-set TPIR on SurvFace.

### Gaps
- NIST FRTE per-column FNIR values were not extracted; the page fetch was truncated.
- No VehicleID, CCPD or Market→Duke cross-domain numbers were retrieved this session.
- No open-set re-ID benchmark numbers were found.

---

## 3. Accuracy drop under surveillance conditions

### Takeaway
The main degradation drivers are, in rough order:
- **resolution** (face is hit hardest),
- **clothing change and long time gaps** (hits whole-body re-ID hardest),
- **domain or camera shift** (hits gait and re-ID),
- pose and lighting.

In a lost-child or suspect search, the gap between the reference and the footage is hours to a few days. Clothing is likely unchanged for a lost child but possibly changed for a suspect.

### Cited Findings
- Face, native low resolution: QMUL-SurvFace's best model gets 29.9 % closed-set Rank-1, compared with 65.2 % for the same model on MegaFace; open-set TPIR is about 13 % at FPIR 10 %. — [arXiv 1804.09691](https://arxiv.org/abs/1804.09691) [S]
- Super-resolution does **not** rescue surveillance faces: open-set AUC falls from 13.8 % on original images to 9.9 % on super-resolved ones. — [arXiv 1912.02851](https://arxiv.org/pdf/1912.02851) [S]
- Clothing change roughly halves re-ID accuracy: Market R1 ≈ 95 % vs LTCC CC R1 ≈ 40–46 % with mAP ≈ 20 %. — [PMC11769178](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11769178/), [arXiv 2501.05851](https://arxiv.org/pdf/2501.05851) [S]
- Gait collapses across domains: 16.5 % R1 for GREW→Gait3D. — [arXiv 2511.06245](https://arxiv.org/pdf/2511.06245) [S]
- The CLIP re-ID domain gap is measurable and can be partly closed with more diverse training data. — [PMC11769178](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11769178/) [S]
- NIST FIVE: non-cooperative video is the hard case for face recognition. — [NIST](https://www.nist.gov/node/1190016) [S]

### Inferences
- With mixed doorbell (close, frontal, fisheye), security cam (elevated, off-angle) and dashcam (moving, motion blur) footage, face will be usable at **a minority of nodes**: doorbells and entrance cameras. Whole-body appearance is visible at most nodes.

### Gaps
- No quantitative study found on recognition accuracy specifically for doorbell or dashcam footage.

---

## 4. Minimum pixels-on-target per modality and typical footage quality

### Takeaway
- **IEC 62676-4 (2014)**: "identification" (human operator) needs 250 px/m, about 40 px across the face.
- **IEC 62676-4 (2025)**: renamed and finer categories, up to 500 px/m ("Validate", 80 px/face) and 1500 px/m. 500 px/m is said to suffice for most automatic face recognition.
- Whole-body re-ID benchmarks use crops of about 128×64 to 256×128 px. The person's height in pixels is far easier to satisfy than face pixels at typical CCTV distances.

### Cited Findings
- IEC 62676-4:2014: Identification = 250 px/m = 40 px/face, assuming a 16 cm face width. — [Axis whitepaper 2014](https://whitepapers.axis.com/en-us/pixel-density-based-on-iec-62676-4-2014) [S]
- IEC 62676-4:2025 levels: Overview 20 px/m (3 px/face), Outline 40, Discern 80, Perceive 125, Characterize 250 (40 px/face), Validate 500 (80 px/face), Scrutinize 1500 (240 px/face). — [Axis whitepaper 2025](https://whitepapers.axis.com/en/pixel-density-based-on-iec-62676-4-2025) [S]
  - The standard targets human operators; "other definitions apply" for software analytics. — same source [S]
- "500 px/m is also sufficient for most automatic face recognition software". Industry claim, not a standard. — [asmag](https://www.asmag.com/showpost/35334.aspx) [S]
- **[M]**: ISO/IEC 19794-5 / ICAO passport photos specify ≥ 90 px inter-eye (120 px recommended). QMUL-SurvFace faces average about 24×20 px. TinyFace faces are ≤ 32×32 px. Market-1501 crops are 128×64.

### Inferences
- Example: a 1080p camera with an approx. 90° horizontal field of view covers about 1920 px over 2·d·tan(45°) m of width. That is roughly 960/d px/m, so 250 px/m holds only to about 4 m and 500 px/m to about 2 m.
  - Under these assumptions, automatic face recognition at typical CCTV ranges (5–20 m) is mostly below the "Characterize" level.
  - Whole-body re-ID needs only about 128 px of person height. A 1.7 m adult at 20 m gives about 960/20 × 1.7 ≈ 80 px, marginal. At 10 m it gives about 160 px, adequate. A 1.1 m child at 10 m gives about 105 px, marginal.
  - This is a back-of-envelope geometric estimate, not a sourced figure.

### Gaps
- No authoritative minimum plate-character height in pixels was found. ALPR guidance commonly cites about 15–20 px per character, but this is unverified.
- No sourced typical resolution or field-of-view distribution for doorbells or dashcams.

---

## 5. Children specifically

### Takeaway
Face recognition is least reliable on children:
- NIST NISTIR 8280 (2019) found elevated false positives at both age extremes, including children.
- False non-match rates rise sharply for ages 0–5. This is reported by a vendor citing NIST and needs checking against the report.

Rapid facial growth also makes old reference photos stale. No dedicated re-ID-for-children benchmark was found.

### Cited Findings
- NISTIR 8280, FRVT Part 3: Demographic Effects (Dec 2019), doi 10.6028/NIST.IR.8280. It reports elevated false positives in the elderly and in children, with the largest effects at the youngest and oldest ages. — secondary summary [defensedaily](https://defensedaily.com/nist-study-finds-demographics-make-difference-face-recognition-algorithms/homeland-security); annexes [NIST annex 11](https://pages.nist.gov/frvt/reports/demographics/annexes/annex_11.pdf) [S]. The wording was not verified against the main report body.
- NIST annexes give cross-age FMR heatmaps on high-quality portraits, so the effect is not explained by blur. — [annex 09](https://pages.nist.gov/frvt/reports/demographics/annexes/annex_09.pdf) [S]
- A vendor citing NIST says FNMR rises for ages 0–5 at FMR 1e-3 and 1e-4. — [SAFR KB](https://support.safr.com/kb/does-face-recognition-accuracy-vary-with-age) [S], vendor source
- "Does Face Recognition Accuracy Get Better With Age? Deep Face Matchers Say No". — [arXiv 1911.06396](https://arxiv.org/pdf/1911.06396) [S], title only, contents not reviewed
- **[M]**: the lost child is typically reported within hours. The reference image (a parent's phone photo taken the same day) shows the same clothing. This favours appearance re-ID plus attributes such as height class and clothing colour.

### Inferences
- For the **lost-child** use case:
  - Face is the weakest modality: higher error for children, small faces in CCTV, and children are short, so elevated cameras see the top of the head.
  - Whole-body appearance (clothing is unchanged within hours) plus a "child-sized" attribute filter is the strongest option.
- For a **suspect**: clothing change is plausible, so a face channel at doorbell and entrance nodes, plus body re-ID, is complementary.

### Gaps
- No benchmark found for person re-ID performance on children or for height-based attribute accuracy.

---

## 6. Legal / privacy constraints (brief)

### Takeaway
- Face, gait and arguably body re-ID used to uniquely identify a person are **biometric data**: a GDPR Art. 9 special category, and in scope of the AI Act's remote biometric identification (RBI) rules.
- Real-time RBI in public spaces for law enforcement is prohibited under AI Act Art. 5(1)(h). There is a narrow exception for targeted searches for victims of abduction, trafficking and sexual exploitation and for **missing persons**, subject to authorisation.
- Text or attribute-only search and vehicle re-ID are not biometric, but they still process personal data.

### Cited Findings
- AI Act (Reg. (EU) 2024/1689), Art. 5(1)(h)(i): exception for targeted search for specific victims of abduction, trafficking or sexual exploitation and **search for missing persons**. Under Recital 33 it is limited to "exhaustively listed and narrowly defined situations" and requires safeguards. — [springlex AI Act text](https://www.springlex.eu/en/packages/ai-act/ai-act-regulation/annex-2/), [Polish law journal](https://pressto.amu.edu.pl/index.php/zpuam/article/download/46484/42160/128282) [S]
- The 2021 Commission proposal used the phrase "missing children" and required prior judicial or independent authorisation, with an urgency exception. — [Ni Loideain, Info Law Centre](https://infolawcentre.blogs.sas.ac.uk/2021/08/04/a-trustworthy-framework-that-respects-fundamental-rights-the-draft-eu-ai-act-and-police-use-of-biometrics/) [S]
- GDPR definitions **[M]**, from the regulation text at [EUR-Lex 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj):
  - Art. 4(14) defines biometric data as data from specific technical processing of physical, physiological or behavioural characteristics that allow or confirm unique identification, explicitly incl. facial images.
  - Art. 9(1) prohibits processing biometric data "for the purpose of uniquely identifying a natural person", with exceptions in 9(2).

### Inferences
- The architecture is well placed legally:
  - The query goes **to** the data; raw footage never leaves the device; only a few-byte score is returned. That is a data-minimisation argument for the paper.
  - It is closer to post (retrospective) RBI on stored footage than to "real-time" RBI. Post-RBI is high-risk under Annex III rather than prohibited. **[M]**: verify this against Art. 26(10).
- Choosing appearance re-ID plus attributes, rather than face, may reduce the biometric-data burden, but this is legally contested.

### Gaps
- The exact Art. 5(1)(h) text was not checked against the Official Journal in this session.
- Not covered: whether whole-body re-ID embeddings legally count as biometric data, and Vietnamese / non-EU law.

---

## 7. Recommendation: which task/modality for this experiment

### Takeaway
Recommended primary choice: **open-set person retrieval with whole-body appearance re-ID, gated by a person/child detector and an attribute filter.** Each node ranks its stored person crops against a few reference images and returns its best-match score as the suspicion score.
- Face is an *optional second channel* at nodes with close frontal views (doorbells, entrances).
- Vehicle re-ID / LPR is a separate query type for vehicle targets.

The main trade-offs:
- Re-ID handles the camera diversity best.
- Face gives stronger identity evidence but works only at a few nodes and is weakest on children.
- Clothing change breaks re-ID: for suspects, LTCC R1 is about 40–46 %.

### Cited Findings (supporting the choice)
- Re-ID on standard benchmarks: R1 82–95 %. — [PMC11769178](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11769178/) [S]
- Face in native surveillance: closed-set R1 29.9 %, open-set TPIR ≈ 13 %. — [arXiv 1804.09691](https://arxiv.org/abs/1804.09691) [S]
- Clothes-changing penalty: LTCC R1 40–46 %. — [arXiv 2501.05851](https://arxiv.org/pdf/2501.05851) [S]
- Gait cross-domain: 16.5–43.9 % R1, and it needs long silhouette sequences. — [arXiv 2511.06245](https://arxiv.org/pdf/2511.06245) [S]
- Text-to-person search: R1 ≈ 65–77 %. It is useful when no image exists (eyewitness description), but weaker than image-based re-ID. — [arXiv 2606.01825](https://arxiv.org/pdf/2606.01825) [S]
- Pixel needs: face identification needs ≥ 250–500 px/m. — [Axis IEC 62676-4:2025](https://whitepapers.axis.com/en/pixel-density-based-on-iec-62676-4-2025) [S]

### Ranked options for the experiment

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **A. Body re-ID + attribute/child filter (open-set retrieval)** | Works at most cameras; same-day clothing for lost child; benchmark R1 82–95 %; query 5–50 kB of embeddings or crops fits the 802.15.4 budget; less clearly biometric | Clothing change; cross-domain drop; closed-set benchmarks overstate field performance | **Primary** |
| B. Face open-set 1:N | Strongest identity evidence when the face is visible; NIST-grade metrics | Fails at most CCTV ranges; worst for children; clearly biometric under Art. 9 / AI Act | Secondary channel at doorbell/entrance nodes |
| C. Text/attribute search only | Tiny query (< 1 kB); needs no reference photo | Low precision; many matches lead to false alarms | Fallback / pre-filter |
| D. Gait | Clothing-invariant | Needs sequences and segmentation; poor cross-domain transfer; heavy compute | Not for this work |
| E. Vehicle re-ID / LPR | High accuracy, plates are a few bytes | Different target class; LPR needs plate resolution | Separate use case (suspect vehicle) |

### Inferences
- For the paper's Layer 1 model, the query is K reference crops or embeddings of 1–3 targets: roughly 2–8 kB per embedding, or 20–50 kB per JPEG crop.
  - A cluster receiving 100 kB–1 MB can therefore hold either full image sets (model-agnostic) or embeddings (model-specific, smaller).
  - This links Layer 1 "how much data is enough" to the number of reference views K. More views (front, back, side) raise re-ID robustness.
- The node's score is max similarity over stored crops, thresholded. False-alarm control at the cluster level (the FPIR analogue) matters more than Rank-1, because each false positive costs a team-2 UAV visit. This is consistent with the 2–3 false suspicion points already modelled in the mission simulation.
- Child case: combine the re-ID score with a height/age-class attribute check to cut false positives from adult look-alikes in similar clothes.

### Gaps
- No published field study was found that measures re-ID or face accuracy on heterogeneous consumer cameras (doorbell, dashcam, vending machine) together.
- No figures retrieved on edge-compute cost (e.g. embedding throughput on embedded SoCs) for scanning days of footage; this needs a separate search.
