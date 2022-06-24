from typing import TYPE_CHECKING

import cv2
import numpy as np
import textract
from gensim.models.fasttext import load_facebook_model
from gensim.utils import tokenize
from nltk.tokenize import sent_tokenize

from seeker.namings import DATA_DIR
from seeker.search.base import BaseModel

if TYPE_CHECKING:
    from pathlib import Path

model = load_facebook_model((DATA_DIR / "hu.szte.w2v.fasttext.bin").as_posix())


def clean_text(text: str) -> str:
    toks = tokenize(text=text, to_lower=True)
    return " ".join(toks)


def vec_from_doc(doc: str):
    sentences = sent_tokenize(doc)
    vec = []
    for sent in sentences:
        cleaned = clean_text(sent)
        if cleaned.strip() != "":
            vec.append(model.wv.get_sentence_vector(cleaned))
    return np.array(
        vec,
        dtype=np.float32,
    )


def cluster_matrix(data):
    cv2.setRNGSeed(0)

    if data.shape[0] == 1:
        return [{**{f"dim{d}": v for d, v in enumerate(data[0])}, "freq": 0.2}]

    n_colors = min(data.shape[0], 6)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(
        data, n_colors, None, criteria, 10, flags
    )  # TODO cosine distance
    _, counts = np.unique(labels, return_counts=True)

    return [
        {**{f"dim{d}": v for d, v in enumerate(dim)}, "freq": freq}
        for dim, freq in zip(palette, counts / counts.sum() * 0.2)
    ]


class TextModel(BaseModel):
    SEARCH_DIST = "cosine"

    @staticmethod
    def read_file(path: "Path") -> str:
        return textract.process(filename=path.as_posix()).decode("UTF-8")

    @staticmethod
    def preprocess(data: str):
        return cluster_matrix(vec_from_doc(data))
