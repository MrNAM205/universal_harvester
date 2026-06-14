# universal_harvester/utils/logger.py

import datetime

def log(msg: str):
    """
    Simple timestamped logger for debugging and tracing.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[HARVESTER] {timestamp} — {msg}")


def log_section(title: str):
    """
    Prints a section header for readability.
    """
    print("\n" + "=" * 60)
    print(f"=== {title}")
    print("=" * 60 + "\n")
