# OmniVeroBrix Cockpit Corpus Intelligence Panel — Specification (v1.0)

The Corpus Panel is the cockpit’s lawful intelligence console, where CFR, USC, UCC, IRM, agency guidance, sovereign archives, and procedural definitions become navigable, searchable, and cross‑linked.

## 1. Panel Layout (High‑Level)
Divided into Corpus Collections (left), Corpus Detail (right), and Cross-Corpus Intelligence (bottom).

## 2. Corpus Header
Displays totals for corpus entries by type (statutes, regulations, manuals, guidance, archives), and entries linked to the current mission/document.

## 3. Left Sidebar
- **Corpus Collections:** Hierarchical list of all sources (CFR, USC, UCC, IRM, Archives).
- **Filters:** By type, jurisdiction, domain, tags, source.
- **Search:** Citation, keyword, full-text, cross-reference.

## 4. Corpus Detail (Right Column)
Deep knowledge viewer.
- **Overview:** entry_id, type, jurisdiction, source, ingested_at.
- **Citation & Title:** citation, official title, descriptive title.
- **Body Viewer:** Scrollable text with syntax/keyword highlighting.
- **Tags & Domain:** structural, procedural, domain tags.
- **Related Entries:** cross-references, linked statutes/definitions.
- **Document Mappings:** Harvested documents mapped to this entry.
- **Remedy Map Links:** Remedy maps referencing this entry.

## 5. Cross‑Corpus Intelligence (Bottom Panel)
Knowledge intelligence layer detecting clusters, patterns, regulatory ecosystems based on shared tags, citations, documents.

## 6. Action Bar (Bottom)
Buttons: Generate Definition Summary, Generate Procedural Map, Generate Cross-Corpus Report, Link to Mission.

## 7. API Endpoints
- `/api/corpus/list`
- `/api/corpus/{entry_id}`
- `/api/corpus/{entry_id}/related`
- `/api/corpus/{entry_id}/documents`
- `/api/corpus/{entry_id}/remedy`
- `/api/corpus/search`
- `/api/corpus/filter`
- `/api/corpus/cross`
