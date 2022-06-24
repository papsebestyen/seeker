import pickle
from abc import ABC, abstractstaticmethod
from typing import TYPE_CHECKING, List

import pandas as pd
from sklearn.neighbors import NearestNeighbors

if TYPE_CHECKING:
    from pathlib import Path

    from seeker.project_config import ProjectConfig

TYPE_CONF = {
    "text": ["txt"],
    "image": ["png", "jpg"],
}

DEFAULT_INDEX = "filename"


class BaseModel(ABC):
    SEARCH_DIST = "euclidean"

    def __init__(self, conf: "ProjectConfig") -> None:
        self.conf = conf

    @abstractstaticmethod
    def read_file(path: "Path"):
        pass

    @abstractstaticmethod
    def preprocess(data) -> List[dict]:
        pass

    def get_files(self) -> List["Path"]:
        files = []
        for dtype in TYPE_CONF[self.conf.dtype]:
            files.extend([f for f in self.data_dir.glob(f"*.{dtype}")])
        return files

    def load_vectors(self, fname_only: bool = False) -> pd.DataFrame:
        vector_path = self.conf.project_dir / "vectors.parquet"
        if vector_path.exists():
            return pd.read_parquet(
                vector_path, columns=[DEFAULT_INDEX] if fname_only else None
            )
        else:
            return pd.DataFrame(columns=[DEFAULT_INDEX])

    def get_new_files(self) -> List["Path"]:
        vectors = self.load_vectors(fname_only=True)
        files = self.get_files()
        return [fp for fp in files if fp.name not in vectors[DEFAULT_INDEX]]

    def extend_vectors(self, new_vectors) -> pd.DataFrame:
        vectors = pd.concat([self.load_vectors(), new_vectors])
        vectors.to_parquet(self.conf.project_dir / "vectors.parquet")
        return vectors

    def preprocess_all(self, path_list: List["Path"]) -> pd.DataFrame:
        new_vectors = []
        for fp in path_list:
            new_vectors.extend(
                [
                    {"filename": fp.name, **comp}
                    for comp in self.preprocess(self.read_file(fp))
                ]
            )
        return pd.DataFrame(new_vectors)

    def build_tree(self, vectors=None):
        vectors = vectors if vectors is not None else self.load_vectors()
        tree = NearestNeighbors(
            n_neighbors=10,
            algorithm="auto",
            metric=self.SEARCH_DIST,
            leaf_size=30,
            n_jobs=-1,
        ).fit(vectors.drop(columns=[DEFAULT_INDEX]))
        (self.conf.project_dir / "tree.pickle").write_bytes(pickle.dumps(tree))

    def search(self, query):
        tree = pickle.loads((self.conf.project_dir / "tree.pickle").read_bytes())
        to_search = max(self.preprocess(query), key=lambda x: x["freq"])
        ind = tree.kneighbors(
            pd.DataFrame([to_search]), n_neighbors=3, return_distance=False
        )
        vectors = self.load_vectors(fname_only=True)
        return vectors.iloc[ind[0]][DEFAULT_INDEX].values
