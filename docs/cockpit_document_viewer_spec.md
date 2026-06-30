# OmniVeroBrix Cockpit Document Viewer — Specification (v1.0)

The Document Viewer is the cockpit’s visual intelligence window, where raw PDFs, images, HTML, emails, and chat logs become navigable, searchable, and cross‑linked evidence.

## 1. Document Header
Displays: document_id, document_type, source, ingested_at, page_count, issuer, quick tags.
Also includes action links: Open in Evidence Panel, Link to Mission, Generate Summary, Generate Timeline.

## 2. Left Sidebar
- **Page Thumbnails:** Click to load page in main viewer.
- **Entities:** Scrollable list of extracted entities (persons, orgs, dates, amounts). Click to highlight on page.
- **Metadata:** filename, filepath, content_type, language, hash_sha256.

## 3. Main Viewer
Primary display area.
- **Page Display:** Renders PDF, Image, HTML, Email, Chat transcript.
- **Text Extraction Overlay:** Shows bounding boxes, page text, OCR confidence. Overlays can be toggled (Raw OCR, Normalized Text, Entities Highlighted, Remittance Zones, Corpus Tags).

## 4. Structured Data Tabs (Right Side)
- **Parties:** sender, recipient, other parties
- **Dates:** document_date, due_date, statement_period, extracted_dates
- **Financials:** amounts, line items, balances
- **Remittance Block:** instrument_type, issuer, routing, account, barcode
- **Corpus Mapping:** relevant entries, citations, procedural context
- **Remedy Map:** summary, deadlines, possible paths

## 5. Action Bar (Bottom)
Buttons: Generate Summary, Generate Timeline, Generate Letter, Generate Notice, Generate Inventory, Link to Mission, Open in Evidence Panel.

## 6. API Endpoints (Cockpit → Backend)
- `/api/documents/{id}`
- `/api/documents/{id}/pages`
- `/api/documents/{id}/entities`
- `/api/documents/{id}/metadata`
- `/api/documents/{id}/remittance`
- `/api/documents/{id}/corpus`
- `/api/documents/{id}/remedy`
- `/api/documents/{id}/timeline`
