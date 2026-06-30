# OmniVeroBrix Knowledge Base Procurement Test Plan (v1.0)

This is the formal, operator-facing validation protocol that ensures the system can acquire, ingest, structure, map, and operationalize all knowledge sources. Run inside the cockpit.

## 1. Document Procurement & Ingestion
- **Objective:** Verify ingestion of all document types and production of structured intelligence.
- **Procedure:** Upload documents, trigger pipeline, inspect OCR/page structure/metadata.
- **Outcomes:** Documents appear in Evidence Panel, OCR confidence ≥ 90%, remittance zones detected.

## 2. Entity Extraction & Normalization
- **Objective:** Ensure entities are extracted, normalized, deduplicated, linked.
- **Procedure:** Inspect entity list, validate normalization/linking, check confidence.
- **Outcomes:** No duplicates, linked to documents/corpus, appear in Knowledge Graph.

## 3. Corpus Acquisition & Mapping
- **Objective:** Validate corpus entries are acquired, indexed, mapped to documents.
- **Procedure:** Load corpus, search citations, validate mapping, inspect procedural context.
- **Outcomes:** Entries in Corpus Panel, correct citations, referenced by remedy maps.

## 4. Remittance Instrument Detection & Parsing
- **Objective:** Ensure remittance instruments are detected, parsed, structured.
- **Procedure:** Upload documents with coupons, validate detection/parsed fields/clustering.
- **Outcomes:** Appear in Remittance Panel, ≥ 85% confidence, clusters in Knowledge Graph.

## 5. Remedy Map Generation & Procedural Intelligence
- **Objective:** Verify procedural intelligence from corpus mappings.
- **Procedure:** Inspect remedy maps, validate deadlines/steps/paths, confirm corpus cross-links.
- **Outcomes:** Remedy maps in Corpus Panel, deadlines in Timeline Panel.

## 6. Knowledge Graph Expansion & Linking
- **Objective:** Ensure global knowledge graph expands correctly.
- **Procedure:** Inspect node count, validate edge creation, inspect clusters/timeline filtering.
- **Outcomes:** Count increases predictably, no orphans, clusters form around issuers/domains/remittance patterns.

## 7. Memory Graph Persistence & Stability
- **Objective:** Ensure long-term memory persists across sessions/missions.
- **Procedure:** Inspect operator/mission/document facts, validate memory timeline.
- **Outcomes:** Nodes persist across restarts, no stale memory, clusters form around operator patterns.

## Final Validation: Knowledge Base Procurement Mission
Run a dedicated audit mission using all documents, corpus entries, and remittance instruments. Produces full procurement report, graph snapshots, and audit logs via Mission Generator.
