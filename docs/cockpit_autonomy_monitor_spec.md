# OmniVeroBrix Cockpit Autonomy Monitor — Specification (v1.0)

The Autonomy Monitor is the cockpit’s neural activity display, showing the autonomy loop’s phases, decisions, reflections, and progress in real time.

## 1. Panel Layout (High‑Level)
Built around the 5‑phase loop: Plan, Act, Observe, Reflect, Decide.
Features a Phase Wheel, Phase Details, Ledger Stream, Step Progress, and Controls.

## 2. Autonomy Header
Displays: mission_id, autonomy_status, current_phase, stop condition. Source: `missions`, `plans`, `thought_ledger`.

## 3. Phase Wheel (Center)
Circular visualization of the loop. Transitions animate. Shows phase name, timestamp, confidence, number of steps involved.

## 4. Phase Details (Right Column)
- **Plan Phase:** planned steps, dependencies, hypotheses.
- **Act Phase:** active step, subsystem, execution status.
- **Observe Phase:** new observations, updated mappings.
- **Reflect Phase:** reflection summary, contradictions, plan adjustments.
- **Decide Phase:** stop condition, reason, next action.

## 5. Step Progress (Left Column)
Shows execution trace of the autonomy loop. Pending, running, complete, blocked steps.

## 6. Ledger Stream (Bottom Panel)
Chronological stream of autonomy events: plan entries, observations, reflections, decisions. Source: `thought_ledger`.

## 7. Controls (Bottom Bar)
Buttons: Run Autonomy Loop, Step Once, Pause, Resume, Stop.

## 8. API Endpoints
- `/api/autonomy/{mission_id}/state`
- `/api/autonomy/{mission_id}/run`
- `/api/autonomy/{mission_id}/step`
- `/api/autonomy/{mission_id}/pause`
- `/api/autonomy/{mission_id}/resume`
- `/api/autonomy/{mission_id}/stop`
- `/api/missions/{id}/steps`
- `/api/missions/{id}/ledger`
- `/api/plans/{mission_id}`
