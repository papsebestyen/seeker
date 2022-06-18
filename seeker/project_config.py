from typing import TYPE_CHECKING, List
from seeker.namings import PROJECT_DIR
import yaml
from hashlib import md5
import pandas as pd

if TYPE_CHECKING:
    from pathlib import Path

TYPE_CONF = {
    "text": ["txt"],
    "image": ["png", "jpg"],
}

# BIG_MODEL = ...

# class TextModel:

#     def preproc(self, objs):
#         BIG_MODEL.predict(obj)
#         ...

class ProjectConfig:
    def __init__(self, name: str, dtype: str):
        self.name = name.strip()
        self.id = self.get_id(name)
        self.dtype = dtype
        self.data_dir = PROJECT_DIR / f"{self.id}"
        self.data_dir.mkdir(exist_ok=True)
        # self.save_config() #TODO

    @staticmethod
    def get_id(name):
        return md5(name.encode()).hexdigest()

    def get_files(self) -> List["Path"]:
        files = []
        for dtype in TYPE_CONF[self.dtype]:
            files.extend([f for f in self.data_dir.glob(f"*.{dtype}")])
        return files

    def get_file_count(self) -> int:
        return len(self.get_files())

    def save_config(self, fp: "Path" = None):
        fp = fp or self.data_dir
        (fp / "config.yaml").write_text(
            yaml.safe_dump({"name": self.name, "dtype": self.dtype})
        )

    @classmethod
    def from_file(cls, file: "Path"):
        conf = yaml.safe_load(file.read_text())
        return cls(name=conf["name"].strip(), dtype=conf["dtype"])

    @classmethod
    def from_name(cls, name: str):
        data_dir = PROJECT_DIR / f"{cls.get_id(name)}"
        return cls.from_file(file=data_dir / "config.yaml")


def load_all_config():
    return [ProjectConfig.from_file(conf) for conf in PROJECT_DIR.rglob("*.yaml")]
