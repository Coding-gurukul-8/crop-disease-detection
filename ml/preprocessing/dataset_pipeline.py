
"""
TensorFlow dataset pipeline for crop disease detection.

Loads train, validation, and test datasets from the split directory.
All images are resized to 224x224 and normalized to [0, 1].

Batching is handled by image_dataset_from_directory() using batch_size.
Validation and test datasets are cached after rescaling.
Prefetching is applied to all three datasets for better performance.

Augmentation is NOT applied here.
It must be applied separately to the training dataset only.
"""

import os
import tempfile
from pathlib import Path
from typing import Tuple, List

import tensorflow as tf


def build_datasets(
    split_dir="ml/dataset/split",
    image_size=(224, 224),
    batch_size=32,
    cache_to_disk=False
) -> Tuple[
    tf.data.Dataset,
    tf.data.Dataset,
    tf.data.Dataset,
    List[str],
]:
    """
    Build train, validation, and test datasets.

    Batching:
        Already performed by image_dataset_from_directory()
        through its batch_size argument.

    Caching:
        Validation and test datasets are cached after rescaling.
        In-memory caching stores the complete datasets in RAM
        after the first complete pass.

        Use cache_to_disk=True to store cache files in the
        system temporary directory when RAM is limited.

        Training data is intentionally NOT cached because
        fresh augmentation should be applied during training.

    Prefetching:
        Uses tf.data.AUTOTUNE to prepare batches ahead of time.

    Returns:
        train_ds: Prefetched training dataset.
        val_ds: Cached and prefetched validation dataset.
        test_ds: Cached and prefetched test dataset.
        class_names: Ordered list of class names.
    """

    split_path = Path(split_dir)

    train_path = split_path / "train"
    val_path = split_path / "val"
    test_path = split_path / "test"

    # Check that all required directories exist.
    for directory in [train_path, val_path, test_path]:
        if not directory.is_dir():
            raise FileNotFoundError(
                f"Dataset directory not found: {directory.resolve()}"
            )

    # Load training dataset with shuffling and fixed seed.
    # Batching is already applied through batch_size.
    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_path,
        label_mode="categorical",
        image_size=image_size,
        batch_size=batch_size,
        shuffle=True,
        seed=42,
    )

    # Load validation dataset without shuffling.
    val_ds = tf.keras.utils.image_dataset_from_directory(
        val_path,
        label_mode="categorical",
        image_size=image_size,
        batch_size=batch_size,
        shuffle=False,
    )

    # Load test dataset without shuffling.
    test_ds = tf.keras.utils.image_dataset_from_directory(
        test_path,
        label_mode="categorical",
        image_size=image_size,
        batch_size=batch_size,
        shuffle=False,
    )

    # Extract class names and verify identical ordering.
    class_names = train_ds.class_names

    if val_ds.class_names != class_names:
        raise ValueError(
            "Validation dataset class names or ordering "
            "do not match the training dataset."
        )

    if test_ds.class_names != class_names:
        raise ValueError(
            "Test dataset class names or ordering "
            "do not match the training dataset."
        )

    # Expected project classes.
    if len(class_names) != 8:
        raise ValueError(
            f"Expected exactly 8 classes, found {len(class_names)}: "
            f"{class_names}"
        )

    # TODO: When Prompt 43 creates class_names.json,
    # verify that its class order matches this class_names list.

    # Normalize image pixels from [0, 255] to [0, 1].
    rescaling_layer = tf.keras.layers.Rescaling(1.0 / 255)

    train_ds = train_ds.map(
        lambda images, labels: (
            rescaling_layer(images),
            labels,
        ),
        num_parallel_calls=tf.data.AUTOTUNE,
    )

    val_ds = val_ds.map(
        lambda images, labels: (
            rescaling_layer(images),
            labels,
        ),
        num_parallel_calls=tf.data.AUTOTUNE,
    )

    test_ds = test_ds.map(
        lambda images, labels: (
            rescaling_layer(images),
            labels,
        ),
        num_parallel_calls=tf.data.AUTOTUNE,
    )

    # Do not cache train_ds.
    # Training augmentation should generate fresh variations
    # during training.

    # Cache validation and test datasets AFTER rescaling.
    # In-memory caching uses RAM after the first complete pass.
    if cache_to_disk:
        cache_dir = tempfile.gettempdir()

        val_ds = val_ds.cache(
            filename=os.path.join(
                cache_dir, "crop_disease_val_cache"
            )
        )

        test_ds = test_ds.cache(
            filename=os.path.join(
                cache_dir, "crop_disease_test_cache"
            )
        )
    else:
        val_ds = val_ds.cache()
        test_ds = test_ds.cache()

    # Preserve class-name metadata after mapping and caching.
    train_ds.class_names = class_names
    val_ds.class_names = class_names
    test_ds.class_names = class_names

    # Prefetching is the final pipeline step.
    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    test_ds = test_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    return train_ds, val_ds, test_ds, class_names
