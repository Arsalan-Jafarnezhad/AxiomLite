import os

# Folders to ignore
IGNORE_DIRS = {
    ".venv", "__pycache__", ".git",".mypy_cache","node_modules",".idea", ".vscode", "env", "dist", "build", "migrations", "brand", "flag", "free", "svg", "staticfiles"
}
file = open("structure.txt", "a", encoding="utf-8")
def print_tree(start_path=".", prefix=""):
    """
    Recursively print the directory tree structure.
    """
    # Separate directories and files
    try:
        entries = sorted(os.listdir(start_path))
    except PermissionError:
        return  # Skip folders you can"t access

    entries = [e for e in entries if e not in IGNORE_DIRS]
    entries_count = len(entries)

    for index, entry in enumerate(entries):
        path = os.path.join(start_path, entry)
        connector = "└── " if index == entries_count - 1 else "├── "
        file.write(prefix + connector + entry + "\n")

        if os.path.isdir(path):
            # Add indentation depending on last element
            new_prefix = prefix + ("    " if index == entries_count - 1 else "│   ")
            print_tree(path, new_prefix)


if __name__ == "__main__":
    print("📁 Project Tree:")
    print_tree(os.getcwd())
    input()
