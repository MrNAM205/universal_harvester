# OmniVeroBrix Corpus Ingestion Pipeline — Specification (v1.0)

## 🎯 Purpose
Provide a unified, deterministic pipeline that ingests **any legal/lawful corpus** and converts it into structured entries that OmniVeroBrix can map to harvested documents.

This pipeline is the *knowledge intake system* for:
- CFR (Code of Federal Regulations)
- USC (United States Code)
- UCC (Uniform Commercial Code)
- IRM (Internal Revenue Manual)
- Agency guidance (IRS pubs, SSA manuals, CFPB bulletins)
- Sovereign knowledge archives (your cockpit materials)

---

## 🧩 1. Corpus Entry Schema
All ingested knowledge becomes a **corpus entry**:
```json
{
  "entry_id": "UUIDv4",
  "type": "statute | regulation | manual | guidance | maxim | archive",
  "jurisdiction": "string | null",
  "citation": "string | null",
  "title": "string",
  "body": "string",
  "tags": ["string"],
  "related_entries": ["string"],
  "source": "string",            // 'CFR', 'USC', 'UCC', 'IRM', 'Archive'
  "ingested_at": "ISO8601"
}
```
This schema is stored in the SQLite database under `corpus_entries`.

---

## 🧠 2. Ingestion Pipeline Architecture
```text
omniverobrix/
│
├── corpus_ingestion/
│   ├── loaders/
│   │   ├── cfr_loader.py
│   │   ├── usc_loader.py
│   │   ├── ucc_loader.py
│   │   ├── irm_loader.py
│   │   └── archive_loader.py
│   │
│   ├── parsers/
│   │   ├── citation_parser.py
│   │   ├── section_parser.py
│   │   ├── title_parser.py
│   │   └── tagger.py
│   │
│   ├── normalizer.py
│   ├── linker.py
│   ├── ingest.py
│   └── schema.json
```

---

## 🔍 3. Loader Responsibilities
Each loader:
- reads raw text/HTML/PDF
- extracts: citation, title, body, section numbers, agency identifiers
- passes raw chunks to the parser layer

### Loader Types
- **CFR Loader:** Parses Title → Part → Section hierarchy. Extracts citations like `12 CFR 1026.5(b)(2)(i)`
- **USC Loader:** Parses Title → Chapter → Section. Extracts citations like `15 U.S.C. § 1692`
- **UCC Loader:** Parses Articles → Sections. Extracts citations like `UCC § 3‑104`
- **IRM Loader:** Parses Part → Chapter → Section. Extracts citations like `IRM 5.1.1.2`
- **Archive Loader:** Ingests sovereign cockpit materials. Tags them as `archive` type corpus entries.

---

## 🧩 4. Parser Responsibilities
### Citation Parser
Extracts: title number, section number, part number, article number, agency identifiers.
### Section Parser
Splits raw text into: headings, subsections, paragraphs, notes.
### Title Parser
Extracts: official title, descriptive title, agency name.
### Tagger
Assigns tags based on: keywords, structural patterns, domain, instrument types.

---

## 🔧 5. Normalizer
Converts parsed data into the **corpus entry schema**. Ensures consistent formatting, citation structure, tagging, and jurisdiction labeling.

---

## 🔗 6. Linker
Creates relationships between entries: cross‑references, related sections, related definitions, related procedures, related agency guidance.
Example: `12 CFR 1026` links to `Truth in Lending Act`.

---

## 🚀 7. Ingest Script
`ingest.py` orchestrates the pipeline:
1. Load raw corpus files
2. Parse citations, titles, bodies
3. Normalize into corpus entries
4. Link related entries
5. Insert into SQLite database

---

## 🔍 8. Query Interface (Corpus Layer)
Once ingested, the Corpus Layer can:
- `find_entries_by_citation("12 CFR 1026.5")`
- `find_entries_by_tags(["remittance", "billing"])`
- `find_entries_by_text("instrument")`
- `find_related_entries(entry_id)`

---

## 🧭 9. Integration with Remittance Parser
The remittance parser outputs: instrument_type, issuer_name, due_date, amount_due, coupon_code.
The Corpus Layer uses these to pull relevant corpus entries.

Example:
- `instrument_type = "utility_bill_coupon"` → tags: `utilities`, `billing`, `remittance` → corpus entries: state utility regulations, billing rules

---

## 📌 10. Integration with Sovereign Thought Engine
The Sovereign Engine uses corpus entries to: generate hypotheses, detect missing information, refine remedy maps, identify procedural steps, detect contradictions.
