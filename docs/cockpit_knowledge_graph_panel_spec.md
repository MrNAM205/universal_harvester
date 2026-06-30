# OmniVeroBrix Cockpit Knowledge Graph Panel — Specification (v1.0)

The Knowledge Graph Panel visualizes the global entity graph, connecting documents, entities, corpus entries, remittance instruments, missions, remedy maps, and autonomy cycles into a navigable universe.

## 1. Knowledge Graph Header
Displays totals for nodes, edges, represented objects, last update, and active filters.

## 2. Graph Canvas (Center)
Interactive visualization.
- **Node Types:** Documents, Entities, Corpus Entries, Remittances, Missions, Maps, Autonomy Phases, Clusters.
- **Edge Types:** mentions, references, derived from, mapped to, timeline dependency.
- **Interactions:** pan, zoom, pin, select to inspect.
- **Graph Modes:** Force-directed, Radial, Hierarchical, Cluster, Mission, Remittance.

## 3. Right Inspector Panel
Shows details for selected node (overview, type-specific content, connected edges). Links to specialized cockpit panels (Document Viewer, Corpus Panel, etc.).

## 4. Left Graph Layers Panel
Toggles visibility for layers (Documents, Entities, etc.), Domain Filters (tax, credit, etc.), and Structural Filters (high-degree, low-confidence).

## 5. Graph Timeline Slider (Bottom)
Temporal scrubber filtering graph nodes by time. Animates edges forming/disappearing over time.

## 6. Action Bar (Bottom)
Generate Graph Report, Generate Cluster Summary, Link Node to Mission, Export.

## 7. API Endpoints
- `/api/graph/full`
- `/api/graph/node/{id}`
- `/api/graph/edges/{id}`
- `/api/graph/layers`
- `/api/graph/filter`
- `/api/graph/timeline`
- `/api/graph/clusters`
