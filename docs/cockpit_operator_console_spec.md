# OmniVeroBrix Cockpit Operator Console — Specification (v1.0)

The Operator Console is the master interface that ties all cockpit panels together into a single sovereign‑grade command environment.

## 1. Global Header
Provides System Identity, Global Search (across all intelligence), and Quick Actions (New Mission, Open Panels, Run Loop).

## 2. Left Navigation Sidebar
Global navigation across all cockpit panels.
Features Mission Quick-Select and Document Quick-Select.

## 3. Main Workspace (Dynamic Panel Area)
Dynamically loads any cockpit panel with smooth transitions.
- **Multi‑Panel Mode:** Vertical, horizontal, or quad-grid splits.
- **Panel Linking:** Selecting an entity in one panel updates others.

## 4. System Status Bar (Bottom)
Persistent bar showing real-time health.
- **Subsystem Indicators:** Status, latency, last error.
- **Resource Metrics:** CPU, memory, disk, DB size.
- **Event Stream:** Live ticker of new missions, documents, autonomy decisions.

## 5. Operator Tools Drawer
Slide-out drawer containing operator utilities: JSON Inspector, Database Browser, Entity Explorer, Citation Finder, Pattern Analyzer, Timeline Scrubber, Debugger, Simulator. Advanced Dev Mode available.

## 6. API Endpoints
- `/api/dashboard`
- `/api/search`
- `/api/missions/list`
- `/api/documents/list`
- `/api/corpus/list`
- `/api/remittance/list`
- `/api/autonomy/state`
- `/api/system/health`
- `/api/system/events`
