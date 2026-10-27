"""Script to package the TripGenie AI project into clean, portable ZIP files."""

import os
import zipfile
from pathlib import Path

def package():
    root = Path(__file__).resolve().parent.parent
    zip_path = root / "TripGenie_AI_Complete_Project.zip"
    exclude_dirs = {".venv", "__pycache__", ".pytest_cache", ".git", ".idea", ".vscode"}
    exclude_files = {"TripGenie_AI_Complete_Project.zip", "raghav_project_complete.zip", "tripgenie_ai.zip"}

    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
            for f in filenames:
                if f in exclude_files or f.endswith(".pyc"):
                    continue
                p = Path(dirpath) / f
                if any(part in exclude_dirs for part in p.parts):
                    continue
                rel = p.relative_to(root)
                zf.write(p, rel)
                count += 1

    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"Successfully packaged {count} files into {zip_path.name} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    package()
