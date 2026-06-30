# OmniVeroBrix Cockpit Timeline Panel — Specification (v1.0)

The Timeline Panel visualizes temporal intelligence extracted from documents, missions, autonomy cycles, and corpus mappings. It shows how events, steps, reflections, and decisions line up across time.

## 1. Panel Layout (High‑Level)
Unifies three timelines: Document Timeline, Mission Timeline, Process Timeline.
Includes Zoom Controls, Filters, Search, and Event Detail Drawer.

## 2. Timeline Header
Displays: mission_id, related_document_id, number of events, date bounds. Quick toggles for visibility layers.

## 3. Zoom Controls
Zoom In/Out (minute → year), Fit to Events, Jump to Today.

## 4. Filters & Search
Filters isolate: document events, mission steps, autonomy phases, reflections, deadlines.
Search supports: date, keyword, entity, amount, citation.

## 5. Unified Timeline View
Three synchronized tracks:
- **Document Events Track:** extracted dates, remittance deadlines, issuer timestamps.
- **Mission Events Track:** mission creation, step execution, autonomy phases, reflections (color-coded).
- **Process Timeline Track:** procedural steps, deadlines from remedy maps.

## 6. Event Detail Drawer
Clicking an event opens details: metadata (timestamp, type, subsystem, confidence), context, cross-links (Open in Document Viewer/Mission Panel/Corpus Entry).

## 7. Action Bar (Bottom)
Generate Timeline Document, Generate Summary, Link Timeline to Mission.

## 8. API Endpoints
- `/api/timeline/{mission_id}`
- `/api/timeline/{document_id}`
- `/api/timeline/process/{document_id}`
- `/api/missions/{id}/steps`
- `/api/missions/{id}/ledger`
- `/api/remedy/{document_id}`
