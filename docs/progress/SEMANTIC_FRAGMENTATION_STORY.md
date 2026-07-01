# Semantic Fragmentation Story

**Purpose:** keep a versioned narrative of the research scenario and design intent
for semantic fragmentation in Scenario 1. This document is a design reference
for simulation work, not an implementation spec yet.

**Status:** working draft
**Last updated:** 2026-05-20

---

## How to Use This Document

- `v0` stores the story as originally described by the researcher.
- `v1` stores the refined interpretation used for simulation design.
- Later revisions should be appended as `v2`, `v3`, ... rather than replacing
  old versions.
- When the story changes, record what changed and why.

---

## v0: Original Research Story

In the designed area, there is a local offline camera network that must search
for a person such as a rescue target or a lost person.

The Base Station (BS) already has the image file of the person to search for.
The BS must transmit the data quickly to the ground nodes (camera nodes) in the
area so they can search at the edge.

If the UAV tries to spread the whole image file to every node in a flooding-like
way, it will take too long. Instead, the idea is to transmit partial data that
contains important information first so the network can narrow the search region
before deeper identification starts.

During the search, ground nodes can exchange data to help one another. Because
of that, the data should be divided into small semantic fragments so that edge
cooperation becomes more effective. For example, one node may receive two
fragments, combine them with one fragment from a neighbor, and then obtain a
better chance of recognizing the target.

From these small fragments, the system should be able to infer missing parts,
also thanks to semantics.

At the beginning, the UAV should quickly broadcast the smallest but most
characteristic identity cues, for example clothing color, so that ground nodes
can first narrow the candidate region.

After the region has been narrowed, the UAV should continue to disseminate
semantic fragments so that the ground nodes in the candidate area can cooperate
to search more effectively.

Nodes that already hold useful semantic data and partial target information
continue trying to identify the target.

Once the target location has been found based on inferred data, the ground nodes
continue cooperating in an effort to recover more of the data.

When the candidate search area becomes sufficiently small, meaning only a few
nodes remain relevant, the UAV flies there and delivers the full data for final
verification.

After exact confirmation, the UAV returns and reports to the BS.

---

## v1: Refined Interpretation for Simulation Design

The core objective is not early full-image reconstruction. The core objective is
fast, progressive target search under communication constraints.

The target image owned by the BS should be transformed into a **multi-layer
target identity package** instead of being treated as a raw file that is simply
cut into bits.

The UAV then disseminates this package in a **coarse-to-fine** manner:

1. very small, very important identity cues first,
2. richer semantic descriptors next,
3. more discriminative local details only where needed,
4. the full reference image only when the suspicious region is already small.

Under this interpretation, the network search process has four stages:

### Stage A: Global Narrowing

- The UAV broadcasts the smallest and highest-utility semantic cues to the whole
  network.
- Ground nodes use these cues to reject obviously irrelevant observations.
- The output is an initial suspicious-region map.

### Stage B: Regional Refinement

- The UAV continues sending richer semantic fragments.
- Ground nodes in suspicious regions exchange fragments or evidence summaries.
- The goal is to shrink the candidate region further.

### Stage C: Cooperative Identification

- The UAV focuses dissemination on promising regions.
- Neighboring nodes combine their own received fragments and search evidence.
- The goal is to reach high-confidence target identification without yet sending
  the full image everywhere.

### Stage D: Final Verification

- Once the candidate region is small enough, the UAV physically approaches that
  region and delivers the full reference image or equivalent full payload.
- Ground nodes perform final confirmation.
- The UAV then returns to the BS with the result.

In this refined interpretation, fragments are best understood as fragments of a
**semantic target profile**, not merely fragments of a binary file.

This means:

- small fragments should carry high search utility,
- partial fragment sets should still be useful,
- neighboring nodes should gain value from cooperation,
- receiving more fragments should improve confidence progressively,
- the full image should be reserved for the final verification phase.

This also means that "inference of missing parts" should primarily be understood
as **semantic inference about the target identity**, not necessarily exact early
pixel reconstruction.

---

## v1 Design Consequences

The refined story implies the simulation should eventually model:

- a structured target profile with multiple semantic layers,
- unequal fragment importance,
- progressive confidence growth from partial data,
- cooperation between neighboring ground nodes,
- region-aware UAV dissemination,
- final full-data delivery only for a small candidate set.

The refined story also suggests two different kinds of cooperation:

### Fragment Cooperation

Nodes exchange received semantic fragments directly.

### Evidence Cooperation

Nodes exchange search evidence such as:

- confidence score,
- candidate ranking,
- local target attributes inferred from observations,
- suspicious event summaries.

Evidence cooperation may later prove cheaper than fragment cooperation and
should be considered explicitly in the simulation design.

---

## Open Questions Recorded from v1

These questions remain intentionally open and should guide later design:

1. Is the main goal progressive recognition or progressive reconstruction?
2. Should fragments be fixed-count or fountain-like / rateless?
3. Which semantic cues belong to the earliest layer?
4. Should nodes exchange raw fragments, evidence summaries, or both?
5. What event causes the UAV to switch from global broadcast to regional focus?
6. What event causes the UAV to switch to full-data delivery?

---

## Revision Log

- `v0` added from the researcher's direct narrative.
- `v1` added as a refined interpretation for simulation-oriented design.
- `v1.1` added as an algorithm-design note for layer-aware fragmentation,
  semantic atoms, and the need for `FragmentPolicy`.
- `v1.2` added after Phase-1 contact-capacity analysis. The main change is
  that Layer 0 remains the global narrowing layer, but it should be modeled as
  a progressive coded evidence stream instead of only a few tiny cue packets.
- `v1.3` added after research-claim calibration. The main change is that the
  bandwidth claim is no longer "one node cannot receive kilobytes during
  contact"; the defensible claim is about useful semantic information under
  radio-class, dense dissemination, energy, fairness, and cooperation
  constraints.

---

## v1.1: Fragmentation Design Notes

This is not a separate story revision. It is the algorithm-design note that
bridges `v1` and implementation.

### Stable Points

- Fragmentation should produce semantic delivery units, not raw image-bit
  slices.
- Fragment generation at the BS and transmission scheduling at the UAV are
  separate design questions.
- Fragment count and size should be layer-aware, not controlled only by one
  global `totalFragments` value.
- Fragments should carry semantic atoms or coded combinations of atoms.
- High-utility atoms should receive stronger protection than low-utility atoms.

### API Direction

`Generate(totalFragments)` is too weak for research because it does not control
per-layer allocation, fragment size, redundancy, systematic-first behavior, or
coding policy.

Minimum useful form:

- `Generate(totalFragments, layerSplit)`

Preferred research form:

- `Generate(const FragmentPolicy& policy)`

`FragmentPolicy` should eventually include per-layer counts, bit budgets,
fragment sizes, redundancy factors, systematic-first options, and coding options
per layer.

### Superseded By v1.2

The detailed `v1.1` Layer-0 budget assumption was too small for the Phase-1
contact capacity observed later. Treat the old Layer-0 "few tiny fragments"
budget as superseded by `v1.2`.

The stable part of `v1.1` is the modeling direction: semantic atoms,
layer-aware generation policy, and separate BS generation vs UAV scheduling.

---

## References Informing v1.1

These references informed the current interpretation at a high level:

- Task-oriented image semantic communication and semantic-rate reasoning:
  [Task-Oriented Image Semantic Communication Based on Rate-Distortion Theory](https://arxiv.org/abs/2201.10929)
- Task-relevant, explainable semantic feature selection:
  [Task-oriented Explainable Semantic Communications](https://arxiv.org/abs/2302.13560)
- Extremely low bitrate semantic image transmission:
  [A Low-Bit-Rate Image Semantic Communication System Based on Semantic Graph](https://www.mdpi.com/2079-9292/13/12/2366)
- Prompt plus structural semantic cues at low bitrate:
  [Latency-Aware Generative Semantic Communications](https://web3.arxiv.org/pdf/2403.17256v1)

---

## v1.2: Progressive Media Evidence Model

This revision records only the differences from `v1`.

### Changes From v1

- `v1` treats the BS input mainly as one target image transformed into a
  semantic profile. `v1.2` allows the BS input to be a richer target asset:
  `IMAGE_PYRAMID`, `IMAGE_SET`, or `VIDEO_CLIP`.

- `v1` describes Layer 0 as a small set of early identity cues. `v1.2` keeps
  Layer 0 as the first global narrowing layer, but expands it into a
  **progressive coarse-evidence stream**.

- `v1` uses semantic layers as the main structure. `v1.2` adds an additional
  progression axis inside a layer, especially for Layer 0: quality level,
  frame/image index, systematic atoms, and coded fragments.

- `v1` says partial fragments should be useful. `v1.2` explains why Layer 0
  must contain enough coded space: at `20 m/s`, a node near the UAV path can
  receive hundreds to more than one thousand small packets during contact.

- `v1` leaves fragment content abstract. `v1.2` makes the next model more
  explicit: fragments should be built from semantic atoms such as color,
  silhouette, body ratio, low-resolution embedding, body-region layout, coarse
  pose, or coarse motion/gait.

- `v1` does not define a data model for media quality. `v1.2` introduces the
  need for target-asset fields such as `assetType`, `frameId`, `qualityLevel`,
  `semanticType`, `systematic`, `coded`, `seed`, `degree`, and `atomIds`.

- `v1` mostly implies fragment-count metrics. `v1.2` requires both communication
  and semantic metrics: planned coded-space ratio, emitted-fragment ratio,
  per-layer semantic coverage, atom-type coverage, progressive confidence, and
  cooperative gain.

### Non-Changes

- Layer separation remains mandatory.

- Phase 1 remains Layer-0 only.

- The fix for too-small Layer 0 is not to mix Layer 1 or Layer 2 into the
  Layer-0 broadcast.

- Layer 1 is still regional refinement, Layer 2 is still cooperative
  identification, and Layer 3 is still final verification.

### Design Consequence

The next implementation should redesign Layer 0 as a larger progressive
coarse-evidence stream while preserving the original phase order:

- keep Phase-1 broadcast Layer-0 only,
- generate Layer-0 systematic atoms plus coded fragments,
- size the Layer-0 coded space from contact capacity and target receive ratio,
- keep packet size within LR-WPAN constraints,
- report both fragment ratios and semantic coverage.

---

## v1.3: Research-Claim and Semantic-Payload Calibration

This revision records how the research claim should be framed after checking
UAV speed, A2G bandwidth, and computer-vision payload sizes.

### Claim Calibration

The weak claim is:

- "A node cannot receive kilobytes of target data while the UAV passes by."

This is not generally defensible. With Wi-Fi or 5G A2G, field measurements show
Mbps to hundreds of Mbps links in favorable conditions, so a single node can
receive far more than a few kilobytes during contact.

The stronger claim is:

- In an offline camera/sensor network using low-power radios, dense broadcast,
  and cooperative edge search, the bottleneck is not only raw byte capacity.
  The bottleneck is early useful information, dissemination fairness,
  contention, energy, partial reception, and cooperative semantic confidence.

This means semantic fragmentation should be evaluated by:

- time-to-first-narrowing,
- confidence-per-byte,
- semantic atom coverage,
- min/median/p90 node reception,
- cooperative gain from neighbor exchange,
- final verification cost after the candidate region is reduced.

### How Image Semantics Are Extracted

For this simulation, "semantic" should be treated as task-oriented information
derived from the target asset, not as a generic compressed image.

A practical extraction pipeline is:

1. Detect or crop the target person from the BS reference image, image set, or
   video frames.
2. Generate low-level identity atoms: dominant upper/lower clothing colors,
   color histograms, body aspect ratio, silhouette area, and coarse body-region
   layout.
3. Generate mid-level atoms: attribute probabilities such as shirt color, pants
   color, backpack, hat, gender-like appearance class if ethically allowed,
   viewpoint, occlusion, and pose bucket.
4. Generate learned embeddings: person ReID embeddings or vision-language
   embeddings. OSNet uses 512-D person ReID vectors from a 256x128 input, and
   CLIP-style models learn image-text aligned representations for broad visual
   concepts.
5. Optionally generate multi-frame atoms from a short video or image set:
   gait/motion cue, stable colors across frames, view diversity, and aggregate
   embedding.
6. Convert atoms into Layer-0/1/2 fragments. Layer 0 should carry coarse,
   high-utility atoms; later layers carry richer embeddings, region details,
   and full-reference data for final verification.

In byte terms, semantic payloads can be much smaller than image payloads:

- A 32-70 attribute vector with confidence values is roughly `64-160 B` if
  stored as one byte per confidence plus compact metadata.
- A 512-D embedding is `2048 B` in fp32, `1024 B` in fp16, `512 B` in int8,
  or `64 B` if binarized.
- A compact L0 semantic atom such as `upperColor + lowerColor + silhouette +
  bodyRatio + confidence` can fit in tens of bytes, but it supports narrowing
  rather than final identity confirmation.

### Accuracy and Payload Reference Table

These numbers are calibration ranges for simulation design, not universal
guarantees. File sizes are engineering estimates for cropped person images; CV
performance depends on camera quality, viewpoint, occlusion, model, dataset,
and whether the target is seen from the same view as the reference.

| Target evidence level | Pixel / media input | Approx image payload | Approx semantic payload | Expected CV utility | Paper-backed anchor |
|---|---:|---:|---:|---|---|
| Tiny detection cue | Person scale around `18 px` or below `20 px` | `0.5-2 KB` JPEG-equivalent crop | `16-128 B` color/size/silhouette atoms | Detect a human-like object, weak identity; around `47-52 APtiny50` in TinyPerson-style detection | TinyPerson reports tiny persons below 20 px and APtiny50 `47.29`, `52.47` with 3x upsample |
| Very low-res ReID cue | About `32x12` crop | `0.8-2 KB` JPEG, `1.1 KB` raw RGB | `64-512 B` attributes or quantized embedding | Initial candidate filtering; difficult low-res ReID often around `25-35%` Rank-1 | Low-resolution ReID reports SING Rank-1 around `33.5%` on CAVIAR and MLR-VIPeR |
| Low-res clothing/body cue | About `64x24` crop | `1.5-5 KB` JPEG, `4.6 KB` raw RGB | `128-768 B` attributes plus int8 embedding | Useful narrowing by clothing/body; easier datasets may reach higher Rank-1, hard cross-camera remains moderate | Low-resolution ReID reports multi-resolution fusion up to `67.7%` Rank-1 on MLR-CUHK03 |
| Attribute-recognition cue | Person crop roughly `128x48` to `128x64` | `4-15 KB` JPEG, `18-24 KB` raw RGB | `100-512 B` attribute confidences | Good for semantic matching such as clothing, bag, viewpoint; not full identity | RAP-style pedestrian attribute recognition reports DeepMAR/related F1 around `75-77%`, newer methods around `79-82%` depending setup |
| Standard ReID embedding | Person crop `256x128` | `15-60 KB` JPEG, `98 KB` raw RGB | `512 B` int8 embedding, `1024 B` fp16, `2048 B` fp32 | Strong benchmark ReID under matched benchmark conditions; real deployment lower | OSNet uses 512-D feature vectors from resized `256x128` images and reports Market-1501 Rank-1 `94.8%`, mAP `84.9%` |
| Multi-frame evidence | `5-10` crops or short clip | `25-300 KB+` compressed media | `2-8 KB` aggregate embeddings, attributes, motion/gait atoms | Best practical robustness for search; supports view diversity and cooperation | Supported by the general observation that richer multi-scale and multi-resolution ReID features improve discrimination |

### Simulation Interpretation

The table suggests the following design direction:

- Layer 0 should not be a tiny finite set of only a few fragments. It should be
  a rateless or rotating coarse semantic evidence stream.
- Layer 0 should mostly represent attributes, colors, silhouettes, coarse body
  layout, and heavily quantized embeddings. It should support fast narrowing,
  not final identity confirmation.
- Layer 1 should add richer attributes, higher-quality embeddings, and multiple
  reference views.
- Layer 2 should support cooperative identification using neighbor evidence and
  partial embedding/attribute fusion.
- Layer 3 remains full-reference delivery for a small candidate region.

### References Informing v1.3

- UAV speed calibration: DJI Mavic 3 Enterprise (`21 m/s` Sport), DJI Matrice
  30/350 (`23 m/s` max), Skydio X10 (`20 m/s`), and Zipline fixed-wing delivery
  (`60-70 mph`) show that `20 m/s` is a realistic fast/stress speed, not an
  impossible speed.
- A2G bandwidth calibration:
  [Yanmaz et al. 802.11a UAV-to-ground measurements](https://www-itec.uni-klu.ac.at/bib/files/WIUAV2011_Yanmaz.pdf),
  [Qualcomm LTE UAS field trial](https://www.qualcomm.com/media/documents/files/lte-unmanned-aircraft-systems-trial-report.pdf),
  [First Experiments with a 5G-Connected Drone](https://arxiv.org/abs/2004.03298),
  [LoRa A2G coverage measurements](https://arxiv.org/abs/1902.11243), and
  [IEEE 802.15.4 UAS gateway measurements](https://www.mdpi.com/1424-8220/19/16/3479).
- Tiny-person detection:
  [Scale Match for Tiny Person Detection](https://openaccess.thecvf.com/content_WACV_2020/papers/Yu_Scale_Match_for_Tiny_Person_Detection_WACV_2020_paper.pdf).
- Pedestrian detection scale:
  [CityPersons](https://openaccess.thecvf.com/content_cvpr_2017/papers/Zhang_CityPersons_A_Diverse_CVPR_2017_paper.pdf).
- Low-resolution person ReID:
  [Deep Low-Resolution Person Re-Identification](https://ssgong.github.io/papers/JiaoEtAl_AAAI2018.pdf).
- Standard person ReID embedding:
  [OSNet](https://openaccess.thecvf.com/content_ICCV_2019/papers/Zhou_Omni-Scale_Feature_Learning_for_Person_Re-Identification_ICCV_2019_paper.pdf).
- Pedestrian attribute recognition:
  [RAP dataset](https://arxiv.org/abs/1603.07054) and
  [pedestrian attribute recognition benchmark summary](https://www.ijcai.org/proceedings/2019/0341.pdf).
- Vision-language semantic extraction:
  [CLIP](https://openai.com/index/clip/).
