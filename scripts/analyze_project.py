import ast
import os
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
import importlib.util
import re

def is_module_available(module_name):
    if module_name in sys.builtin_module_names:
        return True
    try:
        spec = importlib.util.find_spec(module_name.split('.')[0])
        return spec is not None
    except Exception:
        return False

project_root = os.getcwd()
python_files = []

for root, dirs, files in os.walk(project_root):
    if 'venv' in root or '.venv' in root or '__pycache__' in root or 'egg-info' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            python_files.append(os.path.join(root, file))

missing_imports = {}
hardcoded_paths = []
all_imports = set()

path_pattern = re.compile(r'^[a-zA-Z]:\\|^/usr/|^/etc/|\.json$|\.txt$|\.csv$|\.py$|\.log$|copilot_')

for filepath in python_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        rel_path = os.path.relpath(filepath, project_root)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    all_imports.add((alias.name, rel_path))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    if node.level == 0:
                        all_imports.add((node.module, rel_path))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                # avoid matching short random strings
                if len(val) > 4 and path_pattern.search(val):
                    hardcoded_paths.append((val, rel_path, node.lineno))
                    
    except Exception as e:
        print(f"Error parsing {os.path.relpath(filepath, project_root)}: {e}")

print("=== Missing / Unresolvable Imports ===")
for module_name, filepath in sorted(all_imports):
    base_module = module_name.split('.')[0]
    local_path_py = os.path.join(project_root, base_module + ".py")
    local_path_dir = os.path.join(project_root, base_module)
    
    if not os.path.exists(local_path_py) and not os.path.isdir(local_path_dir):
        if not is_module_available(base_module):
            print(f"- '{module_name}' imported in {filepath}")

print("\n=== Hardcoded Paths ===")
for path, filepath, line in sorted(hardcoded_paths, key=lambda x: (x[1], x[2])):
    print(f"- {filepath}:{line} -> '{path}'")
