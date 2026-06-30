# OmniVeroBrix Mission Router — Specification (v1.0)

## 🎯 Purpose
The Mission Router is the central coordinator that interprets user intent and routes tasks to the correct subsystem:
- Assistant Core
- Harvester
- Corpus Layer
- Sovereign Thought Engine
- Remittance Engine
- Document Generator
- Autonomy Loop

It transforms **unstructured user input** into **structured missions**.

---

# 🧠 1. Mission Router Responsibilities
The Mission Router must:
- Interpret user intent
- Classify the request
- Identify required subsystems
- Generate a mission object
- Request missing information
- Track mission progress
- Trigger the autonomy loop when needed
- Stop when the mission is complete

It is **not** responsible for doing the work — only for routing it.

---

# 🧩 2. Mission Types
The router must support the following mission categories:
- **Document Analysis**
- **Harvester Ingestion**
- **Corpus Mapping**
- **Timeline Extraction**
- **Remittance Interpretation**
- **Administrative Document Generation**
- **Evidence Review**
- **General Assistant Query**
- **Autonomy Loop Mission**

Each mission type maps to one or more subsystems.

---

# 🧱 3. Mission Object Schema
Every mission the router creates must follow this structure:
```json
{
  "mission_id": "UUIDv4",
  "mission_type": "string",
  "status": "pending | running | blocked | complete",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",

  "inputs": {
    "raw_user_input": "string",
    "document_id": "string | null",
    "context": "object | null",
    "parameters": "object | null"
  },

  "requirements": {
    "needs_document": "boolean",
    "needs_clarification": "boolean",
    "missing_fields": ["string"]
  },

  "assigned_to": ["assistant", "harvester", "corpus", "sovereign", "remittance", "documents"],

  "steps": [
    {
      "step_id": "UUIDv4",
      "description": "string",
      "subsystem": "string",
      "status": "pending | running | complete",
      "result": "object | null"
    }
  ],

  "result": "object | null"
}
```

---

# 🔍 4. Mission Routing Logic
The router uses a **three‑stage pipeline**:

## Stage 1 — Intent Classification
The router classifies the user request into one of the mission types.

Examples:
- “What is this document?” → **Document Analysis**
- “Scan this PDF” → **Harvester Ingestion**
- “Explain this remittance coupon” → **Remittance Interpretation**
- “Make a letter summarizing this” → **Document Generation**
- “What should I do next?” → **Autonomy Loop**

## Stage 2 — Requirement Resolution
The router checks:
- Do we have the document?
- Do we have the metadata?
- Do we have the extracted entities?
- Do we need clarification?

If something is missing, the router generates a **clarification mission**.

## Stage 3 — Subsystem Assignment
The router assigns the mission to the correct subsystem(s):
- Harvester → extraction
- Corpus → mapping
- Sovereign → reasoning
- Documents → generation
- Assistant → explanation

---

# 🧠 5. Routing Table (Core of the Router)

| Mission Type | Subsystem(s) | Description |
|--------------|--------------|-------------|
| **Document Analysis** | harvester → corpus → assistant | Extract → map → explain |
| **Harvester Ingestion** | harvester | OCR + extraction |
| **Corpus Mapping** | corpus | Statutes, definitions, rules |
| **Timeline Extraction** | harvester → sovereign | Extract dates → build timeline |
| **Remittance Interpretation** | remittance → assistant | Parse coupon → explain |
| **Document Generation** | documents | Letters, notices, summaries |
| **Evidence Review** | assistant → corpus | Summaries + procedural mapping |
| **Assistant Query** | assistant | General Q&A |
| **Autonomy Loop** | sovereign | Plan → act → observe → reflect |

---

# 🔄 6. Mission Lifecycle
A mission moves through:
1. **pending**
2. **running**
3. **blocked** (missing info)
4. **running**
5. **complete**

The router updates the mission ledger after each step.

---

# 🧠 7. Router API (Internal)
The router exposes internal functions:
- `route(user_input)`
- `create_mission(type, inputs)`
- `assign_subsystems(mission)`
- `resolve_requirements(mission)`
- `update_mission(mission, step_result)`
- `complete_mission(mission)`

These are not user‑facing — they are internal to the system.

---

# 🧭 8. Router → Sovereign Thought Engine Integration
The router triggers the Sovereign Thought Engine when:
- a mission requires multi‑step reasoning
- a mission requires planning
- a mission requires reflection
- the user asks “what next?”
- the mission is ambiguous

The Sovereign Engine returns:
- hypotheses
- missing information
- next steps
- confidence levels

The router uses these to update the mission.
