# health_check.py
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT / "universal_harvester"
AGENT = PACKAGE / "agent"
UTILS = PACKAGE / "utils"

REQUIRED_PYTHON = (3, 10)

REQUIRED_MODULES = [
    "playwright",
    "requests",
    "beautifulsoup4",
]

REQUIRED_AGENT = [
    "endpoint_detection.py",
    "sidebar_autoscroll.py",
    "sidebar_dom_extraction.py",
    "completeness_verification.py",
    "copilot_api.py",
    "ui_chat_scroll.py",
    "merge_engine.py",
    "copilot_scraper.py",
    "chat_enhancer.py",
    "harvester.py",
]

REQUIRED_UTILS = [
    "network_capture.py",
]


def check_python_version():
    print("\n[CHECK] Python version")
    if sys.version_info < REQUIRED_PYTHON:
        print(f"  ✖ Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+ required")
    else:
        print(f"  ✔ Python {sys.version.split()[0]}")


def check_virtual_env():
    print("\n[CHECK] Virtual environment")
    if sys.prefix != sys.base_prefix:
        print("  ✔ Virtual environment active")
    else:
        print("  ✖ Virtual environment NOT active")


def check_folders():
    print("\n[CHECK] Folder structure")
    for folder in [PACKAGE, AGENT, UTILS]:
        if folder.exists():
            print(f"  ✔ {folder}")
        else:
            print(f"  ✖ Missing folder: {folder}")


def check_agent_modules():
    print("\n[CHECK] Agent modules")
    for mod in REQUIRED_AGENT:
        path = AGENT / mod
        if path.exists():
            print(f"  ✔ {mod}")
        else:
            print(f"  ✖ Missing: {mod}")


def check_utils_modules():
    print("\n[CHECK] Utils modules")
    for mod in REQUIRED_UTILS:
        path = UTILS / mod
        if path.exists():
            print(f"  ✔ {mod}")
        else:
            print(f"  ✖ Missing: {mod}")


def check_dependencies():
    print("\n[CHECK] Python dependencies")
    installed = subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).decode().lower()

    for pkg in REQUIRED_MODULES:
        if pkg.lower() in installed:
            print(f"  ✔ {pkg}")
        else:
            print(f"  ✖ Missing: {pkg}")


def check_playwright_browsers():
    print("\n[CHECK] Playwright browser installation")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser_path = p.chromium.executable_path
            if Path(browser_path).exists():
                print("  ✔ Playwright browsers installed")
            else:
                print("  ✖ Playwright browsers missing")
    except Exception:
        print("  ✖ Playwright browsers missing")


def main():
    print("\n==============================================")
    print("  UNIVERSAL HARVESTER HEALTH CHECK")
    print("==============================================")

    check_python_version()
    check_virtual_env()
    check_folders()
    check_agent_modules()
    check_utils_modules()
    check_dependencies()
    check_playwright_browsers()

    print("\n[STATUS] Health check complete.\n")


if __name__ == "__main__":
    main()