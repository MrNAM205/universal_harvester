# OmniVeroBrix Cockpit Mission Panel — Specification (v1.0)

The Mission Panel is the **central dashboard** for viewing missions, tracking steps, watching autonomy loop progress, inspecting harvested documents, seeing corpus mappings, reviewing remedy maps, generating summaries, timelines, and letters.

It is the operator’s window into the entire system.

## 1. Panel Layout (High‑Level)
```text
+---------------------------------------------------------------+
| Mission Header                                                |
+---------------------------------------------------------------+
| Left Column                     | Right Column                |
|---------------------------------------------------------------|
| Mission Timeline                | Mission Steps               |
| Harvested Document Preview      | Autonomy Loop State         |
| Corpus Mapping Summary          | Remedy Map Overview         |
| Remittance Block (if present)   | Generated Documents         |
+---------------------------------------------------------------+
| Action Bar (Generate Summary, Timeline, Letter, etc.)         |
+---------------------------------------------------------------+
```

## 2. Mission Header
Displays: mission_id, mission_type, status, created_at, updated_at, assigned subsystems, missing requirements, related document_id. Fed from `missions` table.

## 3. Mission Timeline (Left Column)
A chronological visualization of mission creation, step execution, autonomy loop cycles, reflections, decisions.
Data sources: `missions`, `mission_steps`, `thought_ledger`.
Each entry shows timestamp, type, short summary.

## 4. Mission Steps (Right Column)
A structured list of all steps in the mission: step_id, description, subsystem, status, result summary.
Data source: `mission_steps`. Groups by pending, running, complete.

## 5. Harvested Document Preview (Left Column)
Shows document_type, sender/recipient, key dates/amounts, extracted entities, full_text preview.
Data source: `harvested_documents`.

## 6. Corpus Mapping Summary (Left Column)
Shows relevant corpus entries, citations, definitions, procedural context.
Data source: `document_corpus_mappings`, `corpus_entries`.

## 7. Remedy Map Overview (Right Column)
Shows summary, process description, deadlines, possible paths, notes.
Data source: `remedy_maps`.

## 8. Remittance Block (If Present)
Shows instrument_type, issuer_name, account_number, routing_number, coupon_code, due_date, amount_due, barcode/scanline.
Data source: `remittance_instruments`.

## 9. Autonomy Loop State (Right Column)
Shows current phase, pending steps, completed steps, last reflection summary, stop condition.
Data source: `plans`, `thought_ledger`, `missions`.

## 10. Generated Documents (Right Column)
Shows summaries, timelines, letters, notices, inventories, overviews.
Data source: `generated_documents`. Each item has preview, download, copy.

## 11. Action Bar (Bottom)
Buttons to trigger missions via Mission Router: Generate Summary, Generate Timeline, Generate Letter, Generate Notice, Generate Inventory, Generate Overview, Run Autonomy Loop, Step Autonomy Loop.

## 12. API Endpoints (Cockpit → Backend)
- `/api/missions/{id}`
- `/api/missions/{id}/steps`
- `/api/missions/{id}/ledger`
- `/api/documents/{id}`
- `/api/corpus/{document_id}`
- `/api/remedy/{document_id}`
- `/api/remittance/{document_id}`
- `/api/generated/{mission_id}`
- `/api/autonomy/{mission_id}/run`
- `/api/autonomy/{mission_id}/step`
