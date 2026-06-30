# OmniVeroBrix Sovereign Continuity Protocol (v1.0)

This protocol defines how OmniVeroBrix survives, maintaining coherence, stability, identity, memory, and operational integrity across time, missions, and sessions.

## 1. Context Continuity
Ensures global, mission, procedural, and temporal context is preserved through snapshots and reconciliation.

## 2. Mission Continuity
Ensures missions remain coherent, recoverable, and resumable across sessions through checkpoints and routing persistence.

## 3. Autonomy Continuity
Ensures the autonomy loop remains stable and bounded across cycles through phase snapshots and decision ledger persistence.

## 4. Memory Continuity
Ensures long-term memory remains stable and non-contradictory through memory graph snapshots and stale memory detection.

## 5. Procedural Continuity
Ensures procedural intelligence remains consistent through procedural map snapshots and delta reconciliation.

## 6. System Continuity
Ensures the entire cockpit remains stable across subsystem restarts and surges through heartbeat persistence and health snapshotting.

## Sovereign Continuity Cycle
Snapshot -> Validate -> Reconcile -> Persist -> Monitor -> Recover.
Snapshots must be atomic, reconciliation deterministic, and persistence durable.

## Sovereign Continuity Safety Boundaries
Continuity must never override operator intent or safety boundaries, and must always preserve coherence, stability, and operator sovereignty.

## API Endpoints
- `/api/scp/context`
- `/api/scp/mission`
- `/api/scp/autonomy`
- `/api/scp/memory`
- `/api/scp/procedural`
- `/api/scp/system`
- `/api/scp/audit`
