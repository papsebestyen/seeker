from typing import TYPE_CHECKING

import cv2
import numpy as np

from seeker.search.base import BaseModel

if TYPE_CHECKING:
    from pathlib import Path

file_exts = ["jpg", "jpeg", "JPG", "png"]


def dominant_colors(img):

    pixels = np.float32(img.reshape(-1, 3))
    pixels = pixels[np.random.choice(pixels.shape[0], 100_000), :]

    n_colors = 6
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)

    cluster_list = []
    [
        cluster_list.append(clusters)
        for clusters in zip(palette, counts / counts.sum() * 100)
    ]

    a = [
        ([row for row in cluster_list[i][0]], cluster_list[i][1].reshape(1, -1))
        for i in range(len(cluster_list))
    ]

    a = [np.append(a[i][0][0:3], a[i][1][0][0]) for i in range(len(a))]

    return a


class ImageModel(BaseModel):
    SEARCH_DIST = "euclidean"

    @staticmethod
    def read_file(path: "Path") -> np.array:
        return cv2.cvtColor(cv2.imread(filename=path.as_posix()), cv2.COLOR_BGR2RGB)

    @staticmethod
    def preprocess(data: str):
        dom_colors = dominant_colors(data)
        return [{str(k): v for k, v in enumerate(i)} for i in dom_colors]

    @staticmethod
    def rgb_hex_to_dec(rgb_hex: str) -> np.array:
        rgb_hex = rgb_hex.strip("#")
        r, g, b = [int(rgb_hex[c * 2 : c * 2 + 2], base=16) for c in range(3)]
        return np.array([r, g, b], dtype=np.float32)
