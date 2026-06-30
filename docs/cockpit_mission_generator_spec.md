# OmniVeroBrix Cockpit Mission Generator — Specification (v1.0)

The Mission Generator is the cockpit’s task‑creation engine, defining what OmniVeroBrix should analyze, interpret, generate, or execute.

## 1. Panel Layout (High‑Level)
Features Mission Type Selector, Mission Input Builder, Mission Preview, and Controls.

## 2. Mission Generator Header
Displays: total missions, active, blocked, completed, last created, subsystem availability.

## 3. Mission Type Selector
Selectable templates: Document Analysis, Corpus Mapping, Remittance Parsing, Timeline Extraction, Evidence Inventory, Summary Generation, Letter Generation, Autonomy Loop.

## 4. Mission Input Builder
Structured form:
- **Document Selection:** single, multiple, groups.
- **Corpus Selection:** entries, domains, tags.
- **Remittance Selection:** instruments, issuers.
- **Parameters:** depth, output type, timeline range, subsystem restrictions.
- **Context:** notes, constraints.

## 5. Mission Preview
Live preview of mission object: type, subsystems involved, inputs, plan outline, expected outputs, stop conditions. Generated via Mission Router's dry-run mode.

## 6. Action Bar (Bottom)
Buttons: Create Mission, Validate Inputs, Preview Plan, Preview Autonomy Loop, Clear Form.

## 7. API Endpoints
- `/api/missions/create`
- `/api/missions/validate`
- `/api/missions/preview`
- `/api/missions/preview_plan`
- `/api/missions/preview_autonomy`
- `/api/documents/list`
- `/api/corpus/list`
- `/api/remittance/list`
