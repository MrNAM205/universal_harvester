# visualize_tree.py
from pathlib import Path

def print_tree(path: Path, prefix: str = ""):
    # Ignore common hidden or compiled folders
    exclude = {".git", "__pycache__", ".venv", "venv", ".idea"}
    
    items = sorted(
        [p for p in path.iterdir() if p.name not in exclude], 
        key=lambda p: (p.is_file(), p.name.lower())
    )

    for i, item in enumerate(items):
        connector = "└── " if i == len(items) - 1 else "├── "
        print(prefix + connector + item.name)

        if item.is_dir():
            extension = "    " if i == len(items) - 1 else "│   "
            print_tree(item, prefix + extension)

def main():
    root = Path(__file__).resolve().parent
    print("\nPROJECT TREE\n")
    print(root.name)
    print_tree(root)

if __name__ == "__main__":
    main()