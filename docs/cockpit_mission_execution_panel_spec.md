# OmniVeroBrix Cockpit Mission Execution Panel — Specification (v1.0)

The Mission Execution Panel is the real‑time execution chamber, where the operator watches steps fire, subsystems engage, autonomy cycles advance, and results accumulate.

## 1. Mission Execution Header
Displays: mission_id, mission_type, status, autonomy_mode, current_phase, assigned subsystems.

## 2. Execution Timeline (Left Column)
Chronological list of mission events: planned/executed steps, observations, reflections, decisions. Events are color-coded and clickable for details.

## 3. Step Execution Console (Right Column)
Real-time execution view of the current step.
- **Overview:** step_id, description, status, dependencies.
- **Input:** parameters, autonomy context, harvested/corpus data.
- **Output:** structured result_json, extracted entities, generated docs.
- **Logs:** subsystem logs, warnings, errors.

## 4. Subsystem Activity Monitor (Center-Bottom)
Live visualization of subsystem activity (Assistant Core, Harvester, Corpus Engine, Remittance, Sovereign Engine, Autonomy Loop, Document Generator). Shows status, latency, queue length.

## 5. Output & Results Viewer (Bottom Panel)
Shows all outputs generated during execution: Generated Documents, Updated Corpus Mappings, Updated Remedy Maps, Updated Remittance Interpretations, Updated Mission Status.

## 6. Action Bar (Bottom)
Buttons: Run Mission, Step Mission, Pause, Resume, Stop, Restart.

## 7. API Endpoints
- `/api/missions/{id}`
- `/api/missions/{id}/steps`
- `/api/missions/{id}/run` (and step, pause, resume, stop)
- `/api/missions/{id}/results`
- `/api/autonomy/{mission_id}/state`
