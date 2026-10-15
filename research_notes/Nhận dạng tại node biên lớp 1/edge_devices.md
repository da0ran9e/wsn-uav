# Edge camera device compute capabilities and feasible recognition pipelines (Layer 1 node tiers)

Scope note: 18 tool calls were used. Benchmarks below are tagged **[V]** = vendor-reported (datasheet / model zoo / vendor blog), **[I]** = independent or community measurement, **[R]** = retailer/marketing copy. Unless stated, inference-only time (no decode, pre- or post-processing). Several devices on the requested list could not be verified within budget; they are listed under Gaps with the commonly quoted figure explicitly marked unverified.

## Q1. Per-device compute, memory and measured inference (master table)

### Takeaway
Measured numbers cluster into four clear bands: MCU (ESP32-S3: ~0.25–0.3 s per face embedding; STM32N6: ~25 ms per YOLOv8n-256 person detection), camera SoC NPU 1–2 TOPS (RV1126B: 24 FPS YOLOv8n-640, 145 FPS RetinaFace-mobile-320), SBC + accelerator (Hailo-8L: ~62 FPS YOLOv8n app-level, 1666 FPS ArcFace-MobileFaceNet chip-level), and Jetson Orin Nano Super (161–314 FPS CLIP ViT-B). Only the top two bands can run CLIP image encoders at useful rates.

### Cited Findings

**MCU class**
- ESP32-S3, ESP-WHO face recognition: default model MFN_S8_V1 (1.2 M params, 112×112 aligned crop) ≈ **255 ms**; larger MBF_S8_V1 (3.4 M params) ≈ **1073 ms** per face (2025–26 workshop) **[V]** — [Espressif workshop, assignment 2](https://developer.espressif.com/workshops/edge-ai-with-esp32-s3/assignment-2/)
- ESP-DL v1.1 performance table: human face recognition on ESP32-S3 **287 ms (8-bit)**, 554 ms (16-bit); on original ESP32 13,301 ms (8-bit) **[V]** — [ESP-DL v1.1 performance](https://docs.espressif.com/projects/esp-dl/en/release-v1.1/esp32s3/performance.html)
- ESP32-S3-EYE face *detection* forward pass ≈ **30 ms** + ≈11 ms preprocessing (user log, ESP-WHO master) **[I]** — [esp32.com forum](https://esp32.com/viewtopic.php?p=145368)
- STM32N6 (Neural-ART NPU), ST model card YOLOv8n INT8 per-channel, COCO-Person, STM32N6570-DK: **24.94 ms / 40.1 inf/s at 256×256**; ≈59 inf/s at 192×192; ≈18.8 inf/s at 416×416 (STM32Cube.AI 10.2.0 / STEdgeAI Core 2.2.0) **[V]** — [ST YOLO model card (Hugging Face)](https://huggingface.co/STMicroelectronics/yolov11n/blob/main/README.md)
- Ultralytics reports YOLOv8n 256×256 on STM32N6 ≈ **34 fps (~29 ms)**, ≈ **9.4 mJ/inference** **[V, partner]** — [Ultralytics × ST customer story](https://www.ultralytics.com/customers/embedded-vision-ai-with-ultralytics-yolo-and-stmicroelectronics-mcu). Note: slightly slower than ST's own table; setups differ.
- Sony IMX500 (Raspberry Pi AI Camera, 2024): on-sensor NPU memory **8,388,480 bytes** shared between firmware, network weights and working memory; max input tensor 640×640; INT8 only; model must be packaged as sensor firmware **[V via review]** — [Hackster hands-on](https://hackster.io/news/raspberry-pi-s-ai-eye-hands-on-with-the-raspberry-pi-ai-camera-module-383fb34afcf7); [Imaging Resource](https://imaging-resource.com/news/2024/10/07/raspberry-pi-launches-a-70-ai-powered-camera-module)
- MLPerf Tiny measures VWW (MobileNet person/no-person, 96×96) as inferences/s and µJ/inference, inference only — useful frame for MCU tier, but no MAX78000 v1.x number retrieved — [MLPerf Tiny paper, arXiv 2106.07597](https://arxiv.org/pdf/2106.07597)

**Camera SoCs (IP cameras, doorbells, NVR heads)**
- Rockchip RV1126: **2.0 TOPS** NPU (INT8/INT16); RV1109: 1.2 TOPS (2021) **[V]** — [CNX Software](https://cnx-software.com/2021/01/22/rockchip-rv1126-ai-camera-soc-features-2-0-tops-npu-promises-250ms-fast-boot)
- RKNN Model Zoo FPS (max NPU clock, inference only) **[V]** — [airockchip/rknn_model_zoo](https://github.com/airockchip/rknn_model_zoo):

| Model (input, dtype) | RV1126B | RK3566 | RK3576 (1 core) | RK3588 (1 core) |
|---|---|---|---|---|
| YOLOv5n 640 INT8 | 36.3 | 41.7 | 105.8 | 123.0 |
| YOLOv5s 640 INT8 | 13.6 | 20.1 | 51.2 | 59.6 |
| YOLOv8n 640 INT8 | 24.0 | 35.1 | 83.0 | 97.7 |
| MobileNetV2 224 INT8 | 212.9 | 192.2 | 374.0 | 459.0 |
| RetinaFace-mobile 320 INT8 | 144.8 | 148.9 | 451.6 | 501.8 |
| RetinaFace-R50 320 INT8 | 14.6 | 18.4 | 46.5 | 54.6 |
| CLIP image 224 FP16 | not supported | 2.3 | 5.9 | 6.3 |
| CLIP text (20 tok) FP16 | not supported | 30.8 | 61.0 | 64.3 |

  (Column mapping was reconstructed from a scraped table; verify on the page. RV1106/RV1103 are "limited support" — mainly MobileNet/YOLOv5 — and have no column in the table.) — [rknn_model_zoo](https://github.com/airockchip/rknn_model_zoo); [edgeble fork note](https://github.com/edgeble/rknn_model_zoo)
- HiSilicon Hi3516DV300: Cortex-A7 @900 MHz + NNIE up to **1.0 TOPS** **[R/V]** — [Tindie DV300 board](https://www.tindie.com/products/hiview/hi3516dv300-fhd-ai-ipcamera-development-board/)
- HiSilicon Hi3516CV610: dual A7 @950 MHz + **1 TOPS NPU** (secondary Chinese blog) **[R]** — [CSDN article](https://gitcode.csdn.net/6a1554d1662f9a54cb772c96.html). Hi3519A has NNIE (IP reportedly Cambricon), TOPS not found.
- Ambarella CV28M (Nov 2020): same CVflow AI engine as CV25 but dual A53 instead of quad, up to 30 % lower cost; 10 nm; targets smart-home security, occupancy, retail **[V]** — [Ambarella CV28M press release](https://cn.ambarella.com/news/ambarella-introduces-cv28m-soc-with-cvflow-to-enable-new-categories-of-intelligent-sensing-devices/); [eeNews Europe](https://www.eenewseurope.com/en/camera-soc-targets-new-class-of-smart-edge-devices/)
- Ambarella markets its doorbell chips for on-edge face detection/recognition ("familiar/unfamiliar face") **[V, marketing]** — [Ambarella security applications](https://cn.ambarella.com/applications/security)

**Doorbells / consumer cameras (what chips, where recognition runs)**
- Google Nest Hello (A0077, 2018): camera SoC with Cortex-A9 supplied by **Ambarella** (teardown) **[I]** — [TechInsights](https://www.techinsights.com/ja/node/31272)
- Google Nest Doorbell (GWX3T): main processor **Amlogic C328XG quad-core Arm** (teardown) **[I]** — [TechInsights](https://techinsights.com/ja/node/49751)
- Nest Hello "familiar faces" (2017) relies on Google facial recognition; sources do not state whether matching is on device or cloud — [phys.org/AP](https://phys.org/news/2017-09-labs-doorbell-familiar.html)
- Eufy HomeBase 3 (S380): quad-core Cortex-A55, 16 GB eMMC, expandable to 16 TB; "BionicMind" local face recognition (family vs stranger), human/vehicle/pet detection; no NPU/TOPS figure published **[V]** — [eufy product page (IT)](https://www.eufy.com/eu-it/products/t80303d1)

**SBC and edge accelerators**
- Raspberry Pi 5 CPU only, YOLO11n NCNN 640: ≈ **70 ms/frame** (~14 FPS) on Pi 5 4 GB, ~3× faster than PyTorch; ≈90 ms in a larger app **[I, forum]** — [Ultralytics community](https://community.ultralytics.com/t/raspberry-pi-5-crash-when-running-yolov11n-ncnn/1525); official table is an image (FP32, 640, Ultralytics 8.3.39) — [Ultralytics RPi guide](https://docs.ultralytics.com/guides/raspberry-pi)
- Hailo-8L on Pi 5 (HailoRT 4.19): YOLOv8n **61.9 FPS batch 1 / 121.4 FPS batch 8** measured, vs Model Zoo v2.13 claim **182 / 464 FPS**; Hailo staff: zoo numbers are raw chip throughput, not application FPS **[I vs V]** — [Hailo community thread](https://community.hailo.ai/t/yolov8n-real-performance-didnt-expected-from-hailo-model-zoo-documentation/18904)
- Hailo-8L Model Zoo, face recognition (112×112): **arcface_mobilefacenet 2.04 M params, 1666 FPS** (b1 and b8), LFW 99.4/99.4 %; **arcface_r50 31.0 M params, 93.2 FPS b1 / 300 FPS b8**, LFW 99.7 % **[V, chip-level]** — [Hailo Model Zoo HAILO8L face recognition](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8L/HAILO8L_face_recognition.rst)
- Hailo person re-ID models are RepVGG-A0 based (512-d and 2048-d embeddings), not OSNet; reference multi-camera re-ID pipeline runs real-time on Hailo-8 with 4 FHD RTSP cameras **[V]** — [Hailo re-ID blog](https://hailo.ai/blog/multi-camera-multi-person-re-identification/); [Hailo Model Zoo public models](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/PUBLIC_MODELS.rst)
- Seeed: YOLOv8 640 on CM4-based reComputer R1000 from 0.75 FPS (CPU) to 29.5 FPS with Hailo-8L **[V, integrator]** — [Seeed wiki](https://wiki.seeedstudio.com/yolov8_object_detection_on_recomputer_r1000_with_hailo_8l/)
- Google Coral Edge TPU (official, model only): MobileNet v1 SSD 224: **6.5 ms** USB Accelerator (USB3, desktop host), **11 ms** Dev Board; MobileNet v2 SSD: 7.2 / 14 ms; desktop CPU alone 109 ms **[V]** — [Coral benchmarks](https://www.coral.ai/docs/edgetpu/benchmarks)
- Coral independent (300×300): USB Accelerator USB3 MobileNet v2 SSD 18.2 ms, v1 14.9 ms; over USB2 58.1 / 49.3 ms **[I]** — [aallan/benchmarking-ml-on-the-edge](https://github.com/aallan/benchmarking-ml-on-the-edge)
- NVIDIA Jetson Orin Nano (JetPack 6.2, Dec 2024) **[V]** — [NVIDIA blog](https://developer.nvidia.com/blog/nvidia-jetpack-6-2-brings-super-mode-to-nvidia-jetson-orin-nano-and-jetson-orin-nx-modules):

| | 4 GB orig | 4 GB Super | 8 GB orig | 8 GB Super |
|---|---|---|---|---|
| INT8 TOPS sparse/dense | 20/10 | 34/17 | 40/20 | **67/33** |
| GPU FP16 | 5 TF | 8.5 TF | 10 TF | 17 TF |
| DRAM BW | 34 GB/s | 51 GB/s | 68 GB/s | 102 GB/s |
| Power modes | 7/10 W | up to 25 W / MAXN | 7/15 W | 15/25 W / MAXN |
| CLIP ViT-B/32 FPS (FP16, TRT) | 126.8 | 189.5 | 196 | **314** |
| CLIP ViT-B/16 FPS | 63.2 | 112.4 | 95 | **161** |
| DINOv2-base FPS | 49.3 | 79.3 | 75 | 126 |
| Grounding DINO FPS | – | – | 4.1 | 6.2 |

  Note: "67 TOPS" is sparse; dense INT8 is 33 TOPS — relevant when comparing to Hailo/RK TOPS (which are dense).
- Ultralytics describes Orin Nano Super as configurable 7–25 W; YOLO11 benchmarks on that blog (not YOLOv8) — [Ultralytics blog](https://www.ultralytics.com/blog/ultralytics-yolo11-on-nvidia-jetson-orin-nano-super-fast-and-efficient)

**Storage / retention**
- 2 Mbps stream ≈ 21.6 GB/day → **128 GB ≈ 5.5 days** continuous 24/7 (Foscam FAQ) **[V]** — [Foscam FAQ](https://www.foscam.com/faqs/view.html?id=285)
- Eufy: 128 GB ≈ **384 h (16 days)** at 1080p (bitrate unstated), ≈6 days at 3K 24/7 with H.265 **[V]** — [Eufy continuous recording](https://service.eufy.com/article-description/Learn-about-Continuous-Recording1)
- Rule of thumb: 1080p camera, 128 GB → 1–2 weeks continuous before overwrite **[R]** — [Botslab blog](https://www.botslab.com/blogs/news/no-monthly-fee-security-cameras-microsd-capacity-limits)
- Bitrate-dependent table also at — [EZVIZ FAQ](https://support.ezviz.com/en-au/faq/article/How-many-days-of-video-can-I-record-on-a-16GB-32GB-64GB-128GB-card)

### Inferences
- Vendor "chip-level" FPS can overstate application FPS by ~3× (Hailo 182 → 62 FPS for YOLOv8n). Apply a 2–3× derating to all [V] numbers when estimating scan throughput.
- TOPS is a poor predictor across vendors: RV1126B (2 TOPS) gets 24 FPS YOLOv8n-640, while Hailo-8L (13 TOPS) gets ~62 FPS app-level; memory bandwidth and host overhead dominate.
- Consumer doorbells do ship on-device face recognition in some products (Eufy HomeBase on an A55 hub, Ambarella-based designs), but the "hub" (HomeBase/NVR) — not the battery camera itself — is where stored footage and recognition co-reside.
- Retention: at 1–2 Mbps, a 32–256 GB card holds roughly 1.5–20 days; the scan workload per node is therefore up to ~100–500 h of video, or much less for event-clip-only (motion-triggered) devices like battery doorbells.

### Gaps
- Not verified this session (commonly quoted figures, **do not cite without checking**): STM32N6 Neural-ART "600 GOPS"; IMX500 TOPS; MAX78000 CNN accelerator latencies (MLPerf Tiny v1.x); Alif Ensemble / Ethos-U55 (128–256 MAC/cycle) and U65; Himax WE-I Plus / WE2; Ambarella CV22/CV25/CV5 TOPS (no Ambarella datasheet found); Hi3519A / Hi3519DV500 TOPS; RV1106 (commonly 0.5 TOPS) and RK3588 (6 TOPS) official briefs; Novatek, Ingenic T-series, SigmaStar NPU specs; Hailo-8 (26 TOPS) per-model FPS; Coral FaceNet/MobileFaceNet; Jetson Nano (legacy, 472 GFLOPS) and Intel NCS2 numbers; Ring and dashcam SoC teardowns.
- No OSNet-x0.25/x1.0, SCRFD or BlazeFace benchmark was retrieved on any device; re-ID figures only exist as RepVGG-A0 on Hailo (no FPS retrieved).
- Power draw per device was retrieved only for Jetson (7–25 W) and STM32N6 per-inference energy (9.4 mJ).

## Q2. Which pipeline is feasible per tier, and scan throughput

### Takeaway
(a) detection-only is feasible on every tier including MCUs; (b) face-embedding matching is feasible from ESP32-S3 upward but at ~3–4 faces/s on MCU vs >100/s on NPUs; (c) person re-ID needs a ≥1 TOPS NPU in practice; (d) CLIP image encoders are infeasible below RK3566-class (2.3 FPS) and only comfortable on Jetson Orin (161–314 FPS). Scanning stored footage is bounded on cameras by video decode and sampling rate, not just the NN.

### Cited Findings
- ESP32-S3: detection ~30 ms + recognition ~255–287 ms per face → ≈3 faces/s end-to-end — [esp32.com forum](https://esp32.com/viewtopic.php?p=145368); [Espressif workshop](https://developer.espressif.com/workshops/edge-ai-with-esp32-s3/assignment-2/); [ESP-DL perf](https://docs.espressif.com/projects/esp-dl/en/release-v1.1/esp32s3/performance.html)
- STM32N6: person detector 40 inf/s at 256×256 — [ST model card](https://huggingface.co/STMicroelectronics/yolov11n/blob/main/README.md)
- RV1126B: YOLOv8n-640 24 FPS + RetinaFace-mobile-320 145 FPS; CLIP not supported — [rknn_model_zoo](https://github.com/airockchip/rknn_model_zoo)
- RK3588 single core: CLIP image 6.3 FPS, CLIP text 64 FPS — [rknn_model_zoo](https://github.com/airockchip/rknn_model_zoo)
- Hailo-8L: ArcFace-MobileFaceNet 1666 FPS, ArcFace-R50 93–300 FPS (chip-level) — [Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8L/HAILO8L_face_recognition.rst)
- Jetson Orin Nano 8 GB Super: CLIP ViT-B/32 314 FPS, ViT-B/16 161 FPS; Grounding DINO 6.2 FPS — [NVIDIA](https://developer.nvidia.com/blog/nvidia-jetpack-6-2-brings-super-mode-to-nvidia-jetson-orin-nano-and-jetson-orin-nx-modules)

### Inferences (throughput model — derived, not measured)
Assume scanning samples stored video at **1 frame/s** (person tracks persist for seconds), runs a person/face detector per sampled frame, then an embedding per crop (~2 crops/frame average in urban scenes). Speed-up = hours of video processed per hour of compute ≈ detector FPS / (sample rate) limited by embedding cost. Applying ~2× derating to vendor numbers:

| Tier / example | Detector (derated) | Embedding | Approx. video-h per compute-h @1 fps | Feasible pipelines |
|---|---|---|---|---|
| T0 MCU: ESP32-S3 | ~10–25 FPS face det (30 ms) | 255 ms/face | **~1–2×** (embedding-bound; ~3–4 crops/s) | (a), (b) slow; no (c)/(d) |
| T0+ MCU-NPU: STM32N6, IMX500 | ~20–40 FPS YOLOv8n-256 | small face/reid embed est. ~10–30/s (unmeasured) | **~5–15×** | (a), (b); (c) marginal |
| T1 camera SoC 1–2 TOPS: RV1126B, Hi3516DV300/CV610, CV25/CV28 | ~12 FPS YOLOv8n-640 (24 derated) | RetinaFace-mobile ~70/s; MFN-class est. >100/s | **~6–12×** | (a), (b), (c); (d) no |
| T2 SBC+accel: Pi 5 + Hailo-8L, RK3588, Coral | ~60 FPS YOLOv8n (measured) | ArcFace-MFN ~800/s derated; R50 ~45–150/s | **~30–60×** | (a)–(c); (d) only on RK3588 at ~6 FPS (≈3× @1 fps, 2 crops) |
| T3 Jetson Orin Nano (Super) | YOLO class est. >100 FPS (not retrieved) | CLIP B/32 ~150–314/s | **~50–150×** | (a)–(d) incl. CLIP text/attribute query |

- Example: a 5.5-day (132 h) microSD backlog takes ≈11–22 h on T1, ≈2–4 h on T2, ≈1–3 h on T3, and ~66–130 h on an ESP32-S3 (i.e., infeasible within an evidence-overwrite window unless event clips only).
- On T1 camera SoCs the hardware video decoder is typically shared with live encoding; scanning while still recording may halve the budget (inferred, not sourced).
- ESP32-S3 has no hardware H.264/H.265 decoder as far as found here — it effectively cannot scan compressed stored footage; it can only match on-the-fly or on JPEG stills (inferred; verify).

### Gaps
- No source gave end-to-end "hours of video scanned per hour" for any device; table above is a derived model.
- Video-decode throughput on camera SoCs (e.g., RV1126 VPU decode fps) not retrieved.

## Q3. Memory limits for the query and model weights

### Takeaway
A query of 1 MB is trivial for T1–T3 (hundreds of MB to GB DRAM) and fits in MCUs with PSRAM, but competes with model weights on on-sensor NPUs such as the IMX500 (8 MB total for firmware + weights + activations).

### Cited Findings
- IMX500: 8,388,480 bytes total shared by firmware, weights and working memory — [Hackster](https://hackster.io/news/raspberry-pi-s-ai-eye-hands-on-with-the-raspberry-pi-ai-camera-module-383fb34afcf7)
- ESP32-S3 face models: 1.2 M params (MFN_S8_V1, 8-bit ≈1.2 MB) and 3.4 M params (MBF_S8_V1) — [Espressif workshop](https://developer.espressif.com/workshops/edge-ai-with-esp32-s3/assignment-2/)
- ArcFace-MobileFaceNet 2.04 M params; ArcFace-R50 31.0 M params — [Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8L/HAILO8L_face_recognition.rst)
- Jetson Orin Nano: 4 or 8 GB LPDDR at 51–102 GB/s (Super) — [NVIDIA](https://developer.nvidia.com/blog/nvidia-jetpack-6-2-brings-super-mode-to-nvidia-jetson-orin-nano-and-jetson-orin-nx-modules)
- Eufy HomeBase 3: 16 GB eMMC, up to 16 TB expansion — [eufy](https://www.eufy.com/eu-it/products/t80303d1)

### Inferences
- Embedding sizing: 512-d float32 = 2 KB; INT8 = 512 B. A 1 MB query ≈ 500 FP32 or ~2000 INT8 512-d reference embeddings — far more than needed (typical query: 5–50 reference images × few augmentations ≈ 10–100 KB).
- On IMX500 the query must live on the host (Pi/MCU), since sensor memory is consumed by the model; matching (cosine against N references) is cheap enough to do on the host CPU.
- For ESP32-S3, the 1.2 MB recognition model plus detection model plus frame buffers require external PSRAM (ESP32-S3 SRAM ≈512 KB — figure not verified this session); a 1 MB query is feasible only if quantized to INT8 or kept ≤~100 KB.
- Implication for UAV delivery: query payload of ~10–100 KB (≈100–1000 packets of 99 B) is consistent with all tiers; 1 MB is acceptable from T0+ upward if stored in flash.

### Gaps
- ESP32-S3 SRAM/PSRAM, STM32N6 SRAM (commonly ~4.2 MB), RV1106 integrated DDR (64/128/256 MB variants), RV1126 DDR configs not verified in this session.

## Q4. Proposed tier classification with justification

### Takeaway
Use four tiers split by measured capability rather than TOPS alone: T0 MCU (detection, slow face match, live only), T1 camera SoC 0.5–2 TOPS (face + re-ID matching over stored footage at ~5–12× real time), T2 SBC+accelerator / RK3588 (all except fast CLIP, ~30–60×), T3 Jetson Orin-class (all incl. CLIP, ~50–150×). Most consumer doorbells/cameras sit in T0–T1; hubs/NVRs in T1–T2.

### Cited Findings
- T0 evidence: ESP32-S3 255–287 ms/face embedding — [Espressif](https://developer.espressif.com/workshops/edge-ai-with-esp32-s3/assignment-2/); STM32N6 25 ms YOLOv8n-256 — [ST](https://huggingface.co/STMicroelectronics/yolov11n/blob/main/README.md); IMX500 8 MB — [Hackster](https://hackster.io/news/raspberry-pi-s-ai-eye-hands-on-with-the-raspberry-pi-ai-camera-module-383fb34afcf7)
- T1 evidence: RV1126 2.0 TOPS — [CNX](https://cnx-software.com/2021/01/22/rockchip-rv1126-ai-camera-soc-features-2-0-tops-npu-promises-250ms-fast-boot); Hi3516DV300/CV610 1 TOPS — [Tindie](https://www.tindie.com/products/hiview/hi3516dv300-fhd-ai-ipcamera-development-board/), [CSDN](https://gitcode.csdn.net/6a1554d1662f9a54cb772c96.html); RV1126B 24 FPS YOLOv8n, CLIP unsupported — [RKNN zoo](https://github.com/airockchip/rknn_model_zoo); Ambarella CV25/CV28 CVflow for smart-home security — [Ambarella](https://cn.ambarella.com/news/ambarella-introduces-cv28m-soc-with-cvflow-to-enable-new-categories-of-intelligent-sensing-devices/)
- T2 evidence: Hailo-8L 62 FPS YOLOv8n measured — [Hailo community](https://community.hailo.ai/t/yolov8n-real-performance-didnt-expected-from-hailo-model-zoo-documentation/18904); Coral 6.5–14 ms SSD — [Coral](https://www.coral.ai/docs/edgetpu/benchmarks); RK3588 CLIP 6.3 FPS — [RKNN zoo](https://github.com/airockchip/rknn_model_zoo); Pi 5 CPU ~70 ms YOLO11n — [Ultralytics community](https://community.ultralytics.com/t/raspberry-pi-5-crash-when-running-yolov11n-ncnn/1525)
- T3 evidence: Orin Nano Super 67/33 TOPS, CLIP B/32 314 FPS, 7–25 W — [NVIDIA](https://developer.nvidia.com/blog/nvidia-jetpack-6-2-brings-super-mode-to-nvidia-jetson-orin-nano-and-jetson-orin-nx-modules)

### Inferences
| Tier | Example devices | Compute | Query form it can use | Role in layer-3 design |
|---|---|---|---|---|
| **T0 MCU** (≤0.6 TOPS-class, ≤8 MB) | ESP32-S3, STM32H7/N6, IMX500, MAX78000, Ethos-U55 MCUs, battery doorbells | detection; face embedding at 1–4/s | face embeddings (INT8), attributes | live-only matching / event clips; not a processing point; relay or report "seen person" flags |
| **T1 camera SoC** (0.5–2 TOPS, 64 MB–1 GB) | RV1106/RV1126(B), Hi3516DV300/CV610, Ambarella CV25/CV28, typical IP cameras, dashcams | det 12–24 FPS, face/re-ID embeddings ~100/s | face + re-ID embeddings | scans own SD backlog at ~5–12× real time; candidate "critical cell" only if no better node nearby |
| **T2 SBC+accelerator** (4–26 TOPS) | Pi 5 + Hailo-8L/8, RK3588, Coral boxes, NVR/HomeBase hubs | det ~60 FPS app-level, face embed hundreds/s | face, re-ID; slow CLIP (RK3588) | natural CL / critical-cell processing point; can scan neighbors' clips if raw transfer allowed |
| **T3 Jetson-class** (20–67 TOPS sparse) | Orin Nano / Orin NX edge boxes | CLIP ViT-B 161–314 FPS | all incl. CLIP text/attribute queries | CH candidates; can handle heterogeneous query formats |

- Justification for TOPS bands: they align with qualitative breaks in measured data — CLIP image encoders appear only at RK3566+/Orin; ArcFace-R50 class embeddings become practical at T2; MCU face embedding is ~100× slower than NPU tiers.
- Consequence for the paper's capability attribute ("khả năng tính toán"): a log-scale capability score fits the data (T0≈1, T1≈10, T2≈50, T3≈100 in video-h/compute-h), and query format choice (face embedding vs CLIP) should be tier-aware: the UAV-broadcast query should at minimum include face/re-ID embeddings usable by T1, with CLIP text/image embeddings as an optional extension for T2–T3.

### Gaps
- Distribution of tiers in a real urban deployment (fraction of cameras with NPUs) not researched.
- Ring/Arlo/dashcam SoCs and whether they store continuous video vs event clips (battery doorbells are generally event-only — not verified here).
