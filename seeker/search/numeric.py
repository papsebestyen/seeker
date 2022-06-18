from typing import TYPE_CHECKING
from seeker.search.base import BaseModel

if TYPE_CHECKING:
    from pathlib import Path


class NumericModel(BaseModel):
    SEARCH_DIST = "euclidean"

    @staticmethod
    def read_file(path: "Path"):
        return path.read_text()

    @staticmethod
    def preprocess(data: str):
        return {
            "V1": data.split(" ")[0],
            "V2": data.split(" ")[1],
            "V3": data.split(" ")[2],
        }
