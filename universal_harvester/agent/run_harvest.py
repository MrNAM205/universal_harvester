# scripts/run_harvest.py
import json
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
import argparse
from universal_harvester.agent.harvester import UniversalHarvester


def main():
    parser = argparse.ArgumentParser(description="Universal Harvester")
    parser.add_argument("url", help="Target URL to harvest")
    parser.add_argument("--profile", default=None, help="Path to your real Chrome user data directory")
    
    args = parser.parse_args()

    # Inject the profile for Copilot login bypassing
    harvester = UniversalHarvester(headed=True, user_data_dir=args.profile)
    result = harvester.harvest(args.url)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
