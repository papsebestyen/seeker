from typing import TYPE_CHECKING
from seeker.namings import PROJECT_DIR
import yaml

if TYPE_CHECKING:
    from pathlib import Path


class ProjectConfig:
    def __init__(self, name=str):
        self.name = name.strip()
        self.id = hash(name)
        self.data_dir = PROJECT_DIR / f"{self.id}"
        self.data_dir.mkdir(exist_ok=True)

    def save_config(self, fp: "Path" = None):
        fp = fp or self.data_dir
        (fp / "config.yaml").write_text(yaml.safe_dump({"name": self.name}))

    @classmethod
    def load_config(cls, fp: "Path"):
        conf = yaml.safe_load(fp.read_text())
        return cls(name=conf["name"].strip())

def load_all_config():
    return [ProjectConfig.load_config(conf) for conf in PROJECT_DIR.rglob('*.yaml')]
