from typing import TYPE_CHECKING

import cv2
import numpy as np

from seeker.search.base import BaseModel

if TYPE_CHECKING:
    from pathlib import Path

file_exts = ["jpg", "jpeg", "JPG", "png"]


def dominant_colors(img):
    cv2.setRNGSeed(0)
    np.random.seed(0)

    pixels = np.float32(img.reshape(-1, 3))
    pixels = pixels[np.random.choice(pixels.shape[0], 100_000), :]

    n_colors = 6
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)

    return [
        {"r": color[0], "g": color[1], "b": color[2], "freq": freq}
        for color, freq in zip(palette, counts / counts.sum() * 100)
    ]


class ImageModel(BaseModel):
    SEARCH_DIST = "euclidean"

    @staticmethod
    def read_file(path: "Path") -> np.array:
        return cv2.cvtColor(cv2.imread(filename=path.as_posix()), cv2.COLOR_BGR2RGB)

    @staticmethod
    def preprocess(data: str):
        return dominant_colors(data)

    @staticmethod
    def rgb_hex_to_dec(rgb_hex: str) -> np.array:
        rgb_hex = rgb_hex.strip("#")
        r, g, b = [int(rgb_hex[c * 2 : c * 2 + 2], base=16) for c in range(3)]
        return np.array([r, g, b], dtype=np.float32)
