from typing import TYPE_CHECKING
from seeker.namings import PROJECT_DIR
import yaml
from hashlib import md5

if TYPE_CHECKING:
    from pathlib import Path

TYPE_CONF = {
    "text": ["txt"],
    "image": ["png", "jpg"],
}


class ProjectConfig:
    def __init__(self, name: str, dtype: str):
        self.name = name.strip()
        self.id = md5(name.encode()).hexdigest()
        self.dtype = dtype
        self.data_dir = PROJECT_DIR / f"{self.id}"
        self.data_dir.mkdir(exist_ok=True)

    def get_file_count(self) -> int:
        return len(
            [f for f in self.data_dir.glob("*.txt")]
        )  # TODO make universal for all extensions

    def get_dtype(self):
        suffixes = set([f.suffix.strip(".") for f in self.data_dir.iterdir()])
        dtype = suffixes.difference({"yaml", "pickle"})
        assert len(dtype) == 1  # TODO using jpg and png together
        self.dtype = dtype

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
        data_dir = PROJECT_DIR / f"{md5(name.encode()).hexdigest()}"
        return cls.from_file(file=data_dir / "config.yaml")


def load_all_config():
    return [ProjectConfig.from_file(conf) for conf in PROJECT_DIR.rglob("*.yaml")]
