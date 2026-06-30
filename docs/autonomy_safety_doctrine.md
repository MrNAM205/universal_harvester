# OmniVeroBrix Autonomy Safety Doctrine (v1.0)

The sovereign-grade safety charter governing all autonomous reasoning.

## 1. Phase Safety
Ensures the loop never escapes or corrupts its phases (Plan -> Act -> Observe -> Reflect -> Decide). No phase skipped or repeated without cause. Access via Autonomy Monitor.

## 2. Reflection Safety
Ensures reflections remain coherent, bounded, and non-speculative, grounded in observations. Access via Mission Execution Panel.

## 3. Decision Safety
Ensures decisions are grounded in reflections, bounded by scope, and never trigger external actions or irreversible outcomes. Access via Mission Orchestration Panel.

## 4. Dependency Safety
Ensures autonomy respects mission dependencies and never creates deadlocks. Autonomy must halt when dependencies are missing. Access via Knowledge Graph.

## 5. Temporal Safety
Ensures autonomy respects timelines and deadlines. No timeline collapse or reordering. Access via Timeline Panel.

## 6. Operator Safety
Ensures autonomy remains subordinate to the operator. Overrides and pauses are absolute. Access via Operator Console.

## Autonomy Safety Cycle
Monitor -> Detect -> Halt -> Reconcile -> Resume -> Report.

## API Endpoints
- `/api/asd/phase`
- `/api/asd/reflection`
- `/api/asd/decision`
- `/api/asd/dependency`
- `/api/asd/temporal`
- `/api/asd/operator`
- `/api/asd/audit`
