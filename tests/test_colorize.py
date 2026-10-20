import os
import sys

import cv2
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import colorize


class FakeNet:
    """Stands in for the Caffe network: predicts a/b = 0 (no colour) at its 56x56 output size."""

    def setInput(self, blob):
        assert blob.shape == (1, 1, 224, 224)

    def forward(self):
        return np.zeros((1, 2, 56, 56), dtype="float32")


@pytest.fixture(autouse=True)
def fake_model(monkeypatch):
    monkeypatch.setattr(colorize, "_load_model", lambda: (FakeNet(), None))


def write_gray(path, width, height):
    gradient = np.tile(np.linspace(0, 255, width, dtype="uint8"), (height, 1))
    cv2.imwrite(str(path), cv2.cvtColor(gradient, cv2.COLOR_GRAY2BGR))


def test_small_image_keeps_its_size(tmp_path):
    src, out = tmp_path / "in.png", tmp_path / "out.png"
    write_gray(src, 300, 200)

    colorize.colorize_image(str(src), str(out))

    assert cv2.imread(str(out)).shape == (200, 300, 3)


def test_large_image_is_capped_to_max_side(tmp_path):
    src, out = tmp_path / "in.png", tmp_path / "out.png"
    write_gray(src, 3000, 1500)

    colorize.colorize_image(str(src), str(out), max_side=1000)

    assert cv2.imread(str(out)).shape == (500, 1000, 3)


def test_zero_ab_keeps_a_gray_image_gray(tmp_path):
    src, out = tmp_path / "in.png", tmp_path / "out.png"
    write_gray(src, 64, 32)

    colorize.colorize_image(str(src), str(out))

    result = cv2.imread(str(out)).astype(int)
    original = cv2.imread(str(src)).astype(int)
    assert np.abs(result - original).max() <= 2  # L survives the LAB round trip


def test_unreadable_file_raises_value_error(tmp_path):
    src = tmp_path / "broken.jpg"
    src.write_bytes(b"not an image")

    with pytest.raises(ValueError):
        colorize.colorize_image(str(src), str(tmp_path / "out.png"))
