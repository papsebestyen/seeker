from typing import TYPE_CHECKING
from seeker.search.base import BaseModel
from gensim.utils import tokenize
from gensim.models.fasttext import load_facebook_model
import textract
from seeker.namings import DATA_DIR

if TYPE_CHECKING:
    from pathlib import Path

model = load_facebook_model((DATA_DIR / "hu.szte.w2v.fasttext.bin").as_posix())


def clean_text(text: str) -> str:
    toks = tokenize(text=text, to_lower=True)
    return " ".join(toks)


class TextModel(BaseModel):
    SEARCH_DIST = "cosine"

    @staticmethod
    def read_file(path: "Path") -> str:
        return textract.process(filename=path.as_posix()).decode("UTF-8")

    @staticmethod
    def preprocess(data: str):
        cleaned_data = clean_text(data)
        vec = model.wv.get_sentence_vector(cleaned_data)
        return {str(k): v for k, v in enumerate(vec)}
