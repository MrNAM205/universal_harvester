# scripts/run_harvest.py
import json
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
import argparse
import os
from datetime import datetime
from universal_harvester.agent.harvester import UniversalHarvester
from universal_harvester.utils.exporter import export_to_markdown


def main():
    parser = argparse.ArgumentParser(description="Universal Harvester")
    parser.add_argument("url", help="Target URL to harvest")
    parser.add_argument("--profile", default=None, help="Path to your real Edge user data directory")
    parser.add_argument("--export", action="store_true", help="Export harvested Copilot chats to Markdown files")
    
    args = parser.parse_args()

    # Inject the profile for Copilot login bypassing
    harvester = UniversalHarvester(headed=True, user_data_dir=args.profile)
    result = harvester.harvest(args.url)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Trigger Markdown export if requested and applicable
    if args.export:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        if result.get("mode") == "single_chat":
            chat_id = result.get("chat_id", "unknown_chat")
            filename = f"copilot_chat_{chat_id}_{timestamp}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n[EXPORT] Wrote single chat to {os.path.abspath(filename)}")
        elif result.get("page_type") == "copilot_multi_chat":
            export_path = os.path.join(os.getcwd(), "exports")
            # Note: Chats are now stream-exported during the scrape!
            print(f"\n[SUCCESS] All chats saved to JSON and stream-exported to {export_path}")


if __name__ == "__main__":
    main()
