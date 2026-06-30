# OmniVeroBrix Remittance Parser — Specification (v1.0)

This is the **money‑side interpreter** of OmniVeroBrix: it reads coupons, statements, and payment instruments, turns them into structured data, and hands that to the corpus + sovereign layers for meaning and options.

---

## 1. Purpose
**Goal:** Parse remittance‑related artifacts and normalize them into a consistent structure:
- remittance coupons
- billing statements
- payment stubs
- check images (front only, conceptually)
- online payment pages (HTML snapshots)

It explains **what the instrument is and how it structurally functions**, not what the user should do with it.

---

## 2. Inputs and Outputs
**Inputs:**
- Raw document (PDF, image, HTML, email)
- Harvester JSON (the schema we already defined)
- Optional: barcode/scanline data from OCR

**Outputs (remittance block, refined):**
```json
{
  "account_number": "string | null",
  "routing_number": "string | null",
  "coupon_code": "string | null",
  "payment_address": "string | null",
  "payment_methods": ["string"],
  "due_date": "ISO8601 | null",
  "amount_due": "number | null",
  "barcode_data": "string | null",
  "scanline": "string | null",
  "instrument_type": "string | null",   // 'utility_bill_coupon', 'credit_card_statement_stub', etc.
  "issuer_name": "string | null",
  "issuer_reference": "string | null"
}
```
This block plugs directly into the `remittance` section of the Harvester Schema.

---

## 3. Functional Modules

**1. Layout analyzer**
- Reads `text_blocks` + `bbox` from the harvester.
- Identifies typical coupon regions: bottom third of page, right‑hand stub, “detach and return” sections.

**2. Pattern extractor**
- Uses regex + heuristics to find: account numbers, routing numbers, reference/coupon codes, due dates, amounts.

**3. Instrument classifier**
- Classifies the instrument structurally: `utility_bill_coupon`, `credit_card_statement_stub`, `medical_bill_remittance`, `tax_notice_payment_stub`, `generic_invoice_coupon`.
- Uses: issuer name, document_type, layout patterns, keywords.

**4. Barcode / scanline parser**
- If barcode or scanline is present: capture raw string, store in `barcode_data` or `scanline`. Does **not** attempt bank‑level decoding.

**5. Consistency checker**
- Cross‑checks: `amount_due` vs `financials.amount_due`, `due_date` vs `dates.due_date`, `issuer_name` vs `parties.sender.name`. Flags discrepancies.

---

## 4. Integration with Corpus and Sovereign Layers

### A. Corpus Intelligence Layer — Legal/Lawful Knowledge Ingestion
We extend the Corpus Layer with **knowledge collections**:
- **USC (United States Code)**
- **CFR (Code of Federal Regulations)**
- **UCC (Uniform Commercial Code)**
- **IRM (Internal Revenue Manual)**
- Agency guidance & Internal maxims

Each collection is ingested as corpus entries. The **link** between remittance parser and corpus:
- `instrument_type` + `issuer_name` + `amount_due` + `due_date` → used to select relevant corpus entries.

### B. Knowledge Collection Mechanism (How OmniVeroBrix “Learns”)
1. **Source files:** Local text/HTML/PDF exports.
2. **Ingestion script:** Parse citations, titles, bodies. Normalize and store in DB.
3. **Tagging:** Tag by domain, instrument types, agencies.
4. **Query interface:** `find_entries_by_tags`, `find_entries_by_citation`, `find_entries_by_text`.

---

## 5. API (Internal)
Remittance parser:
- `parse_remittance(document)` → remittance block
- `classify_instrument(remittance_block, document)` → instrument_type + issuer_name
- `validate_consistency(remittance_block, harvested_document)` → discrepancy report

Corpus:
- `map_remittance_to_corpus(remittance_block)` → relevant corpus entries + remedy map
- `explain_instrument(remittance_block, corpus_entries)` → structural explanation for Assistant Core
