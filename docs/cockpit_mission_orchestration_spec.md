# OmniVeroBrix Cockpit Mission Orchestration — Specification (v1.0)

Mission Orchestration is the global coordination layer that manages mission lifecycle, dependencies, scheduling, routing, autonomy integration, and safety.

## 1. Mission Lifecycle Manager
Manages states: created, validated, planned, running, paused, blocked, awaiting_input, completed, archived. Triggered by operator, subsystems, autonomy.

## 2. Mission Dependency Engine
Manages relationships (document/corpus/remittance/mission/timeline-dependent). Resolves dependencies automatically or schedules appropriately.

## 3. Mission Scheduler
Determines when missions run. Modes: manual, step-by-step, auto-run, priority-based, dependency-based, batch.

## 4. Subsystem Routing Matrix
Determines which subsystem handles each step based on mission/step type, requirements, availability, health.

## 5. Autonomy Loop Integrator
Connects missions to the autonomy loop (full, guided, manual, hybrid). Plans, acts, observes, reflects, decides.

## 6. Mission Safety & Escalation Engine
Ensures safety boundaries (no external/irreversible actions, no unbounded loops). Handles escalations (operator intervention, subsystem failure).

## 7. Action Bar (Bottom)
Buttons: Run All, Pause All, Resume All, Stop All, Rebuild Plans, Recalculate Dependencies.

## 8. API Endpoints
- `/api/orchestration/lifecycle`
- `/api/orchestration/dependencies`
- `/api/orchestration/scheduler`
- `/api/orchestration/routing`
- `/api/orchestration/autonomy`
- `/api/orchestration/safety`
- `/api/orchestration/global_controls`
