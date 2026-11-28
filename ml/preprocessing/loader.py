
"""
Image loader and preprocessing module.

Loads images from file paths or raw bytes, converts them to RGB,
resizes them to 224x224 using bilinear interpolation, and normalizes
pixel values to the range [0, 1].
"""

from typing import Union, Tuple
from io import BytesIO

import numpy as np
from PIL import Image


class ImageLoadError(Exception):
    """Raised when an image cannot be loaded or preprocessed."""
    pass


def load_and_preprocess_image(
    path_or_bytes: Union[str, bytes],
    target_size: Tuple[int, int] = (224, 224)
) -> np.ndarray:
    """
    Load and preprocess an image.

    Args:
        path_or_bytes: Image file path or raw image bytes.
        target_size: Target size as (width, height).

    Returns:
        A float32 NumPy array with shape (height, width, 3)
        and pixel values normalized to [0, 1].

    Raises:
        ImageLoadError: If the image cannot be loaded or processed.
    """

    try:
        # Open image from a file path or raw bytes
        if isinstance(path_or_bytes, bytes):
            image_source = BytesIO(path_or_bytes)
        elif isinstance(path_or_bytes, str):
            image_source = path_or_bytes
        else:
            raise ImageLoadError(
                "Input must be a file path (str) or raw image bytes."
            )

        with Image.open(image_source) as img:

            # Convert grayscale, RGBA, etc. into RGB
            img = img.convert("RGB")

            # Resize using bilinear interpolation
            img = img.resize(target_size, Image.BILINEAR)

            # Convert to float32 NumPy array
            image_array = np.asarray(img, dtype=np.float32)

            # Normalize pixel values from [0, 255] to [0, 1]
            image_array = image_array / 255.0

        # Verify output shape
        expected_shape = (target_size[1], target_size[0], 3)
        assert image_array.shape == expected_shape, (
            f"Expected shape {expected_shape}, "
            f"but got {image_array.shape}"
        )

        return image_array

    except ImageLoadError:
        raise

    except Exception as exc:
        raise ImageLoadError(
            f"Could not load or preprocess image: {exc}"
        ) from exc
