from typing import TYPE_CHECKING, List

from attr import field
from seeker.namings import PROJECT_DIR
import yaml
from hashlib import md5
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from pathlib import Path

TYPE_CONF = {
    "text": ["txt"],
    "image": ["png", "jpg"],
}


def name_to_id(name: str) -> str:
    return md5(name.encode()).hexdigest()


@dataclass
class ProjectConfig:
    name: str
    dtype: str
    id: str = field(init=False)
    data_dir: "Path" = field(init=False)

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        self.id = name_to_id(self.name)
        self.data_dir = PROJECT_DIR / f"{self.id}"
        self.data_dir.mkdir(exist_ok=True)

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
        return cls(name=conf["name"], dtype=conf["dtype"])

    @classmethod
    def from_name(cls, name: str):
        return cls.from_file(file=PROJECT_DIR / name_to_id(name) / "config.yaml")


def load_all_config():
    return [ProjectConfig.from_file(conf) for conf in PROJECT_DIR.rglob("*.yaml")]
