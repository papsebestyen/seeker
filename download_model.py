from pathlib import Path

import requests

model_dir = Path("data")
model_dir.mkdir(exist_ok=True)
filename = model_dir / "hu.szte.w2v.fasttext.bin"
url = "http://www.inf.u-szeged.hu/~szantozs/fasttext/hu.szte.w2v.fasttext.bin"
chunk_size = 2_000

resp = requests.get(url, stream=True)

with filename.open(mode="wb") as fd:
    for chunk in resp.iter_content(chunk_size):
        fd.write(chunk)
