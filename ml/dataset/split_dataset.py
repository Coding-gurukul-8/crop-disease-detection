
from pathlib import Path
import argparse
import shutil
import sys

from sklearn.model_selection import train_test_split


# Project folder paths
DATASET_DIR = Path(__file__).resolve().parent
SOURCE_DIR = DATASET_DIR / "filtered"
OUTPUT_DIR = DATASET_DIR / "split"

# Reproducible split settings
RANDOM_STATE = 42
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

def get_images(class_dir):
    """Return supported image files in a predictable order."""
    return sorted(
        [
            path for path in class_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        ],
        key=lambda path: path.relative_to(class_dir).as_posix().lower()
    )


def main():
    parser = argparse.ArgumentParser(
        description="Create a stratified 70/15/15 dataset split."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace the existing split folder."
    )
    args = parser.parse_args()

    # Check source folder
    if not SOURCE_DIR.is_dir():
        print(f"ERROR: Source folder not found: {SOURCE_DIR}")
        sys.exit(1)

    class_dirs = sorted(
        [path for path in SOURCE_DIR.iterdir() if path.is_dir()],
        key=lambda path: path.name.lower()
    )

    if not class_dirs:
        print("ERROR: No class folders found in filtered/.")
        sys.exit(1)

    # Collect all image paths and their class labels
    all_files = []
    all_labels = []
    original_counts = {}

    for class_dir in class_dirs:
        images = get_images(class_dir)
        count = len(images)

        if count < 4:
            print(
                f"ERROR: Class '{class_dir.name}' has only {count} images. "
                "At least 4 are needed for this split."
            )
            sys.exit(1)

        original_counts[class_dir.name] = count
        all_files.extend(images)
        all_labels.extend([class_dir.name] * count)

    print(f"Classes found: {len(class_dirs)}")
    print(f"Total images: {len(all_files)}")

    # Protect an existing split
    if OUTPUT_DIR.exists():
        if not args.force:
            answer = input(
                "\nThe split folder already exists. "
                "Replace it? Type YES to continue: "
            ).strip()

            if answer != "YES":
                print("Cancelled. Existing split was not changed.")
                return

        # Safety check before deleting anything
        if OUTPUT_DIR.resolve().parent != DATASET_DIR.resolve():
            print("ERROR: Unsafe output path. Stopping.")
            sys.exit(1)

        shutil.rmtree(OUTPUT_DIR)

    # First split: 70% train, 30% temporary
    train_files, temp_files, train_labels, temp_labels = train_test_split(
        all_files,
        all_labels,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=all_labels
    )

    # Second split: divide the temporary 30% into 15% val and 15% test
    val_files, test_files, val_labels, test_labels = train_test_split(
        temp_files,
        temp_labels,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=temp_labels
    )

    split_data = {
        "train": (train_files, train_labels),
        "val": (val_files, val_labels),
        "test": (test_files, test_labels),
    }

    # Create class folders and COPY images (never move them)
    for split_name, (files, labels) in split_data.items():
        for class_dir in class_dirs:
            (OUTPUT_DIR / split_name / class_dir.name).mkdir(
                parents=True,
                exist_ok=True
            )

        for source_file, class_name in zip(files, labels):
            relative_path = source_file.relative_to(
                SOURCE_DIR / class_name
            )
            destination = (
                OUTPUT_DIR / split_name / class_name / relative_path
            )
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, destination)

   
    # Count actual copied images and verify no images were lost
    print("\n=== FINAL SPLIT COUNTS ===")
    print(
        f"{'Class':35} {'Original':>9} "
        f"{'Train':>8} {'Val':>8} {'Test':>8} {'Total':>8} {'Check':>8}"
    )
    print("-" * 90)

    all_passed = True
    total_train = total_val = total_test = 0

    for class_dir in class_dirs:
        name = class_dir.name

        train_count = len(get_images(OUTPUT_DIR / "train" / name))
        val_count = len(get_images(OUTPUT_DIR / "val" / name))
        test_count = len(get_images(OUTPUT_DIR / "test" / name))

        total = train_count + val_count + test_count
        passed = total == original_counts[name]
        all_passed = all_passed and passed

        total_train += train_count
        total_val += val_count
        total_test += test_count

        print(
            f"{name:35} {original_counts[name]:9} "
            f"{train_count:8} {val_count:8} {test_count:8} "
            f"{total:8} {'PASS' if passed else 'FAIL':>8}"
        )

    print("-" * 90)
    print(
        f"{'TOTAL':35} {len(all_files):9} "
        f"{total_train:8} {total_val:8} {total_test:8} "
        f"{total_train + total_val + total_test:8}"
    )

    if all_passed and total_train + total_val + total_test == len(all_files):
        print("\nSUCCESS: All copied image counts match the source.")
        print(f"Split folders created at: {OUTPUT_DIR}")
        print(f"Random state: {RANDOM_STATE}")
    else:
        print("\nERROR: Count mismatch detected. Check the split folders.")
        sys.exit(1)

