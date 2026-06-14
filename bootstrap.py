import os
import sys
import runpy

# ---------------------------------------------------------
# 1. FORCE PYTHON TO USE THE PROJECT ROOT AS WORKING DIR
# ---------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)

# ---------------------------------------------------------
# 2. FORCE PYTHON TO IMPORT FROM THE PROJECT ROOT
# ---------------------------------------------------------
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------
# 3. DEBUG PRINT (optional)
# ---------------------------------------------------------
print("[BOOTSTRAP] Project root:", PROJECT_ROOT)
print("[BOOTSTRAP] sys.path[0]:", sys.path[0])

# ---------------------------------------------------------
# 4. RUN THE HARVESTER MODULE SAFELY
# ---------------------------------------------------------
runpy.run_module("universal_harvester.scripts.run_harvest", run_name="__main__")
