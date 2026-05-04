from __future__ import annotations

import os
from pathlib import Path


def run_doctor() -> int:
    """Print package-index related environment and config files for troubleshooting."""
    print("Dependency source doctor")
    print("------------------------")
    print("Environment variables:")
    for key in ["UV_INDEX_URL", "UV_DEFAULT_INDEX", "PIP_INDEX_URL", "PIP_EXTRA_INDEX_URL"]:
        print(f"  {key}={os.getenv(key, '<not set>')}")

    print("\nCommon config files:")
    candidates = [
        Path.home() / ".config" / "uv" / "uv.toml",
        Path.home() / ".uv" / "uv.toml",
        Path.home() / ".config" / "pip" / "pip.conf",
        Path.home() / ".pip" / "pip.conf",
        Path.home() / "Library" / "Application Support" / "pip" / "pip.conf",
    ]
    for path in candidates:
        status = "exists" if path.exists() else "missing"
        print(f"  {path}: {status}")
    return 0
