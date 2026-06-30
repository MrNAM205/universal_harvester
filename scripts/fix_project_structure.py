# fix_project_structure.py
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT / "universal_harvester"
AGENT = PACKAGE / "agent"
UTILS = PACKAGE / "utils"

REQUIRED_DIRS = [
    PACKAGE,
    AGENT,
    UTILS,
]

REQUIRED_INIT_FILES = [
    PACKAGE / "__init__.py",
    AGENT / "__init__.py",
    UTILS / "__init__.py",
]

EXPECTED_AGENT_MODULES = [
    "endpoint_detection.py",
    "sidebar_autoscroll.py",
    "sidebar_dom_extraction.py",
    "completeness_verification.py",
    "copilot_api.py",
]

def ensure_directories():
    print("\n[CHECK] Ensuring required directories exist...")
    for d in REQUIRED_DIRS:
        if not d.exists():
            print(f"  -> Creating missing directory: {d}")
            d.mkdir(parents=True, exist_ok=True)
        else:
            print(f"  -> OK: {d}")

def ensure_init_files():
    print("\n[CHECK] Ensuring __init__.py files exist...")
    for f in REQUIRED_INIT_FILES:
        if not f.exists():
            print(f"  -> Creating missing file: {f}")
            f.write_text("# Auto-generated to fix package imports\n")
        else:
            print(f"  -> OK: {f}")

def check_agent_modules():
    print("\n[CHECK] Verifying agent modules...")
    missing = []
    for mod in EXPECTED_AGENT_MODULES:
        path = AGENT / mod
        if not path.exists():
            print(f"  -> MISSING: {mod}")
            missing.append(mod)
        else:
            print(f"  -> OK: {mod}")
    return missing

def scan_for_misplaced_modules():
    print("\n[SCAN] Searching for misplaced modules...")
    misplaced = []
    for root, dirs, files in os.walk(ROOT):
        for f in files:
            if f in EXPECTED_AGENT_MODULES:
                full = Path(root) / f
                if full.parent != AGENT:
                    misplaced.append(full)
    if misplaced:
        print("  -> Found misplaced modules:")
        for m in misplaced:
            print(f"     - {m}")
    else:
        print("  -> No misplaced modules found.")
    return misplaced

def fix_misplaced_modules(misplaced):
    print("\n[FIX] Moving misplaced modules into agent/ ...")
    for m in misplaced:
        target = AGENT / m.name
        print(f"  -> Moving {m} -> {target}")
        target.write_text(m.read_text())
        m.unlink()

def main():
    print("\n==============================================")
    print("  UNIVERSAL HARVESTER PROJECT STRUCTURE FIXER")
    print("==============================================")

    ensure_directories()
    ensure_init_files()

    missing = check_agent_modules()
    misplaced = scan_for_misplaced_modules()

    if misplaced:
        fix_misplaced_modules(misplaced)

    print("\n[SUMMARY]")
    if missing:
        print("  Missing modules still need to be created:")
        for m in missing:
            print(f"    - {m}")
    else:
        print("  All expected agent modules are present.")

    print("\n[STATUS] Project structure repair complete.\n")

if __name__ == "__main__":
    main()
