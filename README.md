# Universal Harvester

Universal Harvester is a comprehensive pipeline for capturing, archiving, and analyzing Copilot conversations. It operates by fetching chats via API (with a browser automation fallback), parsing them, merging them into a uniform structure, extracting topic clusters, and optionally storing them for dashboard visualization.

## Architecture

1. **Endpoint Detection**: Detects valid endpoints from captured authentication logs.
2. **API Harvesting**: Uses secure HTTP requests with authenticated cookies to fetch conversation histories.
3. **UI Fallback (Playwright)**: If API harvesting fails, it falls back to a CDP-attached browser or standalone Chromium instance.
4. **Merge Engine**: Normalizes and merges API-fetched messages.
5. **Topic Aggregator & Chat Enhancer**: Uses embeddings (`scikit-learn`, `numpy`) to group chats by topic.
6. **Dashboard**: A visualization frontend to explore harvested chats and topic clusters.

## Setup

Ensure you have Python 3.10+ installed.

1. Navigate to the repository.
2. Run the unified setup script (Windows):
   ```cmd
   setup.bat
   ```
   *(This will create a `.venv`, install dependencies, and download Playwright browsers)*

## Usage

### Running the Pipeline

The primary entry point is `run_pipeline.py`.

```cmd
python run_pipeline.py
```

**Options**:
- `--export`: Specify output JSON file (default: `all_chats_verified.json`)
- `--chat-id`: Harvest a specific chat by ID.
- `--limit`: Limit the number of chats processed.

### Starting the Dashboard

```cmd
cd dashboard
python server.py
```
Navigate to `http://localhost:8000` to view the UI.
