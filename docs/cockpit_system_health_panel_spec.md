# OmniVeroBrix Cockpit System Health Panel — Specification (v1.0)

The System Health Panel is the cockpit’s diagnostic core, unifying subsystem performance, resource usage, event streams, errors, and operational telemetry into a single dashboard.

## 1. System Health Header
Displays system_status, uptime, active missions, autonomy cycles, last error, restart count. Links to Operator Console, Autonomy Monitor.

## 2. Subsystem Status Grid
Monitors all major subsystems: Assistant Core, Harvester, Corpus Engine, Remittance Engine, Sovereign Engine, Autonomy Loop, Document Generator, Server, DB, Ingestion Pipeline.
Shows status, latency, queue length, last action, error, restart count, version.

## 3. Resource Monitor
- **CPU:** total, per-subsystem, historical graph.
- **Memory:** total, per-subsystem, garbage collection.
- **Disk:** database size, logs size, cache.
- **Database Health:** table counts, fragmentation, latency.

## 4. Event Stream & Alerts
- **System Events:** new missions, documents, corpus entries, autonomy decisions.
- **Alerts:** categorized by critical/warning/info. Shows timestamp, severity, message, recommended action.

## 5. Action Bar (Bottom)
Buttons: Restart Subsystem, Clear Alerts, Run Diagnostics, Export Health Report, Open Logs.

## 6. API Endpoints
- `/api/system/health`
- `/api/system/subsystems`
- `/api/system/resources`
- `/api/system/events`
- `/api/system/alerts`
- `/api/system/restart/{subsystem}`
- `/api/system/logs/{subsystem}`
