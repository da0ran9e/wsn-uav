# Semantic Fragmentation Story

**Purpose:** keep a versioned narrative of the research scenario and design intent
for semantic fragmentation in Scenario 1. This document is a design reference
for simulation work, not an implementation spec yet.

**Status:** working draft
**Last updated:** 2026-05-14

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
