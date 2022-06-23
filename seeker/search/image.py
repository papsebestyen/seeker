import cv2
import numpy as np
import pandas as pd

from typing import TYPE_CHECKING
from seeker.search.base import BaseModel

if TYPE_CHECKING:
    from pathlib import Path

df = pd.DataFrame(columns=["R", "G", "B", "pc"])
file_exts = ["jpg", "jpeg", "JPG", "png"]


def dominant_color(img):
    pixels = np.float32(img.reshape(-1, 3))
    pixels = pixels[np.random.choice(pixels.shape[0], 100_000), :]
    n_colors = 5
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 5, flags)
    _, counts = np.unique(labels, return_counts=True)
    dominant = palette[np.argmax(counts)]
    return dominant
    # data = pd.DataFrame(
    #     np.append(dominant.tolist(), np.max(counts) / sum(counts)).reshape(1, -1),
    #     index=[str(str(img).split("/")[1])],
    #     columns=data.columns,
    # )
    # return data


class ImageModel(BaseModel):
    SEARCH_DIST = "euclidean"

    @staticmethod
    def read_file(path: "Path") -> np.array:
        return cv2.cvtColor(cv2.imread(filename=path.as_posix()), cv2.COLOR_BGR2RGB)

    @staticmethod
    def preprocess(data: str):
        dom_color = dominant_color(data)
        return {str(k): v for k, v in enumerate(dom_color)}

    @staticmethod
    def rgb_hex_to_dec(rgb_hex: str) -> np.array:
        rgb_hex = rgb_hex.strip("#")
        r, g, b = [int(rgb_hex[c * 2 : c * 2 + 2], base=16) for c in range(3)]
        return np.array([r, g, b], dtype=np.float32)
