import os
import shutil

ROOT = os.path.abspath(os.path.dirname(__file__))
PKG = os.path.join(ROOT, "universal_harvester")
INNER_AGENT = os.path.join(PKG, "agent")
INNER_UTILS = os.path.join(PKG, "utils")
ROOT_SCRIPTS = os.path.join(ROOT, "scripts")
INNER_SCRIPTS = os.path.join(PKG, "scripts")

REQUIRED_INIT_PATHS = [
    PKG,
    INNER_AGENT,
    INNER_UTILS,
    ROOT_SCRIPTS,
]


def ensure_init_files():
    print("\n[+] Checking __init__.py files...")
    for path in REQUIRED_INIT_PATHS:
        init_file = os.path.join(path, "__init__.py")
        if not os.path.exists(init_file):
            print(f"    - Creating missing {init_file}")
            open(init_file, "w").close()
        else:
            print(f"    - OK: {init_file} exists")


def fix_scripts_location():
    print("\n[+] Checking scripts folder location...")

    if os.path.exists(INNER_SCRIPTS):
        print(f"    - Found misplaced scripts folder at {INNER_SCRIPTS}")
        print(f"    - Moving it to {ROOT_SCRIPTS}")

        if not os.path.exists(ROOT_SCRIPTS):
            os.makedirs(ROOT_SCRIPTS)

        for item in os.listdir(INNER_SCRIPTS):
            src = os.path.join(INNER_SCRIPTS, item)
            dst = os.path.join(ROOT_SCRIPTS, item)
            print(f"        Moving {src} -> {dst}")
            shutil.move(src, dst)

        shutil.rmtree(INNER_SCRIPTS)
        print("    - Cleanup complete.")
    else:
        print("    - scripts folder is already in the correct location.")


def ensure_package_structure():
    print("\n[+] Checking package structure...")

    if not os.path.exists(PKG):
        print(f"    - ERROR: Missing inner package folder: {PKG}")
        print("    - Creating it now.")
        os.makedirs(PKG)

    if not os.path.exists(INNER_AGENT):
        print(f"    - ERROR: Missing agent folder: {INNER_AGENT}")
        print("    - Creating it now.")
        os.makedirs(INNER_AGENT)

    if not os.path.exists(INNER_UTILS):
        print(f"    - ERROR: Missing utils folder: {INNER_UTILS}")
        print("    - Creating it now.")
        os.makedirs(INNER_UTILS)

    print("    - Package structure OK.")


def main():
    print("\n========================================")
    print(" UNIVERSAL HARVESTER — STRUCTURE REPAIR ")
    print("========================================")

    ensure_package_structure()
    fix_scripts_location()
    ensure_init_files()

    print("\n[OK] Repair complete.")
    print("[OK] Your project structure is now valid.")
    print("[OK] You may now run: python -m scripts.run_harvest <url>\n")


if __name__ == "__main__":
    main()
