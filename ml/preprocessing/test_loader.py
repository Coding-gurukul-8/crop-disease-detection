
"""
Unit tests for the image loader (Prompt 23).
"""

from pathlib import Path

import numpy as np
import pytest

from ml.preprocessing.loader import (
    ImageLoadError,
    load_and_preprocess_image,
)


FIXTURES_DIR = Path(__file__).parent / "test_fixtures"
VALID_IMAGE = FIXTURES_DIR / "sample_leaf.png"
CORRUPTED_IMAGE = FIXTURES_DIR / "corrupted.png"


def test_output_shape():
    image = load_and_preprocess_image(str(VALID_IMAGE))
    assert image.shape == (224, 224, 3)


def test_output_dtype():
    image = load_and_preprocess_image(str(VALID_IMAGE))
    assert image.dtype == np.float32


def test_pixel_values_in_range():
    image = load_and_preprocess_image(str(VALID_IMAGE))
    assert np.min(image) >= 0.0
    assert np.max(image) <= 1.0


def test_corrupted_image_raises_error():
    with pytest.raises(ImageLoadError):
        load_and_preprocess_image(str(CORRUPTED_IMAGE))


def test_path_and_bytes_produce_identical_output():
    image_from_path = load_and_preprocess_image(str(VALID_IMAGE))

    image_bytes = VALID_IMAGE.read_bytes()
    image_from_bytes = load_and_preprocess_image(image_bytes)

    assert np.allclose(image_from_path, image_from_bytes)

