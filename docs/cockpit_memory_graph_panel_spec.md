# OmniVeroBrix Cockpit Memory Graph Panel — Specification (v1.0)

The Memory Graph Panel visualizes the system's long-term memory as an evolving knowledge structure, showing how missions, documents, entities, corpus entries, and operator facts accumulate into durable memory nodes.

## 1. Memory Graph Header
Displays totals: memory nodes, edges, operator-provided facts, system-derived facts, last update, memory health.

## 2. Memory Graph Canvas (Center)
Interactive visualization of durable memory.
- **Node Types:** Operator Facts, Mission Memories, Document Memories, Corpus Memories, Remittance Memories, Autonomy Memories, Clusters.
- **Edge Types:** derived from, linked to, preference, autonomy insight, etc.
- **Modes:** Operator Memory Mode, Mission Mode, Corpus Mode, Remittance Mode, Cluster Mode.

## 3. Memory Inspector (Right Panel)
Shows details for selected memory node.
- **Overview:** id, type, created_at, origin, confidence.
- **Content:** (e.g., Operator Memory -> preference/fact; Corpus Memory -> frequent citations; Document Memory -> stable metadata).
- **Connected Memory:** Incoming/outgoing edges.

## 4. Memory Layers Panel (Left)
Toggles visibility for layers (Operator, Mission, Corpus, Remittance, Autonomy) and Domain/Structural filters.

## 5. Memory Timeline Slider (Bottom)
Temporal scrubber filtering memory nodes by time. Animates edges forming/disappearing.

## 6. Action Bar (Bottom)
Buttons: Generate Memory Report, Cluster Summary, Evolution Timeline, Export, Link to Mission, Clear Stale Memory.

## 7. API Endpoints
- `/api/memory/graph`
- `/api/memory/node/{id}`
- `/api/memory/edges/{id}`
- `/api/memory/layers`
- `/api/memory/filter`
- `/api/memory/timeline`
- `/api/memory/clusters`
- `/api/memory/cleanup`
