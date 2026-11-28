
"""
Keras image augmentation pipeline.

Apply this ONLY to the training dataset split.
Never apply to validation or test data.

Input images:
- Shape: (224, 224, 3)
- Pixel range: [0, 1]

Augmentation uses realistic transformations:
- Rotation: 15% of a full turn range
- Horizontal flip only
- Zoom: 10%
- Translation: 10% horizontally and vertically
- Brightness: 15%
"""

import tensorflow as tf


def get_augmentation_pipeline() -> tf.keras.Sequential:
    """
    Create and return the training image augmentation pipeline.

    Returns:
        tf.keras.Sequential: A sequence of random image
        preprocessing layers.
    """

    augmentation = tf.keras.Sequential(
        [
            tf.keras.layers.RandomRotation(0.15),
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomZoom(0.1),
            tf.keras.layers.RandomTranslation(0.1, 0.1),
            tf.keras.layers.RandomBrightness(
                0.15, 
                value_range=(0, 1)
            ),
        ],
        name="training_augmentation",
    )

    return augmentation

