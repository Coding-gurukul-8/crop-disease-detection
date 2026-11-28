#!/usr/bin/env python3
"""Detect corrupted and duplicate images in ``ml/dataset/filtered/``.

Usage (paths are resolved relative to this file, so run from anywhere)::

    python ml/dataset/validate_images.py

Run it AFTER ``filter_classes.py`` (Prompt 9) and BEFORE splitting (Prompt 13).

What it checks
--------------
* Corruption: every file is opened with ``PIL.Image.open(path).verify()``.
  ``verify()`` alone can miss truncated JPEGs (it checks structure, not the
  pixel data), so each file is also re-opened and fully decoded with
  ``load()``, which is what ``tf.data`` will effectively do later. Any file
  that raises in either step is listed as corrupted.
* Duplicates: an MD5 hash of each file's raw bytes. Files sharing a hash are
  byte-identical; every group with 2+ files is reported, including copies that
  sit in different class folders (these would leak data across train/val/test).

Output
------
* ``ml/dataset/validation_report.json`` with keys ``total_images_scanned``,
  ``corrupted_files``, ``duplicate_groups`` and ``duplicate_file_count``
  (number of files that are redundant copies, i.e. each group's size minus one).
* A short human-readable summary on stdout (counts only).

This script is READ-ONLY with respect to ``filtered/``: it never modifies,
moves or deletes images. Deciding what to remove is a manual, reviewed step.

Exit code: 0 when the scan completes (even if problems were found, since the
report is the product); 1 if ``filtered/`` is missing or empty.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image

DATASET_DIR = Path(__file__).resolve().parent
FILTERED_DIR = DATASET_DIR / "filtered"
REPORT_PATH = DATASET_DIR / "validation_report.json"

IGNORED_NAMES = {".gitkeep", ".DS_Store", "Thumbs.db"}
CHUNK_SIZE = 1024 * 1024  # 1 MiB


def _iter_files(root: Path):
    """Yield every regular file under ``root`` (sorted, ignoring placeholders)."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            if name in IGNORED_NAMES or name.startswith("."):
                continue
            yield Path(dirpath) / name


def _is_corrupted(path: Path) -> bool:
    """True if PIL cannot verify AND fully decode the file."""
    try:
        with Image.open(path) as img:
            img.verify()  # structural check; invalidates ``img`` afterwards
        with Image.open(path) as img:
            img.load()  # full decode catches truncated pixel data
        return False
    except Exception:  # noqa: BLE001 - any failure means the file is unusable
        return True


def _md5(path: Path) -> str:
    digest = hashlib.md5()  # noqa: S324 - used for dedup, not security
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate() -> int:
    if not FILTERED_DIR.is_dir():
        print(f"ERROR: {FILTERED_DIR} does not exist. Run filter_classes.py first.", file=sys.stderr)
        return 1

    total = 0
    corrupted: list[str] = []
    by_hash: dict[str, list[str]] = defaultdict(list)
    unreadable: list[str] = []

    print("Starting image validation. Please wait...", flush=True)

    for path in _iter_files(FILTERED_DIR):
        total += 1
        full = str(path.resolve())

        if total % 100 == 0:
            print(f"Scanned {total} images...", flush=True)
        if _is_corrupted(path):
            corrupted.append(full)
        try:
            by_hash[_md5(path)].append(full)
        except OSError:
            unreadable.append(full)
            if full not in corrupted:
                corrupted.append(full)

    if total == 0:
        print(f"ERROR: no files found under {FILTERED_DIR}. Run filter_classes.py first.", file=sys.stderr)
        return 1

    duplicate_groups = [sorted(paths) for paths in by_hash.values() if len(paths) > 1]
    duplicate_groups.sort(key=lambda g: g[0])
    duplicate_file_count = sum(len(g) - 1 for g in duplicate_groups)

    report = {
        "total_images_scanned": total,
        "corrupted_files": sorted(corrupted),
        "duplicate_groups": duplicate_groups,
        "duplicate_file_count": duplicate_file_count,
    }
    tmp = REPORT_PATH.with_name(REPORT_PATH.name + ".part")
    tmp.write_text(json.dumps(report, indent=2), encoding="utf-8")
    os.replace(tmp, REPORT_PATH)

    cross_class = sum(1 for g in duplicate_groups if len({Path(p).parent.name for p in g}) > 1)
    print("=== Validation summary ===")
    print(f"Images scanned        : {total}")
    print(f"Corrupted files       : {len(corrupted)}")
    print(f"Duplicate groups      : {len(duplicate_groups)} ({cross_class} span multiple classes)")
    print(f"Redundant copies      : {duplicate_file_count}")
    print(f"Report written to     : {REPORT_PATH}")
    if corrupted or duplicate_groups:
        print("Review the report and decide manually what to remove; nothing was deleted.")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
