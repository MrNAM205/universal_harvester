import sys
import json
from universal_harvester.agent.autopilot import HarvesterAutopilot


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.run_autopilot <URL> [<URL2> ...]")
        sys.exit(1)

    seed_urls = sys.argv[1:]
    autopilot = HarvesterAutopilot(headed=True, max_depth=2, same_domain_only=True)
    results = autopilot.crawl(seed_urls)

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
