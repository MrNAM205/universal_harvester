# OmniVeroBrix Cockpit Remittance Panel — Specification (v1.0)

The Remittance Panel is the cockpit’s financial intelligence console, giving a clear, forensic view of every remittance coupon, billing stub, payment instrument, and financial artifact.

## 1. Panel Layout (High‑Level)
Divided into Remittance List (left), Remittance Detail (right), and Cross-Instrument Analysis (bottom).

## 2. Remittance Header
Displays totals for remittance instruments, mapped routing/accounts, due dates, corpus/remedy mappings.

## 3. Left Sidebar
- **Remittance List:** Scrollable list showing instrument_id, type, issuer, amount, due date, quick tags.
- **Filters:** By type, issuer, presence of barcode/routing/account, date/amount range.
- **Search:** Account/routing, coupon code, issuer, keywords.

## 4. Remittance Detail (Right Column)
Deep structural view.
- **Instrument Overview:** type, issuer, reference, document_id, remittance zone detected.
- **Parsed Fields:** account_number, routing_number, coupon_code, payment_address, due_date, amount_due.
- **Barcode/Scanline:** raw data, interpretation, location.
- **Payment Instructions:** remit-to address, accepted methods, URLs.
- **Corpus Mapping & Remedy Map:** relevant entries, procedural context, deadlines.

## 5. Cross‑Instrument Analysis (Bottom Panel)
Financial intelligence layer. Detects patterns: matching account/routing numbers, issuers, dates, amounts, similar layouts. Source: `remittance_instruments`, `document_corpus_mappings`.

## 6. Action Bar (Bottom)
Buttons: Generate Summary, Generate Timeline, Link to Mission, Open in Document Viewer.

## 7. API Endpoints
- `/api/remittance/list`
- `/api/remittance/{instrument_id}`
- `/api/remittance/{instrument_id}/corpus`
- `/api/remittance/{instrument_id}/remedy`
- `/api/remittance/search`
- `/api/remittance/filter`
- `/api/remittance/cross`
