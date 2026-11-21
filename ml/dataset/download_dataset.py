#!/usr/bin/env python3
"""Download the PlantVillage dataset from Kaggle into ``ml/dataset/raw/``.

Usage (from anywhere; paths are resolved relative to this file)::

    python ml/dataset/download_dataset.py            # download only if raw/ is empty
    python ml/dataset/download_dataset.py --force    # wipe raw/ and download again

How to get a Kaggle API token (``kaggle.json``)
-----------------------------------------------
1. Sign in (or create a free account) at https://www.kaggle.com.
2. Click your profile picture -> **Settings** -> **API** section.
3. Click **Create New Token**. Your browser downloads ``kaggle.json``.
4. Move it to the standard location:
     * macOS / Linux:  ``~/.kaggle/kaggle.json``   then ``chmod 600 ~/.kaggle/kaggle.json``
     * Windows:        ``C:\\Users\\<you>\\.kaggle\\kaggle.json``
5. Never commit this file (it is git-ignored) and never paste it into code or chat.

Design notes
------------
* Approach: the official ``kaggle`` **Python package** (``KaggleApi``), not a
  subprocess call to the CLI. This avoids depending on the ``kaggle`` executable
  being on PATH and lets us turn library errors into friendly messages.
* Credentials are read from the standard ``~/.kaggle/kaggle.json`` location.
  They are never hard-coded or taken from CLI arguments.
* The archive is downloaded and extracted into a hidden *staging* folder first.
  ``raw/`` is only touched after extraction has been verified, so a failure
  (network, disk full, bad zip, Ctrl-C) never leaves a half-populated ``raw/``.
* If the archive wraps the classes in a single parent folder (e.g.
  ``PlantVillage/``), that wrapper is removed so the result is
  ``raw/<class_name>/*.jpg``. Class folders and images are otherwise untouched.
* Exit code: 0 on success (or when skipping), 1 on any failure.
"""
from __future__ import annotations

import argparse
import errno
import json
import os
import shutil
import sys
import traceback
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Kaggle "owner/dataset" slug for the 38-class PlantVillage set. The archive has
# color, grayscale, and segmented variants; _find_class_root selects color.
# If Kaggle ever renames or removes it, change only this line.
DATASET_SLUG = "arjuntejaswi/plant-village"

DATASET_DIR = Path(__file__).resolve().parent
RAW_DIR = DATASET_DIR / "raw"
STAGING_DIR = DATASET_DIR / ".raw_staging"  # hidden + git-ignored (ml/dataset/*)
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
IGNORED_NAMES = {".gitkeep", ".DS_Store", "__MACOSX", "Thumbs.db"}


class DownloadError(Exception):
    """A failure with a message that is safe and useful to show the user."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _visible_entries(folder: Path) -> list[Path]:
    """Entries of ``folder`` ignoring placeholders / OS noise (.gitkeep etc.)."""
    if not folder.is_dir():
        return []
    return [p for p in folder.iterdir() if p.name not in IGNORED_NAMES and not p.name.startswith(".")]


def _is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTS


def _count_classes(root: Path) -> dict[str, int]:
    """Map class folder name -> image count for the immediate subfolders of ``root``."""
    counts = {}
    for d in sorted(p for p in _visible_entries(root) if p.is_dir()):
        counts[d.name] = sum(1 for f in d.iterdir() if _is_image(f))
    return counts


def _rmtree_quiet(folder: Path) -> None:
    shutil.rmtree(folder, ignore_errors=True)


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------
def _check_credentials() -> None:
    """Fail early with an actionable message if no usable Kaggle credentials exist."""
    cred_file = Path.home() / ".kaggle" / "kaggle.json"
    how_to = (
        "Get a token: Kaggle account -> Settings -> API -> 'Create New Token', then place the\n"
        f"downloaded kaggle.json at {cred_file}"
        + ("\nand run: chmod 600 " + str(cred_file) if os.name != "nt" else "")
    )

    if not cred_file.is_file():
        raise DownloadError(f"Kaggle credentials not found at {cred_file}.\n{how_to}")
    try:
        data = json.loads(cred_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise DownloadError(f"{cred_file} is not valid JSON. Re-download it from Kaggle.\n{how_to}")
    if not isinstance(data, dict) or not data.get("username") or not data.get("key"):
        raise DownloadError(f"{cred_file} must contain non-empty 'username' and 'key' fields.\n{how_to}")

    if os.name != "nt" and cred_file.stat().st_mode & 0o077:
        print(
            f"WARNING: {cred_file} is readable by other users. Run: chmod 600 {cred_file}",
            file=sys.stderr,
        )


# ---------------------------------------------------------------------------
# Download / extract
# ---------------------------------------------------------------------------
def _download_zip(dest_dir: Path) -> Path:
    """Download the dataset archive (unextracted) into ``dest_dir`` and return its path."""
    try:
        # Importing 'kaggle' authenticates immediately and may raise OSError or even
        # call sys.exit() when credentials are bad, so guard the import itself.
        from kaggle.api.kaggle_api_extended import KaggleApi  # type: ignore
    except ImportError:
        raise DownloadError(
            "The 'kaggle' package is not installed. Activate the ml venv and run:\n"
            "  pip install -r ml/requirements.txt"
        )
    except (SystemExit, OSError) as exc:
        raise DownloadError(
            f"Kaggle rejected the credentials while loading the API ({exc}).\n"
            "Check ~/.kaggle/kaggle.json (username + key) or create a new token on Kaggle."
        )

    try:
        api = KaggleApi()
        api.authenticate()
        print(f"Downloading '{DATASET_SLUG}' from Kaggle (this is roughly 1 GB; please wait)...")
        api.dataset_download_files(DATASET_SLUG, path=str(dest_dir), unzip=False, quiet=False)
    except SystemExit as exc:
        raise DownloadError(
            "Kaggle could not authenticate. Check ~/.kaggle/kaggle.json or create a fresh token "
            "(Kaggle account -> Settings -> API -> Create New Token)."
        ) from exc

    zips = sorted(dest_dir.glob("*.zip"))
    if not zips:
        raise DownloadError("Kaggle reported success but no .zip file was downloaded.")
    return zips[0]


def _extract_zip(zip_path: Path, dest_dir: Path) -> None:
    print(f"Extracting {zip_path.name} ...")
    try:
        with zipfile.ZipFile(zip_path) as zf:
            bad = zf.testzip()
            if bad is not None:
                raise DownloadError(f"Downloaded archive is corrupt (bad member: {bad}). Re-run with --force.")
            zf.extractall(dest_dir)  # zipfile strips absolute paths and '..' components
    except zipfile.BadZipFile:
        raise DownloadError("Downloaded file is not a valid zip archive (interrupted download?). Re-run with --force.")


def _find_class_root(extracted: Path) -> Path:
    """Find the class folders, preferring the color images in multi-variant archives."""
    root = extracted
    while True:
        entries = _visible_entries(root)
        color_dirs = [p for p in entries if p.is_dir() and p.name.lower() == "color"]
        if color_dirs and sum(_count_classes(color_dirs[0]).values()) > 0:
            return color_dirs[0]
        if sum(_count_classes(root).values()) > 0:
            return root
        if len(entries) == 1 and entries[0].is_dir():
            root = entries[0]
        else:
            return root


def _install_into_raw(class_root: Path, force: bool) -> None:
    """Build the replacement beside raw/ and swap it in only after it is complete."""
    prepared = STAGING_DIR / "raw"
    backup = STAGING_DIR / "raw_previous"
    if RAW_DIR.exists() and _visible_entries(RAW_DIR) and not force:
        raise DownloadError(f"{RAW_DIR} already contains data. Re-run with --force to replace it.")
    prepared.mkdir()
    try:
        for item in sorted(class_root.iterdir()):
            if item.name in IGNORED_NAMES or item.name.startswith("."):
                continue
            shutil.move(str(item), str(prepared / item.name))

        placeholder = RAW_DIR / ".gitkeep"
        if placeholder.is_file():
            shutil.copy2(placeholder, prepared / placeholder.name)

        if RAW_DIR.exists():
            os.replace(RAW_DIR, backup)
        try:
            os.replace(prepared, RAW_DIR)
        except OSError:
            if backup.exists():
                os.replace(backup, RAW_DIR)
            raise
    except BaseException:
        if backup.exists() and not RAW_DIR.exists():
            os.replace(backup, RAW_DIR)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def run(force: bool) -> None:
    if _visible_entries(RAW_DIR) and not force:
        counts = _count_classes(RAW_DIR)
        print(
            f"{RAW_DIR} already contains data ({len(counts)} class folders, "
            f"{sum(counts.values())} images). Skipping download. Use --force to re-download."
        )
        return

    _check_credentials()

    _rmtree_quiet(STAGING_DIR)  # leftovers from an earlier crashed run
    try:
        STAGING_DIR.mkdir(parents=True)
        zip_path = _download_zip(STAGING_DIR)
        extracted = STAGING_DIR / "extracted"
        extracted.mkdir()
        _extract_zip(zip_path, extracted)
        zip_path.unlink()  # extraction succeeded -> free the disk space
        print("Deleted the downloaded .zip archive.")

        class_root = _find_class_root(extracted)
        counts = _count_classes(class_root)
        if not counts or sum(counts.values()) == 0:
            raise DownloadError(
                "The archive does not look like the expected PlantVillage layout "
                "(<class_name>/*.jpg). Nothing was written to raw/. Check DATASET_SLUG."
            )
        _install_into_raw(class_root, force)
    finally:
        _rmtree_quiet(STAGING_DIR)

    final = _count_classes(RAW_DIR)
    print(f"\nDone. {RAW_DIR}: {len(final)} class folders, {sum(final.values())} images.")
    for name, n in final.items():
        print(f"  {name:<55} {n:>6}")
    empty = [n for n, c in final.items() if c == 0]
    if empty:
        print(f"\nWARNING: {len(empty)} class folder(s) contain no images: {', '.join(empty)}")


# ---------------------------------------------------------------------------
# Error translation + CLI
# ---------------------------------------------------------------------------
def _explain(exc: BaseException) -> str:
    """Turn an unexpected exception into one actionable sentence."""
    if isinstance(exc, DownloadError):
        return str(exc)
    if isinstance(exc, OSError) and exc.errno == errno.ENOSPC:
        return "Disk is full. Free at least ~3 GB in the project folder and run again."
    if isinstance(exc, PermissionError):
        return f"Permission denied: {exc.filename or exc}. Check write access to {DATASET_DIR}."
    text = f"{type(exc).__name__}: {exc}"
    low = text.lower()
    if "401" in low or "unauthorized" in low:
        return "Kaggle rejected your credentials (401). Create a fresh token (Settings -> API -> Create New Token)."
    if "403" in low or "forbidden" in low:
        return (
            "Kaggle refused access (403). Open https://www.kaggle.com/datasets/"
            f"{DATASET_SLUG} while signed in and accept its terms, then retry."
        )
    if "404" in low or "not found" in low:
        return f"Dataset '{DATASET_SLUG}' was not found on Kaggle. Check DATASET_SLUG at the top of this file."
    if any(k in low for k in ("connection", "timeout", "timed out", "max retries", "name resolution", "network")):
        return "Network error while talking to Kaggle. Check your internet connection and retry."
    return f"Unexpected error - {text}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download the PlantVillage dataset from Kaggle into ml/dataset/raw/.")
    parser.add_argument("--force", action="store_true", help="re-download even if ml/dataset/raw/ already has data")
    parser.add_argument("--verbose", action="store_true", help="show the full traceback on failure")
    args = parser.parse_args(argv)

    try:
        run(force=args.force)
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted. Staging files removed; ml/dataset/raw/ was left unchanged.", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001 - deliberate catch-all, translated below
        print(f"\nERROR: {_explain(exc)}", file=sys.stderr)
        if args.verbose:
            traceback.print_exc()
        else:
            print("(re-run with --verbose for technical details)", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
