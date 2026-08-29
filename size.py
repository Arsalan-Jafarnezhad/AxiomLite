from pathlib import Path
import subprocess


def format_size(size):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:,.2f} {unit}"
        size /= 1024
    return f"{size:,.2f} PB"


root = Path(__file__).resolve().parent

try:
    files = subprocess.check_output(
        ["git", "ls-files", "-z"],
        cwd=root,
    ).split(b"\0")
except (subprocess.CalledProcessError, FileNotFoundError):
    raise SystemExit("This directory is not a Git repository or Git is not installed.")

total = 0
count = 0

for file in files:
    if not file:
        continue

    path = root / file.decode()

    if path.is_file():
        size = path.stat().st_size
        total += size
        count += 1

        # print(f"{format_size(size):>12}  {path.relative_to(root)}")

print("\n" + "=" * 60)
print(f"Tracked files : {count:,}")
print(f"Project size  : {format_size(total)}")
print(f"Project size  : {total:,} bytes")