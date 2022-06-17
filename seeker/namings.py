from pathlib import Path

DATA_DIR = Path("data")
PROJECT_DIR = DATA_DIR / "projects"

DATA_DIR.mkdir(exist_ok=True)
PROJECT_DIR.mkdir(exist_ok=True)
