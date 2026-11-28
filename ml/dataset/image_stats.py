#!/usr/bin/env python3
"""Report image dimension statistics (width x height) per class.

Usage (paths are resolved relative to this file, so run from anywhere)::

    python ml/dataset/image_stats.py

Run it after ``filter_classes.py`` (Prompt 9). It is read-only with respect to
``ml/dataset/filtered/``.

Why this matters
----------------
The preprocessing pipeline (Prompt 16) resizes every image to 224x224. If most
images are larger than that, the resize is a harmless downscale. If many are
smaller, they get upscaled, which degrades quality and should be mentioned in
the report's limitations section. The ``below_224_count`` column counts images
where width OR height is under 224, to make that visible.

Output
------
* A pandas DataFrame printed to stdout and saved to
  ``ml/dataset/image_dimension_stats.csv``: one row per class plus one
  aggregate row named ``ALL``. Columns: class, num_images, min/max/mean width,
  min/max/mean height, below_224_count, skipped_unreadable.
* Files PIL cannot open are skipped and counted (never a crash); they should
  already have been listed by ``validate_images.py`` (Prompt 10).

Sanity check
------------
PlantVillage images are normally 256x256, so every min/max/mean here should be
about 256. If the numbers are wildly different (for example a mean far from 256,
or a large ``below_224_count``), suspect a data issue: a wrong dataset slug, a
different PlantVillage variant (segmented/grayscale versions differ), or stray
non-leaf images. Investigate before training.

Exit code: 0 on success, 1 if ``filtered/`` is missing or has no readable images.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
from PIL import Image

DATASET_DIR = Path(__file__).resolve().parent
FILTERED_DIR = DATASET_DIR / "filtered"
OUTPUT_CSV = DATASET_DIR / "image_dimension_stats.csv"

MODEL_INPUT_SIZE = 224  # Prompt 16 resize target
IGNORED_NAMES = {".gitkeep", ".DS_Store", "Thumbs.db"}
COLUMNS = [
    "class", "num_images",
    "min_width", "max_width", "mean_width",
    "min_height", "max_height", "mean_height",
    "below_224_count", "skipped_unreadable",
]


def _class_dirs(root: Path) -> list[Path]:
    return sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))


def _files_in(folder: Path):
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames.sort()
        for name in sorted(filenames):
            if name in IGNORED_NAMES or name.startswith("."):
                continue
            yield Path(dirpath) / name


def _read_size(path: Path) -> tuple[int, int] | None:
    """Return (width, height), or None if PIL cannot open the file."""
    try:
        with Image.open(path) as img:
            return img.size
    except Exception:  # noqa: BLE001 - unreadable files are skipped, not fatal
        return None


def _row(label: str, sizes: list[tuple[int, int]], skipped: int) -> dict:
    if not sizes:
        return {c: float("nan") for c in COLUMNS} | {
            "class": label, "num_images": 0, "below_224_count": 0, "skipped_unreadable": skipped}
    widths = pd.Series([w for w, _ in sizes])
    heights = pd.Series([h for _, h in sizes])
    below = sum(1 for w, h in sizes if w < MODEL_INPUT_SIZE or h < MODEL_INPUT_SIZE)
    return {
        "class": label,
        "num_images": len(sizes),
        "min_width": int(widths.min()), "max_width": int(widths.max()), "mean_width": round(float(widths.mean()), 2),
        "min_height": int(heights.min()), "max_height": int(heights.max()), "mean_height": round(float(heights.mean()), 2),
        "below_224_count": below,
        "skipped_unreadable": skipped,
    }


def main() -> int:
    if not FILTERED_DIR.is_dir():
        print(f"ERROR: {FILTERED_DIR} does not exist. Run filter_classes.py first.", file=sys.stderr)
        return 1
    classes = _class_dirs(FILTERED_DIR)
    if not classes:
        print(f"ERROR: no class folders in {FILTERED_DIR}. Run filter_classes.py first.", file=sys.stderr)
        return 1

    rows: list[dict] = []
    all_sizes: list[tuple[int, int]] = []
    total_skipped = 0
    for class_dir in classes:
        sizes: list[tuple[int, int]] = []
        skipped = 0
        for path in _files_in(class_dir):
            size = _read_size(path)
            if size is None:
                skipped += 1
            else:
                sizes.append(size)
        rows.append(_row(class_dir.name, sizes, skipped))
        all_sizes.extend(sizes)
        total_skipped += skipped

    if not all_sizes:
        print("ERROR: no readable images found.", file=sys.stderr)
        return 1

    rows.append(_row("ALL", all_sizes, total_skipped))
    df = pd.DataFrame(rows, columns=COLUMNS)
    df.to_csv(OUTPUT_CSV, index=False)

    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(df.to_string(index=False))
    print("\n=== Summary ===")
    print(f"Classes             : {len(classes)}")
    print(f"Images measured     : {len(all_sizes)}")
    print(f"skipped_unreadable  : {total_skipped}")
    print(f"Below {MODEL_INPUT_SIZE}px (would be upscaled): {int(df.iloc[-1]['below_224_count'])}")
    print(f"Saved to            : {OUTPUT_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())