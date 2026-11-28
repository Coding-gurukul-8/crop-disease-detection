
from pathlib import Path
from sklearn.model_selection import train_test_split

DATASET_DIR = Path(__file__).resolve().parent
SOURCE_DIR = DATASET_DIR / "filtered"
SPLIT_DIR = DATASET_DIR / "split"

EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
SEED = 42


def get_images(folder):
    return sorted(
        [
            p for p in folder.rglob("*")
            if p.is_file() and p.suffix.lower() in EXTENSIONS
        ],
        key=lambda p: p.relative_to(folder).as_posix().lower()
    )


def main():
    files = []
    labels = []

    for class_dir in sorted(SOURCE_DIR.iterdir()):
        if not class_dir.is_dir():
            continue

        images = get_images(class_dir)
        files.extend(images)
        labels.extend([class_dir.name] * len(images))

    train_files, temp_files, train_labels, temp_labels = (
        train_test_split(
            files, labels,
            test_size=0.30,
            random_state=SEED,
            stratify=labels
        )
    )

    val_files, test_files, _, _ = train_test_split(
        temp_files,
        temp_labels,
        test_size=0.50,
        random_state=SEED,
        stratify=temp_labels
    )

    expected = set()

    for split_name, split_files in [
        ("train", train_files),
        ("val", val_files),
        ("test", test_files)
    ]:
        for source in split_files:
            class_name = source.parent.name
            relative = source.relative_to(
                SOURCE_DIR / class_name
            )
            expected.add(
                (Path(split_name) / class_name / relative).as_posix()
            )

    actual = {
        p.relative_to(SPLIT_DIR).as_posix()
        for p in SPLIT_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSIONS
    }

    missing = expected - actual
    extra = actual - expected

    print("Expected files:", len(expected))
    print("Actual files:", len(actual))
    print("Missing files:", len(missing))
    print("Extra files:", len(extra))

    if expected == actual:
        print("\nPASS: Existing split matches the reproducible seed-42 split.")
    else:
        print("\nFAIL: Split does not match the expected result.")

        if missing:
            print("Example missing:", next(iter(missing)))

        if extra:
            print("Example extra:", next(iter(extra)))


if __name__ == "__main__":
    main()
