from typing import TYPE_CHECKING
from seeker.search.base import BaseModel
from gensim.utils import tokenize
import numpy as np
from gensim.models.fasttext import load_facebook_model
import textract
from seeker.namings import DATA_DIR

model = load_facebook_model((DATA_DIR/"hu.szte.w2v.fasttext.bin").as_posix())
if TYPE_CHECKING:
    from pathlib import Path


class TextModel(BaseModel):
    SEARCH_DIST = "cosine"

    @staticmethod
    def read_file(path: "Path"):
        doc = textract.process(path).decode("UTF-8").replace("\n", " ")
        tokens = tokenize(doc)
        return tokens

    @staticmethod
    def preprocess(data: str):
        return np.nanmean(
            np.array([model.wv.get_vector(word) for word in data]), axis=0
        )
