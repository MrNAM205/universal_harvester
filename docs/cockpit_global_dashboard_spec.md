# OmniVeroBrix Cockpit Global Dashboard — Specification (v1.0)

The Global Dashboard is the top‑level, all‑systems‑at‑a‑glance command surface that sits above every other cockpit panel.

## 1. Global Header
Displays: system_name, version, uptime, active_operator, global_status, last events.

## 2. Mission Overview (Top‑Left)
Real‑time summary of mission activity.
- Counters: active, blocked, completed, waiting.
- Activity Feed: last 10 mission events.

## 3. Evidence Intake Monitor (Top‑Center)
Ingestion radar.
- Counters: documents ingested, remittances detected, mappings created.
- Pipeline Status: harvester status, latency, queue length.

## 4. Knowledge Base Procurement Monitor (Top‑Right)
Knowledge acquisition dashboard.
- Counters: total entries, new mappings, entities added.
- Throughput: ingestion rate per hour.
- Integrity Checks: stale, conflicting, unmapped entities.

## 5. Autonomy Overview (Bottom‑Left)
Compact view of the autonomy loop’s global state.
- Counters: active cycles, reflections, decisions today.
- Current Phase Indicators: Plan, Act, Observe, Reflect, Decide.

## 6. System Health Overview (Bottom‑Center)
Condensed version of the System Health Panel.
- Subsystem Status: Assistant, Harvester, Corpus, Remittance, etc.
- Resource Summary: CPU, memory, disk, DB latency.

## 7. Operator Activity (Bottom‑Right)
Operator telemetry: recent actions, missions created, documents opened.

## 8. Action Bar (Bottom)
Global controls: Create Mission, Run Autonomy, Pause/Resume Missions.

## 9. API Endpoints
- `/api/dashboard/global`
- `/api/dashboard/missions`
- `/api/dashboard/evidence`
- `/api/dashboard/knowledge`
- `/api/dashboard/autonomy`
- `/api/dashboard/system`
- `/api/dashboard/operator`
