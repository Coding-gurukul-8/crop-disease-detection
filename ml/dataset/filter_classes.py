#!/usr/bin/env python3
"""Copy the 8 target PlantVillage classes from ``raw/`` into ``filtered/``.

Usage (paths are resolved relative to this file, so run from anywhere)::

    python ml/dataset/filter_classes.py

This script is the scope boundary between "everything Kaggle gives us" and
"what we actually train on": the project deliberately covers a defined set of
crops and diseases rather than claiming to detect every crop disease.

Behaviour
---------
* Reads only from ``ml/dataset/raw/`` (populated by ``download_dataset.py``).
  ``raw/`` is never modified or deleted: files are *copied*, never moved.
* Writes ``filtered/<class>/<same filenames>``. Filenames are preserved.
* A missing class folder in ``raw/`` is skipped with a warning (no crash).
* Idempotent: a destination file that already exists with the same size is
  left alone; a missing or different-size one is (re)copied. Copies go to a
  temporary name first and are renamed into place, so an interrupted run never
  leaves a corrupted image behind. Running twice gives an identical result.
* Exit code: 0 if at least one class was copied and none were skipped,
  1 otherwise (so CI / scripts can notice an incomplete dataset).
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATASET_DIR = Path(__file__).resolve().parent
RAW_DIR = DATASET_DIR / "raw"
FILTERED_DIR = DATASET_DIR / "filtered"

# The exact 8 target classes. These are the names used in ``filtered/`` and by
# everything downstream (splitting, training, class_names.json, the backend).
TARGET_CLASSES: list[str] = [
    "Tomato___healthy",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Potato___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    # Actual downloaded dataset uses "Pepper,_bell___" instead of "Pepper__bell___".
    "Pepper,_bell___healthy",
    "Pepper,_bell___Bacterial_spot",
]

# NAMING MISMATCH NOTE
# --------------------
# Folder naming differs between PlantVillage mirrors. The Kaggle dataset used by
# download_dataset.py (arjuntejaswi/plant-village) names the Potato and Pepper
# folders exactly as above, but, to the best of our knowledge, its Tomato
# folders use a SINGLE underscore (``Tomato_healthy``, ``Tomato_Early_blight``,
# ``Tomato_Late_blight``). Because ``raw/`` was not available when this was
# written, the names could not be verified against the real download. Rather than
# fail, each target may list alternative raw spellings below; the first one that
# exists in ``raw/`` is used, and the class is always written to ``filtered/``
# under its canonical TARGET_CLASSES name. If the script reports a class as
# skipped, compare ``ls ml/dataset/raw`` with this table and add the real name.
RAW_ALIASES: dict[str, list[str]] = {
    "Tomato___healthy": ["Tomato_healthy"],
    "Tomato___Early_blight": ["Tomato_Early_blight"],
    "Tomato___Late_blight": ["Tomato_Late_blight"],
    "Pepper__bell___healthy": ["Pepper_bell___healthy", "Pepper___bell___healthy"],
    "Pepper__bell___Bacterial_spot": ["Pepper_bell___Bacterial_spot", "Pepper___bell___Bacterial_spot"],
}

IGNORED_NAMES = {".gitkeep", ".DS_Store", "Thumbs.db", "__MACOSX"}
TMP_SUFFIX = ".part"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _files_in(folder: Path) -> list[Path]:
    """Regular files directly in ``folder``, ignoring OS noise and temp files."""
    return sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.name not in IGNORED_NAMES
        and not p.name.startswith(".") and not p.name.endswith(TMP_SUFFIX)
    )


def _resolve_source(class_name: str) -> Path | None:
    """Find the raw folder for a target class (canonical name first, then aliases)."""
    for candidate in [class_name, *RAW_ALIASES.get(class_name, [])]:
        path = RAW_DIR / candidate
        if path.is_dir():
            return path
    return None


def _copy_file(src: Path, dst: Path) -> bool:
    """Copy ``src`` to ``dst`` unless an identical-size file is already there.

    Returns True if a copy happened, False if it was skipped.
    """
    if dst.is_file() and dst.stat().st_size == src.stat().st_size:
        return False
    tmp = dst.with_name(dst.name + TMP_SUFFIX)
    try:
        shutil.copy2(src, tmp)
        os.replace(tmp, dst)  # atomic on the same filesystem
    finally:
        if tmp.exists():
            tmp.unlink()
    return True


def filter_classes() -> int:
    if not RAW_DIR.is_dir():
        print(f"ERROR: {RAW_DIR} does not exist. Run download_dataset.py first.", file=sys.stderr)
        return 1

    FILTERED_DIR.mkdir(parents=True, exist_ok=True)

    copied_classes: dict[str, int] = {}
    skipped: list[str] = []
    files_written = files_unchanged = 0

    for class_name in TARGET_CLASSES:
        src_dir = _resolve_source(class_name)
        if src_dir is None:
            print(f"WARNING: class folder '{class_name}' not found in {RAW_DIR}; skipping.", file=sys.stderr)
            skipped.append(class_name)
            continue
        if src_dir.name != class_name:
            print(f"NOTE: using raw folder '{src_dir.name}' for target class '{class_name}'.")

        images = _files_in(src_dir)
        if not images:
            print(f"WARNING: '{src_dir.name}' contains no files; skipping.", file=sys.stderr)
            skipped.append(class_name)
            continue

        dst_dir = FILTERED_DIR / class_name
        dst_dir.mkdir(parents=True, exist_ok=True)
        for img in images:
            if _copy_file(img, dst_dir / img.name):
                files_written += 1
            else:
                files_unchanged += 1
        copied_classes[class_name] = len(images)
        print(f"  {class_name:<32} {len(images):>6} images")

    total = sum(copied_classes.values())
    print("\n=== Summary ===")
    print(f"Classes copied : {len(copied_classes)} / {len(TARGET_CLASSES)}")
    print(f"Images total   : {total} ({files_written} written, {files_unchanged} already up to date)")
    print(f"Classes skipped: {', '.join(skipped) if skipped else 'none'}")
    return 0 if copied_classes and not skipped else 1


if __name__ == "__main__":
    sys.exit(filter_classes())