# run_batch.py
import argparse
import json
from universal_harvester.agent.batch_auto import harvest_parallel

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Text file containing chat URLs")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--export", default="batch_output.json")
    args = parser.parse_args()

    with open(args.file, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    results = harvest_parallel(urls, args.profile)

    with open(args.export, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[BATCH] Exported {len(results)} chats to {args.export}")

if __name__ == "__main__":
    main()