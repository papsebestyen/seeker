import cv2
import numpy as np
import pandas as pd

from typing import TYPE_CHECKING
from seeker.search.base import BaseModel
from sklearn.cluster import KMeans
from sklearn.neighbors import KDTree

if TYPE_CHECKING:
    from pathlib import Path

df = pd.DataFrame(columns=["R", "G", "B", "pc"])
file_exts = ["jpg", "jpeg", "JPG", "png"]


def dominant_color(img, data):
    pixels = np.float32(img.reshape(-1, 3))
    pixels = pixels[np.random.choice(pixels.shape[0], 100_000), :]
    n_colors = 5
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 5, flags)
    _, counts = np.unique(labels, return_counts=True)
    dominant = palette[np.argmax(counts)]
    data = pd.DataFrame(
        np.append(dominant.tolist(), np.max(counts) / sum(counts)).reshape(1, -1),
        index=[str(str(image).split("/")[1])],
        columns=data.columns,
    )
    return data


class NumericModel(BaseModel):
    SEARCH_DIST = "euclidean"

    @staticmethod
    def read_file(path: "Path"):
        return cv2.cvtColor(
            cv2.imread(path), cv2.COLOR_BGR2RGB
        )  # itt szopja be a png-t

    @staticmethod
    def preprocess(data: str):

        df = dominant_color(data, df)

        return df.to_dict(orient="records")[0]
