"""
Deployment Bundle Exporter for DeadlockGuard.
Creates a clean, production-ready zip archive containing all source files,
models, configurations, and deployment descriptors, ready for GitHub or cloud upload.
"""

import os
import zipfile
from pathlib import Path


EXCLUDE_PATTERNS = {
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".venv",
    "venv",
    ".DS_Store",
    "Thumbs.db",
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".zip",
    ".tar.gz",
}


def build_deployment_bundle(output_zip: str = "deadlockguard_deployable.zip") -> str:
    root_dir = Path(__file__).resolve().parent
    out_path = root_dir / output_zip

    file_count = 0
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in root_dir.rglob("*"):
            if file_path.is_dir():
                continue

            rel_path = file_path.relative_to(root_dir)
            parts = rel_path.parts

            # Check exclusions
            if any(p in EXCLUDE_PATTERNS for p in parts):
                continue
            if file_path.suffix.lower() in EXCLUDE_EXTENSIONS:
                continue

            zf.write(file_path, arcname=str(rel_path))
            file_count += 1

    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"Deployment bundle created successfully: {output_zip}")
    print(f"Total files included: {file_count}")
    print(f"Archive size: {size_mb:.2f} MB")
    return str(out_path)


if __name__ == "__main__":
    build_deployment_bundle()
