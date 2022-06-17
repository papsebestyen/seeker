from typing import TYPE_CHECKING, Iterable
from sklearn.neighbors import KDTree
import numpy as np

if TYPE_CHECKING:
    from seeker.project_config import ProjectConfig

def read_numeric_data(conf: 'ProjectConfig'):
    raw_data = [np.array(file.read_text().split(' '), dtype=np.float64) for file in conf.data_dir.rglob('*.txt')]
    return np.array(raw_data, dtype=np.float64)

def preprocess_numeric_data(data: Iterable) -> KDTree:
    tree = KDTree(data, leaf_size=1)
    return tree

def search_numeric(tree: KDTree, query: Iterable):
    return tree.query(np.array(query).reshape(1, -1) , k = 10)