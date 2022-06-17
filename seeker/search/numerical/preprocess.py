from typing import TYPE_CHECKING, Iterable
from sklearn.neighbors import KDTree
import numpy as np

if TYPE_CHECKING:
    from seeker.project_config import ProjectConfig

def read_numeric_data(conf: 'ProjectConfig'):
    raw_data = [file.read_text() for file in conf.data_dir.rglob('*.txt')]
    return np.array(raw_data, dtype=np.float64).reshape(1, -1)

def preprocess_numeric_data(data: Iterable):
    tree = KDTree(data, leaf_size=1)
    return tree

def search_numeric(tree: KDTree, query: float):
    return tree.query(query, k = 10)