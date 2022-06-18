from typing import TYPE_CHECKING
from seeker.search.base import BaseModel
#model = load_facebook_model('hu.szte.w2v.fasttext.bin')

if TYPE_CHECKING:
    from pathlib import Path


class NumericModel(BaseModel):
    SEARCH_DIST = "cosine"

    @staticmethod
    def read_file(path: "Path"):
        doc = textract.process(path).decode("UTF-8").replace("\n", " ")
        tokens = tokenize(doc)
        return tokens

    @staticmethod
    def preprocess(data: str):
        return np.nanmean(np.array([model.wv.get_vector(word) for word in data]), axis=0)