# OmniVeroBrix Autonomy Loop — Specification (v1.0)

This is the **self‑driving spine** of OmniVeroBrix: it takes a mission, plans steps, executes them through subsystems, watches what happens, reflects, and decides when to stop.

---

## 1. Purpose
**Goal:** Run missions semi‑autonomously while staying:
- bounded
- observable
- interruptible
- safe

It never gives legal advice or makes user decisions—only advances missions procedurally.

---

## 2. Core Cycle
The autonomy loop follows a strict 5‑phase cycle:
1. **Plan**
2. **Act**
3. **Observe**
4. **Reflect**
5. **Decide** (continue or stop)

Each cycle is logged in the `thought_ledger` and `mission_steps` tables.

---

## 3. Data Flow
- **Input:** `mission` (from Mission Router)
- **Internal state:** `plan` (from Sovereign planner), `steps` (mission_steps), `ledger` (thought_ledger)
- **Output:** updated mission, updated steps, updated ledger, optional generated documents

---

## 4. Phase Details

### 4.1 Plan
- Called via `sovereign.planner.plan(mission, harvested_document, corpus_mapping, remedy_map)`
- Produces: ordered steps, dependencies, initial hypotheses
- Writes: `plans` table, `thought_ledger` entry (type: plan)

### 4.2 Act
- For each pending step: route to correct subsystem (assistant, harvester, corpus, remittance, documents), execute step, store result in `mission_steps.result_json`
- Uses the **Mission Router** as the execution dispatcher.

### 4.3 Observe
- Collects: step results, new harvested data, new corpus mappings, new remedy maps
- Writes: `thought_ledger` entry (type: observation)

### 4.4 Reflect
- Called via `sovereign.reflection.reflect(mission, steps, observations)`
- Tasks: detect contradictions, detect missing information, adjust hypotheses, adjust plan (add/remove/reorder steps)
- Writes: `thought_ledger` entry (type: reflection), updates `plans.steps_json`

### 4.5 Decide
- Called via `sovereign.autonomy_loop.should_stop(mission, plan, steps)`
- Stop conditions:
  - **Goal achieved:** mission result is complete.
  - **No further meaningful actions:** no pending steps that add value.
  - **Blocked by missing info:** user input or external data required.
  - **Safety boundary:** mission would cross into advice or unsafe territory.
- Writes: `thought_ledger` entry (type: decision), updates `missions.status` to `complete` or `blocked`.

---

## 5. API (Internal)
Autonomy loop module exposes:
- `run(mission_id)`: Loads mission + related data. Executes full cycle until stop condition.
- `step(mission_id)`: Executes a single Plan→Act→Observe→Reflect→Decide iteration.
- `should_stop(mission, plan, steps)`: Returns `{ stop: bool, reason: str }`.

---

## 6. Safety and Boundaries
- Never runs indefinitely—always checks stop conditions.
- Never bypasses the Mission Router.
- Never surfaces internal chain‑of‑thought; only user‑facing summaries via Assistant Core.
- Always logs decisions and reflections for traceability.
