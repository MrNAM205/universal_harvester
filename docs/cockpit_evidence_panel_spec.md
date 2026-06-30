# OmniVeroBrix Cockpit Evidence Panel — Specification (v1.0)

The Evidence Panel gives the operator a complete, structured, multi‑layered view of all harvested documents and their associated intelligence.

## 1. Evidence Header
Displays totals: harvested docs, linked to current mission, with remittance blocks, with corpus mappings, with remedy maps.

## 2. Evidence List (Left Column)
Scrollable list of harvested documents. 
Shows document_id, type, source, ingested_at, quick tags.
Sorting and filtering by type, issuer, amount, date, corpus mapping, etc.
Full-text and entity search.

## 3. Evidence Detail (Right Column)
Deep inspection view.
- **Metadata:** filename, filepath, content_type, language, page_count, hash
- **Parties:** sender, recipient, other parties
- **Dates:** document, due, statement period, extracted dates
- **Financials:** amounts, balances, charges, line items
- **Remittance Block:** instrument type, issuer, account/routing, barcode
- **Entities:** persons, organizations, addresses, keywords
- **Corpus Mapping Summary:** relevant entries, citations, context
- **Remedy Map Summary:** summary, process description, deadlines

## 4. Cross‑Document Analysis (Bottom Panel)
Forensic intelligence layer showing documents with matching parties, account numbers, issuers, dates, corpus tags, remittance patterns. Reveals clusters and anomalies.

## 5. Action Bar (Bottom)
Buttons: Generate Summary, Generate Timeline, Generate Letter, Link to Mission, Open Document Viewer.

## 6. API Endpoints (Cockpit → Backend)
- `/api/evidence/list`
- `/api/evidence/{document_id}`
- `/api/evidence/{document_id}/corpus`
- `/api/evidence/{document_id}/remittance`
- `/api/evidence/{document_id}/remedy`
- `/api/evidence/search`
- `/api/evidence/filter`
- `/api/evidence/cross`
