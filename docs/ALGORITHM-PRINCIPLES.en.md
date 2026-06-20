# WizMap Algorithm Principles

> This document explains the **algorithmic principles** behind WizMap's pipeline from raw text to a zoomable, interactive map. It does not cover code-level implementation.

## In One Sentence

WizMap's goal: turn **massive high-dimensional text embeddings** into a **zoomable, terrain-like map with landmarks**.

It achieves this by combining three core algorithms:

1. **UMAP dimensionality reduction** — high-dimensional vectors → 2D coordinates
2. **Gaussian Kernel Density Estimation (KDE)** — scattered points → continuous density contours (terrain)
3. **Quadtree + term-frequency topic extraction** — spatial regions → multi-resolution semantic labels (place names)

All three share the same 2D coordinate system, so "where each point is", "how dense a region is", and "what a region is about" stay consistent on a single map, and granularity switches with zoom level — just like a real map.

---

## 1. Text Embedding

### Principle
A pre-trained language model maps each piece of text to a high-dimensional vector (typically hundreds to thousands of dimensions), such that **semantically similar texts are close together in vector space**. This vector is the semantic foundation of the entire map — every subsequent geometric and clustering step relies on the assumption that "vector distance ≈ semantic difference."

### Key Points
- The vector itself is not rendered on the frontend; it only feeds the dimensionality reduction step.
- The distance metric is usually **cosine similarity** (direction-focused rather than magnitude), matching the intuition behind semantic comparison.

---

## 2. UMAP Dimensionality Reduction (High-D → 2D)

### Principle
UMAP (Uniform Manifold Approximation and Projection) is a manifold-learning dimensionality reduction algorithm. Its core assumption is that **data is sampled from an underlying low-dimensional manifold**, and it tries to reproduce the high-dimensional local topology in a low-dimensional space.

The algorithm has two phases:

**Phase 1: Build the high-dimensional topological graph**
- For each point, find its **k nearest neighbors** (k = `n_neighbors`).
- Connect them with weighted edges, where the weight reflects "closeness" (closer = higher weight).
- This graph encodes the data's **local manifold structure**.

**Phase 2: Low-dimensional layout optimization**
- Initialize positions for all points in 2D space.
- Optimize an objective function (based on cross-entropy) so that the 2D layout satisfies:
  - Points connected in the high-dimensional graph (neighbors) → **attract each other** in 2D
  - Points not connected → **repel each other** in 2D (to avoid collapse)
- This is essentially a **force-directed optimization**, like a spring system.

### Key Parameters
| Parameter | Meaning | Effect |
|---|---|---|
| `n_neighbors` | Number of neighbors k used to build the graph | Large → global structure; Small → local detail |
| `min_dist` | Minimum allowed distance between points in 2D | Small → points clump tighter; Large → points spread out |

### Result
Each point gets an (x, y). Semantically related texts form "archipelagos / continents"; semantically distant ones separate.

But at this stage the 2D output is just a scattered cloud of points — it lacks **a sense of terrain** and **semantic annotation**. That is exactly what the next two steps provide.

---

## 3. Terrain via Contours (Gaussian KDE)

### Motivation
Scatter plots are hard to read — you can't tell at a glance "where are most points?" So we convert the point cloud into a **continuous density field**, then render it as contours, making dense regions visually appear as "peaks."

### Principle: Kernel Density Estimation (KDE)
- Lay a grid over the 2D plane (e.g., 200×200).
- Treat each data point as the "source" of a **Gaussian bump** (a bell-shaped surface).
- For each grid cell center, sum the contributions of all Gaussian bumps at that location → that cell's **density estimate**.
- All grid density values together form a smooth **density surface**.

```
Point cloud      Sum of Gaussian bumps      Density grid → contours
 ·   ·                  ╱╲    ╱╲              ────╲────
  · ·      ──►         ╱  ╲╱╲╱  ╲      ──►     ╲   ╲
 ·   ·                 ╱      ╲╲                ╲___╲
```

### Role of Bandwidth
Bandwidth controls how "fat" each Gaussian bump is — the most important parameter of KDE:
- **Too large** → over-smoothed, all peaks merge into a blob, detail lost.
- **Too small** → noisy, spurious small peaks appear.

Typically set adaptively based on point count (more samples → narrower bandwidth).

### Acceleration Strategy
KDE over a large grid × many points is expensive. A **random subsample** is used to fit the KDE: only a capped number of points (e.g. up to 100k) are randomly drawn to estimate the overall density distribution, approximating the full set.

### Output
A grid matrix of log-density values. The frontend uses a marching-squares isoline algorithm to render it as contours, visually producing a "terrain map" that directly answers **"where is it dense?"**

---

## 4. Multi-Resolution Semantic Labels (Quadtree + Term-Frequency Topics)

This is WizMap's most central design — **map-style zoom**: zoom out far and you see coarse topics of large regions; zoom in close and you see fine topics of small regions. It mimics how a real map reveals finer place names as you zoom in.

### (a) Quadtree Spatial Indexing

Recursively **quarter** the 2D plane:

```
Level 1:  2×2  = 4    cells     (large region, coarse)
Level 2:  4×4  = 16   cells
Level 3:  8×8  = 64   cells
...
Level l:  2^l × 2^l cells       (small region, fine)
```

- Each leaf cell owns a rectangular spatial region.
- All texts within a cell are aggregated into a "bag of documents."
- **Level = resolution**: shallow levels → large regions; deep levels → small regions.

The quadtree provides the ability to "aggregate texts by spatial range" quickly — given any region, you can retrieve all its contained points in O(log n).

### (b) Per-Cell Topic Extraction

For the texts inside each spatial cell, run a **term-frequency topic analysis**:

1. Use a CountVectorizer to tally term frequencies across all texts in the cell (while removing stop words).
2. Apply a TF-style weighting to select the **most representative high-frequency terms** for that region.
3. Concatenate the top terms into a topic name (e.g. `research-model-learning`).

Each spatial cell thus gets a "semantic label," answering **"what is this region about?"**

To handle large vocabularies efficiently, term-frequency counting uses a sparse matrix and only keeps each cell's top-n terms, avoiding full-vocabulary overhead.

### (c) Automatic Level Selection

The quadtree could theoretically subdivide indefinitely, but we don't need to compute all levels. The algorithm back-computes which levels to extract based on **view geometry**:

Inputs: canvas size, max zoom scale, ideal tile pixel width (~35px).
Principle: at a given zoom scale, compute how many screen pixels each level's tile actually occupies, then pick the level closest to 35px.

```
At zoom scale s:
  on-screen length   = s × canvas length
  # tiles this level = 2^l
  tile pixel width   = on-screen length / 2^l

  → choose l that makes "tile pixel width ≈ 35px"
```

Iterating over all zoom steps yields a `[min_level, max_level]` range, and **topics are extracted only for these levels**, skipping pointless full computation. This guarantees:
- Each label occupies roughly an ideal-sized region on screen — neither crowded nor sparse.
- Compute is strictly bounded to the levels the view will actually use.

### (d) Zoom Switching on the Frontend
Every topic label carries an `(x, y, level)` triple. On zoom/pan, the frontend **only renders labels for the level matching the current zoom scale**, switching seamlessly between levels — enabled by pre-computed multi-level topics, not real-time computation.

---

## 5. Three Layers Synthesized into One Map

| Visual Layer | Data Source | Algorithm | Question Answered |
|---|---|---|---|
| **Scatter points** | each point's (x, y, text) | UMAP | "where is each datum?" |
| **Contours** | density grid | Gaussian KDE | "where is it dense?" |
| **Topic labels** | per-level quadtree topics | term frequency + quadtree | "what is this region about?" |

All three **share the same (x, y) coordinate system**, so:
- Scatter points sit on the contour "peaks" (dense areas).
- Topic labels are placed at the geometric center of their region.
- At any zoom level, the three layers stay semantically consistent.

---

## 6. Why This Design Scales

The key is **separating preprocessing from rendering**:

- All expensive computation — UMAP, KDE, quadtree topics — is done **once, offline, during the preprocessing stage**.
- The output is just a few static files: a density grid, hierarchical topic labels, and a list of point coordinates.
- What the frontend receives is **already graded, already smoothed, already topic-aggregated**.
- During zoom/pan, the frontend only performs **coordinate transforms + level filtering** — no ML computation in the browser.

So even with **hundreds of thousands to millions of points**, frontend interaction stays smooth — all the heavy lifting was done in the backend pipeline after upload. This is the fundamental source of WizMap's "scalability."

---

## Appendix: Algorithm Pipeline Overview

```
Raw text
  │
  │  ① Embedding (pre-trained model)
  ▼
High-dim semantic vectors  ───────► "semantic similarity ⇒ proximity"
  │
  │  ② UMAP (k-NN graph + force-directed optimization)
  ▼
2D coordinates (x, y)  ───────────► "where each datum sits on the map"
  │
  ├──────────────────────────────────────┐
  │                                      │
  │  ③ Gaussian KDE (sum of bumps)       │  ④ Quadtree (recursive quartering)
  ▼                                      ▼
Density surface / contours             Multi-level spatial cells
  │                                      │  + term-frequency topic extraction
  │                                      ▼
  │                                 Hierarchical topic labels (x,y,level,name)
  │                                      │
  └──────────────► share (x,y) ◄─────────┘
                       │
                       ▼
              Zoomable interactive map
       (scatter + terrain + zoom-switched place names)
```
