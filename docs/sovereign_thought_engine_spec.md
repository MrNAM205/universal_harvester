# OmniVeroBrix Sovereign Thought Engine — Specification (v1.0)

This is the **internal brain** of OmniVeroBrix: it plans, reflects, and reasons—but its thoughts are never shown directly to the user. It exists to support the Mission Router, Assistant Core, Harvester, Corpus Layer, and Remittance Engine.

---

## 1. Purpose
**Goal:** Provide structured, hidden reasoning for:
- multi‑step missions
- ambiguous requests
- missing‑information detection
- “what’s next?” questions
- autonomy loop execution

It does **not** give legal advice; it only structures thinking and mission flow.

---

## 2. Core Responsibilities
- **Mission decomposition:** Break high‑level missions into sub‑missions and atomic steps.
- **Hypothesis generation:** Propose possible interpretations, timelines, or next actions with confidence scores.
- **Requirement detection:** Identify missing documents, fields, evidence, or clarifications.
- **Reflection:** Review previous steps, detect contradictions, refine outputs.
- **Stop conditions:** Decide when a mission is complete, blocked, or requires user input.

---

## 3. Internal Data Structures

### 3.1 Thought Ledger (Internal Only)
```json
{
  "ledger_id": "UUIDv4",
  "mission_id": "UUIDv4",
  "entries": [
    {
      "entry_id": "UUIDv4",
      "timestamp": "ISO8601",
      "type": "observation | hypothesis | plan | reflection | decision",
      "content": "string",
      "metadata": {
        "confidence": "number",
        "related_entities": ["string"],
        "related_steps": ["UUIDv4"]
      }
    }
  ]
}
```

### 3.2 Plan Object
```json
{
  "plan_id": "UUIDv4",
  "mission_id": "UUIDv4",
  "steps": [
    {
      "step_id": "UUIDv4",
      "description": "string",
      "subsystem": "assistant | harvester | corpus | remittance | documents",
      "status": "pending | running | complete | blocked",
      "dependencies": ["UUIDv4"]
    }
  ]
}
```

### 3.3 Hypothesis Object
```json
{
  "hypothesis_id": "UUIDv4",
  "mission_id": "UUIDv4",
  "statement": "string",
  "confidence": "number",
  "supporting_evidence": ["string"],
  "missing_evidence": ["string"]
}
```

---

## 4. Functional Modules
- **Observation module:** Ingests mission state, harvested data, corpus mappings, and user input.
- **Planning module:** Generates ordered steps to achieve the mission goal.
- **Hypothesis module:** Suggests interpretations, timelines, or next actions.
- **Reflection module:** Reviews completed steps, checks consistency, and adjusts plan.
- **Decision module:** Signals to the Mission Router:
  - mission complete
  - mission blocked (needs user)
  - mission can continue

---

## 5. Autonomy Loop Integration
The Sovereign Thought Engine powers the autonomy loop:
1. **Plan:** Build a stepwise plan from mission + harvested data.
2. **Act:** Trigger subsystems (via Mission Router) to execute steps.
3. **Observe:** Record results into the Thought Ledger.
4. **Reflect:** Adjust hypotheses, detect contradictions, refine plan.
5. **Stop:** Signal completion or need for user input.

**Stop conditions:**
- All required steps complete
- No further meaningful actions exist
- Critical information missing and cannot be inferred
- User clarification required

---

## 6. API (Internal Only)
- `analyze_mission(mission)` → plan, hypotheses, requirements
- `update_with_result(mission, step_result)` → new observations, reflections
- `get_next_steps(mission)` → ordered list of steps
- `should_stop(mission)` → boolean + reason
- `summarize_internal_state(mission)` → compact summary for Assistant Core

None of this is exposed directly to the user; the Assistant Core translates it into calm, procedural explanations.

---

## 7. Safety and Tone Constraints
- Never output internal chain‑of‑thought directly.
- Only surface **summaries**, **steps**, and **requirements**.
- Always frame outputs as:
  - what is known
  - what is unknown
  - what is needed
  - what can be done procedurally
