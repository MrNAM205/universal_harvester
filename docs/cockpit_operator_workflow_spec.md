# OmniVeroBrix Cockpit Operator Workflow — Specification (v1.0)

The Operator Workflow is the master blueprint for how an operator actually uses the cockpit end-to-end. It defines the operator's lived experience through seven operational phases.

## 1. Intake & Ingestion Phase
- **Actions:** Upload documents, trigger pipeline.
- **Panels:** Evidence Panel, Document Viewer.
- **Behavior:** Harvester extracts data, Remittance engine detects coupons, Corpus identifies statutes.

## 2. Evidence Review Phase
- **Actions:** Review metadata, validate entities, tag documents.
- **Panels:** Evidence Panel, Document Viewer.
- **Behavior:** Updates entity graph, refines corpus mappings.

## 3. Document Analysis Phase
- **Actions:** Inspect OCR, review timeline, validate remittance geometry.
- **Panels:** Document Viewer, Timeline Panel.
- **Behavior:** Refines structural interpretation.

## 4. Corpus Intelligence Alignment Phase
- **Actions:** Open corpus entries, review citations, validate procedural context.
- **Panels:** Corpus Intelligence Panel, Knowledge Graph.
- **Behavior:** Updates corpus mappings, creates cross-references.

## 5. Remittance Interpretation Phase
- **Actions:** Review routing/accounts, inspect barcodes, compare instruments.
- **Panels:** Remittance Panel, Evidence Panel.
- **Behavior:** Updates remittance table, detects issuer patterns.

## 6. Mission Creation & Execution Phase
- **Actions:** Select mission type, provide inputs, preview plan, run mission.
- **Panels:** Mission Generator, Mission Panel, Mission Execution Panel.
- **Behavior:** Router builds plan, Autonomy Loop executes steps, subsystems produce outputs.

## 7. Autonomy Oversight & System Health Phase
- **Actions:** Watch phases, inspect reflections, monitor health, review alerts.
- **Panels:** Autonomy Monitor, System Health Panel, Operator Console.
- **Behavior:** Logs cycles, tracks telemetry, ensures system stability.

## Full Operator Workflow Map
`Intake → Evidence → Document → Corpus → Remittance → Mission → Autonomy → Health`
