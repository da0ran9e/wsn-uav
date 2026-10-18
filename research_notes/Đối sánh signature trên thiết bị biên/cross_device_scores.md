# Cross-device match-score variation: same recognition model, same reference signatures, different edge devices

Scope: a UAV delivers 3–5 signature files (~4–5 KB, about one 512-d fp16 embedding or a few smaller codes per file). Heterogeneous cameras (HiSilicon/Ambarella/Rockchip SoCs, doorbells, RPi + Hailo/Coral, Jetson) embed their own crops and answer YES if cosine ≥ a fixed threshold in the 0.70–0.90 range. The question is how much the score moves because of the device.

Research budget note: about 15 search/fetch calls. Several primary PDFs could not be read (403, or binary PDF with no text extraction available), so some numbers come from search-result snippets of the named source. Each one is marked. Items marked **[VENDOR]** are vendor-measured or vendor-claimed. Items marked **[INFERENCE]** are my own extrapolation.

---

## (a) Quantization (fp32 / fp16 / int8 / int4) and NPU compilers: how much do score and accuracy move?

### Takeaway
With competent post-training quantization, published benchmark accuracy (LFW verification, ImageNet top-1) barely moves: about 0–0.8 pp. But benchmark accuracy is a saturated, threshold-re-tuned metric. It hides the per-pair cosine shift. The one practitioner measurement found reports an int8 cosine offset of about +0.025 on Hailo, against about ±0.017 threshold-estimation noise. Nobody publishes per-pair |Δcos| tables for these toolchains. Vendor tools (RKNN `accuracy_analysis`) do expose per-layer cosine between float and quantized outputs, so the drift can be measured on each device.

### Cited Findings
- **[VENDOR] Hailo Model Zoo (Hailo-8), face recognition, LFW verification accuracy:** arcface_mobilefacenet float 99.4 % → hardware-quantized 99.4 %. arcface_r50 float 99.7 % → quantized 99.7 %. Δ = 0.0 pp at this precision. — [Hailo Model Zoo HAILO8_face_recognition.rst](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8/HAILO8_face_recognition.rst)
- The same Hailo model (512-d embedding, 112×112×3 input, LFW 99.4 %) is re-listed by Seeed SenseCraft. — [Seeed SenseCraft arcface_mobilefacenet](https://sensecraft.seeed.cc/ai-lab/en/models/arcface_mobilefacenet)
- A Hailo community user asked for the float teacher of `arcface_mobilefacenet--112x112_quant_hailort_hailo8l_1`, to check that its embedding matches the quantized one "minus some %". So the float reference for per-pair comparison is not readily published. No answer confirming availability was found. — [Hailo community thread](https://community.hailo.ai/t/providing-original-model-of-arcface-mobilefacenet-112x112-quant-hailort-hailo8l-1/18630)
- **[VENDOR] ONNX Model Zoo:** int8 ArcFace LResNet100E-IR reports a 0 % accuracy drop ratio on LFW vs fp32, with a 1.78× speed-up. — [onnxmodelzoo/arcfaceresnet100-11-int8](https://huggingface.co/onnxmodelzoo/arcfaceresnet100-11-int8)
- **Peer-reviewed (GI/BIOSIG):** sub-byte quantization of MobileFaceNet reaches 98.68 % (8-bit) and 98.63 % (4-bit) on LFW. — [dl.gi.de 20.500.12116/39700](https://dl.gi.de/handle/20.500.12116/39700) (abstract via search snippet; fp32 baseline not retrieved)
- **Ef-QuantFace (arXiv 2402.18163):** R50 w8a8 reaches 94.13 % TAR@FAR=1e-4 on IJB-C. The QuantFace-style w8a8 baseline for R100 is listed at about 96.38 %. The table header was garbled in extraction, so column alignment is unconfirmed. — [Ef-QuantFace](https://arxiv.org/abs/2402.18163); QuantFace claims up to 5× size reduction "while maintaining, to a large degree" full-precision verification performance — [QuantFace arXiv 2206.10526 / hyper.ai IJB-C listing](https://hyper.ai/en/sota/tasks/quantization/benchmark/quantization-on-ijb-c)
- **Reference fp32 operating point:** ArcFace R100/MS1MV2 reaches TAR@FAR=1e-4 of 94.2 % (IJB-B) and 95.6 % (IJB-C). — [ArcFace CVPR 2019](https://openaccess.thecvf.com/content_CVPR_2019/papers/Deng_ArcFace_Additive_Angular_Margin_Loss_for_Deep_Face_Recognition_CVPR_2019_paper.pdf)
- **Practitioner measurement (not peer-reviewed; page returned 403, figures from the search snippet only):** for a pretrained ArcFace encoder compiled through a Hailo toolchain to int8, the re-fitted int8 cosine gap was about **+0.025**. Resampling the evaluation pairs moved the fp32 threshold by **±0.017** (95 % half-width), so the gap is only about 1.5× the threshold noise. The author warns that keeping the fp32 threshold on the int8 model can make FAR look better while hiding extra false rejects, so both FAR and FRR must be checked at the operating threshold. — [Towards Data Science, "The Number Your Quantization Gate Doesn't Have"](https://towardsdatascience.com/the-number-your-quantization-gate-doesnt-have/)
- **RKNN-Toolkit2** ships `accuracy_analysis`, which "will give the Euclidean or cosine distance of each layer of inference results before and after the model is quantized". It can run on the PC simulator or on the connected NPU device. — [Rockchip Quick Start RKNN Toolkit (Radxa mirror)](https://dl.radxa.com/rockpin10/docs/sw/rknn-toolkit/Rockchip_Quick_Start_RKNN_Toolkit_V1.3.0_EN.pdf); [RKNN-Toolkit2 docs](https://docsearch.algolia.com/mcp/docs/repo/rockchip-linux/rknn-toolkit2)
- **Failure case (forum, not peer-reviewed):** a PyTorch → ONNX → RKNN conversion on RK3588 reported a "cliff-like" accuracy drop of 20–30 % or more until it was debugged layer by layer. — [CSDN/GitCode post](https://gitcode.csdn.net/6a277c7110ee7a33f279960f.html)
- **TensorRT INT8:** a third-party 2026 evaluation on A5000 reports < 0.5 % top-1 degradation for ResNet/ResNeXt. — [NPU Hardware Evaluation v1.0, arXiv 2609.13166](https://arxiv.org/pdf/2609.13166). NVIDIA's INT8 sample documentation says FP32 and INT8 top-1/top-5 "should be within 1 %" (a tolerance, not a measurement; secondary mirror). — [8-bit Inference with TensorRT (Scribd copy)](https://www.scribd.com/document/640713581/8-Bit-Inference-With-TensorRT)
- **Calibration matters:** in TVM, ResNet-50 top-1 fell from 76.25 % to about 50–55 % under a misconfigured KL calibration, against 75.61 % with another scaling mode. — [TVM forum](https://discuss.tvm.apache.org/t/quantization-accuracy-drop-with-kl-divergence/5642)
- **[VENDOR] OpenVINO** publishes an INT8-vs-FP32 accuracy table per model. Not fetched. — [OpenVINO 2022.1 int8 vs fp32](https://docs.openvino.ai/2022.1/openvino_docs_performance_int8_vs_fp32.html)
- **Person re-ID on Edge TPU:** the Coral re-ID paper compares re-ID accuracy on GPU vs Coral TPU across parser backbones. The figures could not be extracted. — [arXiv 2209.11024](https://arxiv.org/abs/2209.11024). STMicro publishes an int8 TFLite OSNet (α = 0.25, 0.197 M params) with no accuracy figures. — [STMicroelectronics/osnet](https://huggingface.co/STMicroelectronics/osnet/commit/7e31643338e77ee1b73409d43a7ebd99271d07e5)

### Inferences
- **[INFERENCE]** Benchmark tables (Hailo, ONNX zoo, OpenVINO) report accuracy after an optimal threshold is chosen for each model variant, and LFW is saturated near 99.x %. A "0.0 pp" entry therefore does **not** mean the same cosine score. It means the ranking and separability are preserved. In our system the threshold is fixed and shared, so what matters is the systematic offset (a bias, like the +0.025 above) plus per-pair jitter.
- **[INFERENCE]** A working estimate for a well-calibrated int8 PTQ face embedder vs its fp32 reference: per-pair |Δcos| of about 0.01–0.03 (1–3 pp of a percentage score), sometimes with a consistent sign. fp16 vs fp32 should be about an order of magnitude smaller (fp16 has 11 significant bits; LayerNorm/BN-folded CNNs rarely amplify that). int4 or a badly calibrated int8 can be far worse; the RKNN and TVM cases show 20–30 pp failures. This number comes from one practitioner datapoint plus the zoo accuracy tables. It is not a published per-pair statistic.
- **[INFERENCE]** The signatures are delivered as fp16. If each device embeds its crops in int8, the comparison is "int8 query vs fp16 reference produced by the fp32 model". That is an asymmetric cross-precision comparison, and every device has its own quantization error on its side only.

### Gaps
- No peer-reviewed table of per-pair cosine drift (mean/p95 |Δcos|) between fp32 and int8 for ArcFace, MobileFaceNet, OSNet, ResNet50-IBN or CLIP on Hailo, Edge TPU, RKNN, SNPE/QNN or TensorRT was found.
- RKNN Model Zoo, Coral and Qualcomm AI Hub accuracy tables for face/re-ID embedders were not retrieved. Qualcomm AI Hub is believed to report on-device vs reference numerical similarity, but this was not verified.
- No int8 re-ID mAP/Rank-1 drop (OSNet on Market-1501) was found from a citable source.
- CLIP int8 embedding drift was not covered.

---

## (b) Do different hardware give bit-identical fp32 results? Model-version and backbone mismatch across devices

### Takeaway
The same fp32 model is **not** bit-exact across hardware. Floating-point addition is non-associative, and kernels, reduction orders and batch sizes differ, so results diverge at the last-bit level. For a single embedding with cosine scoring this is negligible (far below 0.001; [INFERENCE]), unlike in long autoregressive LLM generations. A different model version or backbone on different devices is catastrophic: embeddings from independently trained models are not comparable at all, unless they are trained to be compatible (BCT).

### Cited Findings
- Under bf16 and greedy decoding, DeepSeek-R1-Distill-Qwen-7B varies by up to 9 % in accuracy (and 9,000 tokens in length) when GPU count, GPU type or batch size changes. The root cause is non-associative floating-point arithmetic at limited precision. — [Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference (arXiv 2506.09501)](https://alphaxiv.org/abs/2506.09501)
- Frameworks pick different matmul kernels on each GPU architecture, with different reduction orders and unspecified tensor-core arithmetic. The rounding differences can flip output tokens. — [Emergent Mind summary of arXiv 2609.25624](https://www.emergentmind.com/papers/2609.25624) (secondary)
- Serving frameworks give different outputs when tensor-parallel size or batch size changes, even with greedy decoding. Tree-based invariant kernels are proposed as a fix. — [arXiv 2511.17826](https://arxiv.org/html/2511.17826v1)
- In ResNet training on TensorFlow, GPU non-determinism alone gave a test-accuracy std of 0.02 (fixed seeds) vs 0.027 (varied seeds). — [Non-Determinism in TensorFlow ResNets (arXiv 2001.11396)](https://ar5iv.arxiv.org/html/2001.11396)
- **BCT (Shen, Xiong, Xia, Soatto, CVPR 2020):** proposes backward-compatible training so that new embeddings can be compared directly with old gallery embeddings without "backfilling". This works even when dimension, architecture or loss differ. The compatibility criterion is that the cross-model test (new query vs old gallery) beats the old-vs-old test. On face recognition the authors report compatibility without loss of accuracy. — [CVPR 2020 open access](https://openaccess.thecvf.com/content_CVPR_2020/html/Shen_Towards_Backward-Compatible_Representation_Learning_CVPR_2020_paper.html); [arXiv 2003.11942](https://arxiv.org/pdf/2003.11942); follow-up [Universal BCT, arXiv 2203.01583](https://arxiv.org/pdf/2203.01583)

### Inferences
- **[INFERENCE]** The LLM figures do not carry over directly. Token-flip cascades amplify ULP-level differences across thousands of steps, while a single CNN forward pass followed by an L2-normalised dot product does not. With all devices running fp32/fp16 *the same weights*, expect |Δcos| ≪ 0.001. This is not a design concern compared with quantization or image effects.
- **[INFERENCE]** If two devices run *different* face models (e.g. a vendor's built-in doorbell model vs ArcFace), the cosine between their embeddings is meaningless, near the impostor level. The system **must** pin one model family, or deliver signatures per model family, or require BCT-style compatible models. That is a protocol requirement, not a tolerance.
- **[INFERENCE]** For our 4–5 KB payload, this argues for a "model ID" field in the signature header, and for possibly sending one signature per backbone family present in the cluster.

### Gaps
- No measured cross-hardware |Δcos| for an identical fp32 vision embedder (e.g. ArcFace on x86 CPU vs Jetson GPU vs ARM CPU) was found.
- The BCT numeric tables (cross-test vs self-test accuracies on IMDBFace) were not retrieved.

---

## (c) Camera, ISP, resolution and compression differences: genuine-score variation

### Takeaway
Image-side differences dominate by a wide margin. Cross-camera or cross-domain shift in person re-ID cuts Rank-1 by about 45–55 pp, and heavy compression or low resolution measurably lowers face comparison scores. This variation is **much larger** than any numeric/quantization effect from (a)/(b). Image quality is the main source of "device-induced" score variation, not the silicon.

### Cited Findings
- **Re-ID domain shift:** a ResNet-50 baseline gives 92.6 % Rank-1 / 79.6 % mAP within Market-1501 but falls to **37.6 % Rank-1** when tested directly on DukeMTMC-reID (about −55 pp). — [Learn by Guessing, arXiv 2101.01215 (search snippet)](https://arxiv.org/pdf/2101.01215)
- Other direct-transfer figures for Market→Duke: 31.8 % Rank-1 vs 80.2 % supervised; another paper reports 27.3 % (Market→Duke) and 46.8 % (Duke→Market). The gap is asymmetric. — [Unsupervised Domain Adaptive Re-ID, arXiv 1807.11334](https://arxiv.org/pdf/1807.11334); [arXiv 2007.15560](https://arxiv.org/pdf/2007.15560) (figures from search snippets; attribution between these two papers not verified line by line)
- Camera-level shift *within* a dataset is treated as its own domain gap in re-ID work (camera adaptation). — [Domain Camera Adaptation, arXiv 2208.08624](https://arxiv.org/pdf/2208.08624)
- **Compression:** Schlett et al. tested a state-of-the-art face recogniser (ArcFace per the NIST IFPC slides) under PNG resize, JPEG, JPEG 2000 and JPEG XL at fixed target sizes. JPEG XL gives better mean and worst-case recognition, especially below about 5 kB (ROI variant). At larger sizes there is no critical difference. "Effect on comparison scores" is analysed. — [arXiv 2302.12593](https://arxiv.org/abs/2302.12593); [NIST IFPC 2022 slides](https://pages.nist.gov/ifpc/2022/presentations/6_IFPC%202022-Compressed_Face_Image_Quality_Torsten%20Schlett.pdf)
- A 2026 IWBF paper (Andreas, Busch et al.) measures compression damage as the score between each image and its own compressed version, for targets ≥ 2 kB. — [Andreas FR with 1 kB, IWBF 2026](https://christoph-busch.de/files/Andreas-FRwith1kB-IWBF-2026.pdf); [Master thesis, h-da 2026](https://dasec.h-da.de/wp-content/uploads/2026/04/Masters-thesis-Paul-Andreas-Assessing-Lossy-Image-Compression-for-Face-Recognition.pdf)
- Lossy compression hurts ArcFace performance more for darker skin tones (up to 34.55 %), and chroma subsampling raises FMR. This is a news summary of an Imperial College study; check the original. — [Unite.AI summary](https://www.unite.ai/jpeg-compression-increases-facial-recognition-error-rate-for-non-caucasian-faces-study-finds/)
- **Quality ↔ score:** MagFace ties embedding magnitude to quality and shows FNMR@FMR=1e-3 falling as low-quality samples are rejected (error-vs-reject curves). Magnitude correlates strongly with cosine to the class centre. — [MagFace CVPR 2021](https://openaccess.thecvf.com/content/CVPR2021/papers/Meng_MagFace_A_Universal_Representation_for_Face_Recognition_and_Quality_Assessment_CVPR_2021_paper.pdf)
- QMagFace reports a linear relation between MagFace quality and comparison score. That relation is exploited to build a quality-aware score. SER-FIQ yields a more complex relation. — [QMagFace, WACV 2023](https://openaccess.thecvf.com/content/WACV2023/papers/Terhorst_QMagFace_Simple_and_Accurate_Quality-Aware_Face_Recognition_WACV_2023_paper.pdf)
- Survey of face image quality assessment methods. — [FIQA survey, arXiv 2009.01103](https://arxiv.org/pdf/2009.01103)
- **Demographic shift of score distributions** (ArcFace): the female impostor distribution is shifted higher, and female genuine distributions are lower. — [arXiv 2304.07175](https://arxiv.org/pdf/2304.07175)
- Human and machine accuracy on low-resolution faces. — [Peepers & Pixels, arXiv 2503.20108](https://arxiv.org/pdf/2503.20108)

### Inferences
- **[INFERENCE]** Camera optics, ISP tone mapping, H.264 bitrate, mounting height and viewing angle differ across a doorbell, a HiSilicon IPC and a Jetson-attached camera. These are the main drivers of genuine-score spread. For the same person, the spread is plausibly tenths of cosine (e.g. 0.2–0.4 between a frontal well-lit crop and a small, compressed, off-angle crop). No source in this session gave an exact per-pair Δcos vs resolution/bitrate figure, so this range is unverified.
- **[INFERENCE]** This shift is mostly **downward and quality-correlated** (it lowers genuine scores), not symmetric noise. A fixed threshold therefore turns low-quality devices into "always NO" devices (false non-matches), not into random answerers.

### Gaps
- No exact numbers were extracted for genuine-score drop vs JPEG size or resolution (Schlett et al. and the Andreas thesis have them; full text not read).
- No NIST FRVT/FRTE "quality" report figures were retrieved.
- No source gave re-ID cosine-score (as opposed to Rank-1) changes across cameras.

---

## (d) Consequences for a fixed threshold: portability, calibration, normalisation, and a defensible "score noise" number

### Takeaway
Standard practice (NIST FRTE methodology, vendor guidance) sets a threshold **per algorithm** to hit a target FMR on representative data. A raw cosine threshold is not portable across algorithms, and it is only approximately portable across precisions/compilers of the same model. Proposed working budget: device-numeric noise (same model, fp16/int8 compiled well) about 0.01–0.03 cos. Image/camera-induced genuine-score shift about 0.1–0.4 cos (unverified range). Different model families: incompatible. The 70 % vs 75 % example (Δ = 0.05) is about 2× the quantization noise, but small compared with image-quality effects. The genuine–impostor confusion band for ArcFace in hard conditions sits around cos 0.3–0.4. So a 0.70–0.90 threshold is very conservative for ArcFace-type models: it will mostly cause false NOs on poor cameras, not false YESes.

### Cited Findings
- NIST FRTE 1:1 defines FNMR as the proportion of mated comparisons below "a threshold set to achieve the false match rate (FMR) specified". FMR is "fixed independently for each dataset". Thresholds are therefore derived per algorithm and per dataset. — [NIST FRTE 1:1](https://pages.nist.gov/frvt/html/frvt11.html); example report card [id3_008](https://face.nist.gov/frte/reportcards/11/id3_008.html)
- NIST demographics slides describe high-threshold operation for automated use where false positives must be rare. — [NIST demographics 1:N slides](https://pages.nist.gov/frvt/html/slides/demographics_1N.pdf)
- **[VENDOR]** Innovatrics: public FNIR figures are computed at thresholds that limit FPIR to a chosen level (commonly 0.003). An accuracy number without an operating point is not comparable. — [Innovatrics glossary: threshold](https://www.innovatrics.com/glossary/threshold/); [Paravision intro to NIST FRVT](https://www.paravision.ai/news/introduction-to-nist-frvt/)
- **ArcFace confusion band:** on the DFW2019 disguised-face set, genuine and impostor ArcFace similarities are confused around the [0.3, 0.4] interval. — [ArcFace for Disguised Face Recognition, ICCVW 2019](https://openaccess.thecvf.com/content_ICCVW_2019/papers/DFW/Deng_ArcFace_for_Disguised_Face_Recognition_ICCVW_2019_paper.pdf)
- No single threshold separates genuine from impostor perfectly on CASIA-Face-Africa for any model tested. — [CASIA-Face-Africa, arXiv 2105.03632](https://arxiv.org/pdf/2105.03632)
- A threshold copied from fp32 to int8 can mask false-reject growth. The threshold's own estimation noise (±0.017) is comparable to the int8 shift (+0.025). — [Towards Data Science (practitioner)](https://towardsdatascience.com/the-number-your-quantization-gate-doesnt-have/)
- Quality-aware scoring (QMagFace) folds quality into the score, which acts as a quality-dependent threshold. — [QMagFace WACV 2023](https://openaccess.thecvf.com/content/WACV2023/papers/Terhorst_QMagFace_Simple_and_Accurate_Quality-Aware_Face_Recognition_WACV_2023_paper.pdf)

### Inferences
- **[INFERENCE] Defensible budget for the paper:**

  | Source of device-to-device difference | Typical score effect (cosine) | Evidence strength |
  |---|---|---|
  | Same fp32 model, different CPU/GPU (non-bit-exact) | ≪ 0.001 | Mechanism cited; magnitude is my estimate |
  | fp16 vs fp32 | ≈ 0.001–0.005 | Estimate only |
  | Well-calibrated int8 PTQ (Hailo/TensorRT/RKNN/Edge TPU) | ≈ 0.01–0.03, possibly a consistent bias | One practitioner datapoint (+0.025); zoo tables show ≤ 0.5–1 pp accuracy change |
  | Bad int8 calibration / int4 / unsupported ops | Up to accuracy collapse (20–30 pp) | Forum and TVM reports |
  | Camera/ISP/resolution/compression | ≈ 0.1–0.4 genuine-score drop (unverified); re-ID Rank-1 −45 to −55 pp cross-domain | Re-ID numbers cited; cosine range is an estimate |
  | Different model version or backbone | Incompatible (≈ impostor level) unless BCT-trained | BCT CVPR 2020 |

- **[INFERENCE]** For ArcFace-type models the genuine/impostor separation at operating points like FAR = 1e-4 is a gap of several tenths of cosine (impostors near 0, confusion near 0.3–0.4). Quantization noise of 0.01–0.03 is therefore an order of magnitude smaller than the class gap. It flips a YES/NO only for pairs already within about 0.03 of the threshold. Image quality can move a genuine pair across the gap.
- **[INFERENCE] Design recommendations:**
  1. Pin the model family and ship a model ID in the signature.
  2. Define the threshold in FMR terms, and map it to a per-device-class cosine value using a small calibration set run on each compiled binary (precision × compiler).
  3. Add a quality gate or quality-aware score (MagFace/QMagFace-style), so low-quality crops answer "UNSURE" instead of NO.
  4. Report a margin, i.e. a three-level answer (≥ T+δ YES, ≤ T−δ NO, otherwise UNSURE) with δ ≈ 0.03 to absorb quantization jitter.
  5. A raw 0.70–0.90 cosine threshold is model-specific. For ArcFace it is far above typical verification thresholds and will give low recall on poor cameras.

### Gaps
- ISO/IEC 19795-1/-2 text on threshold setting and reporting was not retrieved; it is paywalled. Cite it only generically, as the biometric performance testing and reporting standard.
- No explicit NIST sentence saying "thresholds are not portable across algorithms" was found. The statement is implied by the FRTE methodology (per-algorithm thresholds at fixed FMR).
- No published genuine/impostor cosine histogram for ArcFace on IJB-C, with exact means, was found.
- No study directly measures per-device score variance across a heterogeneous IoT camera fleet running one shared model. This appears to be an open gap and a possible contribution.
