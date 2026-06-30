# OmniVeroBrix Corpus Intelligence Layer — Specification (v1.0)

This is the **knowledge spine** of OmniVeroBrix: it connects harvested, messy documents to structured statutes, definitions, procedures, and “remedy maps” without ever pretending to be a lawyer.

---

## 1. Purpose
**Goal:** Transform harvested document data into:
- mapped statutes and rules
- definitions of terms
- procedural context (who, what, when, where, how)
- remedy maps (options, deadlines, dependencies)

It explains **structure and relationships**, not legal advice.

---

## 2. Core Responsibilities
- **Corpus management:** Store and organize:
  - statutes
  - regulations
  - agency guidance
  - definitions
  - procedural rules
  - internal maxims (non‑legal, structural)

- **Document–corpus mapping:** Link harvested fields (dates, amounts, parties, document_type) to relevant corpus entries.

- **Remedy map generation:** Build structured “maps” of:
  - what the document is
  - what it appears to be doing
  - what processes it belongs to
  - what deadlines and steps exist procedurally

- **Term clarification:** Explain terms, labels, and roles in plain language.

---

## 3. Corpus Data Structures

### 3.1 Corpus Entry
```json
{
  "entry_id": "string",
  "type": "statute | regulation | definition | procedure | guidance | maxim",
  "jurisdiction": "string | null",
  "citation": "string | null",
  "title": "string",
  "body": "string",
  "tags": ["string"],
  "related_entries": ["string"]
}
```

### 3.2 Document–Corpus Mapping
```json
{
  "mapping_id": "string",
  "document_id": "string",
  "corpus_entries": [
    {
      "entry_id": "string",
      "reason": "string",
      "confidence": "number"
    }
  ],
  "derived_context": {
    "process_type": "string | null",
    "roles": ["string"],
    "key_terms": ["string"]
  }
}
```

### 3.3 Remedy Map
```json
{
  "remedy_map_id": "string",
  "document_id": "string",
  "summary": "string",
  "process": {
    "name": "string | null",
    "description": "string | null"
  },
  "deadlines": [
    {
      "label": "string",
      "date": "ISO8601 | null",
      "confidence": "number"
    }
  ],
  "possible_paths": [
    {
      "path_id": "string",
      "description": "string",
      "requirements": ["string"],
      "dependencies": ["string"],
      "risk_notes": "string | null"
    }
  ],
  "notes": "string | null"
}
```

---

## 4. Functional Modules
- **Corpus loader:** Loads corpus entries from files, DB, or external sources.
- **Tagging engine:** Tags harvested documents with relevant corpus entries based on:
  - document_type
  - keywords
  - entities
  - structure
- **Remedy mapper:** Builds remedy maps from:
  - document classification
  - corpus entries
  - dates and amounts
  - roles and parties
- **Definition explainer:** Given a term, returns:
  - definition
  - related corpus entries
  - procedural context

---

## 5. Integration Points
- **Harvester → Corpus:** Harvester sends normalized document JSON. Corpus returns mappings + remedy map.
- **Mission Router → Corpus:** Router requests:
  - “map this document”
  - “explain this term”
  - “generate remedy map”
- **Assistant Core → Corpus:** Assistant uses corpus outputs to explain:
  - what the document is
  - what process it belongs to
  - what deadlines exist
  - what options structurally exist

---

## 6. API (Internal)
- `map_document(document)` → document–corpus mapping + remedy map
- `explain_term(term)` → definition + related entries
- `get_related_entries(entry_id)` → linked corpus entries
- `summarize_process(document)` → process description + steps

---

## 7. Constraints
- Never claim to give legal advice.
- Never tell the user what they “should” do.
- Only describe:
  - structures
  - relationships
  - definitions
  - procedural patterns
