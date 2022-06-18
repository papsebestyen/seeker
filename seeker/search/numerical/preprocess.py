import pickle
from typing import TYPE_CHECKING, List
from pyparsing import col
from sklearn.neighbors import KDTree
import numpy as np
from abc import ABC, abstractmethod, abstractstaticmethod
import pandas as pd

if TYPE_CHECKING:
    from pathlib import Path
    from seeker.project_config import ProjectConfig

TYPE_CONF = {
    "text": ["txt"],
    "image": ["png", "jpg"],
}
DEFAULT_INDEX = "filename"


class BaseModel(ABC):
    SEARCH_DIST = 'euclidean'

    def __init__(self, conf: "ProjectConfig") -> None:
        self.conf = conf

    @abstractstaticmethod
    def read_file(path: "Path"):
        pass

    @abstractstaticmethod
    def preprocess(data) -> dict:
        pass

    def get_files(self) -> List["Path"]:
        files = []
        for dtype in TYPE_CONF[self.conf.dtype]:
            files.extend([f for f in self.data_dir.glob(f"*.{dtype}")])
        return files

    def load_vectors(self, fname_only: bool = False) -> pd.DataFrame:
        vector_path = self.conf.data_dir / "vectors.parquet"
        if vector_path.exists():
            return pd.read_parquet(
                vector_path, columns=DEFAULT_INDEX if fname_only else None
            )
        else:
            return pd.DataFrame(columns=[DEFAULT_INDEX])

    def get_new_files(self) -> List["Path"]:
        vectors = self.load_vectors(fname_only=True)
        files = self.get_files()
        return [fp for fp in files if fp.name not in vectors[DEFAULT_INDEX]]

    def extend_vectors(self, new_vectors) -> pd.DataFrame:
        vectors = pd.concat([self.load_vectors(), new_vectors])
        vectors.to_parquet(self.conf.data_dir / "vectors.parquet")
        return vectors

    def preprocess_all(self, path_list: List["Path"]) -> pd.DataFrame:
        new_vectors = []
        for fp in path_list:
            new_vectors.append(
                {"filename": fp.name, **self.preprocess(self.read_file(fp))}
            )
        return pd.DataFrame(new_vectors)

    def build_tree(self):
        vectors = self.load_vectors()
        tree = KDTree(vectors.drop(columns=[DEFAULT_INDEX]))
        (self.conf.data_dir / "tree.pickle").write_bytes(pickle.dumps(tree))

class NumericModel(BaseModel):
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


# def build_tree(conf: "ProjectConfig"):
#     raw_data = [
#         preprocess_file(file.read_text()) for file in conf.data_dir.rglob("*.txt")
#     ]
#     return np.array(raw_data, dtype=np.float64)


# def preprocess_numeric_data(data: Iterable) -> KDTree:
#     tree = KDTree(data, leaf_size=1)
#     return tree


# def search_numeric(tree: KDTree, query: Iterable):
#     return tree.query(np.array(query).reshape(1, -1), k=10)
