"""Shared path setup for every notebook in ``ml/notebooks/``.

Notebooks import this instead of copy-pasting path logic. It plays the role of the
path-setup cell in ``00_colab_setup.ipynb``: find the project root, check that the
project really is there, and make it the working directory.

The project root is derived from this file's own location
(``<root>/ml/notebooks/project_setup.py``), so it works unchanged on a laptop and in
Colab (where the folder lives on the mounted Google Drive).
"""
from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

NOTEBOOKS_DIR = Path(__file__).resolve().parent


def setup_project() -> SimpleNamespace:
    """chdir to the project root and return the standard project paths."""
    project_root = NOTEBOOKS_DIR.parents[1]
    ml_dir = project_root / "ml"

    if not (ml_dir / "requirements.txt").is_file():
        raise FileNotFoundError(
            f"Missing {ml_dir / 'requirements.txt'}\n"
            "Make sure the whole project (including the ml/ folder) is present next to this notebook."
        )

    os.chdir(project_root)
    print("Working directory:", os.getcwd())
    return SimpleNamespace(
        project_root=project_root,
        ml_dir=ml_dir,
        raw_dir=ml_dir / "dataset" / "raw",
        eval_dir=ml_dir / "evaluation",
    )
