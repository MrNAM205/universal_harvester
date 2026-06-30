# OmniVeroBrix Package Layout (v1.0)
*(This is the full Python package structure.)*

```text
omniverobrix/
│
├── __init__.py
│
├── assistant/
│   ├── __init__.py
│   ├── core.py
│   ├── mission_router.py
│   ├── procedural_reasoner.py
│   ├── output_formatter.py
│   └── state_manager.py
│
├── harvester/
│   ├── __init__.py
│   ├── ui_harvester.py
│   ├── hybrid_message_extractor.py
│   ├── entity_extractor.py
│   ├── document_classifier.py
│   ├── ocr_engine.py
│   ├── normalizer.py
│   └── schemas/
│       ├── __init__.py
│       └── harvested_document.json
│
├── corpus/
│   ├── __init__.py
│   ├── corpus_engine.py
│   ├── remedy_mapper.py
│   ├── definition_explainer.py
│   ├── process_mapper.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── cfr_loader.py
│   │   ├── usc_loader.py
│   │   ├── ucc_loader.py
│   │   ├── irm_loader.py
│   │   ├── archive_loader.py
│   │   ├── citation_parser.py
│   │   ├── section_parser.py
│   │   ├── title_parser.py
│   │   ├── tagger.py
│   │   ├── normalizer.py
│   │   └── linker.py
│   └── schemas/
│       ├── __init__.py
│       └── corpus_entry.json
│
├── sovereign/
│   ├── __init__.py
│   ├── planner.py
│   ├── reflection.py
│   ├── hypothesis_engine.py
│   ├── thought_ledger.py
│   └── autonomy_loop.py
│
├── remittance/
│   ├── __init__.py
│   ├── coupon_scanner.py
│   ├── instrument_identifier.py
│   ├── routing_extractor.py
│   ├── endorsement_templates.py
│   └── schemas/
│       ├── __init__.py
│       └── remittance_coupon.json
│
├── documents/
│   ├── __init__.py
│   ├── generator.py
│   ├── renderers/
│   │   ├── __init__.py
│   │   ├── text_renderer.py
│   │   └── html_renderer.py
│   └── templates/
│       ├── __init__.py
│       ├── letters/
│       ├── notices/
│       ├── timelines/
│       └── affidavits/
│
├── cockpit/
│   ├── __init__.py
│   ├── server.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── missions.py
│   │   ├── evidence.py
│   │   ├── documents.py
│   │   └── health.py
│   ├── static/
│   └── index.html
│
├── database/
│   ├── __init__.py
│   ├── omniverobrix.db
│   ├── migrations/
│   └── schema.sql
│
├── scripts/
│   ├── __init__.py
│   ├── analyze_project.py
│   ├── generate_embeddings.py
│   ├── ingest_json_to_db.py
│   ├── validate_modules.py
│   └── (all your existing utility scripts)
│
├── tests/
│   ├── __init__.py
│   ├── test_merge_engine.py
│   ├── test_harvester.py
│   ├── test_corpus.py
│   ├── test_remittance.py
│   └── test_autonomy_loop.py
│
├── run_pipeline.py
├── README.md
└── pyproject.toml
```

## 🔥 Why this layout works

### ✔ Modular
Each subsystem is isolated and testable.

### ✔ Extensible
You can add new loaders, templates, renderers, or engines without breaking anything.

### ✔ Sovereign‑grade
The Corpus + Sovereign layers sit at the center, feeding intelligence to the Assistant and Cockpit.

### ✔ Compatible with your existing Universal Harvester
Your current scripts and dashboard drop directly into this structure.

### ✔ Ready for autonomy
The autonomy loop has a clean home and clear integration points.
