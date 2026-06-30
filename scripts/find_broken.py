import ast
import os
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

project_root = os.getcwd()
python_files = []

for root, dirs, files in os.walk(project_root):
    if 'venv' in root or '.venv' in root or '__pycache__' in root or 'egg-info' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            python_files.append(os.path.join(root, file))

local_module_names = set()
for f in python_files:
    rel = os.path.relpath(f, project_root)
    parts = os.path.normpath(rel).replace('.py', '').split(os.sep)
    local_module_names.add('.'.join(parts))
    if parts[-1] == '__init__':
        local_module_names.add('.'.join(parts[:-1]))
    # Also add top-level names for scripts in root
    if len(parts) == 1:
        local_module_names.add(parts[0])

# Also add universal_harvester submodules manually
known_packages = ['universal_harvester', 'agent', 'utils', 'scripts']

missing_internal_imports = []

for filepath in python_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        rel_path = os.path.relpath(filepath, project_root)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    base = alias.name.split('.')[0]
                    if base in known_packages or base in local_module_names or alias.name.startswith('universal_harvester'):
                        # Check if it resolves
                        parts = alias.name.split('.')
                        # If the module is not in local_module_names and we can't find it
                        # This is a naive check. Let's build a path and check if it exists
                        p1 = os.path.join(project_root, *parts) + '.py'
                        p2 = os.path.join(project_root, *parts, '__init__.py')
                        if not os.path.exists(p1) and not os.path.exists(p2):
                            missing_internal_imports.append((alias.name, rel_path, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    if node.level > 0:
                        continue # Skip relative for now
                    base = node.module.split('.')[0]
                    if base in known_packages or base in local_module_names or node.module.startswith('universal_harvester'):
                        parts = node.module.split('.')
                        p1 = os.path.join(project_root, *parts) + '.py'
                        p2 = os.path.join(project_root, *parts, '__init__.py')
                        if not os.path.exists(p1) and not os.path.exists(p2):
                            missing_internal_imports.append((node.module, rel_path, node.lineno))
                        else:
                            # Module exists, check if the imported names are valid (could be classes, functions, or submodules)
                            for alias in node.names:
                                name = alias.name
                                # skip if it's a known python thing or we can't easily parse. 
                                # But we want to find missing files. If a submodule is imported:
                                p3 = os.path.join(project_root, *parts, name) + '.py'
                                p4 = os.path.join(project_root, *parts, name, '__init__.py')
                                
                                # We need to check if 'name' is in the ast of the module, but that's too complex.
                                # Let's just flag the missing modules for now.
    except Exception as e:
        pass

print("=== Broken Internal Imports ===")
for b, f, l in missing_internal_imports:
    print(f"{f}:{l} -> {b}")
